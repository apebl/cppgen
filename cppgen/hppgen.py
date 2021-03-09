import os, argparse
from os import path
from pathlib import Path
import cppgen.convention as convention
from cppgen.utils import query_yn

def arg_parser():
    parser = argparse.ArgumentParser(description='Generate a header')
    parser.add_argument('type', metavar='TYPE', nargs='?', default='class',
                        choices=['class', 'struct', 'enum'],
                        help='Type: class, struct, or enum (default: class)')
    parser.add_argument('name', metavar='NAME', type=str, nargs=1,
                        help='(<NAMESPACE>::)*<NAME>')
    parser.add_argument('--suffix', action='store', type=str, default='.hpp',
                        help='Suffix for the generated header file (default: .hpp)')
    parser.add_argument('-f', '--file-convention', default='snake_case',
                        choices=['snake_case', 'hyphen-case', 'lowercase', 'UPPERCASE', 'camelCase', 'PascalCase', 'CONST_CASE'],
                        help='Specify file naming convention (default: snake_case)')
    parser.add_argument('-c', '--convention', default='default', choices=['default', 'gnu', 'google'],
                        help='Specify coding convention (default: default)')
    parser.add_argument('-i', '--indent', default='convention', choices=['convention', 'space', 'tab'],
                        help='Specify indentation character (default: follow convention)')
    parser.add_argument('-t', '--tabsize', type=int, default=0,
                        help='Specify tab size (default: 0; follow convention)')
    return parser

def generate(type: str, namespaces: list[str], class_name: str, suffix: str) -> str:
    guard = convention.header_guard(namespaces, class_name, suffix)
    result = '#ifndef ' + guard + '\n'
    result += '#define ' + guard + '\n\n'
    if namespaces:
        result += 'namespace '
        result += '::'.join(namespaces) + convention.block_start() + '\n'

    result += type + ' ' + class_name + convention.block_start()
    if type == 'class':
        result += 'public:\n'
    if type == 'class' or type == 'struct':
        result += convention.indent() + class_name + convention.space_after_func_name() + '();\n'
    if type == 'class':
        result += convention.indent() + '~' + class_name + convention.space_after_func_name() + '();\n'
        arg_type = convention.type_spacing('const ' + class_name + ' &')
        result += convention.indent() + class_name + convention.space_after_func_name() + '(' + arg_type + 'other);\n'
        arg_type = convention.type_spacing(class_name + ' &&')
        result += convention.indent() + class_name + convention.space_after_func_name() + '(' + arg_type + 'other);\n'
        result += '\nprivate:\n'
    result += '};\n'

    if namespaces:
        result += '\n} /* namespace '
        result += '::'.join(namespaces) + ' */\n'
    result += '\n#endif /* ' + guard + ' */\n'
    return result

def main():
    argparser = arg_parser()
    args = argparser.parse_args()
    convention.filename_style = args.file_convention
    convention.style = args.convention
    convention.indent_style = args.indent
    convention.tabsize_style = args.tabsize

    identifiers = args.name[0].strip().split('::')
    identifiers = [id.strip() for id in identifiers]
    namespaces = identifiers[:-1]
    class_name = identifiers[-1]

    src = generate(args.type, namespaces, class_name, args.suffix)
    filename = convention.convert_case(class_name) + args.suffix
    dir = ''
    if namespaces:
        dir = os.path.sep.join(namespaces) + os.path.sep
        filename = dir + filename
    if path.exists(filename):
        res = query_yn(f"Overwrite?: {filename}")
        if not res:
            print(f'Skip: {filename} (already exists)')
            return
    Path(dir).mkdir(parents=True, exist_ok=True)
    with open(filename, 'w') as f:
        f.write(src)
    print(f'Generate: {filename}')
