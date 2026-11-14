"""Extrai um recorte compacto dos dados do projeto para o protótipo (só leitura do projeto)."""
import json, sys
import numpy as np, pandas as pd

P = sys.argv[1]; OUT = sys.argv[2]; GEO = sys.argv[3]
SEL = ['2311306', '2311405', '2302800', '2313302', '2304103', '2312908', '2305506', '2304202', '2313401', '2307601']

chuva = pd.read_parquet(f'{P}/conselho/analises/saidas/chuva_mun_diaria.parquet')
srtm = pd.read_parquet(f'{P}/dados_resumo/derivados/srtm_municipios_ce.parquet')
pam = pd.read_parquet(f'{P}/dados_resumo/derivados/ibge_pam_mun_anual.parquet')
ind = pd.read_parquet(f'{P}/dados_resumo/derivados/indices_clima_mensal.parquet')

nomes = dict(zip(srtm.codarea.astype(str), srtm.municipio))
relevo = {str(r.codarea): [round(r.elev_media), round(r.decl_media_graus, 1), round(r.frac_ondulado_8a20 + r.frac_forte_20a45 + r.frac_montanhoso_gt45, 3)] for r in srtm.itertuples()}

# chuva diária (décimos de mm) dos municípios selecionados
inicio = str(chuva.index[0].date())
rain = {c: ','.join(str(int(round(v * 10))) if np.isfinite(v) else '0' for v in chuva[c].values) for c in SEL}

# ONI: média jul–set de cada ano (o que se sabe em novembro)
oni = ind[ind.variavel == 'ONI'].copy(); oni['ano'] = oni.data.dt.year; oni['mes'] = oni.data.dt.month
oni_jas = oni[oni.mes.isin([7, 8, 9])].groupby('ano').valor.mean().round(2)
oni_jas = {int(a): float(v) for a, v in oni_jas.items() if a >= 1996}

def sen_trend(anos, y):
    anos = np.asarray(anos, float); y = np.asarray(y, float)
    i, j = np.triu_indices(len(anos), 1)
    s = np.median((y[j] - y[i]) / (anos[j] - anos[i]))
    b = np.median(y - s * anos)
    return s, b

# rendimento relativo à tendência (Theil-Sen em log), por município x cultura
CULT = {'Milho (em grão)': 'milho', 'Feijão (em grão)': 'feijao', 'Mandioca': 'mandioca', 'Sorgo (em grão)': 'sorgo',
        'Fava (em grão)': 'fava', 'Castanha de caju': 'caju', 'Gergelim': 'gergelim', 'Batata-doce': 'batata',
        'Amendoim (em casca)': 'amendoim', 'Algodão herbáceo (em caroço)': 'algodao'}
p = pam[pam.produto.isin(CULT) & (pam.ano >= 1990)].copy()
p['c'] = p.produto.map(CULT)
p['rend'] = np.where(p.area_plantada_ha > 0, p.producao_t * 1000 / p.area_plantada_ha, np.nan)
# preço implícito estadual (R$/kg) mediana 2019–2025
pr = p[(p.ano >= 2019) & (p.producao_t > 0)].groupby(['c', 'ano']).agg(v=('valor_mil_moeda', 'sum'), q=('producao_t', 'sum'))
preco = (pr.v / pr.q).groupby('c').median().round(2).to_dict()  # mil R$/t = R$/kg

yrel = {}   # cod -> cultura -> {ano: rel}
culturas = {}
for (cod, c), g in p.groupby(['cod_local', 'c']):
    g = g[(g.rend > 0) & np.isfinite(g.rend)]
    if len(g) < 15:
        continue
    s, b = sen_trend(g.ano, np.log(g.rend))
    rel = np.exp(np.log(g.rend) - (s * g.ano + b))
    yrel.setdefault(cod, {})[c] = {int(a): round(float(r), 2) for a, r in zip(g.ano, rel)}
    if cod in SEL:
        r01 = rel[g.ano.values >= 2001]
        if len(r01) < 12:
            continue
        rend_hoje = float(np.exp(s * 2025 + b))
        piores = np.sort(r01)[:3].mean()
        area = p[(p.cod_local == cod) & (p.c == c) & (p.ano >= 2019)].area_plantada_ha.mean()
        culturas.setdefault(cod, {})[c] = dict(rend=round(rend_hoje), ruim=round(float(piores), 2),
                                             p50=round(float((r01 < 0.5).mean()), 2), anos=int(len(r01)),
                                             area=round(float(area)),
                                             serie={int(a): round(float(r), 2) for a, r in zip(g.ano, rel) if a >= 1998})

# resumo anual de todos os municípios: % do normal da chuva acumulada até 28/fev, 31/mar, 30/abr e fev–mai
ch = chuva.copy(); ch['ano'] = ch.index.year; ch['doy'] = ch.index.day_of_year
anual = {}
cortes = {'fev': 59, 'mar': 90, 'abr': 120}
tab = {}
for k, d in cortes.items():
    tab[k] = ch[ch.doy <= d].groupby('ano').sum(numeric_only=True).drop(columns='doy')
tab['fm'] = ch[(ch.index.month >= 2) & (ch.index.month <= 5)].groupby('ano').sum(numeric_only=True).drop(columns='doy')
anos = list(range(1998, 2027))
for cod in chuva.columns:
    linha = {}
    for k, t in tab.items():
        base = t.loc[1998:2025, cod].median()
        linha[k] = [round(float(t.loc[a, cod] / base * 100)) if a in t.index else None for a in anos]
    linha['milho'] = [yrel.get(cod, {}).get('milho', {}).get(a) for a in anos]
    linha['feijao'] = [yrel.get(cod, {}).get('feijao', {}).get(a) for a in anos]
    anual[cod] = linha

geo = json.load(open(GEO))
feats = [{'c': f['properties']['codarea'], 'g': f['geometry']} for f in geo['features']]

out = dict(inicio=inicio, sel=SEL, nomes=nomes, relevo=relevo, rain=rain, oni_jas=oni_jas,
           oni_ultimo={'mes': str(oni.data.max().date()), 'valor': float(oni.sort_values('data').valor.iloc[-1])},
           preco=preco, culturas=culturas, anos=anos, anual=anual, geo=feats)
json.dump(out, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
print('ok', len(json.dumps(out)) // 1024, 'KB'); print(preco); print(culturas.get('2311306')); print({a: v for a, v in oni_jas.items()})
