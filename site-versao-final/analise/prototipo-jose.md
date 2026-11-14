# Protótipo do José como núcleo (prototipo-jose)

## Resumo
O motor do José (protótipo/motor.py, consultar(), motor.py:968-1036) serve como núcleo do sistema final. Ele já entrega, por município, o local, o clima, o cardápio com janelas por solo, o "este ano" (El Niño, SMAP, início da chuva), o plano A/B/C + baixio + bordas e a agenda até dez/2027. Falta tudo o que as telas novas pedem: perguntas além do solo, áreas para a distribuição, financeiro, série histórica e projeção por ciclo. Medi a resposta em 0,47–0,70 s por município, sem cache de resposta (curl e frio.py). A subida a frio leva 3,7 s no import do motor e mais 1,2 s no SMAP. Recomendo exportar 1 JSON estático por município (contrato quadra-mun-v1) e 1 índice global. Assim o site roda sem Python e não depende do POWER ao vivo, porque os 1.794 municípios do NE já têm a assinatura pré-calculada. A /api/local fica só para as variantes de solo e as perguntas. Os blocos novos (financeiro, série e projeção) saem do painel PAM 1998–2025 em R$ de 2025 e da chuva da estação (IMERG). A projeção usa quantis empíricos do próprio município; só o ciclo de 2027 é condicionado aos anos de El Niño forte (em Quixadá, o milho cai para 29% do normal e a mandioca fica em 58%). Estes pontos ainda abertos afetam a tela: (1) fora do CE, os ciclos de cultivar do ZARC não foram conferidos (1.610 de 1.794 municípios no caupi); (2) onde a mandioca fica "fora" (cerca de 590 municípios), o giro põe gramínea depois de gramínea; (3) no oeste da BA, a PAM municipal é de agronegócio; (4) o site tem duas definições de El Niño (a do motor e a do painel do JP).

