"""Gera as tabelas derivadas da Frente C em E:/campeonato-nasa/dados/derivados/ (formato longo:
data, aoi, variavel, valor, unidade, fonte). Rodar depois dos downloads."""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import DADOS, DERIV

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
DERIV.mkdir(parents=True, exist_ok=True)
UNID = {"ndvi_mediana": "adimensional", "ndmi_mediana": "adimensional", "ndvi_p90": "adimensional",
        "frac_solo_exposto": "fracao", "frac_veg_densa": "fracao", "frac_valida_media": "fracao", "n_cenas_validas": "contagem"}


def ler(p):
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_localize(None)
    return df


def mensal_aoi(df, fonte, min_valida=0.3):
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["data"] = df.datetime.dt.to_period("M").dt.to_timestamp()
    tudo = df.groupby(["data", "aoi"]).frac_valida.mean().rename("frac_valida_media")
    ok = df[(df.frac_valida >= min_valida) & df.get("ndvi_mediana", pd.Series(np.nan, index=df.index)).notna()]
    agg = ok.groupby(["data", "aoi"]).agg(ndvi_mediana=("ndvi_mediana", "median"), ndmi_mediana=("ndmi_mediana", "median"),
                                           ndvi_p90=("ndvi_p90", "max"), frac_solo_exposto=("frac_solo_exposto", "mean"),
                                           frac_veg_densa=("frac_veg_densa", "mean"), n_cenas_validas=("id", "count"))
    w = agg.join(tudo, how="outer").reset_index()
    longo = w.melt(id_vars=["data", "aoi"], var_name="variavel", value_name="valor").dropna(subset=["valor"])
    longo["unidade"] = longo.variavel.map(UNID)
    longo["fonte"] = fonte
    return longo


def mensal_ce(meta, fonte):
    if meta.empty:
        return pd.DataFrame()
    meta = meta.copy()
    meta["data"] = meta.datetime.dt.to_period("M").dt.to_timestamp()
    g = meta.groupby("data").agg(n_cenas=("id", "count"), nuvem_media=("cloud_cover", "mean"),
                                 frac_cenas_nuvem_lt20=("cloud_cover", lambda s: (s < 20).mean()))
    longo = g.reset_index().melt(id_vars="data", var_name="variavel", value_name="valor")
    longo["aoi"] = "ceara_estado"
    longo["unidade"] = longo.variavel.map({"n_cenas": "contagem", "nuvem_media": "%", "frac_cenas_nuvem_lt20": "fracao"})
    longo["fonte"] = fonte
    return longo[["data", "aoi", "variavel", "valor", "unidade", "fonte"]]


# junta as cenas S2 processadas em paralelo (um processo por AOI) no arquivo unico
S = DADOS / "sentinel2"
partes = sorted(S.glob("s2_aoi_cenas_*.parquet"))
if partes:
    base = [pd.read_parquet(S / "s2_aoi_cenas.parquet")] if (S / "s2_aoi_cenas.parquet").exists() else []
    tudo = pd.concat(base + [pd.read_parquet(p) for p in partes], ignore_index=True).drop_duplicates(["aoi", "id"], keep="last")
    tudo.to_parquet(S / "s2_aoi_cenas.parquet", index=False)
    for p in partes:
        p.unlink()
    print("S2 cenas unificadas:", tudo.groupby("aoi").size().to_dict())

L = DADOS / "landsat"
la = pd.concat([mensal_aoi(ler(L / "landsat_aoi_cenas_hist.parquet"), "Landsat C2 L2 TM/ETM+ (L4/5/7) - Planetary Computer"),
                mensal_aoi(ler(L / "landsat_aoi_cenas_l89.parquet"), "Landsat C2 L2 OLI (L8/9) - Planetary Computer")], ignore_index=True)
la.to_parquet(DERIV / "landsat_aoi_mensal.parquet", index=False)
mensal_ce(ler(L / "landsat_stac_ceara.parquet"), "Landsat C2 L2 metadados STAC (todas as cenas que tocam o Ceara)").to_parquet(
    DERIV / "landsat_ce_mensal.parquet", index=False)

S = DADOS / "sentinel2"
mensal_aoi(ler(S / "s2_aoi_cenas.parquet"), "Sentinel-2 L2A 20 m - Planetary Computer").to_parquet(DERIV / "sentinel2_aoi_mensal.parquet", index=False)
mensal_ce(ler(S / "s2_stac_ceara.parquet"), "Sentinel-2 L2A metadados STAC").to_parquet(DERIV / "sentinel2_ce_mensal.parquet", index=False)
h = ler(S / "hls_aoi_cenas.parquet")
if not h.empty:
    h = h.assign(frac_solo_exposto=np.nan, frac_veg_densa=np.nan) if "frac_solo_exposto" not in h else h
    mensal_aoi(h, "HLS v2 L30+S30 30 m - Planetary Computer").to_parquet(DERIV / "hls_aoi_mensal.parquet", index=False)

for f in sorted(DERIV.glob("*")):
    if any(k in f.name for k in ("landsat", "sentinel2", "hls", "srtm")):
        d = pd.read_parquet(f)
        print(f.name, len(d), list(d.columns)[:6], d["data"].min() if "data" in d else "")

# manifestos atualizados (o processo principal do S2 foi dividido em processos por AOI)
from comum import registrar_manifesto, tamanho_pasta
for base in ("landsat", "sentinel2", "srtm"):
    p = DADOS / base
    registrar_manifesto(base, {"arquivos": sorted(f.name for f in p.iterdir() if f.is_file()), "tamanho_bytes": tamanho_pasta(p)})
registrar_manifesto("sentinel2", {
    "fonte": "Microsoft Planetary Computer - sentinel-2-l2a (ESA Copernicus, Sen2Cor); HLS v2 (hls2-l30/hls2-s30). Earth Search C1 descartado por arquivo incompleto",
    "url": "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a",
    "periodos": {"S2 cubos 20 m": "2017-01 a hoje (cenas com nuvem <= 90%)", "HLS": "2020-01 a hoje (nuvem <= 80%)"},
    "grade": "EPSG:32724 20 m (B04/B08 media 10->20 m); offset -0.1 para baseline >= 04.00",
})
print("manifestos ok")
