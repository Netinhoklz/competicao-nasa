"""Teste por municipio da cadeia oceano -> chuva -> rendimento nos 1.794 municipios do Nordeste.

Mesma linha de jp_expansao_nordeste.py (por estado), agora na escala em que o agricultor decide:
  1. estacao chuvosa de cada municipio (4 meses consecutivos mais chuvosos, IMERG 1998-2025);
  2. chuva da estacao x anomalia de rendimento de milho e feijao (IBGE PAM municipal);
  3. dipolo do Atlantico (fev-mai) x chuva da estacao;
  4. chuva da estacao nos anos que vieram depois de El Nino forte (1998, 2010, 2016, 2024: os mesmos
     analogos de scripts/el_nino_2026.py), em % da mediana do municipio;
  5. umidade do solo na zona da raiz no ultimo mes completo (SMAP L4), como % dos mesmos meses de anos
     anteriores que foram mais secos (o pctl_media do derivado tem nulos justamente onde esta mais seco).
Spearman por municipio; com ~27 anos, |rho| < 0,38 nao e significativo a 5%.

Entradas (dados_resumo/derivados/): ibge_ne_mun_imerg_mensal, ibge_ne_pam_mun_anual,
  ibge_ne_municipios_referencia, ibge_ne_mun_smap_mensal, indices_clima_mensal.
Saidas (conselho/analises/saidas/): jp_nordeste_municipios.parquet (uma linha por municipio),
  jp_nordeste_municipios_chuva.parquet (chuva da estacao por municipio e ano).
Uso: python conselho/analises/jp_nordeste_municipios.py
"""
from __future__ import annotations

import polars as pl

from jp_expansao_nordeste import DERIV, SAIDAS, anomalia_rendimento, estacao_chuvosa, soma_estacao

ANALOGOS = [1998, 2010, 2016, 2024]   # estacoes que vieram depois de El Nino forte, dentro do periodo do IMERG
N_MIN = 20                            # anos minimos para calcular correlacao
RHO_SIG = 0.38                        # |rho| significativo a 5% (bicaudal) com n ~ 27
CULTURAS = {"Milho": "milho", "Feijão": "feijao"}
K = "cod_mun"


def corr_por_municipio(df: pl.DataFrame, a: str, b: str, por: list[str]) -> pl.DataFrame:
    """Spearman e inclinacao (b sobre a) por grupo, so onde ha N_MIN anos."""
    return (df.drop_nulls([a, b]).group_by(por)
            .agg(pl.corr(a, b, method="spearman").alias("rho"),
                 (pl.cov(a, b) / pl.col(a).var()).alias("incl"), pl.len().alias("n"))
            .filter(pl.col("n") >= N_MIN))


