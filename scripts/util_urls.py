"""Lista URLs (decodificadas) de um HTML. Uso: python util_urls.py arquivo.html [filtro1 filtro2 ...]"""
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
for _ in range(3):
    t = urllib.parse.unquote(t)
t = t.replace("\\/", "/")
filtros = [f.lower() for f in sys.argv[2:]]
for u in sorted(set(re.findall(r"https?://[^\s\"'<>\\]+", t))):
    if not filtros or any(f in u.lower() for f in filtros):
        print(u)
