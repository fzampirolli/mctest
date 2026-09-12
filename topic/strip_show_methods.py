#!/usr/bin/env python3
"""
Remove métodos cujo nome comece com 'show' (e seus decorators, ex: @staticmethod)
de um arquivo Python, usando apenas indentação -- não usa ast/compile, pois o
arquivo de origem pode ter sintaxe incompatível com a versão local do Python
(ex: `obj[*expr]`, válido só a partir do Python 3.11).

Uso:
    python3 strip_show_methods.py /caminho/para/morph.py
"""
import re
import sys


def strip_show_methods(src: str) -> str:
    lines = src.split('\n')
    result = []
    i = 0
    n = len(lines)
    removed = []

    while i < n:
        line = lines[i]
        m = re.match(r'^([ \t]*)def\s+(show\w*)\s*\(', line)
        if m:
            indent = m.group(1)
            removed.append(m.group(2))

            # remove decorators (@staticmethod, @classmethod, etc.) já
            # adicionados ao result, desde que no mesmo nível de indentação
            while result:
                prev = result[-1]
                prev_indent = len(prev) - len(prev.lstrip(' \t'))
                if prev.lstrip().startswith('@') and prev_indent == len(indent):
                    result.pop()
                else:
                    break

            # pula a assinatura + corpo do método inteiro
            i += 1
            while i < n:
                nxt = lines[i]
                if nxt.strip() == '':
                    i += 1
                    continue
                cur_indent = len(nxt) - len(nxt.lstrip(' \t'))
                if cur_indent <= len(indent):
                    break
                i += 1
            continue

        result.append(line)
        i += 1

    print(f"[strip_show_methods] métodos removidos: {removed}", file=sys.stderr)
    return '\n'.join(result)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 strip_show_methods.py <arquivo.py>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    cleaned = strip_show_methods(src)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"[strip_show_methods] arquivo atualizado: {path}", file=sys.stderr)