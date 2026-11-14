"""Mercado: AMS Market News (EUA, amostra aberta), FAOSTAT (precos ao produtor e producao, global)
e Banco Mundial Pink Sheet (precos mensais de commodities, global).

Uso: python -I baixar_mercado.py [baixar|tratar|tudo]
Saidas:
  dados/mercado/brutos/...                     arquivos originais
  dados/derivados/faostat_precos_produtor.parquet   (todos os paises, culturas candidatas)
  dados/derivados/faostat_producao_qcl.parquet      (todos os paises, culturas candidatas)
  dados/derivados/faostat_brasil_anual.parquet      (Brasil: area, producao, produtividade, preco)
  dados/derivados/mercado_precos_mensal.parquet     (Pink Sheet, formato longo)
"""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
P = pasta("mercado")
BR = P / "brutos"
BR.mkdir(exist_ok=True)

FONTES = {
    "faostat_prices.zip": "https://bulks-faostat.fao.org/production/Prices_E_All_Data_(Normalized).zip",
    "faostat_qcl.zip": "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip",
    "wb_pink_sheet_mensal.xlsx": "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx",
    "wb_pink_sheet_anual.xlsx": "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx",
}
# AMS: API MARS exige chave (403); relatorios .txt legados congelados em 2020; PDFs publicos avulsos.
AMS = {
    "ams_gx_gr110_legado.txt": "https://www.ams.usda.gov/mnreports/gx_gr110.txt",
    "ams_3192.pdf": "https://www.ams.usda.gov/mnreports/ams_3192.pdf",
}

# Culturas candidatas (nomes FAOSTAT, em ingles)
CULTURAS = [
    "Maize (corn)", "Sorghum", "Beans, dry", "Cow peas, dry", "Cassava, fresh", "Seed cotton, unginned",
    "Soya beans", "Rice", "Wheat", "Millet", "Groundnuts, excluding shelled", "Sugar cane", "Bananas",
    "Cashew nuts, in shell", "Sunflower seed", "Sesame seed", "Coconuts, in shell", "Cantaloupes and other melons",
    "Watermelons", "Papayas", "Mangoes, guavas and mangosteens", "Pigeon peas, dry", "Castor oil seeds",
    "Pineapples", "Tomatoes", "Onions and shallots, dry (excluding dehydrated)",
]


def baixar_tudo():
    s = sessao_http()
    for nome, url in {**FONTES, **AMS}.items():
        d = BR / nome
        try:
            baixar(url, d, s)
            print("ok", nome, d.stat().st_size, flush=True)
        except Exception as e:
            print("FALHOU", nome, e, flush=True)
    registrar_manifesto("mercado", {
        "fontes": {**FONTES, **AMS},
        "ams_status": ("MARS API v1.2 (marsapi.ams.usda.gov) responde 403 sem chave; mymarketnews.ams.usda.gov deu "
                        "timeout; datamart mpr responde 500; relatorios .txt legados param em jul/2020. AMS cobre so EUA."),
        "conab_status": "portaldeinformacoes.conab.gov.br: certificado TLS com nome errado; http redireciona para 404.",
        "cobertura": "FAOSTAT e Pink Sheet: globais. AMS: so EUA.",
    })


def _ler_zip_csv(zp: Path, contem: str) -> pd.DataFrame:
    with zipfile.ZipFile(zp) as z:
        nomes = [n for n in z.namelist() if n.endswith(".csv") and contem in n and "Flags" not in n
                 and "AreaCodes" not in n and "ItemCodes" not in n and "Elements" not in n]
        print(zp.name, "->", nomes, flush=True)
        try:
            with z.open(nomes[0]) as f:
                return pd.read_csv(f, encoding="utf-8", low_memory=False)
        except UnicodeDecodeError:
            with z.open(nomes[0]) as f:
                return pd.read_csv(f, encoding="latin-1", low_memory=False)