## Recomendações
- **P0** (1.5 h) Escrever site-versao-final/ferramentas/exportar_estatico.py. Ele importa uma cópia do motor, chama consultar() no ponto interno dos 1.794 municípios com hoje=2026-11-15 (precisa de um parâmetro hoje em consultar, ou de um monkeypatch na agenda), aplica o _limpa do app.py e grava indice.json (fontes, ONI, cartões, CICLO, cardápio, perguntas, lista de municípios) e mun/<cod>.json no contrato v1. O motor.CACHE vai para uma pasta por processo. — Com isso o site roda sem Python, cada município abre em um fetch de ~6 KB com gzip e a demo deixa de depender da 8765. São ~18 min por variante num processo.
- **P0** (2.5 h) Acrescentar ao export os blocos 'serie' (rendimento por ha plantado 1998–2025 por produto PAM + chuva da estação do ONS + anos de El Niño forte), 'financeiro' (P10/P50/P90 da receita em R$ de 2025, % de anos com receita zero, desembolso CONAB familiar da UF, margem) e 'projecao' (por linha da agenda com colheita: quantis incondicionais e, só no ciclo de 2027, os anos de El Niño forte um a um). — São as telas de financeiro e de segurança. Os dados já estão em disco (painel_mun_cultura_ano.parquet, conab_custos_ne.csv, onset_ne_mun.csv), e as fórmulas já existem em notebooks/secoes_financeiro/04_receita.py e 06_risco.py.
- **P0** (1 h) Fazer o front ler primeiro o arquivo estático e, quando houver variante de solo, chamar /api/local?lat&lon&textura&ad se o servidor responder. Sem servidor, mostrar 'solo: melhor caso'. Recalcular a linha de hoje e o 'O que fazer agora' no navegador a partir de agenda.linhas[].barras. — O site degrada sem Python e não mostra 'Janela aberta agora' com data velha para quem abrir depois de 15/11.
- **P0** (0.5 h) Unificar o El Niño em uma definição, a do motor (FORTES: ONI OND–NDJ ≥ 1,5; quadras 1998, 2010, 2016, 2024), e trocar o 'enso' do painel do JP por ela. — Hoje o painel do JP e o motor mostram anos análogos diferentes na mesma jornada.
- **P0** (1 h) Pôr selos na tela: 'datas do ZARC fora do CE incluem grupos de ciclo sem cultivar conferida', 'janela estimada (suposição)' e 'colheita = plantio + ciclo suposto'. Sinalizar a PAM de agronegócio, por exemplo quando o P50 do rendimento passa de 2× a produtividade CONAB familiar da UF, e não mostrar o R$ nesses casos. — Separa o medido da suposição sem precisar ler as portarias dos 8 estados antes do prazo, e evita prometer ao roçado familiar a receita de uma lavoura comercial.
- **P1** (1 h) Giro de 3 fases sem mandioca: escrever no plano e na distribuição que 2 de 3 fases são gramíneas e a lagarta não se quebra. Se der tempo, trocar a 3ª fase por uma não-gramínea do cardápio (guandu/palma perene, ou pousio pastejado). — Atinge cerca de 590 municípios, e a percolação do Vicente vai mostrar esse bloco contínuo de hospedeiro.
- **P1** (1 h) Exportar as 3 variantes de solo (arenoso, médio, argiloso → textura 1/2/3 + AD 12/14/16, mapeamento suposto) em mun/<cod>.solo<k>.json, só com plano e agenda. Primeiro para cerca de 10 municípios da demo, depois para todos. — A resposta ao 'como fica a terra quando chove' passa a mudar as datas também sem Python. Para os 1.794 municípios são ~54 min num processo só.
- **P1** (0.5 h) Alinhar a 9.7 e o deck com os números que a API dá hoje (Quixadá: ponderado leguminosa→cereal 28%, soma_w 0,46; melhor análogo Bom Jesus w 0,95), ou o contrário. — A2 continua pendente, e o júri vai ver um número no slide e outro no site.
- **P2** (8 h) Portar janela()/_linha() para JS lendo vetores de decêndios do ZARC por cultura e solo, para qualquer solo no navegador. Conferir as portarias de ciclo com cultivar nos 8 estados. Fazer a tábua plurianual fora do CE. — Tira de vez o Python do caminho e corrige a base. Não cabe até 15/11 23:59.

