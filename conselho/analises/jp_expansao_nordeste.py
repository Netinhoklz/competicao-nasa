"""Expansao da cadeia oceano -> chuva -> rendimento do Ceara para os 9 estados do Nordeste.

Mesma linha do notebook (secoes 13 e 20), agora por estado:
  1. estacao chuvosa de cada estado (4 meses consecutivos mais chuvosos, IMERG 1998-2025);
  2. chuva da estacao x anomalia de rendimento (IBGE PAM estadual, razao a mediana movel de 7 anos);
  3. ONI (out-jan, antes do plantio) e dipolo do Atlantico (durante a estacao) x chuva da estacao;
  4. NDVI MODIS da estacao x anomalia de rendimento.
Correlacao de Spearman; n ~ 27 anos por estado, entao |rho| < ~0,38 nao e significativo a 5%.

Entradas: dados_resumo/derivados/{imerg_ne,modis_ne,indices_clima}_mensal.parquet + API SIDRA (tabela 1612, estados).
Saida: conselho/analises/saidas/jp_expansao_nordeste.csv e jp_pam_ne_estados.parquet
Uso: python conselho/analises/jp_expansao_nordeste.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl
import requests

RAIZ = Path(__file__).resolve().parents[2]
DERIV = RAIZ / "dados_resumo" / "derivados"
SAIDAS = Path(__file__).resolve().parent / "saidas"
UFS = {21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA"}
PRODUTOS = {2711: "milho", 2702: "feijao", 2715: "mandioca"}
ANOS = (1998, 2024)
sys.stdout.reconfigure(encoding="utf-8")
pl.Config.set_tbl_rows(40).set_tbl_cols(20).set_tbl_width_chars(200).set_ascii_tables(True)


def baixar_pam_estados() -> pl.DataFrame:
    """Rendimento medio (kg/ha) por estado, produto e ano - SIDRA 1612, variavel 112."""
    cache = SAIDAS / "jp_pam_ne_estados.parquet"
    if cache.exists():
        return pl.read_parquet(cache)
    url = (f"https://apisidra.ibge.gov.br/values/t/1612/n3/{','.join(map(str, UFS))}/v/112/"
           f"p/{ANOS[0]}-{ANOS[1]}/c81/{','.join(map(str, PRODUTOS))}")
    linhas = requests.get(url, timeout=300).json()[1:]  # a primeira linha e o cabecalho
    df = pl.DataFrame({
        "uf": [UFS[int(x["D1C"])] for x in linhas],
        "ano": [int(x["D3C"]) for x in linhas],
        "cultura": [PRODUTOS[int(x["D4C"])] for x in linhas],
        "rend": [x["V"] for x in linhas],
    }).with_columns(pl.col("rend").cast(pl.Float64, strict=False))  # "-", "..." viram nulo
    df.write_parquet(cache)
    return df


def anomalia_rendimento(pam: pl.DataFrame) -> pl.DataFrame:
    """log(rendimento / mediana movel centrada de 7 anos): tira a tendencia tecnologica."""
    return (pam.sort(["uf", "cultura", "ano"])
            .with_columns(pl.col("rend").rolling_median(7, center=True, min_samples=4).over(["uf", "cultura"])
                          .alias("tend"))
            .with_columns((pl.col("rend") / pl.col("tend")).log().alias("anom"))
            .filter(pl.col("anom").is_finite()))


def estacao_chuvosa(chuva: pl.DataFrame) -> pl.DataFrame:
    """Para cada estado: mes inicial da janela de 4 meses consecutivos com mais chuva na climatologia."""
    clim = chuva.group_by(["uf", "mes"]).agg(pl.col("valor").mean().alias("p"))
    janelas = (clim.join(pl.DataFrame({"ini": list(range(1, 13))}), how="cross")
               .filter(((pl.col("mes") - pl.col("ini")) % 12) < 4)
               .group_by(["uf", "ini"]).agg(pl.col("p").sum().alias("p4")))
    anual = clim.group_by("uf").agg(pl.col("p").sum().alias("p_ano"))
    return (janelas.sort("p4", descending=True).group_by("uf", maintain_order=True).first()
            .join(anual, on="uf").with_columns((pl.col("p4") / pl.col("p_ano")).alias("frac_na_estacao")))


def soma_estacao(serie: pl.DataFrame, est: pl.DataFrame, agg: str = "sum") -> pl.DataFrame:
    """Agrega a serie mensal na estacao de cada estado. O ano da estacao e o ano em que ela termina
    (ex.: estacao nov-fev de 2011/12 conta como 2012, ano da colheita)."""
    s = (serie.join(est.select("uf", "ini"), on="uf")
         .with_columns(((pl.col("mes") - pl.col("ini")) % 12).alias("k"))
         .filter(pl.col("k") < 4)
         .with_columns((pl.col("ano") + ((pl.col("ini") + 3) > 12).cast(pl.Int32)
                        * (pl.col("mes") >= pl.col("ini")).cast(pl.Int32)).alias("ano_est")))
    e = pl.col("valor").sum() if agg == "sum" else pl.col("valor").mean()
    return s.group_by(["uf", "ano_est"]).agg(e.alias("x"), pl.len().alias("n")).filter(pl.col("n") == 4).drop("n")


def spearman(df: pl.DataFrame, a: str, b: str, por: list[str]) -> pl.DataFrame:
    return df.drop_nulls([a, b]).group_by(por).agg(pl.corr(a, b, method="spearman").round(2).alias("rho"),
                                                    pl.len().alias("n"))


def main() -> None:
    SAIDAS.mkdir(exist_ok=True)
    mensal = lambda d: d.with_columns(pl.col("data").dt.year().alias("ano"), pl.col("data").dt.month().alias("mes"))
    imerg = mensal(pl.read_parquet(DERIV / "imerg_ne_mensal.parquet")
                   .filter((pl.col("variavel") == "precip_total") & (pl.col("uf") != "NE")))
    imerg = imerg.filter(pl.col("ano") <= 2025)
    # no MODIS o estado vem como codigo IBGE (21..29); codigos fora do mapa (regiao inteira) saem
    ndvi = mensal(pl.read_parquet(DERIV / "modis_ne_mensal.parquet").filter(pl.col("variavel") == "ndvi")
                  .with_columns(pl.col("uf").replace_strict(UFS, default=None, return_dtype=pl.String))
                  .drop_nulls("uf"))
    idx = mensal(pl.read_parquet(DERIV / "indices_clima_mensal.parquet"))

    est = estacao_chuvosa(imerg)
    print("== 1. Estacao chuvosa por estado (4 meses consecutivos mais chuvosos, IMERG)")
    print(est.select("uf", "ini", pl.col("p4").round(0), pl.col("p_ano").round(0),
                     pl.col("frac_na_estacao").round(2)).sort("ini"))

    chuva = soma_estacao(imerg, est).rename({"x": "chuva"})
    verde = soma_estacao(ndvi, est, "mean").rename({"x": "ndvi"})
    anom = anomalia_rendimento(baixar_pam_estados())
    painel = (anom.join(chuva, left_on=["uf", "ano"], right_on=["uf", "ano_est"], how="left")
              .join(verde, left_on=["uf", "ano"], right_on=["uf", "ano_est"], how="left"))

    print("\n== 2. Chuva da estacao x anomalia de rendimento (Spearman por estado)")
    r_chuva = spearman(painel, "chuva", "anom", ["uf", "cultura"])
    print(r_chuva.pivot(on="cultura", index="uf", values="rho").sort("uf"))
    # elasticidade: % de rendimento por +100 mm (regressao linear simples do log-anomalia na chuva)
    elast = (painel.drop_nulls(["chuva", "anom"]).group_by(["uf", "cultura"])
             .agg((pl.cov("chuva", "anom") / pl.col("chuva").var()).alias("b"))
             .with_columns((((pl.col("b") * 100).exp() - 1) * 100).round(1).alias("pct_por_100mm")))
    print("   elasticidade (% de rendimento por +100 mm na estacao):")
    print(elast.pivot(on="cultura", index="uf", values="pct_por_100mm").sort("uf"))

    print("\n== 3. Oceano x chuva da estacao")
    # ONI medio de out-jan (jan pertence ao ano da colheita) e dipolo medio de fev-mai
    oni = (idx.filter((pl.col("variavel") == "ONI") & pl.col("mes").is_in([10, 11, 12, 1]))
           .with_columns((pl.col("ano") + (pl.col("mes") >= 10).cast(pl.Int32)).alias("ano_est"))
           .group_by("ano_est").agg(pl.col("valor").mean().alias("oni_out_jan")))
    dip = (idx.filter((pl.col("variavel") == "DIPOLO_TNA_menos_TSA") & pl.col("mes").is_in([2, 3, 4, 5]))
           .group_by(pl.col("ano").alias("ano_est")).agg(pl.col("valor").mean().alias("dipolo_fev_mai")))
    tele = chuva.join(oni, on="ano_est").join(dip, on="ano_est")
    r_oni = spearman(tele, "oni_out_jan", "chuva", ["uf"]).rename({"rho": "rho_oni"})
    r_dip = spearman(tele, "dipolo_fev_mai", "chuva", ["uf"]).rename({"rho": "rho_dipolo"}).drop("n")
    print(r_oni.join(r_dip, on="uf").join(est.select("uf", "ini"), on="uf").sort("rho_dipolo"))

    print("\n== 4. NDVI da estacao x anomalia de rendimento (Spearman por estado)")
    r_ndvi = spearman(painel, "ndvi", "anom", ["uf", "cultura"])
    print(r_ndvi.pivot(on="cultura", index="uf", values="rho").sort("uf"))

    resumo = (r_chuva.rename({"rho": "rho_chuva_rend"})
              .join(r_ndvi.rename({"rho": "rho_ndvi_rend"}).drop("n"), on=["uf", "cultura"])
              .join(elast.drop("b"), on=["uf", "cultura"]).join(r_oni.drop("n"), on="uf").join(r_dip, on="uf")
              .join(est.select("uf", pl.col("ini").alias("mes_inicio_estacao")), on="uf").sort(["cultura", "uf"]))
    resumo.write_csv(SAIDAS / "jp_expansao_nordeste.csv")
    print("\nsalvo:", SAIDAS / "jp_expansao_nordeste.csv")


if __name__ == "__main__":
    main()