def tratar():
    DERIV.mkdir(parents=True, exist_ok=True)
    # FAOSTAT precos ao produtor
    pr = _ler_zip_csv(BR / "faostat_prices.zip", "All_Data")
    pr = pr[pr["Item"].isin(CULTURAS)]
    pr.to_parquet(DERIV / "faostat_precos_produtor.parquet", index=False)
    print("precos", pr.shape, sorted(pr["Element"].unique()), flush=True)
    # FAOSTAT producao
    q = _ler_zip_csv(BR / "faostat_qcl.zip", "All_Data")
    q = q[q["Item"].isin(CULTURAS) & q["Element"].isin(["Area harvested", "Production", "Yield"])]
    q.to_parquet(DERIV / "faostat_producao_qcl.parquet", index=False)
    print("qcl", q.shape, flush=True)
    # Brasil anual
    qb = q[q["Area"] == "Brazil"].pivot_table(index=["Item", "Year"], columns="Element", values="Value").reset_index()
    pb = pr[(pr["Area"] == "Brazil") & (pr["Element"] == "Producer Price (USD/tonne)")]
    if "Months" in pb.columns:
        pb = pb[pb["Months"] == "Annual value"]
    pb = pb.groupby(["Item", "Year"])["Value"].mean().rename("preco_usd_t").reset_index()
    br = qb.merge(pb, on=["Item", "Year"], how="left")
    br.to_parquet(DERIV / "faostat_brasil_anual.parquet", index=False)
    print("brasil", br.shape, flush=True)
    # Pink Sheet mensal (aba Monthly Prices: cabecalho em ~linha 5, unidades na seguinte)
    xl = pd.ExcelFile(BR / "wb_pink_sheet_mensal.xlsx")
    aba = [a for a in xl.sheet_names if "Monthly Prices" in a][0]
    raw = pd.read_excel(xl, aba, header=None)
    lin = raw.index[raw.iloc[:, 0].astype(str).str.fullmatch(r"\d{4}M\d{2}")][0]
    cab = raw.iloc[lin - 2].tolist()
    uni = raw.iloc[lin - 1].tolist()
    dados = raw.iloc[lin:].copy()
    dados.columns = ["periodo"] + [str(c).strip() for c in cab[1:]]
    dados["data"] = pd.to_datetime(dados["periodo"].str.replace("M", "-") + "-01")
    longo = dados.drop(columns="periodo").melt(id_vars="data", var_name="commodity", value_name="preco")
    longo["preco"] = pd.to_numeric(longo["preco"], errors="coerce")
    mapa_uni = {str(c).strip(): str(u).strip() for c, u in zip(cab[1:], uni[1:])}
    longo["unidade"] = longo["commodity"].map(mapa_uni)
    longo = longo.dropna(subset=["preco"])
    longo.to_parquet(DERIV / "mercado_precos_mensal.parquet", index=False)
    print("pink sheet", longo.shape, longo["data"].min(), longo["data"].max(), longo["commodity"].nunique(), flush=True)
    registrar_manifesto("mercado", {
        "derivados": [str(DERIV / n) for n in ["faostat_precos_produtor.parquet", "faostat_producao_qcl.parquet",
                                              "faostat_brasil_anual.parquet", "mercado_precos_mensal.parquet"]],
        "faostat_periodo_precos": [int(pr["Year"].min()), int(pr["Year"].max())],
        "faostat_periodo_producao": [int(q["Year"].min()), int(q["Year"].max())],
        "faostat_n_paises_precos": int(pr["Area"].nunique()),
        "faostat_n_paises_producao": int(q["Area"].nunique()),
        "pink_sheet_periodo": [str(longo["data"].min().date()), str(longo["data"].max().date())],
        "tamanho_bytes": tamanho_pasta(P),
    })


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if modo in ("baixar", "tudo"):
        baixar_tudo()
    if modo in ("tratar", "tudo"):
        tratar()
