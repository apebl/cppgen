import sys, os, argparse
from os import path
import cppgen.nodes as nodes
import cppgen.convention as convention
from cppgen.utils import query_yn

def arg_parser():
    parser = argparse.ArgumentParser(description='Generate definitions from headers')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='A header file')
    parser.add_argument('--cpp', action='store', type=str, default='.cpp',
                        help='Suffix for files containing function definitions (default: .cpp)')
    parser.add_argument('--ipp', action='store', type=str, default='.ipp',
                        help='Suffix for files containing inline/template function definitions (default: .ipp)')
    parser.add_argument('-c', '--convention', default='default', choices=['default', 'gnu', 'google'],
                        help='Specify coding convention (default: default)')
    parser.add_argument('-i', '--indent', default='convention', choices=['convention', 'space', 'tab'],
                        help='Specify indentation character (default: follow convention)')
    parser.add_argument('-t', '--tabsize', type=int, default=0,
                        help='Specify tab size (default: 0; follow convention)')
    parser.add_argument('--no-todo', action='store_true',
                        help='Do not insert todo comments')
    return parser

def generate(header_name: str, args: argparse.Namespace, tree: nodes.Tree) -> str:
    result = ''
    if not tree.need_ipp:
        result += f'#include "{header_name}"\n\n'

    # Global namespace
    functions = tree.get_functions_for(None)
    if functions:
        result += '\n\n'.join(fn.repr for fn in functions)
        result += '\n\n'

    ns_results = []
    root_namespaces = tree.root_namespaces
    for ns in root_namespaces:
        text = ns.repr_start
        functions = tree.get_functions_for(ns)
        text += '\n\n'.join(fn.repr for fn in functions)
        text += ns.repr_end
        ns_results.append(text)
    result += '\n\n\n'.join(ns_results) + '\n'
    return result

def main():
    argparser = arg_parser()
    args = argparser.parse_args()
    convention.style = args.convention
    convention.indent_style = args.indent
    convention.tabsize_style = args.tabsize
    convention.insert_todo = not args.no_todo
    for filename in args.files:
        if filename.endswith(args.cpp) or filename.endswith(args.ipp):
            print(f'Skip: {filename} (definition file)')
            continue
        with open(filename, 'r') as f:
            source = f.read()
            tree = nodes.Tree(source)
            basepath = os.path.splitext(filename)[0]
            new_filename = basepath + (args.ipp if tree.need_ipp else args.cpp)
            if path.exists(new_filename):
                res = query_yn(f"Overwrite?: {new_filename}")
                if not res:
                    print(f'Skip: {filename} (definition already exists)')
                    continue
            newsrc = generate(path.basename(filename), args, tree)
            with open(new_filename, 'w') as w:
                w.write(newsrc)
            print(f'Generate: {filename} -> {new_filename}')

