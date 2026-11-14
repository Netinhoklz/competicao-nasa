"""Recorte compacto para a página do agricultor: 184 municípios, sem preços (só leitura do projeto)."""
import json, sys
import numpy as np, pandas as pd

P = sys.argv[1]; OUT = sys.argv[2]; GEO = sys.argv[3]

chuva = pd.read_parquet(f'{P}/conselho/analises/saidas/chuva_mun_diaria.parquet')
srtm = pd.read_parquet(f'{P}/dados_resumo/derivados/srtm_municipios_ce.parquet')
pam = pd.read_parquet(f'{P}/dados_resumo/derivados/ibge_pam_mun_anual.parquet')
ind = pd.read_parquet(f'{P}/dados_resumo/derivados/indices_clima_mensal.parquet')

nomes = dict(zip(srtm.codarea.astype(str), srtm.municipio))
relevo = {str(r.codarea): [round(r.elev_media), round(r.decl_media_graus, 1),
                           round(r.frac_ondulado_8a20 + r.frac_forte_20a45 + r.frac_montanhoso_gt45, 3)] for r in srtm.itertuples()}

# chuva diária 1º/jan–30/jun (181 dias) de 1998 a 2026, mm inteiros; zero vira vazio
anos = list(range(1998, 2027))
rain = {}
for cod in chuva.columns:
    vals = []
    for a in anos:
        s = chuva.loc[f'{a}-01-01':, cod].values[:181]
        s = np.pad(s.astype(float), (0, 181 - len(s)), constant_values=np.nan)
        vals += ['' if (not np.isfinite(v) or round(v) == 0) else str(int(round(v))) for v in s]
    rain[cod] = ','.join(vals)

oni = ind[ind.variavel == 'ONI'].copy(); oni['ano'] = oni.data.dt.year; oni['mes'] = oni.data.dt.month
oni_jas = {int(a): round(float(v), 2) for a, v in oni[oni.mes.isin([7, 8, 9])].groupby('ano').valor.mean().items() if a >= 1996}

def sen_trend(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    i, j = np.triu_indices(len(x), 1)
    s = np.median((y[j] - y[i]) / (x[j] - x[i])); return s, np.median(y - s * x)

CULT = {'Milho (em grão)': 'milho', 'Feijão (em grão)': 'feijao', 'Mandioca': 'mandioca', 'Sorgo (em grão)': 'sorgo',
        'Fava (em grão)': 'fava', 'Castanha de caju': 'caju', 'Gergelim': 'gergelim', 'Batata-doce': 'batata',
        'Amendoim (em casca)': 'amendoim', 'Algodão herbáceo (em caroço)': 'algodao'}
p = pam[pam.produto.isin(CULT) & (pam.ano >= 1990)].copy()
p['c'] = p.produto.map(CULT)
p['rend'] = np.where(p.area_plantada_ha > 0, p.producao_t * 1000 / p.area_plantada_ha, np.nan)
milho = {}; culturas = {}
for (cod, c), g in p.groupby(['cod_local', 'c']):
    g = g[(g.rend > 0) & np.isfinite(g.rend)]
    if len(g) < 15: continue
    s, b = sen_trend(g.ano, np.log(g.rend))
    rel = np.exp(np.log(g.rend) - (s * g.ano + b))
    if c == 'milho': milho[cod] = {int(a): round(float(r), 2) for a, r in zip(g.ano, rel)}
    r01 = rel[g.ano.values >= 2001]
    if len(r01) < 12: continue
    area = p[(p.cod_local == cod) & (p.c == c) & (p.ano >= 2019)].area_plantada_ha.mean()
    if not area or area < 5: continue
    culturas.setdefault(cod, {})[c] = [round(float(np.sort(r01)[:3].mean()), 2), int((r01 < 0.5).sum()), int(len(r01)), round(float(area))]

fm = chuva[(chuva.index.month >= 2) & (chuva.index.month <= 5)].groupby(chuva[(chuva.index.month >= 2) & (chuva.index.month <= 5)].index.year).sum()
anual = {}
for cod in chuva.columns:
    base = fm.loc[1998:2025, cod].median()
    anual[cod] = {'fm': [round(float(fm.loc[a, cod] / base * 100)) if a in fm.index else None for a in anos],
                  'milho': [milho.get(cod, {}).get(a) for a in anos]}

geo = json.load(open(GEO))
feats = [{'c': f['properties']['codarea'], 'g': f['geometry']} for f in geo['features']]
out = dict(anos=anos, nomes=nomes, relevo=relevo, rain=rain, oni_jas=oni_jas,
           oni_ultimo={'mes': str(oni.data.max().date()), 'valor': float(oni.sort_values('data').valor.iloc[-1])},
           culturas=culturas, anual=anual, geo=feats)
json.dump(out, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
print('ok', len(json.dumps(out, ensure_ascii=False)) // 1024, 'KB', len(culturas), 'municípios com culturas')
print(culturas.get('2311306'))
