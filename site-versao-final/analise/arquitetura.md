# Arquitetura do sistema único (arquitetura)

## Resumo
Recomendo uma pilha só: um site 100% estático (HTML, CSS e JS em módulos, sem etapa de build) que lê JSON pré-calculado por município. Esses JSON saem de scripts Python que importam o motor do protótipo do José sem copiá-lo, e um servidor Python só com a biblioteca padrão apenas serve os arquivos. O motivo é medido: o motor depende de uns 6 GB locais em E: (GAEZ 2,3 GB, SMAP 2,0 GB, complementares 1,4 GB) e leva 1 a 2 min para subir, então não dá para hospedar um backend até amanhã. Já a resposta de /api/local tem 40 KB por município (9 KB com gzip), sai em 0,5 a 0,9 s e não chama o POWER ao vivo em nenhum dos 1.794 municípios: as 1.794 assinaturas já estão em disco, e a geração toda leva uns 20 min. A interface parte do site-nasa-v2, que já é estático e traz bibliotecas e fontes locais. Do João Pedro entram o painel Roça Certa, o painel lateral e os easter eggs, com os caminhos absolutos /static trocados por relativos. A jornada do município fica numa página própria e leve (plano.html?cod=), que funciona até sem WebGL. O PercolaCampo do Vicente entra isolado num iframe, recebendo do plano a cultura, o solo, as faixas A/B/C e as bordas como barreira. Isolar é necessário porque o Tailwind por CDN dele reseta o CSS de qualquer página onde entre. Para não perder autoria antes do prazo: cópia com cabeçalho de origem (branch@sha e autor) mais um CREDITOS.md; o merge de verdade fica opcional, já que a branch do Vicente entra sem conflito e a do JP tem 7 arquivos em conflito. Para o júri, o GitHub Pages gratuito exige repositório público, e o atual é privado; a sugestão é um repositório público só com web/, mas a decisão é do José. O mínimo indispensável (P0) soma umas 14 h, o que cabe até 15/11 se o escopo for congelado às 20h. As variantes de solo, o modo ao vivo e os ladrilhos offline ficam para depois.