## Achados
- **Tempo de resposta e subida a frio medidos**: Os tempos de /api/local na 8765 são estes: Quixadá 0,69 s, Arapiraca 0,55 s, Barreiras 0,47 s e Quixadá com textura=1&ad=11 0,70 s. A 2ª chamada leva o mesmo tempo, porque não existe cache da resposta, só do GAEZ e do POWER. Num processo isolado, o import do motor leva 3,7 s e o SMAP fica pronto 1,2 s depois, com o cache válido. O custo está em cardapio(), com 0,85 s por consulta: janelas_por_solo e zarc_plurianual filtram o pandas linha a linha. A agenda leva 0,35 s. /api/municipios responde em 0,006 s, mas tem 2,8 MB (733 KB com gzip). Pré-calcular os 1.794 municípios leva cerca de 18 min por variante de solo num processo só. _[scratchpad/analise10/prototipo-jose/frio.py (saída: import 3,7 s; SMAP +1,2 s; cProfile cardapio 2,53 s/3 consultas); curl -w %{time_total} nos 3 pontos]_
- **O JSON de hoje: tamanho e blocos**: Cada resposta tem 40–44 KB (8–9 KB com gzip). Os blocos são evidencia ~10,5 KB, agenda 10–12 KB, cardapio ~9 KB, plano 6,4–6,8 KB e este_ano ~1,5 KB. Os 11 cartões de evidencia.regras e os 6 de plano.principios são iguais em todos os municípios, e fontes também. Esses blocos vão para um índice global, e o arquivo de cada município cai para cerca de 25 KB. _[scratchpad/analise10/prototipo-jose/estrutura.py sobre quixada.json, arapiraca.json e barreiras.json]_
- **No NE o site não precisa do POWER ao vivo**: assinatura() só chama a API do POWER quando o município não está em MUNA (motor.py:366-377). MUNA tem os 1.794 municípios com chuva_anual_mm. Como o fluxo final começa pela escolha da parte do NE, o POWER ao vivo sai do caminho. O que depende de rede está nas interfaces: tiles do OSM e Leaflet pelo cdnjs (protótipo/static/app.js:6, index.html:7,55), tiles do Esri Wayback e a malha do IBGE por município no JP (colegas/joao-pedro/site-nasa/static/js/mapa.js:69,81,427) e o Nominatim no geocode e no reverse (app.py do JP, _buscar e _reverso). _[frio.py: MUNA com chuva = 1794; nos 3 pontos, a fonte do clima é 'NASA POWER (clima do município: célula do ponto interno)']_
- **consultar() não recebe a data de hoje: o JSON estático congela 'agora'**: agenda() aceita o parâmetro hoje (motor.py:863,867), mas consultar() a chama sem ele (motor.py:1032). As barras de preparo, o marco 'Hoje' e a lista 'O que fazer agora' usam date.today(). VIS_INI e VIS_FIM também são fixos (motor.py:555). Para exportar, falta passar hoje=2026-11-15 de forma explícita. No site, a linha de hoje e o 'agora' devem ser recalculados no navegador a partir das barras. _[motor.py:555, 863-867, 1032]_
- **A trava do cache vale só dentro de um processo**: _TRAVA é um threading.Lock (motor.py:259), e _grava_cache faz os.replace do arquivo inteiro (274-280). Se o export rodar em vários processos para ficar mais rápido, o último a gravar apaga as entradas dos outros em cache_gaez_v2.json e cache_power_v2.json. O arquivo não corrompe, mas as entradas se perdem. Para exportar em paralelo, cada processo precisa do seu motor.CACHE, ou o export roda num processo só (cerca de 18 min por variante). _[motor.py:259-280]_
- **Sem mandioca apta, o giro de 3 fases põe gramínea depois de gramínea (achado novo)**: No giro sem mandioca (motor.py:683-687), as fases são forragem → leguminosa → pos_leg. A cultura de pos_leg é 'seco', ou seja, a mesma forragem (motor.py:672-676). Em Arapiraca, a Parte B fica Feijão-caupi → Sorgo forrageiro → Sorgo forrageiro, e a Parte C fica Sorgo forrageiro → Sorgo forrageiro → Feijão-caupi. Isso contradiz a própria nota do motor sobre a lagarta-do-cartucho (motor.py:713). A revisão só conferiu 'gramínea após gramínea' no CE, que tem mandioca. Na tábua GZT, a mandioca está 'fora' em 591 de 1.794 municípios (562 fora do CE). A tela de distribuição e a percolação do Vicente vão mostrar o problema. _[resumo_planos.py sobre arapiraca.json; contagens.py: mandioca {'só aptidão': 1203, 'fora': 591}]_
- **Fora do CE, as janelas do ZARC não têm os ciclos de cultivar conferidos**: O ponto da revisão 'Ciclos com cultivar fora do CE: não conferidos' (REVISAO_10_AGENTES.md:322) continua aberto. No caupi, ciclos_conferidos=False em 1.610 de 1.794 municípios. Em Arapiraca e Barreiras, as 9 culturas do ZARC levam o aviso 'grupos de ciclo sem conferência de cultivar'. No CE, esse mesmo erro (C3) atrasava o início do caupi de 21/02 para 11/03. Nos outros 8 estados, as datas de plantio da agenda podem estar até ~3 decêndios adiantadas. _[contagens.py (Feijão Caupi ciclos_conferidos {False: 1610, True: 184}); resumo_planos.py]_
- **Pontos abertos da revisão que aparecem na tela**: (a) A1 parcial: a portaria plurianual só entra no CE. Fora dele, a janela da mandioca é estimada pelo início da chuva no IMERG + 40 dias. Em Barreiras, isso aparece como 'Janela aberta agora: Mandioca, janela estimada'. (b) A2: os números canônicos da proposta não foram atualizados. A API dá leguminosa→cereal ponderado 28% (soma_w 0,46) e Bom Jesus w 0,95 em Quixadá; a 9.7 diz +36% (soma 0,62). O deck e o site vão divergir. (c) M20: em 2028, as Partes A–C de Quixadá ficam sem leguminosa (Mandioca, Sorgo forrageiro, Mandioca) e, em 2029, sem forragem. (d) M15: o rebaixamento de grau quando w < 0,3 não existe. (e) CICLO: 10 das 12 durações são 'suposição' (motor.py:540-553), então as datas de colheita e o momento da receita são suposições. (f) B15/B16: textos com '2027' fixo e caches sem versão. (g) M12/M30 se resolvem no fluxo novo se o site usar sempre o ponto interno do município. _[quixada.json evidencia.leguminosa_cereal; REVISAO_10_AGENTES.md:314-322; resumo_planos.py]_
- **Duas definições de El Niño no mesmo site**: O motor usa FORTES = ONI OND–NDJ ≥ 1,5 (motor.py:109). Na série IMERG, ficam 2010, 2016 e 2024, porque a quadra de 1998 cai fora (ONS começa em 1998) e o alerta sai com n = 3 (motor.py:241-256, 982-987). O painel do JP usa 'ONI jul–set ≥ 0,5', com anos [1998, 2003, 2005, 2010, 2016, 2024] e análogos [1998, 2010, 2016, 2024] (static/data/municipios_ne.json, chave enso). O site final precisa de uma definição só. Proposta: a do motor (≥ 1,5), com 1998 incluído onde a série é a PAM. _[E:/campeonato-nasa/dados/el_nino_2026/eventos.csv; jp_json.py]_
- **A série que temos hoje basta para uma projeção honesta por ciclo**: painel_mun_cultura_ano.parquet tem 1998–2025 por município × 8 produtos. Por ha plantado, traz rendimento e receita em R$ de 2025, preço e perda de área. Com ≥ 10 anos plantados entre 2010 e 2025, há Feijão em 1.655 municípios, Milho em 1.623 e Mandioca em 1.497, mas Sorgo só em 62 e Girassol em 0. Em Quixadá, a mediana do milho é 492 kg/ha e, nos 4 El Niños fortes, 144 kg/ha (29%). A mandioca vai de 8.895 para 5.200 kg/ha (58%), e o feijão de 297 para 164 (55%). Com 28 pontos dominados pelo regime do ano, ARIMA ou tendência não se sustentam. O caminho é o quantil empírico, com os anos análogos mostrados um a um. _[scratchpad/analise10/prototipo-jose/projecao_demo.py e contagens.py]_
- **No oeste da BA, a PAM municipal é de agronegócio e o alerta contradiz a produção**: Em Barreiras, o milho tem P50 de 7.453 kg/ha, o algodão de 3.935 e o feijão de 1.719, valores de lavoura comercial e não de roçado de sequeiro. Nos El Niños fortes, o rendimento ficou em 103% do normal. Mesmo assim, o motor dá nivel_alerta='alerta', porque olha a chuva da estação no IMERG. Usar o financeiro da PAM aqui superestima o roçado familiar e coloca o alerta e o dinheiro em contradição na mesma tela. _[projecao_demo.py (Barreiras); resumo_planos.py (alerta: alerta)]_
- **A pergunta do Vicente sobre o solo já cabe no motor**: O PercolaCampo v3 já pergunta 'Como fica a terra quando chove?' e 'o que tem em volta' (slider de mata de 15–75%, limiar χc = 0,5927 + k·p_b, regra dos 40% de habitat). A primeira resposta pode virar a textura (1–3) e a AD (11–16) que o motor já aceita em _decs (motor.py:600-605). A segunda é a entrada da percolação na tela de distribuição. _[colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_*.html:641-789 (grep)]_

