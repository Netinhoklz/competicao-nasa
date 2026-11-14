"""Confere a afirmacao do El Nino: o percentil pronto do SMAP L4 (sm_rootzone_pctl) existe no Ceara em out-nov?
E compara a umidade da zona da raiz (sm_rootzone, m3/m3) nos 30 dias ate 10/11 entre os anos 2015-2026, por UF."""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import xarray as xr  # noqa: E402

from comum import DADOS, nordeste_gdf  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
sm = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
fim = pd.Timestamp(sm.time.values.max())
lo, la = np.meshgrid(sm.lon.values, sm.lat.values)
ne = nordeste_gdf()
linhas = []
for _, u in ne.iterrows():
    sig = UF[str(u.codarea)]
    m = shapely.contains_xy(u.geometry, lo, la)
    mx = xr.DataArray(m, dims=("lat", "lon"), coords={"lat": sm.lat, "lon": sm.lon})
    for ano in range(2015, 2027):
        f = pd.Timestamp(ano, fim.month, fim.day)
        jan = sm.sel(time=slice(f - pd.Timedelta(days=29), f))
        if jan.sizes["time"] == 0:
            continue
        pct = jan.sm_rootzone_pctl.where(mx)
        cobertura = float(pct.notnull().mean("time").where(mx).sum() / m.sum())
        linhas.append({"UF": sig, "ano": ano, "rz_m3m3": float(jan.sm_rootzone.where(mx).mean()),
                       "pctl_pronto_medio": float(pct.mean()), "frac_celulas_com_pctl": round(cobertura, 2)})
d = pd.DataFrame(linhas)
d["posto_rz_de_baixo"] = d.groupby("UF").rz_m3m3.rank(method="min").astype(int)  # 1 = mais seco
d["percentil_proprio"] = (d.groupby("UF").rz_m3m3.rank(pct=True) * 100).round(0)
print(f"Janela: 30 dias até {fim:%d/%m} de cada ano (2015 começa em 31/03, então tem a janela completa)")
for uf in ["CE", "MA", "PE", "PB", "BA"]:
    x = d[d.UF == uf].set_index("ano")[["rz_m3m3", "posto_rz_de_baixo", "percentil_proprio", "pctl_pronto_medio", "frac_celulas_com_pctl"]]
    print(f"\n== {uf}\n", x.round(3).to_string())
d.to_csv(DADOS / "el_nino_2026" / "checagem_smap_novembro.csv", index=False)
