"""Engenheiro de viabilidade: inventário rápido do que o MVP precisa e já existe em disco.
Só lê arquivos; não escreve nada além do stdout."""
import sys, os, json, time
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import pandas as pd

D = "E:/campeonato-nasa/dados/derivados"
S = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises"


def resumo(path, datecol=None):
    t0 = time.time()
    try:
        df = pd.read_parquet(path)
    except Exception as e:
        print(f"  ERRO {os.path.basename(path)}: {e}")
        return None
    print(f"\n== {os.path.basename(path)} | {df.shape} | {os.path.getsize(path)/1e6:.1f} MB | {time.time()-t0:.1f}s")
    print("  colunas:", list(df.columns)[:20])
    for c in df.columns:
        if c.lower() in ("data", "date", "dia", "ano", "time") or (datecol and c == datecol):
            try:
                print(f"  {c}: {df[c].min()} -> {df[c].max()}  (n únicos {df[c].nunique()})")
            except Exception:
                pass
    for c in ("aoi", "variavel", "municipio", "cod_mun", "codigo", "mun", "cd_mun", "nome", "fonte"):
        if c in df.columns:
            u = df[c].unique()
            print(f"  {c}: {len(u)} únicos; ex.: {list(u[:12])}")
    return df


print("### Séries diárias municipais (núcleo do replay)")
for f in ["chuva_mun_diaria.parquet", "designer_chuva_mun_diaria.parquet"]:
    df = resumo(os.path.join(S, f))
    if df is not None:
        print(df.head(3).to_string())
df = resumo(os.path.join(A, "estrategista_cache_chuva_mun_diaria.parquet"))
if df is not None:
    print(df.head(3).to_string())

print("\n### Painéis municipais e saídas de modelo")
for f in ["painel_mun_ce.parquet", "agronomo_isna_mun_ano.parquet", "hidrologo_fao56_mun_ano.parquet",
          "agronomo_zarc_sintetico_prob.parquet", "carteira_cvar_municipios.parquet", "anom_milho.parquet"]:
    df = resumo(os.path.join(S, f))
    if df is not None:
        print(df.head(2).to_string()[:800])

print("\n### AOIs (barcode, açude, visibilidade)")
for f in ["hls_aoi_mensal.parquet", "landsat_aoi_mensal.parquet", "sentinel2_aoi_mensal.parquet",
          "modis_aoi_mensal.parquet", "imerg_aoi_mensal.parquet", "srtm_aoi_estatico.parquet",
          "srtm_municipios_ce.parquet", "imerg_late_ce_mensal.parquet", "grace_ce_mensal.parquet",
          "gldas_ce_mensal.parquet", "indices_clima_mensal.parquet", "mercado_precos_mensal.parquet",
          "viirs_ce_mensal.parquet", "ibge_pam_mun_anual.parquet"]:
    df = resumo(os.path.join(D, f))
    if df is not None and "variavel" in df.columns and "data" in df.columns:
        g = df.groupby("variavel")["data"].agg(["min", "max", "count"])
        print(g.head(25).to_string())
