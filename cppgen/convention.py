import re, math

style = 'default'
indent_style = 'convention'
filename_style = 'snake_case'
tabsize_style = 0
insert_todo = True

def block_start() -> str:
    if style == 'gnu' or style == 'google':
        return '\n{\n'
    return ' {\n'

def space_after_func_name() -> str:
    if style == 'google':
        return ''
    return ' '

def type_spacing(type: str) -> str:
    if type.endswith('*') or type.endswith('&'):
        if style == 'google':
            return type + ' '
        match = re.search(r'(.+?)\s*([*&\s]+?)$', type)
        name = match.group(1)
        pt = match.group(2)
        if style == 'gnu':
            return name + ' ' + pt + '\n'
        return name + ' ' + pt
    if style == 'gnu':
        return type + '\n'
    return type + ' '

def columns() -> int:
    return 78

def indent_char() -> str:
    if indent_style != 'convention':
        return ' ' if indent_style == 'space' else '\t'
    if style == 'gnu' or style == 'google':
        return ' '
    return ' '

def indent() -> str:
    ch = indent_char()
    return ch * tabsize() if ch == ' ' else ch

def tabsize() -> int:
    if tabsize_style != 0:
        return tabsize_style
    if style == 'gnu' or style == 'google':
        return 2
    return 4

def spaces_to_indent(spaces: str) -> str:
    if indent_char() == ' ':
        return spaces
    else:
        num = len(spaces) / tabsize()
        return '\t' * int(round(num))

def param_indent_style() -> str:
    if style == 'gnu' or style == 'google':
        return 'double_indent'
    return 'vert_align'

def convert_case(text: str) -> str:
    if filename_style == 'snake_case':
        return snakecase(text)
    elif filename_style == 'hyphen-case':
        return snakecase(text).replace('_', '-')
    elif filename_style == 'lowercase':
        return snakecase(text).replace('_', '')
    elif filename_style == 'UPPERCASE':
        return snakecase(text).replace('_', '').upper()
    elif filename_style == 'camelCase':
        return camelcase(text)
    elif filename_style == 'PascalCase':
        return pascalcase(text)
    elif filename_style == 'CONST_CASE':
        return snakecase(text).upper()
    else:
        raise 'Invalid filename style'

def snakecase(text: str) -> str:
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    text = re.sub(r'__+', '_', text)
    return text.lower()

def camelcase(text: str) -> str:
    text = re.sub(r'_+([a-z])', lambda m: m.group(1).upeer(), text)
    text = re.sub(r'^([A-Z]+)([A-Z][a-z])', lambda m: m.group(1).lower() + m.group(2), text)
    text = re.sub(r'^([A-Z])', lambda m: m.group(1).lower(), text)
    return text

def pascalcase(text: str) -> str:
    text = re.sub(r'_+([a-z])', lambda m: m.group(1).upeer(), text)
    text = re.sub(r'^([a-z]+)([A-Z][a-z])', lambda m: m.group(1).upper() + m.group(2), text)
    text = re.sub(r'^([a-z])', lambda m: m.group(1).upper(), text)
    return text

def header_guard(namespaces: list[str], class_name: str, suffix: str) -> str:
    suffix = suffix.replace('.', '').upper()
    ns = '_'.join(ns.replace('_', '').upper() for ns in namespaces)
    name = class_name.replace('_', '').upper()
    return f'{ns}_{name}_{suffix}'
