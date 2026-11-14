import sys, re, json, html
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")
src = open(sys.argv[1], encoding="utf-8", errors="replace").read()

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0
        self.href = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag == "a" and a.get("href"):
            self.href = a["href"]
            self.out.append(" [LINK " + a["href"] + "] ")
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "br", "section", "tr"):
            self.out.append("\n")
        if tag in ("h1", "h2", "h3", "h4"):
            self.out.append("## ")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip -= 1
    def handle_data(self, d):
        if self.skip <= 0 and d.strip():
            self.out.append(d.strip() + " ")

p = P()
p.feed(src)
txt = "".join(p.out)
txt = re.sub(r"\n\s*\n+", "\n", txt)
print(txt)

print("\n===== SCRIPTS COM JSON =====")
for m in re.finditer(r"<script[^>]*>(.*?)</script>", src, re.S):
    s = m.group(1)
    if len(s) > 2000:
        print("script len", len(s), s[:300].replace("\n", " "))
