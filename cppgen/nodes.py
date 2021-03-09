from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractproperty
import re
from cppgen.utils import ptn, recur_ptn, xstrip
import cppgen.convention as convention

class Ptn:
    IDENTIFIER = r'(?:[a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)'
    BLOCK = recur_ptn(r'(?:{(?:[^{}]|(?:?R))*})')

    NAMESPACE_START = ptn(rf'namespace ({IDENTIFIER})\s*')

    TEMPLATE_PARAMS = recur_ptn(r'(?:<(?:[^<>]|(?:?R))*>)')
    TEMPLATE = ptn(rf'template ({TEMPLATE_PARAMS})')

    CLASS_START = ptn(rf'(?:{TEMPLATE} )?(class|struct) ({IDENTIFIER})\s*')
    CLASS_BLOCK = ptn(rf'({BLOCK})\s*;')

    TYPE_TMP = recur_ptn(r'(?:[<(](?:[^<>()]|(?:?R))*[)>])')
    TYPE = ptn(rf'(?:const )?(?:{IDENTIFIER})\s*(?:{TYPE_TMP})?(?: |\s*\*+\s*)(?:const)?\s*&*')

    FUNC_HEAD_SPECIFIER = r'(?:static|inline|_Noreturn)'
    FUNC_TAIL_SPECIFIER = r'(?:const|(?:noexcept|throw)(?:\([^()]*\))?)'
    FUNC = ptn(rf'(?:{TEMPLATE} )?({FUNC_HEAD_SPECIFIER}(?: {FUNC_HEAD_SPECIFIER})*)?({TYPE})?\s*(~?{IDENTIFIER})\s*\(([^;]*?)\)\s*({FUNC_TAIL_SPECIFIER}(?: {FUNC_TAIL_SPECIFIER})*)?\s*;')

@dataclass
class Node(ABC):
    start: int
    end: int
    parent: Optional[Node]

    @abstractproperty
    def repr_name(self) -> str:
        pass

@dataclass
class Namespace(Node):
    name: str

    @property
    def repr_name(self) -> str:
        return self.name

    @property
    def repr_start(self) -> str:
        return 'namespace %s%s\n' % (self.name, convention.block_start())

    @property
    def repr_end(self) -> str:
        return '\n\n} /* namespace %s */' % (self.name)

@dataclass
class Class(Node):
    template_params: Optional[str]
    keyword: str
    name: str

    @property
    def repr_name(self) -> str:
        if self.template_params is None:
            return self.name
        else:
            typenames = self.extract_template_typenames()
            typenames = ','.join(typenames)
            return f'{self.name}<{typenames}>'

    def extract_template_typenames(self) -> list[str]:
        assert self.template_params is not None
        return re.findall(r'(?:typename|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)', self.template_params)

@dataclass
class Func(Node):
    template_params: Optional[str]
    head_specifiers: Optional[str]
    return_type: Optional[str]
    name: str
    parameters: str
    tail_specifiers: Optional[str]

    @property
    def repr_name(self) -> str:
        return self.name

    @property
    def is_inline(self) -> str:
        return self.head_specifiers is not None and 'inline' in self.head_specifiers

    @property
    def rel_name(self) -> str:
        """The name relative to the root"""
        prefix = ''
        p = self
        while p.parent is not None:
            p = p.parent
            if self.ns is not None and p.parent is None:
                break
            prefix = p.repr_name + '::' + prefix if prefix else p.repr_name
        return prefix + '::' + self.name if prefix else self.name

    @property
    def repr(self) -> str:
        template = ''
        if isinstance(self.parent, Class) and self.parent.template_params is not None:
            template += 'template ' + self.parent.template_params + '\n'
        template += 'template ' + self.template_params + '\n' if self.template_params else ''
        rtn_type = convention.type_spacing(self.return_type) if self.return_type is not None else ''
        head_spec = 'inline ' if self.is_inline else ''
        tail_spec = ' ' + self.tail_specifiers if self.tail_specifiers is not None else ''

        pre_params = template + head_spec + rtn_type + self.rel_name + convention.space_after_func_name() + '('
        post_params = ')' + tail_spec
        params = self.repr_params(pre_params, post_params)
        body = (convention.indent() + '// TODO\n') if convention.insert_todo else ''
        return pre_params + params + post_params + convention.block_start() + body + '}'

    def repr_params(self, pre_params: str, post_params: str) -> str:
        piter = re.finditer(rf'(?:^|,)\s*({Ptn.TYPE})({Ptn.IDENTIFIER})', self.parameters)
        params = []
        for match in piter:
            p = match.group(1).lstrip() + match.group(2).rstrip()
            params.append(p)
        pre = pre_params.splitlines()[-1]
        singleline_params = ', '.join(params)
        multiline = len(pre) + len(', '.join(params)) + len(post_params) > convention.columns()
        if not multiline:
            return singleline_params
        else:
            indents = convention.spaces_to_indent(' ' * len(pre)) if convention.param_indent_style() == 'vert_align' else (convention.indent() * 2)
            result = ''
            if convention.param_indent_style() == 'double_indent' \
            or len(pre) + len(params[0]) + len(',') > convention.columns():
                indents = convention.indent() * 2
                result += '\n' + indents
            for i, p in enumerate(params):
                if i < len(params) - 1:
                    result += p + ',\n' + indents
                else:
                    result += p
            return result

    @property
    def root_ns(self) -> Optional[Namespace]:
        p = self
        while p.parent is not None:
            p = p.parent
        return p if isinstance(p, Namespace) else None

    @property
    def ns(self) -> Optional[Namespace]:
        p = self
        while p.parent is not None:
            p = p.parent
            if isinstance(p, Namespace):
                return p
        return None

