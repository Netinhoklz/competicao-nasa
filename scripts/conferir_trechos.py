"""Procura trechos nos textos completos baixados (E:/campeonato-nasa/tmp/textos) para conferir afirmacoes."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
T = Path("E:/campeonato-nasa/tmp/textos")
BUSCAS = {
    "10_1038_s41467_025_64567_9": [r"738", r"\b4[16]\s?%", r"fertili[sz]er", r"revenue[^.]{0,80}\d+\s?%", r"dietary energy[^.]{0,60}\d+\s?%", r"protein[^.]{0,60}\d+\s?%", r"countr(y|ies)[^.]{0,60}"],
    "10_1038_s41467_022_32464_0": [r"53 countries", r"\b1959\b", r"[Mm]eta-?[Ff]orest", r"random forest", r"50 kg", r"236", r"per 50"],
    "10_1038_s41467_025_67757_7": [r"\b50\b[^.]{0,40}years", r"40 years", r"crop yield[^.]{0,80}"],
    "10_1038_s41893_022_00911_x": [r"Kenya|Malawi|Mozambique|Nigeria|South Africa|Zambia|Zimbabwe"],
    "10_1038_s43247_023_00746_0": [r"functional richness[^.]{0,120}", r"increased over time[^.]{0,100}"],
    "10_1126_science_adj1914": [r"11 countries[^.]{0,150}", r"Asia|Africa|Europe|America"],
    "10_1088_1748_9326_ae0f45": [r"fertili[sz]er[^.]{0,200}", r"nitrogen[^.]{0,160}", r"subsequent crop[^.]{0,120}", r"limitation[^.]{0,200}", r"only (the|one)[^.]{0,120}crop"],
}
for arq, pads in BUSCAS.items():
    f = T / f"{arq}.txt"
    if not f.exists():
        print(f"\n### {arq}: SEM TEXTO")
        continue
    t = f.read_text(encoding="utf-8")
    print(f"\n### {arq} ({len(t)} chars)")
    for p in pads:
        ms = list(re.finditer(p, t))
        print(f"  [{p}] {len(ms)} ocorrências")
        for m in ms[:3]:
            a, b = max(0, m.start() - 160), min(len(t), m.end() + 160)
            print("     …" + t[a:b].replace("\n", " ") + "…")