def main() -> None:
    ref = pl.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").select(
        K, "municipio", "uf", pl.col("semiarido_2022").alias("semiarido"))
    imerg = (pl.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
             .select(K, pl.col("data").dt.year().alias("ano"), pl.col("data").dt.month().alias("mes"),
                     pl.col("precip_mm").alias("valor")))
    ultimo = imerg.select(pl.col("ano").max()).item()
    est = estacao_chuvosa(imerg.filter(pl.col("ano") <= 2025), K)
    chuva = soma_estacao(imerg, est, chave=K).rename({"x": "chuva"})
    # mediana e tercil inferior da estacao (1998-2025) e chuva em % da mediana
    base = (chuva.filter(pl.col("ano_est") <= 2025).group_by(K)
            .agg(pl.col("chuva").median().alias("mediana"), pl.col("chuva").quantile(1 / 3).alias("t1")))
    chuva = chuva.join(base, on=K).with_columns((pl.col("chuva") / pl.col("mediana") * 100).alias("pct"))

    # 2. chuva x rendimento
    pam = (pl.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
           .filter(pl.col("produto").is_in(list(CULTURAS)) & (pl.col("ano") >= 1995)
                   & (pl.col("rendimento_kg_ha") > 0) & (pl.col("area_colhida_ha") > 0))
           .select(K, "ano", pl.col("produto").replace_strict(CULTURAS).alias("cultura"),
                   pl.col("rendimento_kg_ha").alias("rend")))
    painel = anomalia_rendimento(pam, K).join(chuva, left_on=[K, "ano"], right_on=[K, "ano_est"])
    r = (corr_por_municipio(painel, "chuva", "anom", [K, "cultura"])
         .with_columns((((pl.col("incl") * 100).exp() - 1) * 100).alias("pct100")))
    r = r.pivot(on="cultura", index=K, values=["rho", "pct100", "n"])

    # 3. dipolo do Atlantico x chuva
    idx = pl.read_parquet(DERIV / "indices_clima_mensal.parquet")
    dip = (idx.filter((pl.col("variavel") == "DIPOLO_TNA_menos_TSA") & pl.col("data").dt.month().is_in([2, 3, 4, 5]))
           .group_by(pl.col("data").dt.year().alias("ano_est")).agg(pl.col("valor").mean().alias("dipolo")))
    rd = (corr_por_municipio(chuva.filter(pl.col("ano_est") <= 2025).join(dip, on="ano_est"), "dipolo", "chuva", [K])
          .select(K, pl.col("rho").alias("rho_dipolo")))

    # 4. anos depois de El Nino forte
    an = (chuva.filter(pl.col("ano_est").is_in(ANALOGOS)).group_by(K)
          .agg(pl.col("pct").median().alias("analogo_pct"), (pl.col("chuva") <= pl.col("t1")).sum().alias("analogo_secos"),
               pl.len().alias("analogo_n")))

    # 5. solo agora (SMAP): ultimo mes com pelo menos 25 dias
    smap = pl.read_parquet(DERIV / "ibge_ne_mun_smap_mensal.parquet").filter(pl.col("dias") >= 25)
    mes_smap = smap.select(pl.col("data").max()).item()
    mesmo_mes = smap.filter(pl.col("data").dt.month() == mes_smap.month)
    solo = (mesmo_mes.filter(pl.col("data") < mes_smap)
            .join(mesmo_mes.filter(pl.col("data") == mes_smap).select(K, pl.col("sm_rootzone").alias("agora")), on=K)
            .group_by(K).agg(((pl.col("sm_rootzone") < pl.col("agora")).mean() * 100).alias("solo_pctl"),
                             pl.len().alias("solo_n")))

    mun = (ref.join(est.select(K, "ini", "frac_na_estacao"), on=K, how="left").join(base, on=K, how="left")
           .join(r, on=K, how="left").join(rd, on=K, how="left").join(an, on=K, how="left").join(solo, on=K, how="left")
           .sort(K))
    SAIDAS.mkdir(exist_ok=True)
    mun.write_parquet(SAIDAS / "jp_nordeste_municipios.parquet")
    (chuva.select(K, "ano_est", "chuva", "pct").sort([K, "ano_est"])
     .write_parquet(SAIDAS / "jp_nordeste_municipios_chuva.parquet"))

    def sig(c: str) -> pl.Expr:
        return ((pl.col(c) >= RHO_SIG).mean() * 100).round(0)

    def resumo(por: str) -> pl.DataFrame:
        return (mun.group_by(por).agg(
            pl.len().alias("mun"), pl.col("rho_milho").count().alias("com_milho"),
            pl.col("rho_milho").median().round(2).alias("rho_milho"), sig("rho_milho").alias("%sig_milho"),
            pl.col("rho_feijao").median().round(2).alias("rho_feijao"), sig("rho_feijao").alias("%sig_feijao"),
            pl.col("pct100_milho").median().round(1).alias("milho_%/100mm"),
            pl.col("rho_dipolo").median().round(2).alias("rho_dipolo"),
            ((pl.col("rho_dipolo") <= -RHO_SIG).mean() * 100).round(0).alias("%sig_dipolo"),
            pl.col("analogo_pct").median().round(0).alias("analogo_%"),
            pl.col("solo_pctl").median().round(0).alias("solo_pctl")).sort(por))

    print(f"IMERG ate {ultimo}; SMAP: mes {mes_smap:%Y-%m}; analogos {ANALOGOS}")
    print(f"%sig = % dos municipios com rho >= {RHO_SIG} (o acaso daria ~2,5%)\n")
    print("== Por estado (mediana dos municipios)")
    print(resumo("uf"))
    print("\n== Semiarido (delimitacao 2022) x resto")
    print(resumo("semiarido"))
    print("\n== Mes de inicio da estacao chuvosa: municipios por estado")
    print(mun.group_by("uf", "ini").len().sort("ini").pivot(on="ini", index="uf", values="len").sort("uf"))
    print("\nsalvo:", SAIDAS / "jp_nordeste_municipios.parquet")


if __name__ == "__main__":
    main()