class Tree:
    source: str
    namespaces: list[Namespace]
    classes: list[Class]
    functions: list[Func]

    def __init__(self, source: str):
        self.source = source
        self.namespaces = []
        self.classes = []
        self.functions = []
        self._fetch_namespaces()
        self._fetch_classes()
        self._fetch_functions()

    @property
    def need_ipp(self) -> bool:
        for cls in self.classes:
            if cls.template_params:
                return True
        for fn in self.functions:
            if fn.template_params or fn.is_inline:
                return True
        return False

    @property
    def root_namespaces(self) -> list[Namespace]:
        return [ns for ns in self.namespaces if ns.parent is None]

    def get_functions_for(self, root_ns: Optional[Namespace]) -> list[Func]:
        result = []
        for fn in self.functions:
            if fn.root_ns is root_ns:
                result.append(fn)
        return result

    def _fetch_namespaces(self) -> None:
        block_regex = re.compile(Ptn.BLOCK)
        for match in re.finditer(Ptn.NAMESPACE_START, self.source):
            match2 = block_regex.search(self.source, match.end())
            if match2:
                name = match.group(1).strip()
                start = match.start()
                end = match2.end()
                parent = None
                for ns in self.namespaces:
                    if ns.start < start and ns.end > end:
                        parent = ns
                obj = Namespace(start, end, parent, name)
                self.namespaces.append(obj)

    def _fetch_classes(self) -> None:
        block_regex = re.compile(Ptn.CLASS_BLOCK)
        for match in re.finditer(Ptn.CLASS_START, self.source):
            match2 = block_regex.search(self.source, match.end())
            if match2:
                template = xstrip( match.group(1) )
                keyword = match.group(2).strip()
                name = match.group(3).strip()
                start = match.start()
                end = match2.end()
                parent = None
                for clz in self.classes:
                    if clz.start < start and clz.end > end:
                        parent = clz
                if parent is None:
                    for ns in self.namespaces:
                        if ns.start < start and ns.end > end:
                            parent = ns
                obj = Class(start, end, parent, template, keyword, name)
                self.classes.append(obj)

    def _fetch_functions(self) -> None:
        for match in re.finditer(Ptn.FUNC, self.source):
            template = xstrip( match.group(1) )
            head_specifiers = xstrip( match.group(2) )
            if head_specifiers is not None:
                head_specifiers = re.sub(r'\s+', ' ', head_specifiers)
            return_type = xstrip( match.group(3) )
            name = match.group(4).strip()
            params = match.group(5).strip()
            tail_specifiers = xstrip( match.group(6) )
            if tail_specifiers is not None:
                tail_specifiers = re.sub(r'\s+', ' ', tail_specifiers)
            start = match.start()
            end = match.end()
            parent = None
            for clz in self.classes:
                if clz.start < start and clz.end > end:
                    parent = clz
            if parent is None:
                for ns in self.namespaces:
                    if ns.start < start and ns.end > end:
                        parent = ns
            obj = Func(start, end, parent, template, head_specifiers, return_type, name, params, tail_specifiers)
            self.functions.append(obj)
