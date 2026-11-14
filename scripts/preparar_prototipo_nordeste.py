"""Prepara os dados do protótipo QUADRA para os 1.794 municípios do Nordeste (o protótipo começou só no Ceará).

Tarefas (rodam na ordem dada; padrão = todas):
- zarc        : tábua de risco do ZARC (MAPA, dados abertos) 2025/26 e 2026/27, filtrada em fluxo para as 9 UFs do NE
                -> complementares/zarc_ne/tabua_risco_ne_<safra>.csv
- assinaturas : assinatura climática do NASA POWER no ponto interno de cada município (cache por célula 0,5° × 0,625°;
                reaproveita as células já calculadas no CE) -> analogos_aprofundado/ne_mun_assinaturas.csv
- inicio      : início da estação pela chuva IMERG diária 0,1° (mesma regra do CE: a partir de 1/dez, 1º dia com ≥ 20 mm
                em 3 dias sem veranico de ≥ 10 dias secos nos 30 seguintes). Município sem centro de célula dentro usa a
                célula mais próxima do ponto interno -> analogos_aprofundado/onset_ne_mun.csv
- gaez_zarc   : situação de cada cultura em cada município (mesma regra decidida em 14/11) -> gaez_zarc/nordeste_<safra>.csv
Uso: python -I preparar_prototipo_nordeste.py [zarc] [assinaturas] [inicio] [gaez_zarc]
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import xarray as xr  # noqa: E402
from scipy import sparse  # noqa: E402

import analogos_climaticos_artigos as AC  # noqa: E402
import gaez_zarc_municipio as GZ  # noqa: E402
from comum import DADOS, pasta, registrar_manifesto, sessao_http  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
UFS = {"MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"}
SAFRAS = ["2025-2026", "2026-2027"]
OUT_A = DADOS / "analogos_aprofundado"


def municipios():
    """Malha do IBGE dos 1.794 municípios do NE com nome, UF e mesorregião, e o ponto interno."""
    g = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
    g["cod"] = g.codarea.astype(str)
    loc = {str(m["id"]): m for m in json.loads((DADOS / "ibge_nordeste" / "localidades_municipios_ne.json").read_text(encoding="utf-8"))}
    g["municipio"] = g.cod.map(lambda c: loc[c]["nome"])
    g["uf"] = g.cod.map(lambda c: loc[c]["microrregiao"]["mesorregiao"]["UF"]["sigla"])
    g["mesorregiao"] = g.cod.map(lambda c: loc[c]["microrregiao"]["mesorregiao"]["nome"])
    rp = g.geometry.representative_point()
    g["lat"], g["lon"] = rp.y, rp.x
    return g


def zarc():
    base = pasta("complementares/zarc_ne")
    raiz = "https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f/resource/"
    arq = {"2025-2026": "f9d597f9-0fee-47eb-9344-8642274ca9da/download/dados-abertos-tabua-de-risco-safra-2025-2026.csv",
           "2026-2027": "139e5a60-1f43-4cc8-aeab-a35dbbf816c0/download/dados-abertos-tabua-de-risco-safra-2026-2027.csv"}
    s = sessao_http()
    res = {}
    for safra, rel in arq.items():
        t0, n_tot, n_ne = time.time(), 0, 0
        with s.get(raiz + rel, stream=True, timeout=180) as r, open(base / f"tabua_risco_ne_{safra}.csv", "w", encoding="utf-8") as f:
            r.raise_for_status()
            r.encoding = "utf-8-sig"
            cab = iuf = None
            for linha in r.iter_lines(decode_unicode=True):
                if linha is None:
                    continue
                if cab is None:
                    cab = linha.lstrip("\ufeff")
                    f.write(cab + "\n")
                    iuf = cab.split(";").index("UF")
                    continue
                n_tot += 1
                p = linha.split(";")
                if len(p) > iuf and p[iuf] in UFS:
                    f.write(linha + "\n")
                    n_ne += 1
        res[safra] = {"linhas_brasil": n_tot, "linhas_ne": n_ne}
        print("zarc", safra, res[safra], f"{time.time() - t0:.0f}s", flush=True)
    registrar_manifesto("complementares/zarc_ne", {"fonte": "MAPA, ZARC - Tábua de Risco, dados abertos",
                                                   "url": "https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f",
                                                   "recorte": "UF do Nordeste (MA, PI, CE, RN, PB, PE, AL, SE, BA), filtro em fluxo",
                                                   "safras": res, "script": "scripts/preparar_prototipo_nordeste.py"}, base=base)


def assinaturas():
    g = municipios()
    chave = lambda la, lo: (round(la * 2) / 2, round(lo / 0.625) * 0.625)  # noqa: E731  célula nativa do POWER
    cache = {}  # não reaproveita o CE antigo: ele usava a Tmax/Tmin recorde da climatologia (revisão C2)
    faltam = sorted({chave(la, lo): (la, lo) for la, lo in zip(g.lat, g.lon)}.items())
    print(f"assinaturas: {len(g)} municípios; {len(faltam)} células do POWER a consultar", flush=True)

    def uma(item):
        k, (la, lo) = item
        for tentativa in range(4):
            try:
                time.sleep(0.4)
                return k, AC.assinatura(la, lo)
            except Exception as e:  # a API do POWER às vezes devolve 429/5xx
                time.sleep(5 * (tentativa + 1))
                erro = e
        print("  falhou", k, erro, flush=True)
        return k, None

    with ThreadPoolExecutor(4) as ex:
        for i, (k, v) in enumerate(ex.map(uma, faltam), 1):
            if v:
                cache[k] = v
            if i % 50 == 0:
                print(f"  {i}/{len(faltam)} células", flush=True)
    linhas = [{"cod": r.cod, "municipio": r.municipio, "uf": r.uf, "mesorregiao": r.mesorregiao, "lat": r.lat, "lon": r.lon,
               **cache.get(chave(r.lat, r.lon), {})} for r in g.itertuples()]
    A = pd.DataFrame(linhas)
    A.to_csv(OUT_A / "ne_mun_assinaturas.csv", index=False)
    # o arquivo do CE (usado pelos notebooks) passa a ser o recorte do mesmo cálculo
    A[A.uf == "CE"].drop(columns="uf").to_csv(OUT_A / "ceara_mun_assinaturas.csv", index=False)
    print("assinaturas:", len(A), "municípios; sem assinatura:", int(A.chuva_anual_mm.isna().sum()), flush=True)


def inicio():
    g = municipios()
    ref = xr.open_dataset(DADOS / "imerg" / "imerg_ne_diario_2010.nc")
    lat, lon = ref.lat.values, ref.lon.values
    lo, la = np.meshgrid(lon, lat)
    idx = np.full(lo.size, -1)
    for j, geom in enumerate(g.geometry):
        idx[shapely.contains_xy(geom, lo, la).ravel()] = j
    sem = [j for j in range(len(g)) if not (idx == j).any()]
    # matriz de média: célula -> município; quem não tem centro de célula dentro usa a célula mais próxima do ponto interno
    linhas_m, colunas_m = list(np.where(idx >= 0)[0]), list(idx[idx >= 0])
    for j in sem:
        i = int(np.argmin((la.ravel() - g.lat.iloc[j]) ** 2 + (lo.ravel() - g.lon.iloc[j]) ** 2))
        linhas_m.append(i)
        colunas_m.append(j)
    M = sparse.csr_matrix((np.ones(len(linhas_m)), (linhas_m, colunas_m)), shape=(lo.size, len(g)))
    M = M.multiply(1 / np.asarray(M.sum(0)).ravel()).tocsr()
    print(f"inicio: {len(g)} municípios; {len(sem)} sem centro de célula (usam a mais próxima)", flush=True)
    partes = []
    for a in range(1998, 2027):
        p = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc").precip
        v = np.nan_to_num(p.values.reshape(p.sizes["time"], -1), nan=0.0)
        partes.append(pd.DataFrame(np.asarray(M.T @ v.T).T, index=pd.to_datetime(p.time.values), columns=g.cod.values))
    S = pd.concat(partes)
    S = S[~S.index.duplicated()]
    # regime de chuva de cada município: os 4 meses seguidos mais chuvosos da climatologia IMERG (anos completos 1998–2025).
    # O Nordeste tem três regimes: quadra do norte (fev–mai), litoral leste (abr–jul) e Cerrado/sul da BA (nov–mar).
    clim = S[S.index.year <= 2025].groupby(S.index[S.index.year <= 2025].month).sum() / 28  # mm/mês
    m0 = {}
    for c in S.columns:
        tot4 = [sum(clim[c].iloc[(k + j) % 12] for j in range(4)) for k in range(12)]
        m0[c] = int(np.argmax(tot4)) + 1  # mês de início dos 4 meses mais chuvosos
    MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    reg = pd.DataFrame({"cod": list(m0), "mes_inicio_estacao": list(m0.values())})
    reg["estacao"] = reg.mes_inicio_estacao.map(lambda m: f"{MESES[m - 1]}–{MESES[(m + 2) % 12]}")
    reg["chuva_estacao_media_mm"] = [round(float(sum(clim[c].iloc[(m - 1 + j) % 12] for j in range(4))), 0) for c, m in m0.items()]
    reg["fracao_do_ano"] = [round(float(r / clim[c].sum()), 2) for c, r in zip(reg.cod, reg.chuva_estacao_media_mm)]
    reg.to_csv(OUT_A / "regime_chuva_ne_mun.csv", index=False)
    print("regimes (mês de início dos 4 meses mais chuvosos):", reg.estacao.value_counts().to_dict(), flush=True)

    reg["regra"] = np.where(reg.mes_inicio_estacao <= 2, "quadra do norte: busca de 1/dez a 31/mai; chuva da quadra fev–mai",
                            "busca de 2 meses antes da estação até o fim dela; chuva dos 4 meses mais chuvosos")
    reg.to_csv(OUT_A / "regime_chuva_ne_mun.csv", index=False)

    def janela(a, m):
        """Estação 'a' do município.
        - Quadra do norte (4 meses mais chuvosos começando em jan ou fev): a mesma regra do CE, para os números do CE não
          mudarem — busca de 1/dez de a−1 a 31/mai de a; chuva da estação = fev–mai.
        - Outros regimes (litoral leste mar/abr–jun/jul; Cerrado e sul da BA out/nov/dez–jan/fev/mar): busca de 2 meses
          antes do 1º mês da estação até o fim do 4º mês. Rótulo = ano em que cai o 1º mês se ele for ≤ 6; senão, o ano
          seguinte (ex.: nov–fev de 2026/27 = estação 2027)."""
        if m <= 2:
            return pd.Timestamp(a - 1, 12, 1), pd.Timestamp(a, 2, 1), pd.Timestamp(a, 5, 31)
        ano_m0 = a if m <= 6 else a - 1
        ini = pd.Timestamp(ano_m0, m, 1) - pd.DateOffset(months=2)
        fim_est = pd.Timestamp(ano_m0, m, 1) + pd.DateOffset(months=4) - pd.Timedelta(days=1)
        return ini, pd.Timestamp(ano_m0, m, 1), fim_est

    linhas = []
    for c in S.columns:
        x = S[c]
        m = m0[c]
        for a in range(1998, 2028):
            ini, i0, fim = janela(a, m)
            if ini < S.index.min() or fim > S.index.max():
                continue  # estação sem dado completo (IMERG via POWER de 1998 a 14/09/2026: Final até 30/09/2025, depois Late, preliminar)
            jan = x[(x.index >= ini) & (x.index <= fim)]
            v = jan.values
            on = pd.NaT
            for i in range(len(v) - 32):
                if v[i:i + 3].sum() >= 20:
                    seco = v[i + 3:i + 33] < 1
                    corrida = maxc = 0
                    for s_ in seco:
                        corrida = corrida + 1 if s_ else 0
                        maxc = max(maxc, corrida)
                    if maxc < 10:
                        on = jan.index[i]
                        break
            linhas.append({"cod": c, "ano": a, "mes_inicio_estacao": m, "inicio_chuva": on,
                           "chuva_estacao_mm": float(x[(x.index >= i0) & (x.index <= fim)].sum())})
    R = pd.DataFrame(linhas)
    R.to_csv(OUT_A / "onset_ne_mun.csv", index=False)
    print("sem início por UF (%):", R.assign(uf=R.cod.str[:2]).groupby("uf").inicio_chuva.apply(lambda s: round(s.isna().mean() * 100, 1)).to_dict(),
          flush=True)
    print("inicio:", R.cod.nunique(), "municípios ×", R.ano.nunique(), "quadras; sem início:", f"{R.inicio_chuva.isna().mean():.1%}",
          "| IMERG até", S.index.max().date(), flush=True)


def gaez_zarc(safra="2026-2027"):
    g = municipios()
    si = GZ.aptidao(list(zip(g.lon, g.lat)))
    Z = pd.read_csv(DADOS / "complementares" / "zarc_ne" / f"tabua_risco_ne_{safra}.csv", sep=None, engine="python")
    Z = Z[Z.Nome_Outros_Manejos == "Sequeiro"]
    todas = []
    for i, r in enumerate(g.itertuples()):
        T = GZ.tabela({k: v[i] for k, v in si.items()}, Z[Z.geocodigo == int(r.cod)])
        T["situacao"] = T.apply(GZ.situacao, axis=1)
        T["zarc_no_municipio"] = T._tem_zarc
        T["ZARC"] = T.ZARC.where(T.GAEZ != "—", "Mamona")
        T.insert(0, "geocodigo", r.cod)
        T.insert(1, "municipio", r.municipio)
        T.insert(2, "uf", r.uf)
        T.insert(3, "mesorregiao", r.mesorregiao)
        todas.append(T)
    A = pd.concat(todas)
    A["cultura"] = A.ZARC.where(A.ZARC != GZ.SEM_ZARC, A.GAEZ)
    saida = DADOS / "gaez_zarc"
    A.drop(columns=[c for c in A.columns if c.startswith("_")]).to_csv(saida / f"nordeste_{safra}.csv", index=False)
    print(f"gaez_zarc: {A.geocodigo.nunique()} municípios; ZARC {safra}; municípios com alguma linha de ZARC: "
          f"{Z.geocodigo.nunique()}", flush=True)
    print(pd.crosstab(A.uf, A.situacao).to_string(), flush=True)


if __name__ == "__main__":
    tarefas = sys.argv[1:] or ["zarc", "assinaturas", "inicio", "gaez_zarc"]
    for t in tarefas:
        t0 = time.time()
        {"zarc": zarc, "assinaturas": assinaturas, "inicio": inicio, "gaez_zarc": gaez_zarc}[t]()
        print(f"[{t}] {time.time() - t0:.0f}s", flush=True)
