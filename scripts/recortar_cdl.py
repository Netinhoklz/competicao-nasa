"""Recorta janelas do CDL nacional (lidas direto do .zip, sem descompactar) + visao nacional reduzida.

Saida: E:/campeonato-nasa/estudo_cdl/recortes/<regiao>_<camada>.tif e nacional_<camada>_960m.tif
"""
import sys
import time
import zipfile

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from pyproj import Transformer  # noqa: E402
from rasterio.enums import Resampling  # noqa: E402
from rasterio.windows import Window  # noqa: E402

from comum import ESTUDO_CDL, registrar_manifesto  # noqa: E402

REGIOES = {
    "iowa_story": (-93.6, 42.0, "Corn Belt: milho-soja"),
    "kansas_ogallala": (-100.9, 37.6, "Ogallala: milho irrigado, trigo, sorgo (pivos)"),
    "california_fresno": (-119.8, 36.4, "Vale Central: perenes (amendoa, uva), algodao, tomate"),
    "mississippi_delta": (-90.6, 33.6, "Delta: soja, algodao, arroz"),
    "north_dakota_cass": (-97.2, 46.9, "Planicies do norte: trigo, soja, milho, girassol"),
    "texas_lubbock": (-101.85, 33.6, "Semiarido: algodao de sequeiro (analogo ao sertao)"),
}
LADO = 1333  # pixels de 30 m ~ 40 km
OUT = ESTUDO_CDL / "recortes"


def tifs_do_zip(zp):
    z = zipfile.ZipFile(zp)
    return [i.filename for i in z.infolist() if i.filename.lower().endswith(".tif")]


def recortar(zp, rotulo):
    OUT.mkdir(parents=True, exist_ok=True)
    feitos = {}
    for tif in tifs_do_zip(zp):
        nome = f"{rotulo}_{tif.rsplit('/', 1)[-1][:-4]}" if len(tifs_do_zip(zp)) > 1 else rotulo
        caminho = f"/vsizip/{zp.as_posix()}/{tif}"
        with rasterio.open(caminho) as r:
            tr = Transformer.from_crs("EPSG:4326", r.crs, always_xy=True)
            prof = r.profile.copy()
            prof.update(driver="GTiff", compress="deflate", tiled=True, blockxsize=256, blockysize=256)
            cmap = None
            try:
                cmap = r.colormap(1)
            except ValueError:
                pass
            for reg, (lon, lat, _) in REGIOES.items():
                x, y = tr.transform(lon, lat)
                col, row = ~r.transform * (x, y)
                w = Window(int(col) - LADO // 2, int(row) - LADO // 2, LADO, LADO)
                t0 = time.time()
                a = r.read(1, window=w)
                p = prof.copy()
                p.update(width=LADO, height=LADO, transform=r.window_transform(w))
                dst = OUT / f"{reg}_{nome}.tif"
                with rasterio.open(dst, "w", **p) as d:
                    d.write(a, 1)
                    if cmap:
                        d.write_colormap(1, cmap)
                feitos[dst.name] = {"regiao": reg, "seg": round(time.time() - t0, 1), "unicos": int(len(np.unique(a)))}
                print(dst.name, feitos[dst.name], flush=True)
            # visao nacional ~960 m (fator 32) pelo overview
            t0 = time.time()
            h, wd = r.height // 32, r.width // 32
            a = r.read(1, out_shape=(h, wd), resampling=Resampling.nearest)
            p = prof.copy()
            p.update(width=wd, height=h, transform=r.transform * r.transform.scale(r.width / wd, r.height / h))
            dst = OUT / f"nacional_{nome}_960m.tif"
            with rasterio.open(dst, "w", **p) as d:
                d.write(a, 1)
                if cmap:
                    d.write_colormap(1, cmap)
            feitos[dst.name] = {"regiao": "nacional", "seg": round(time.time() - t0, 1)}
            print(dst.name, feitos[dst.name], flush=True)
    return feitos


if __name__ == "__main__":
    tudo = {}
    for arg in sys.argv[1:]:  # ex.: 2024_30m_cdls
        zp = ESTUDO_CDL / f"{arg}.zip"
        tudo.update(recortar(zp, arg.replace("_30m_cdls", "")))
    registrar_manifesto("cdl", {"recortes": {"regioes": REGIOES, "lado_px": LADO, "arquivos": tudo}}, base=ESTUDO_CDL)