## Reaproveitar
- protótipo/motor.py consultar() + app.py _limpa() → site-versao-final/ferramentas/exportar_estatico.py (com uma cópia do motor em site-versao-final/motor/): Rodar como gerador do JSON estático. O motor continua sendo a fonte única das regras, e o site final só lê o contrato.
- notebooks/secoes_financeiro/04_receita.py e 06_risco.py → exportar_estatico.py, função financeiro(cod): Copiar as fórmulas de P10/P50/P90, receita por ha plantado, % de anos com receita zero e CVaR10 por município × produto para o bloco financeiro.
- colegas/joao-pedro/site-nasa/static/data/malha_ne.json e o formato compacto de municipios_ne.json (campos + m{cod: [...]}) → site-versao-final/dados/v1/indice.json e a tela de escolha: Malha SVG leve (457 KB) para escolher a parte do NE sem tiles, e o mesmo formato tabular para indice.municipios.
- protótipo/static/app.js cartaoCalendario() e rocado() → site-versao-final/js/plano.js: Base do Gantt por parte e do roçado visto de cima. A tela de distribuição do Vicente pinta por cima, com indice.culturas[].familia.
- PercolaCampo v3: perguntas 'Como fica a terra quando chove?' e o slider de mata em volta → cartão de perguntas (indice.perguntas): A primeira vira o seletor de solo do motor (textura/AD); a segunda é a entrada da percolação.
- site-nasa-v2/vendor/ → site-versao-final/vendor/: Bibliotecas locais para o site abrir sem CDN.