## Recomendações
- **P0** (1 h) Criar site-versao-final/ com web/ copiado do site-nasa-v2, mais um servidor.py só com a biblioteca padrão (serve web/, porta 8090, tipos MIME fixos para .js, .mjs, .json, .geojson, .webp e .woff2) e um CREDITOS.md (arquivo → autor → branch@sha → o que foi adaptado) — É uma pilha só, roda com um comando, não colide com a 8765 (protótipo) nem com a 8080 (v2), e evita o problema de MIME do http.server.
- **P0** (1.5 h) ferramentas/gerar_municipios.py: importar ../protótipo/motor.py; para cada município da malha (lat e lon do ponto interno, motor.municipios_geojson) chamar consultar() com hoje fixo em 15/11/2026 via functools.partial; gravar web/dados/m/<cod>.json com json.dumps(allow_nan=False); mandar 'fontes' e 'evidencia.regras' para web/dados/comum.json; gerar busca.json (nome, UF, lat, lon); rodar num processo só — Sem isso o site estático não tem conteúdo. São ~20 min de máquina, sem POWER ao vivo, e um processo só evita a corrida no cache.
- **P0** (2 h) Portar o painel Roça Certa do JP para estático (painel.html?cod=&embutido=1, caminhos relativos, fontes locais) e ligar na chegada ao município no mapa da v2, com um botão 'Montar o plano do meu roçado' que leva a plano.html?cod= — Mantém visível a contribuição do JP e liga o globo e o mapa à jornada sem misturar páginas pesadas e leves.
- **P0** (3 h) plano.html + js/dados.js (carrega m/<cod>.json, s/<cod>.json e comum.json com ?v=gerado_em) + js/estado.js (respostas na URL, localStorage com try/catch) + js/jornada.js (etapas por âncora #); mover para js/etapas/ as funções de desenho do protótipo/static/app.js (cardápio, calendário, roçado, plano, evidência, fontes), trocando /api/local pelo JSON — É o núcleo do fluxo do José. Reaproveitar as funções revisadas por 10 agentes evita reescrever a lógica e manter duas versões.
- **P0** (1 h) Etapa de perguntas logo depois de escolher o município e antes das opções: solo (não sei, arenoso, médio, argiloso), acesso a água, tamanho do roçado, mandioca já no chão, criação, mata em volta. Todas com 'não sei' e guardadas na URL — O solo troca o arquivo pré-calculado (agenda e plano), então precisa vir antes; as outras só filtram ou multiplicam no navegador. A URL torna cada cenário um link compartilhável para o júri e para o vídeo.
- **P0** (1.5 h) PercolaCampo em iframe (web/modulos/percolacampo/index.html): ler os parâmetros da URL (cultura, solo, padrão de plantio, barreira, mata, modo=embutido) para o appState, vendorizar o Tailwind play, mapear cardápio→FARM_CROPS (milho→milho, caupi e feijão comum→feijao, mandioca→mandioca; o resto: 'sem parâmetro') e rotular como ilustrativo — O iframe isola o reset do Tailwind, preserva o arquivo e a autoria do Vicente e liga as Partes A/B/C e as bordas do plano à simulação de foco de praga.
- **P0** (3 h) ferramentas/gerar_series.py: web/dados/s/<cod>.json com chuva IMERG mensal, percentil do SMAP, PAM 1998–2025 (rendimento, R$ 2025/ha, perda de área) e projeção por ciclo (2027, 2028, 2029: P10, P50, P90 e chance de prejuízo), cada bloco com 'tipo' (medido, projeção ou suposição) e 'fonte'; etapa Retorno e Segurança em SVG (medido em linha cheia, projeção em faixa) — Atende à 'perspectiva dos dados atuais e projeção por ciclo'. Calcular no Python deixa o método auditável e o navegador só desenha. O método fica com o agente de projeção.
- **P0** (1 h) Publicar para o júri: repositório público novo só com site-versao-final/web (git subtree split --prefix=site-versao-final/web), arquivo .nojekyll, Pages saindo de main/(root); conferir o link em aba anônima — O repositório atual é privado (404), e Pages privado é pago. Publicar é voz pública e repositório pago é dinheiro: as duas decisões são do José.
- **P1** (0.5 h) Variantes de solo m/<cod>_t1|t2|t3.json só com {agenda, plano}, geradas em 3–4 processos depois da primeira passada; dados.js cai no arquivo padrão com aviso quando faltar — Mantém o seletor de solo do protótipo sem backend. Custa ~65–100 MB e ~1 h de máquina.
- **P1** (1.5 h) Modo sem internet: malha_ne.geojson simplificada local no lugar da API de malhas do IBGE (mapa.js:576), busca.json antes do Nominatim, e um estilo do MapLibre sem ladrilhos (fundo + municípios coloridos) quando os ladrilhos falharem — A demo ao vivo não pode depender de 5 serviços externos. O globo, o painel, o plano e o PercolaCampo já ficam locais.
- **P1** (1 h) ferramentas/conferir_dados.py (1.794 arquivos em m/ e s/, cod igual ao nome do arquivo, sem NaN, data de geração, tamanho total) + teste de fumaça headless em Quixadá, Barreiras e Arapiraca com o ferramentas/captura.mjs da v2 — Validar o artefato antes de mostrar: um arquivo faltando quebra justamente o município que o júri clicar.
- **P1** (0.3 h) Link 'ver sem 3D' no index.html, levando a plano.html com busca local — O laptop do júri pode ter WebGL fraco; o conteúdo não pode depender do globo.
- **P2** (1 h) Modo ao vivo opcional: servidor.py --ao-vivo importa o motor e responde /api/local para qualquer ponto e solo; dados.js tenta a API e cai no JSON — Devolve a precisão por ponto (pixel do GAEZ, SMAP) na demo local, mas não é necessário para a entrega.
- **P2** (1 h) Merge real das branches numa branch de integração: estudo-vicente sem conflito; estudo-jp resolvendo 7 arquivos (site-nasa/ do lado do JP, .gitignore como união) — Preserva o git blame dos colegas. Não é necessário para a entrega e mexe no site-nasa/ do José.
- **P2** (4 h) Pacote de ladrilhos Sentinel-2 cloudless do NE em z4–z9 (~800 ladrilhos, ~20 MB) e vento do POWER e declive do SRTM nos terrenos do PercolaCampo, sem o Tailwind — Melhora o modo offline e tira o caráter de exemplo do PercolaCampo, mas não cabe com segurança até 23:59.

## Achados
- **O motor não é hospedável até amanhã: depende de ~6 GB locais**: motor.py lê dezenas de CSV, GeoJSON e ZIP de E:/campeonato-nasa/dados no import (linhas 95–164) e amostra os rasters do GAEZ e o NetCDF do SMAP na hora. Subir isso num serviço externo significaria enviar GBs e esperar 1 a 2 min por partida a frio. Para o júri, o caminho viável é pré-calcular. _[du -sh E:/campeonato-nasa/dados/{gaez,smap,complementares} → 2.3G, 2.0G, 1.4G; protótipo/motor.py:95-164, 287-319]_
- **A resposta por município é pequena e rápida: dá para pré-calcular os 1.794**: Quixadá 0,69 s e 42.953 B; Barreiras 0,48 s; Arapiraca 0,52 s; Juazeiro do Norte 0,89 s. Em JSON compacto, Quixadá tem 40.470 B (8.994 B com gzip). Os 1.794 municípios em um processo levam ~20 min, ~63 MB brutos (~14 MB trafegados no total, ~9 KB por clique). _[curl -w '%{time_total} %{size_download}' http://127.0.0.1:8765/api/local?lat=-4.9113&lon=-39.0277; scratchpad/analise10/arquitetura/checa.py]_
- **A geração em lote não chama o NASA POWER (sem risco de 429)**: Quando o ponto cai num município do NE, assinatura() usa a tabela MUNA já pré-calculada. A MUNA tem as 1.794 linhas, nenhuma sem chuva, e nenhum município da malha fica sem assinatura. A API ao vivo só seria chamada fora do Nordeste. _[protótipo/motor.py:366-375; checa.py → 'MUNA linhas 1794 sem chuva 0', 'malha sem MUNA 0']_
- **Partes constantes da resposta podem ir para um comum.json**: 'fontes' (459 B) e 'evidencia.regras' (5.384 B) são idênticos entre Quixadá, Barreiras, Arapiraca e Juazeiro do Norte. Tirar os dois de cada arquivo economiza ~10 MB. _[checa.py: 'fontes constante=True', 'evidencia regras True 5384']_
- **O solo muda só a agenda (e às vezes o plano)**: Com textura=1&ad=11 mudam 'plano' e 'agenda'; com textura=2&ad=13 ou 3&ad=16, só 'agenda'. Dez culturas usam a textura 1–3 do ZARC; milho e feijão comum usam a classe de água disponível (AD) 11–16. Combinar tudo daria 28 variações, o que não cabe. Viável: 3 variantes (arenoso, médio, argiloso, com a AD derivada da textura, o que é suposição), guardando só agenda e plano. _[scratchpad/analise10/arquitetura/checa_solo.py; protótipo/motor.py:588-607 (a escolha entre AD e textura)]_
- **O 'hoje' do motor é date.today(): o pré-cálculo congela a data**: agenda() aceita o parâmetro hoje, mas consultar() não o repassa. No script de geração dá para fixar a data com motor.agenda = functools.partial(motor.agenda, hoje=date(2026,11,15)), porque consultar() busca o nome global na hora da chamada. A tela deve dizer 'situação em 15/11/2026'. _[protótipo/motor.py:863-867 ('hoje = hoje or date.today()') e a chamada em consultar() perto da linha 1030]_
- **A trava do cache do motor vale só dentro de um processo**: _grava_cache usa threading.Lock e um .tmp de nome fixo, e reescreve o JSON inteiro a cada chave nova. Vários processos ao mesmo tempo na primeira passada podem perder entradas ou falhar no os.replace (Windows). Portanto: primeira passada (solo 'não sei') num processo só, o que enche o cache_gaez_v2. Depois disso, as variantes de solo podem rodar em paralelo, porque não gravam chaves novas. A máquina tem 24 núcleos e 15 GB livres, e o motor ocupa 287 MB. _[protótipo/motor.py:259-280; tasklist PID 35724 = 286.784 K; wmic FreePhysicalMemory 15.685.348 KB]_
- **O site-nasa do JP é o v1 do José com acréscimos; o merge tem só 7 conflitos**: As duas branches saem de 48a3608. Em site-nasa/, o JP soma +3.721 e −19 linhas sobre o José; o espaco.js dele difere em apenas 38 linhas do commit a3b8019 do José. Arquivos mudados dos dois lados com conteúdo diferente: .gitignore, site-nasa/README.md, app.py, static/css/style.css, static/js/espaco.js, static/js/principal.js e templates/index.html. A branch estudo-vicente não tem nenhum arquivo em comum com estudo-jose. _[git diff --stat estudo-jose origin/estudo-jp -- site-nasa (35 arquivos, +3721 −19); comparação de rev-parse dos 26 caminhos comuns; comm entre os diffs da base para vicente: vazio]_
- **O código do JP supõe Flask e a raiz do domínio**: painel.js e rocacerta.js fazem fetch('/static/data/municipios_ne.json') e abrem o iframe '/painel/${cod}?embutido=1'. O painel.html usa url_for e {{ cod }}. MapLibre vem do jsDelivr e as fontes do Google Fonts. Do jeito que está, quebra no GitHub Pages de projeto (servido em /<repo>/) e sem internet. _[colegas/joao-pedro/site-nasa/static/js/painel.js:8,26; static/js/rocacerta.js:14-15; templates/painel.html:12-17; templates/index.html (cdn.jsdelivr maplibre 5.24.0)]_
- **site-nasa-v2 já está pronto para estático e para o júri**: Bibliotecas locais (three 0.160.0, MapLibre 5.24.0), fontes woff2 locais, texturas WebP de 1K a 8K, qualidade adaptativa e todos os caminhos relativos; o README mede 0,7–0,8 MB até a abertura. Ainda depende de rede para: ladrilhos EOX S2, Esri Wayback, AWS Terrain e OpenFreeMap, a malha do IBGE na hora e o Nominatim. Autor não confirmado: a pasta foi criada entre 12:14 e 12:59 na pasta do José e está fora do git. _[site-nasa-v2/README.md; site-nasa-v2/js/mapa.js:10-16 e 576 (fetch da API de malhas do IBGE); js/busca.js:7; ls -la --time-style]_
- **O protótipo depende de CDN, de OSM e de rotas absolutas**: Leaflet 1.9.4 vem do cdnjs, os ladrilhos do tile.openstreetmap.org, e o app.js chama '/api/local' e '/api/municipios', que tem 2,8 MB. Na versão final, o mapa vem da v2 (MapLibre) e o app.js vira só funções que desenham, lendo o JSON. _[protótipo/static/index.html (links do cdnjs); protótipo/static/app.js:6,11; curl /api/municipios → 2.807.372 bytes]_
- **PercolaCampo v3: um arquivo só, com Tailwind por CDN e um motor de coeficientes fixos**: São 1.836 linhas com <script src='https://cdn.tailwindcss.com'> (o reset global do Tailwind quebra o CSS de quem o embutir) e Google Fonts. Terrenos e culturas são fixos: FARM_TERRAINS com dois sítios de exemplo e FARM_CROPS só com milho, feijão, hortaliças e mandioca. O computeCalibratedMetrics (linha 915) usa constantes como xc = 0,5927 + 0,56·pb, T_eff·2,35 e protegida = 108 − 34·R_eff, que são forma ilustrativa, não medição. _[colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html:840-990, 1539-1557]_
- **O repositório é privado: GitHub Pages grátis não serve**: Sem login, github.com/Netinhoklz/competicao-nasa e netinhoklz.github.io/competicao-nasa dão 404, e o gh não está autenticado. Pages num repositório privado exige plano pago. Saída sem custo: um repositório público só com o web/ (voz pública, decisão do José). _[curl -s -o /dev/null -w '%{http_code}' https://github.com/Netinhoklz/competicao-nasa → 404; gh repo view → 'gh auth login']_
- **Tipo MIME: servidor Python puro pode não carregar módulos JS em outra máquina**: Nesta máquina, mimetypes dá application/javascript para .js, mas text/plain para .mjs e nada para .woff2 e .geojson. Em Windows com o registro alterado, .js vira text/plain e o navegador recusa módulo ES. O servidor.py precisa fixar extensions_map. _[python -c 'mimetypes.guess_type(...)' → ('application/javascript') ('text/plain') ... (None) (None)]_
- **Ninguém usa biblioteca de gráfico: tudo é SVG feito à mão**: O protótipo desenha cartões e Gantt em HTML/SVG, e o rocacerta.js do JP tem barras, réguas e escala do ONI em SVG. O leque de projeção e as barras de retorno seguem o mesmo padrão, sem dependência nova. _[protótipo/static/app.js:208-305; colegas/joao-pedro/site-nasa/static/js/rocacerta.js:77-132]_
- **Narrativas diferentes sobre o El Niño entre JP e José**: O painel do JP mostra o sinal por ESTADO, porque no teste dele os anos análogos por município deram AUC ≈ 0,5 em novembro. O motor do José mostra a perspectiva por MUNICÍPIO, com os El Niños fortes da série IMERG. Na mesma jornada isso confunde: é preciso escolher uma narrativa ou dizer a escala de cada uma. _[colegas/joao-pedro/site-nasa/README.md (seção Painel Roça Certa); protótipo/motor.py consultar() → este_ano.perspectiva]_
- **Disco e direitos autorais**: C: está a 96% (11 GB livres) e E: tem 33 GB livres; os ~90–190 MB de JSON cabem. O .gitignore só barra artigos/**/*.pdf na raiz, então os PDFs de editoras do Vicente (PhysRevE, PHYTO, 8 MB) estão versionados em pesquisa_vicente/artigos e não devem ir para o web/ público. _[df -h /c /e; .gitignore linha 'artigos/**/*.pdf'; git diff --stat 48a3608 origin/estudo-vicente]_
- **Outras peças dos colegas ficam de fora do site**: Ficam fora: src/ingestion/stac_and_soil.py do JP (piloto de condado dos EUA com SSURGO e CDL), interface-nordeste-jp (já coberta pelo painel Roça Certa) e interface-inicial-vicente (só o CE, 184 municípios, 1,8 MB com dados embutidos). Dela vale reaproveitar a linguagem dos cartões e a página 'Como eu funciono'. _[colegas/joao-pedro/src/ingestion/stac_and_soil.py:1-25; colegas/vicente/interface-inicial-vicente/README.md]_

## Reaproveitar
- c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/site-nasa-v2/ (index.html, js/espaco.js, mapa.js, qualidade.js, nordeste.js, busca.js, principal.js, vendor/, fontes/, texturas/, dados/nordeste.json) → site-versao-final/web/ (raiz): Cópia integral como casca da versão final: já é estático, tem caminhos relativos, bibliotecas e fontes locais e qualidade adaptativa. Só mudam o gancho na chegada ao município (abrir o painel e o botão do plano) e a malha local no lugar da API do IBGE.
- colegas/joao-pedro/site-nasa/templates/painel.html + static/js/rocacerta.js + static/css/rocacerta.css + static/data/municipios_ne.json + malha_ne.json → site-versao-final/web/painel.html, web/js/rocacerta.js, web/css/rocacerta.css, web/dados/: Painel Roça Certa como página estática painel.html?cod=: tirar url_for e {{ cod }}, trocar '/static/...' por caminhos relativos, Google Fonts pelas fontes locais da v2. Cabeçalho de origem estudo-jp@29f81f6.
- colegas/joao-pedro/site-nasa/static/js/painel.js + static/css/painel.css + static/js/ovos.js → site-versao-final/web/js/painel.js, ovos.js, css/painel.css: Painel lateral em iframe e easter eggs, ligados ao principal.js da v2 (o JP acrescentou +62 linhas ao principal.js do v1; portar só os ganchos). Caminhos relativos.
- c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/protótipo/static/app.js (cartaoCardapio, cartaoCalendario, rocado, cartaoPlano, cartaoEvidencia, cartaoFontes, linhas 97–330) + estilo.css → site-versao-final/web/js/etapas/ e web/css/jornada.css: Mover as funções de desenho para js/etapas/*.js, trocando fetch(urlLocal) por dados.municipio(cod, solo). O mapa Leaflet do protótipo sai, porque o mapa é o da v2.
- c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/protótipo/motor.py (consultar, municipios_geojson) e app.py (_limpa) → site-versao-final/ferramentas/gerar_municipios.py: Importar sem copiar (fonte única revisada por 10 agentes) nos scripts de geração; copiar só a _limpa (NaN vira null). Data fixa via functools.partial na agenda.
- colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html → site-versao-final/web/modulos/percolacampo/index.html: Copiar quase intacto como módulo em iframe: ~20 linhas para ler parâmetros da URL para o appState, modo embutido, Tailwind vendorizado, rótulo de ilustrativo e cabeçalho estudo-vicente@18fd0e3.
- E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet (386.543 linhas: município × produto × ano 1998–2025, rendimento, preço e receita em R$ 2025, perda de área) + conab_custos_ne.csv + notebooks/secoes_financeiro/*.py → site-versao-final/ferramentas/gerar_series.py → web/dados/s/<cod>.json: Fonte do histórico medido e da base da projeção por ciclo no s/<cod>.json, calculado em Python (gerar_series.py), sem conta nenhuma no navegador.
- dados_resumo/derivados/ibge_ne_mun_imerg_mensal.parquet (618.930 linhas) e ibge_ne_mun_smap_mensal.parquet (252.954) → web/dados/s/<cod>.json (blocos chuva e solo): Séries mensais medidas de chuva e de solo por município, para a 'perspectiva dos dados que temos hoje' no s/<cod>.json.
- site-nasa-v2/ferramentas/captura.mjs → site-versao-final/ferramentas/captura.mjs: Teste de fumaça headless e fotos para o vídeo em Quixadá, Barreiras e Arapiraca.
- colegas/vicente/interface-inicial-vicente/fonte/pagina.html (página 'Como eu funciono', cartões simples para o agricultor) → web/js/etapas/fontes.js (P2): Reaproveitar o texto e o padrão visual na etapa #fontes e nos cartões; não integrar a página, que cobre só o CE e tem dados embutidos.

## Proposta detalhada
## 1. Decisão de pilha
Front estático (HTML, CSS e JS em módulos ES, sem build, sem framework, sem biblioteca de gráfico) + dados JSON pré-calculados por município + scripts Python que importam o motor do protótipo (fonte única: c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/protótipo/motor.py) + servidor.py só com a biblioteca padrão para rodar localmente. O Node não entra: o servidor.js e o captura.mjs da v2 podem vir como ferramentas opcionais.
Por que não Python ao vivo: são ~6 GB em E:, 1–2 min para subir, e não dá para hospedar até amanhã. Por que não Node + Python: duas linguagens no caminho crítico para nada.

## 2. Árvore de pastas
```
site-versao-final/
├── README.md                 como rodar, gerar dados, publicar; de onde vem cada parte
├── CREDITOS.md               arquivo → autor → branch@sha → adaptação (ex.: rocacerta.js ← estudo-jp@29f81f6, JP)
├── servidor.py               stdlib; serve web/ em http://127.0.0.1:8090; MIME fixo (.js .mjs .json .geojson .webp .woff2)
├── ferramentas/              (só roda na máquina do José: lê E:/ e ../protótipo, ../scripts)
│   ├── gerar_municipios.py   motor.consultar no ponto interno → web/dados/m/<cod>.json (+ comum.json, busca.json)
│   ├── gerar_solos.py        (P1) m/<cod>_t1|t2|t3.json só {agenda, plano}; paralelo DEPOIS da 1ª passada
│   ├── gerar_series.py       IMERG/SMAP mensal + PAM/CONAB/IPCA + projeção por ciclo → web/dados/s/<cod>.json
│   ├── gerar_malha.py        (P1) malha IBGE simplificada → web/dados/malha_ne.geojson
│   ├── conferir_dados.py     (P1) 1.794 m/ e s/, cod = nome, sem NaN, datas, tamanhos
│   └── captura.mjs           (da v2) fotos e fumaça headless
└── web/                      ← é isto que vai para o Pages; tudo com caminho relativo
    ├── .nojekyll
    ├── index.html            globo 3D → Nordeste → mapa (base: site-nasa-v2)  + link "ver sem 3D"
    ├── painel.html           Roça Certa do JP (?cod=&embutido=1)
    ├── plano.html            jornada: ?cod=2311306&solo=0..3&agua=chuva|cisterna|poco|acude|irriga&area=2&mandioca=0|1&criacao=0|1&mata=45#etapa
    ├── css/  estilo.css fontes.css (v2) · painel.css rocacerta.css (JP) · jornada.css (novo)
    ├── js/
    │   ├── principal.js espaco.js mapa.js qualidade.js nordeste.js busca.js   (v2; mapa.js passa a ler malha local)
    │   ├── painel.js ovos.js rocacerta.js                                      (JP; caminhos relativos)
    │   ├── dados.js     fetch de m/, s/, comum.json com ?v=gerado_em; variante de solo com recuo para a padrão
    │   ├── estado.js    respostas ⇄ URL ⇄ localStorage (try/catch)
    │   ├── jornada.js   etapas #perguntas #opcoes #calendario #rocado #retorno #fontes
    │   ├── selo.js      selo único [MEDIDO] [MODELO] [SUPOSIÇÃO] [PROJEÇÃO] a partir do campo "tipo"
    │   ├── graficos.js  SVG à mão: Gantt, leque P10–P50–P90, barras
    │   └── etapas/ perguntas.js opcoes.js calendario.js rocado.js retorno.js fontes.js
    │        (opcoes, calendario, rocado e fontes = funções do protótipo/static/app.js:97-330 lendo JSON)
    ├── modulos/percolacampo/index.html + tailwind (vendorizado)   ← Vicente v3, num iframe
    ├── vendor/ three.module.min.js maplibre-gl.js/.css (+ licenças)        (v2)
    ├── fontes/  texturas/                                                   (v2, 0,3 MB + 6,8 MB)
    └── dados/
        ├── nordeste.json                  contorno (v2 = JP)
        ├── municipios_ne.json malha_ne.json   (JP, painel)   0,44 + 0,46 MB
        ├── malha_ne.geojson               (P1) 1.794 polígonos simplificados (~1 MB) no lugar da API do IBGE
        ├── busca.json                     1.794 nomes + UF + lat/lon do ponto interno (busca offline)
        ├── comum.json                     fontes, regras, catálogo de cartões, gerado_em, sha do motor
        ├── m/<cod>.json                   saída do motor (solo "não sei"), ~35 KB cada, ~63 MB no total
        ├── m/<cod>_t1|t2|t3.json          (P1) agenda e plano por solo, ~65–100 MB
        └── s/<cod>.json                   séries e projeções, ~8–10 KB cada, ~15–18 MB
```
Total publicado: ~90 MB no P0 e ~190 MB com o P1, em 3.588 a 8.970 arquivos (o limite do Pages é 1 GB). Por clique trafegam ~9 KB (m) + ~3 KB (s) com gzip.

## 3. Fluxo de dados
```
E:/campeonato-nasa/dados/* ─┐                         ┌─ web/dados/m/<cod>.json ─┐
dados_resumo/derivados/*  ──┼─► ferramentas/gerar_*.py ┼─ web/dados/s/<cod>.json ─┼─► navegador (fetch relativo) ─► telas
protótipo/motor.py ─────────┘   (importa o motor;     ├─ comum.json, busca.json ─┘        ▲
scripts/*.py (GZ, AC, comum)     hoje fixo 15/11/2026; └─ malha_ne.geojson                 │ respostas na URL (estado.js)
                                 1 processo na 1ª passada)                                  │ filtros e escalas no cliente
```
- gerar_municipios.py: `motor.agenda = functools.partial(motor.agenda, hoje=date(2026,11,15))`. Para cada linha de `json.loads(motor.municipios_geojson())`: `r = motor.consultar(lat, lon)`, depois `app._limpa(r)` (copiar a função) e `json.dumps(..., allow_nan=False, separators=(",",":"))`. Tira `fontes` e `evidencia.regras` e acrescenta `meta = {gerado_em, hoje, ponto:{lat,lon}, solo:null, motor_sha: git rev-parse HEAD}`. Nenhuma chamada ao POWER, porque a MUNA cobre os 1.794.
- Contrato do s/<cod>.json (o método fica com o agente de projeção; aqui só a forma):
```json
{"cod":"2311306","gerado_em":"2026-11-15",
 "chuva":{"tipo":"medido","fonte":"GPM IMERG V07 via POWER","inicio":"1998-01","mm":[...],"normal_mes":[12 valores],"preliminar_desde":"2025-10"},
 "solo":{"tipo":"medido","fonte":"SMAP L4","inicio":"2015-04","pctl":[...]},
 "culturas":{"Milho":{
    "historico":{"tipo":"medido","fonte":"IBGE PAM, R$ de 2025 (IPCA)","anos":[1998..2025],"rend_kg_ha":[...],"receita_ha":[...],"perda_area":[...]},
    "custo_ha":{"tipo":"medido|suposicao","fonte":"CONAB <UF/praça>","valor":0},
    "ciclos":[{"ciclo":"2027","colheita":"mai–jul/2027","tipo":"projecao","p10":0,"p50":0,"p90":0,"chance_prejuizo":0.0,"n_anos":28,"condicao":"El Niño forte (n=6)"}]}}}
```
- No cliente: o solo escolhe o arquivo (m/<cod>_tK, com recuo); água, área, mandioca, criação e mata só filtram, escalam ou parametrizam (área × R$/ha; mata → forestPct do PercolaCampo; água → mostra ou esconde baixio e irrigação), e cada regra dessas aparece como "suposição da interface".

## 4. Roteiro de telas (URL por etapa)
```
index.html  globo (v2) ─► "Me leva pro Nordeste" ou busca (busca.json → Nominatim) ─► mergulho ─► município aceso
   └─ painel lateral = painel.html?cod=…&embutido=1 (JP: Inverno 2027 · Plantar · Alerta)  [Montar o plano do meu roçado]
plano.html?cod=…  (leve; funciona sem WebGL; "dados de 15/11/2026")
 ┌───────────────────────────────────────────────────────────────────────┐
 │ QUADRA · Quixadá–CE · situação em 15/11/2026            [voltar ao mapa] │
 │ (1)Perguntas (2)Opções (3)Calendário (4)Roçado (5)Retorno (6)Fontes      │
 ├───────────────────────────────────────────────────────────────────────┤
 │ #perguntas  solo · água · tamanho · mandioca no chão · criação · mata    │
 │ #opcoes     cardápio 15 culturas + "o que fazer agora"  [MODELO][MEDIDO] │
 │ #calendario Gantt por parte até dez/2027 (motor.agenda)                  │
 │ #rocado     desenho A/B/C + baixio + bordas, ano a ano  ──► iframe       │
 │             modulos/percolacampo/?cultura=milho&solo=arenosa&padrao=strips│
 │             &barreira=1&mata=45&modo=embutido   [ILUSTRATIVO]            │
 │ #retorno    histórico PAM (linha cheia) + leque por ciclo 2027/28/29     │
 │             + chance de prejuízo + rotação vs monocultura  [PROJEÇÃO]    │
 │ #fontes     comum.json + cartões + CREDITOS                              │
 └───────────────────────────────────────────────────────────────────────┘
```
Ligação Vicente ↔ José: Partes A/B/C viram o padrão "strips" (faixas); as bordas perenes (gliricídia e palma em curva de nível) acendem `windBorderOn`; a cultura do ano no interruptor do roçado vai em `cultura`; o solo do item 3 vai em `soilId` (1→arenosa, 2→mista, 3→argilosa); a resposta sobre mata vai em `forestPct`. Os terrenos continuam os de exemplo (rotular), e vento do POWER e declive do SRTM ficam para o P2. Mudança no arquivo do Vicente: ~20 linhas lendo URLSearchParams para o appState e escondendo o cabeçalho no modo embutido, com o cabeçalho de origem no topo.

## 5. Autoria (sem git perigoso antes do prazo)
- As fontes são os worktrees já existentes: colegas/joao-pedro (destacado em 29f81f6, JpLimags) e colegas/vicente (18fd0e3, Vicente Lima).
- Cada arquivo copiado ganha cabeçalho: `// Origem: estudo-jp@29f81f6 site-nasa/static/js/rocacerta.js — autor: João Pedro (JpLimags). Adaptado em 15/11/2026: caminhos relativos, ?cod=.` (em HTML, comentário `<!-- -->`).
- CREDITOS.md com a tabela completa. Para ressincronizar se eles mandarem algo novo: `git fetch origin` e depois `git diff 29f81f6 origin/estudo-jp -- <arquivo>`.
- Trailers `Co-authored-by:` com o JP e o Vicente no commit de integração: decisão do José (a regra da memória é só sobre não pôr o Claude como coautor).
- Depois da entrega (P2): merge real. estudo-vicente entra limpo; estudo-jp tem 7 conflitos, resolvidos com o lado do JP em site-nasa/ e união no .gitignore.

## 6. Como rodar
- Site: `E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 site-versao-final/servidor.py` → http://127.0.0.1:8090 (qualquer Python 3 serve, porque é só biblioteca padrão). Outra máquina: `python servidor.py` (o `python -m http.server -d web` também funciona onde o .js tiver o MIME certo).
- Dados: `python ferramentas/gerar_municipios.py` (~20 min) → `gerar_series.py` → (P1) `gerar_solos.py --processos 4` → `conferir_dados.py`. Roda em segundo plano, destacado, sem abrir janela.

## 7. Sem internet (demo)
- Já locais: globo, texturas, fontes, three e MapLibre (v2), painel do JP com JSON local, plano e PercolaCampo (Tailwind vendorizado).
- Trocar por versão local: a malha do IBGE (mapa.js:576 → dados/malha_ne.geojson) e o Nominatim (busca.json primeiro).
- Ladrilhos: plano B de estilo sem ladrilho (fundo + municípios coloridos), acionado no erro de ladrilho ou quando navigator.onLine é falso. No P2, o pacote S2 z4–z9 (~20 MB, CC BY-NC-SA com atribuição).

## 8. Publicação
- Opção A (recomendada, grátis): repositório público novo só com o web/. Comandos: `git subtree split --prefix=site-versao-final/web -b web-pages` e `git push <novo> web-pages:main`; Pages saindo de main/(root); .nojekyll. URL: https://netinhoklz.github.io/<nome>/
- Opção B: tornar o competicao-nasa público, com um workflow do Actions publicando site-versao-final/web. O repositório inteiro fica exposto, incluindo os PDFs de editoras.
- Opção C: Netlify ou Cloudflare Pages arrastando a pasta (exige conta).
- Não publicar: PDFs de artigos, _netrc, dados brutos.

## 9. Cronograma (1 pessoa + IA)
- 14/11, 19h–01h: estrutura e créditos (1 h), gerar_municipios rodando (1,5 h + 20 min de máquina), painel do JP estático com o botão para o plano (2 h), esqueleto do plano.html e do dados.js (1 h).
- 15/11, 08h–20h: etapas (3 h), perguntas (1 h), PercolaCampo em iframe (1,5 h), séries e retorno (3 h), offline e conferência (2 h), publicação e vídeo (1,5 h).
- Congelar às 20:00; 20h–23:59 é folga para correções, envio e o vídeo.

## Riscos
- Perde-se a precisão por ponto: no estático, o GAEZ (pixel de 5') e o SMAP valem no ponto interno do município, não onde a pessoa clicou. Em municípios grandes, como Barreiras, rotular 'no ponto central do município'. O modo ao vivo (P2) devolve a precisão.
- Dados congelados em 15/11/2026: 'o que fazer agora' e as janelas 'abertas agora' envelhecem se o júri abrir dias depois. A data precisa aparecer na tela.
- Corrida no cache do motor: a trava é threading.Lock dentro de um processo e o .tmp tem nome fixo (motor.py:259-280). Várias gerações em paralelo na primeira passada podem falhar no os.replace do Windows.
- WebGL fraco ou software no laptop do júri: o plano.html precisa funcionar sozinho, com link 'ver sem 3D' e busca local.
- Ladrilhos externos (EOX S2, Esri Wayback, OpenFreeMap, AWS Terrain) podem cair ou limitar pedidos; a licença CC BY-NC-SA do EOX exige atribuição visível.
- Tailwind por CDN no PercolaCampo: precisa de internet, não é para produção e reseta o CSS global. Só funciona isolado em iframe e vendorizado.
- PercolaCampo diz 'calibrado por meta-análise', mas o motor usa constantes fixas (0,56·pb; 2,35; 108 − 34·R_eff) e terrenos fictícios. Sem o rótulo de ilustrativo, o júri pode contestar a credibilidade do projeto inteiro.
- Narrativa do El Niño em conflito: estado (JP, AUC ≈ 0,5 por município) contra município (motor do José). As duas na mesma jornada confundem o agricultor.
- Direitos autorais: PDFs de editoras (PhysRevE, PHYTO) estão versionados em estudo-vicente; não podem ir para o web/ nem para um repositório público.
- Publicação depende de decisão do José: o repositório atual é privado (404), Pages privado é pago, e criar um repositório público é voz pública.
- Tamanho no git: 90–190 MB de JSON; regenerar e commitar várias vezes multiplica o histórico. Commitar os dados uma vez, ou só no repositório público.
- Disco C: a 96% (11 GB livres): a geração deve escrever direto em web/dados, sem cópias intermediárias no C:.
- Prazo: o P0 soma ~14 h. Sem congelar às 20h de 15/11, o PercolaCampo ou a projeção ficam pela metade.
- Autoria do site-nasa-v2 não confirmada: usá-lo como casca sem deixar visíveis o painel e os easter eggs do JP pode parecer descarte do trabalho dele.

## Perguntas abertas
- Quem fez o site-nasa-v2? O JP concorda que ele seja a casca, com o painel Roça Certa e os easter eggs dele portados?
- Publicar num repositório público novo só com o web/ (qual nome?), ou abrir o competicao-nasa? Os dados derivados do GAEZ (CC BY-NC-SA 3.0 IGO) podem ir junto?
- Qual narrativa do El Niño vale na jornada: por estado (teste do JP) ou por município (motor)? Ou as duas, deixando a escala explícita?
- Pergunta de solo: só 3 texturas, com a classe AD do ZARC derivada (suposição), ou uma segunda pergunta 'a terra segura água?' para a AD?
- Fazer o merge real das branches antes da entrega (preserva o git blame) ou só a cópia com créditos? Pôr Co-authored-by do JP e do Vicente no commit de integração?
- O Vicente aceita o PercolaCampo rotulado como ilustrativo e alimentado pelos parâmetros do plano (faixas A/B/C, bordas, solo)?
- Nome para o júri: QUADRA (produto) com o Roça Certa como a tela do agricultor? JP e Vicente usam os dois nomes.
- O painel lateral fica com o Roça Certa do JP como está, ou com um resumo do motor do José (Este ano e Cardápio)?