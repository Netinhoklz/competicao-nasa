"""Gera web/texturas/earth_day_4k.webp e earth_night_4k.webp a partir das 8K (teto 4K na página inicial, 15/11).

A reamostragem é feita em luz linear (sRGB -> linear -> Lanczos -> sRGB), como a GPU faz os mipmaps de uma textura
sRGB: reamostrando direto nos valores sRGB, as luzes pequenas das cidades perdiam brilho e o limiar do shader
(espaco.js, smoothstep 0,05-0,45) apagava parte delas. WebP qualidade 85, method 6 (PSNR ~42 dB no dia e ~45 dB na
noite contra a 4K sem perda; abaixo do que se vê no globo).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 ferramentas/preparar_texturas_4k.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

TEX = Path(__file__).resolve().parent.parent / "web" / "texturas"
Image.MAX_IMAGE_PIXELS = None


def para_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def para_srgb(lin):
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


for nome in ("day", "night"):
    rgb = np.asarray(Image.open(TEX / f"earth_{nome}_8k.webp").convert("RGB"), np.float32) / 255
    lin = para_linear(rgb)
    canais = [np.asarray(Image.fromarray(lin[..., k], "F").resize((4096, 2048), Image.LANCZOS)) for k in range(3)]
    img = Image.fromarray((para_srgb(np.stack(canais, -1)) * 255 + 0.5).astype(np.uint8), "RGB")
    saida = TEX / f"earth_{nome}_4k.webp"
    img.save(saida, "WEBP", quality=85, method=6)
    print(saida, saida.stat().st_size // 1024, "KB")