## Proposta detalhada
## 1. Fluxo e de onde cada tela lê

1. Abrir → escolher a parte do NE. Lê indice.json: municipios e malha SVG do JP (malha_ne.json, 457 KB, funciona sem tiles). A busca é local, sem Nominatim.
2. "O que o seu lugar permite". Lê mun/<cod>.json: local, este_ano, cardapio (aptidão + janela + risco) e clima. Ainda sem perguntas: o lugar já basta para essa tela.
3. **Perguntas: um cartão só, entre a tela 2 e o plano**, com no máximo 5 perguntas e "não sei" em todas.
   - Por que nesse momento: depois do valor imediato do lugar e antes de tudo que depende da família (datas por solo, áreas, R$).
   - As perguntas estão na seção 3.
4. "Seu plano". Lê plano + agenda; com o solo respondido, lê mun/<cod>.solo<k>.json ou /api/local.
5. "Como plantar e distribuir" (José + Vicente). Lê plano.faixas, mais as áreas calculadas no front a partir das respostas e indice.culturas[].familia para a percolação.
6. "Retorno e segurança". Lê financeiro, serie e projecao.

## 2. Contrato quadra-mun-v1

Arquivos:
- `dados/v1/indice.json`: global, cerca de 150 KB.
- `dados/v1/mun/<cod>.json`: um por município, cerca de 25 KB (6 KB com gzip).
- `dados/v1/mun/<cod>.solo<k>.json`: k = 1, 2, 3; só `plano` e `agenda`.

Legenda da origem: [M] dado medido, [R] regra ou derivação do motor, [S] suposição, [P] projeção, [F] resposta do usuário (calculado no front).

### indice.json

