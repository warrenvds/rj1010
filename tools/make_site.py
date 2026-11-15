"""Assemble a page: python3 make_site.py <data.json> <out.html> [title]"""
import sys
t = open('tools/tpl.html').read()
t = t.replace('__DATA__', open(sys.argv[1]).read()).replace('__HIST__', open('tools/hist.json').read())
if len(sys.argv) > 3: t = t.replace('<title>RJ 10/10 Challenge 2026</title>', f'<title>{sys.argv[3]}</title>')
open(sys.argv[2], 'w').write(t); print(sys.argv[2], len(t))
