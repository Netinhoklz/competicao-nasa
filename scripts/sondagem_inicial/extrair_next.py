import sys, re, json
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")
src = open(sys.argv[1], encoding="utf-8", errors="replace").read()

parts = []
for m in re.finditer(r"self\.__next_f\.push\((\[.*?\])\)</script>", src, re.S):
    try:
        arr = json.loads(m.group(1))
    except Exception as e:
        continue
    if len(arr) > 1 and isinstance(arr[1], str):
        parts.append(arr[1])
blob = "".join(parts)
open(sys.argv[2], "w", encoding="utf-8").write(blob)

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.out.append(" <" + a["href"] + "> ")
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "br", "tr"):
            self.out.append("\n")
        if tag == "li":
            self.out.append("- ")
        if tag in ("h1", "h2", "h3", "h4"):
            self.out.append("## ")
    def handle_data(self, d):
        if d.strip():
            self.out.append(d.strip() + " ")

# trechos de HTML no blob: sequencias que comecam com <p ou <h ou <ul
for m in re.finditer(r"(<(?:p|h\d|ul|ol|div)[\s>].*?)(?=\"[,\]\}]|\n[0-9a-f]+:)", blob, re.S):
    frag = m.group(1)
    if len(frag) < 40:
        continue
    p = P()
    p.feed(frag)
    t = re.sub(r"\n\s*\n+", "\n", "".join(p.out)).strip()
    if t:
        print("=" * 60)
        print(t)