```
{
 "contrato": "quadra-index-v1",
 "gerado_em": "2026-11-15T..", "hoje_ref": "2026-11-15",
 "motor_sha": "<sha1 de motor.py>"                       // liga o dado ao código (B16)
 "fontes": {POWER, GAEZ, ZARC, IMERG, SMAP, ONI,
            PAM, CONAB, IPCA}                            // motor.FONTES (motor.py:39) + NOVO: PAM/CONAB/IPCA
 "oni": {"valor": 2.46, "trimestre": "ASO/2026",
         "rotulo": "El Niño muito forte", "texto": ".."} // [M] EN['ONI_ultimo'] + _rotulo_oni (motor.py:980, 492)
 "el_nino_fortes": [1998, 2010, 2016, 2024]              // [M] eventos.csv ONI_OND_NDJ >= 1.5 (motor.py:109); definição ÚNICA do site
 "culturas": [ {"nome", "grupo", "papel",                 // CARDAPIO (motor.py:49-65)
                "tipo_rot",                               // TIPO_ROT (motor.py:67)
                "familia",                                // NOVO [R] gramínea|leguminosa|euforbiácea|cactácea|malvácea|asterácea, para a percolação
                "ciclo_dias": [min, max], "ciclo_fonte",  // CICLO (motor.py:540-553); [S] onde a fonte diz "suposição"
                "produto_pam": "Milho"|"Feijão"|..|null } ],  // NOVO: liga ao painel financeiro (Feijão-caupi e Feijão comum -> "Feijão")
 "cartoes": { "<id>": cartao(id) },                       // motor.cartao (motor.py:521) para REGRAS + princípios + 'perto'; sai do arquivo do município
 "perguntas": [ ...seção 3... ],
 "municipios": [["2311306", "Quixadá", "CE", "Sertões Cearenses", -4.9113, -39.0277], ...]
                                                          // municipios_geojson() rp (motor.py:1039-1045); o ponto interno resolve M12/M30
}
```

### mun/<cod>.json

```
{
 "contrato": "quadra-mun-v1", "cod": "2311306", "variante_solo": null,
 "local": {cod, municipio, uf, mesorregiao, lat, lon},  // [M] localizar() (motor.py:344); UF pelo código IBGE
 "clima": {chuva_anual_mm, sazonalidade_walsh, meses_umidos, aridez_P_ET0,
           tmax_estacao_umida, tmax_mes_mais_quente,
           fonte},                                       // [M] MUNA, POWER pré-calculado (motor.py:366-369); nunca chama o POWER ao vivo no NE
 "analogos": [{lugar, grupo, artigos, dist, w}] x5,      // [R] analogos() w=exp(-d²/2) (motor.py:390)
 "confianca": {w, texto},                                // [R] motor.py:1026
 "este_ano": {
   "nivel_alerta": "alerta|sinal fraco|sem alerta",      // [R] n=3 anos IMERG (motor.py:982-987)
   "perspectiva": "texto",
   "el_nino_mun": {anos:[2010, 2016, 2024],
                   pct:[58, 55, 103], inferior: 2},      // NOVO: expor PERSP_MUN (motor.py:241-256) como número, para o gráfico
   "chuva_recente", "smap": {status, fim, valor, posto, anos, classe, texto},  // [M] preliminar / SMAP até 10/11/2026
   "regime": {mes_inicio, estacao, chuva_mm, fracao, quadra, texto},          // [M] IMERG
   "inicio": {mediana, p10, p90, dif_el_nino_dias, anos_el_nino_forte, n_anos}, // [M] ONS ≤ 2025
   "zarc_primeiro": {ate40, risco20}                    // [R] ZPRIM
 },
 "cardapio": [{cultura, grupo, papel, aptidao, aptidao_alta, classe,
               risco20, risco30, risco40, solo_ciclo, situacao, base,
               por_solo: [{cod_solo, solo, risco20, risco30, risco40}],
               "ciclos_conferidos": bool}],              // [M] ZARC/GAEZ; NOVO campo explícito (hoje só no texto de 'base') -> selo na tela
 "plano": {anos: [2027, 2028, 2029],
           faixas: [{parte, por_que, anos: [{cultura, tipo, texto}] x3}],
           interruptor, notas, leguminosa,
           principios: ["<id cartão>"..],               // ids; o texto vem de indice.cartoes
           "giro": "4 fases|3 fases",                    // NOVO [R]; com 3 fases a tela avisa gramínea após gramínea
           "fracao_area": {"Parte A": .., "Parte B": .., "Parte C": .., "Baixio": .., "Bordas": ..}},
                                                         // NOVO [S] padrão (bordas 0,10; baixio 0,15; o resto em 3 partes); o front reescala com [F]
 "agenda": {inicio, fim, hoje_ref,
            linhas: [{parte, cultura, tipo, estacao,
                      barras: [{de, ate, tipo: preparo|risco|plantio|estimado|roca|colheita|pousio,
                               pista, rotulo, segue}],
                      plantar, colher, fonte,
                      "janela_nivel": 20|30|40|null,     // NOVO: expor j['nivel'] (motor.py:624); alimenta "8 em 10"
                      "janela_zarc": bool}],             // NOVO: expor j['zarc']; false = estimada [S]
            marcos: [{data, dia, rotulo, texto}], nota_portoes, portoes,
            agora_ref: [..],                             // texto de 15/11; o front recalcula pela data do navegador
            culturas: [..], solo},
 "evidencia": {"perto": [{id, w}], "leguminosa_cereal": {ponderado_pct, soma_w, central_motor}},
 "serie": {                                              // NOVO [M] "dados que temos hoje"
   "anos": [1998..2025],
   "rend_kg_ha": {"Milho": [0, 600, ..], "Feijão": [..], "Mandioca": [..]},  // painel_mun_cultura_ano.rend_plantado_kg_ha (perda total = 0)
   "chuva_estacao_mm": [..],                             // onset_ne_mun.csv chuva_estacao_mm (IMERG; 2026 fica fora, preliminar)
   "fonte": "IBGE PAM 1998–2025; IMERG V07"
 },
 "financeiro": {                                         // NOVO; só produtos com ≥ 10 anos plantados
   "<produto_pam>": {n_anos,
     rend_kg_ha: {p10, p50, p90},                        // [M]
     receita_r2025_ha: {p10, p50, p90},                  // [M] receita_plantado_r2025_ha (IPCA)
     anos_receita_zero_pct, cvar10_r2025_ha,             // [M] 06_risco.py
     preco_r2025_kg_p50,                                 // [M]
     desembolso_conab_r2025_ha: {valor, uf_ref, safra, familiar: true},  // [M] conab_custos_ne.csv (familiar, sequeiro; a UF mais próxima, se faltar)
     margem_r2025_ha: {p10, p50, p90},                   // [P] receita − desembolso
     "aviso_agronegocio": bool}                          // [R] P50 > 2× produtividade CONAB familiar -> o front não mostra o R$
 },
 "projecao": [                                           // NOVO [P]: uma por linha da agenda com colheita
   {parte, cultura, estacao, colheita_de, colheita_ate, produto_pam,
    "chance_janela": {"nivel": 20, "frase": "o ZARC aceita perda por falta de água em até 2 de 10 anos"},  // [R] janela_nivel
    "rend_kg_ha": {p10, p50, p90},                       // [P] quantis empíricos 1998–2025, sem tendência
    "anos_parecidos": [{ano: 1998, rend: 0}, {ano: 2010, rend: 392}, {ano: 2016, rend: 60}, {ano: 2024, rend: 228}],
                                                         // [M] só na estação 2027 (El Niño hoje); n=4: pontos, não faixa
    "anos_ruins_pct": 11,                                // [M] % de anos < 30% da mediana
    "receita_r2025_ha": {p10, p50, p90},                 // [P]; [F] × área da parte = R$ da família
    "metodo": "quantis do próprio município; 2027 com os anos de El Niño forte mostrados; 2028+ sem condição (o ENSO não se prevê com > 9 meses)",
    "tipo": "projeção"}
 ]
}
```

## 3. Perguntas (indice.perguntas): o que cada uma muda

| id | texto | opções | muda | onde |
|---|---|---|---|---|
| solo | Como fica a terra quando chove? (frase do Vicente) | encharca / segura um pouco / seca logo / não sei | textura 3/2/1 + AD 16/14/12 [S] | motor (variante) |
| area | Tamanho do roçado | tarefas ou ha (1 tarefa CE ≈ 0,3 ha [S]) | ha por parte e R$ | front |
| baixio | Tem uma parte mais baixa que guarda água? | sim / não / não sei | mostra ou esconde a linha do baixio; sem baixio, milho fora do plano | front |
| agua | Que água você tem? | cisterna / barreiro / poço / açude / nenhuma | v1 só dá aviso (o plano é de sequeiro; ZARC irrigado não modelado) e a forragem guardada | front |
| animais | Cria animais? | não / poucos / muitos | peso da forragem e das bordas; forragem sem R$ medido | front |
| mandioca_chao | Já tem mandioca plantada? | sim / não | nota do tampão (motor.py:716-718) | front |
| em_volta | Quanto de mata/caatinga tem em volta? | 15–75% (slider do Vicente) | percolação | front |

## 4. Rede e degradação

- POWER ao vivo: nunca no NE. Fora do NE, a tela diz "fora do recorte".
- Tiles (OSM, Wayback): opcionais. Sem rede, o mapa usa a malha SVG local (JP) ou o geojson.
- Bibliotecas JS: copiar para a pasta vendor/, como em site-nasa-v2/vendor/, em vez de carregar pelo cdnjs.
- Nominatim: trocar pela busca local em indice.municipios.
- IBGE malha por município: usar a malha local.
- /api/local: só para as variantes de solo que não foram exportadas. Sem servidor, a tela mostra "melhor caso entre os solos".

## 5. Como medir o sucesso

- O export gera 1.794 arquivos sem erro.
- Quixadá/Arapiraca/Barreiras estáticos = /api/local, campo a campo, fora `agora` e `hoje`.
- O site abre servido por `python -m http.server`, sem o motor rodando.
- O financeiro de Barreiras sai com aviso_agronegocio = true.

## Riscos
- Congelar a data no JSON estático: quem abrir depois de 15/11 veria 'Janela aberta agora' errado se o front não recalcular pela data do navegador.
- O export em vários processos perde entradas do cache, porque a trava é por thread (motor.py:259). Rodar num processo só ou com um CACHE por processo.
- O tamanho total cresce rápido: 1.794 × ~25 KB = ~45 MB só no padrão, e as 3 variantes de solo somam ~+80 MB. Pesa no git e no deploy. Começar pelo padrão + os municípios da demo.
- Fora do CE, as datas do ZARC podem incluir ciclos sem cultivar (1.610 municípios no caupi). Datas adiantadas na tela de calendário são o erro mais visível para um agrônomo do júri.
- A PAM municipal mistura agronegócio e roçado familiar (Barreiras: milho P50 7.453 kg/ha). Sem o aviso, o retorno financeiro promete uma receita que a família não terá.
- O caupi e o feijão comum caem no mesmo produto 'Feijão' da PAM. A projeção do caupi herda a série do feijão em geral (suposição a declarar).
- A projeção com El Niño tem n = 4 anos (n = 3 no IMERG). Mostrar como faixa daria falsa precisão; mostrar como pontos, ano a ano.
- O mapeamento textura → AD (arenoso = AD2, médio = AD4, argiloso = AD6) é suposição. Ele pode deslocar a janela do milho e do girassol, que usam a AD.
- A tabela CICLO tem 10 de 12 durações supostas. As datas de colheita e o mês da receita na tela de retorno herdam essa suposição.
- Os números da proposta v3 (A2) e os da API divergem. O deck e o site vão mostrar números diferentes se ninguém alinhar.

## Perguntas abertas
- O site final vai rodar sem servidor (GitHub Pages ou um arquivo para o júri) ou com o Python do motor ao lado? Isso define se as variantes de solo saem exportadas para todos os municípios.
- A área entra em tarefas ou em hectares? Que tamanho de tarefa usar fora do CE?
- A forragem (sorgo forrageiro, palma, milheto) entra no retorno financeiro? Não há preço na PAM. Uma opção é 'ração que deixa de comprar' (suposição), outra é deixar sem R$.
- Quem decide a definição única de El Niño? O motor usa ONI ≥ 1,5 (quadras 1998, 2010, 2016, 2024); o painel do JP usa ONI JAS ≥ 0,5.
- Nos municípios de agronegócio (oeste da BA), o financeiro some da tela ou usa a produtividade CONAB familiar no lugar da PAM?
- Antes do deck, a 9.7 da proposta vai ser atualizada com os números de hoje da API (ponderado 28%, Bom Jesus 0,95)?