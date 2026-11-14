# Perguntas ao agricultor e inferência (perguntas)

## Resumo
Recomendo não fazer nenhuma pergunta antes da primeira resposta. O lugar sozinho já dá o cardápio, as janelas e o El Niño, e os valores padrão saem do Censo Agro 2017. As perguntas entram depois das opções e na hora em que mudam o que está na tela: um bloco de 5 perguntas em 2 telas ("Sua terra" e "Sua roça") entre as opções e a tela da plantação/distribuição, e um bloco de 2 perguntas ("Seu bolso") na entrada da tela de dinheiro e segurança. Cada resposta vira depois um selo editável nas telas seguintes. São 7 perguntas, em cerca de 60 segundos, com o botão "pular" para ficar com o padrão do município. A pergunta que mais muda a resposta é a do solo, e há um defeito hoje: o "não sei" usa o melhor caso entre os solos (motor.py:969; app.js:10), ao contrário da regra da proposta, que pede a faixa entre o solo mais restritivo e o mais permissivo (3.5; estrutura_gaez_zarc.md:192; revisão A7). Medi pela API em funcionamento: no caupi de Quixadá, o "não sei" dá 11/03–20/04 (41 dias), e a terra arenosa, 11/03–20/03 (10 dias); no milho do baixio em Barreiras, 82 dias contra 10 dias no AD2. Para dar segurança, o "não sei" deve mostrar a janela que vale em todos os solos. A pergunta do solo deve usar as palavras e os ícones do Vicente ("Como fica a terra quando chove?"), que alimentam o motor do José (textura e AD do ZARC) e o PercolaCampo ao mesmo tempo. As outras respostas mexem em parâmetros que já existem: área e baixio (A_F e A_B, hoje fixos em 2/3 e 1,0 ha), maniva (o ramo do plano sem mandioca já existe), água (área salvável = volume ÷ 620 m³/ha, ou aviso de irrigado), prioridade (o número de destaque no financeiro) e Garantia-Safra (limite de 5 ha e item do P1).

## Recomendações
- **P0** (1.5 h) Trocar o 'não sei' do solo pela janela que vale em todos os solos (interseção dos decêndios entre os Cod_Solo de cada nível em _decs). A extensão do solo mais permissivo aparece como barra 'depende da sua terra' com o selo 'confirme o solo'. Se a interseção for vazia, mostrar 'depende do solo: responda a pergunta 1'. — É a resposta que mais muda a segurança. O padrão de hoje promete uma janela 4 a 8 vezes maior a quem tem terra arenosa (caupi em Quixadá: 41 contra 10 dias; milho em Barreiras: 82 contra 10 dias), e contradiz a proposta 3.5 e a revisão A7.
- **P0** (1 h) Pergunta 1 com as palavras e os ícones do Vicente (Seca rápido / Segura sem empoçar / Encharca), passando textura 1/2/3 e ad 12/13/15 para a API e soilId arenosa/mista/argilosa para o PercolaCampo. Os selects AD1–AD6 ficam só no 'modo técnico'. — Uma pergunta só alimenta os dois motores, e o agricultor não sabe o que é AD. O mapeamento textura→AD é uma suposição, rotulada e confirmada pelo técnico.
- **P0** (3 h) Criar a 'ficha da roça': um objeto resp no JS com os padrões, selos editáveis em todas as telas, as respostas na URL (?t=1&b=1&ha=1.0…) para compartilhar e um aviso curto de 'o que mudou' quando a pessoa troca uma resposta. Montar os 2 blocos de perguntas: 5 depois das opções e 2 na entrada do financeiro. — É o momento certo: valor primeiro, perguntas quando mudam o que está na tela, e o 'pular' garante que ninguém trava.
- **P0** (0.5 h) Exportar um JSON de padrões por município a partir do Censo 2017: roçado (máximo entre milho e caupi por estabelecimento familiar), % irrigação, % cisterna, % semente guardada de milho e de caupi, % familiar. — Cada 'não sei' precisa de um padrão local com fonte, e não de um número inventado.
- **P0** (1 h) Área do roçado e baixio substituem A_F = 2/3 e A_B = 1,0 do financeiro: A_B = área × fração do baixio; A_F = (área − A_B)/3. A elegibilidade do Garantia-Safra sai da mesma resposta (≤ 5 ha). — O R$ é linear na área. Com ~1 ha (Censo) em vez de 3 ha (ficção), tudo cai cerca de 3 vezes.
- **P0** (0.5 h) Pergunta 5 = 'não consigo maniva' liga o ramo do plano sem mandioca (motor.py:683), com um parâmetro maniva no plano e na API. — O ramo já existe e a mudança é de uma linha. Sem maniva, o plano com mandioca não se cumpre (a proposta lista a maniva como primeiro risco).
- **P1** (1.5 h) 'Já tenho mandioca plantada' faz a Parte A colher em 2027, tira a nota 'o tampão só protege a partir de 2028' e põe a receita da mandioca em 2027 no financeiro. — Muda o ano caro de 2027 (cerca de +R$ 4.600 numa conta rápida com 2/3 ha, cenário B) e o recado de segurança para o El Niño.
- **P1** (1 h) Pergunta de água: 'cisterna de beber' não muda nada e diz isso; 'barreiro, açude ou calçadão' pede o tamanho e mostra a área salvável = V/620 m³/ha no marco P4 (30/abr); 'poço ou irrigação' mostra o aviso de que o calendário de sequeiro não é o limite, com o GAEZ de insumo alto (aptidao_alta), e põe o caso no roteiro. — Água é o dado que o José pediu. Assim ela muda a inferência sem prometer o salvamento que a cisterna de beber não dá.
- **P1** (1.5 h) Pergunta 6 (prioridade) escolhe o número de destaque do financeiro: 'garantir comida e criação' → pior ano em 10 e cenário El Niño em primeiro, em kg e em R$; 'equilibrar' → mediana com faixa; 'vender' → mediana e sensibilidade ao preço da raiz (MULT_MAND: plano − S0 vai de R$ 13.978 a R$ 4.009 do preço de Quixadá ao P25 do CE). O padrão é 'garantir' quando nivel_alerta == 'alerta', e a tela mostra o porquê. — É a forma intuitiva de mostrar segurança contra retorno sem um otimizador, que a proposta adia para a próxima versão (3.5).
- **P1** (1 h) Parâmetro ad_baixio (AD5 quando o agricultor marca baixio) usado só na linha Baixio da agenda. A Parte B usa o AD da terra alta. — Hoje um ad único vale para o milho alto e o do baixio. O plano põe o milho no baixio justamente porque lá a terra guarda mais água (AD5–AD6 em Quixadá).
- **P2** (2 h) Criação muda o papel da Parte C e das bordas e o valor de uso da forragem (kg MS → cabeças × dias). Fica para depois, porque falta um número de forragem com grau e não há rebanho por município no projeto (IBGE PPM). — Sem animais, a forragem não tem uso. Mas o número precisa de base, e até amanhã só cabe o texto.
- **P2** (2 h) Perguntas da temporada no calendário, fora das 7: data de plantio por parte no P2 (avisa 'fora do ZARC') e o pluviômetro do vizinho do Vicente no P3/P4. — É o momento certo para elas segundo a proposta 3.3, mas não é cadastro.

## Achados
- **O 'não sei' do solo hoje mostra o melhor caso, contra a regra da proposta**: Sem solo escolhido, _decs junta todos os solos e mostra a janela mais permissiva. Nos três lugares que testei, o padrão saiu igual ao argiloso/AD6. A proposta (3.5), a estrutura (seção 6) e a revisão A7 pedem a faixa do solo mais restritivo ao mais permissivo. Para quem tem terra arenosa, o padrão de hoje promete uma janela 4 a 8 vezes maior. _[protótipo/motor.py:969 ('None = não sei: melhor caso entre os solos'); motor.py:600-607; protótipo/static/app.js:10 e 173-175; proposta/estrutura_gaez_zarc.md:192; protótipo/REVISAO_10_AGENTES.md:92 (A7). Medido com o script scratchpad/analise10/perguntas/sens.py contra http://127.0.0.1:8765: Quixadá, caupi: não sei 11/03–20/04, arenoso 11/03–20/03, médio 11/03–31/03, argiloso 11/03–20/04; mandioca: não sei 01/02–10/03, arenoso 11/02–28/02. Barreiras, milho do baixio: não sei 11/11/2026–31/01/2027, AD2 21/11–30/11, AD3 21/11–20/01. Arapiraca, milho: não sei 01/05–20/06, AD2 01/06–10/06.]_
- **O seletor de solo atual é técnico (AD1–AD6) e o do Vicente já está em linguagem de agricultor**: O protótipo do José tem dois selects: 'Textura' e 'Água disponível AD1…AD6'. O agricultor não sabe o que é AD. O PercolaCampo do Vicente pergunta 'Como fica a terra quando chove?' com três cartões: Absorve bem, Encharca fácil, Seca rápido. Eles correspondem direto aos Cod_Solo 1–3 do ZARC e aos SOIL_TYPES dele (mista, argilosa, arenosa). Uma pergunta só alimenta os dois motores. _[protótipo/static/app.js:169-176; colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html:556-567 (cartões) e 884-888 (SOIL_TYPES com smapFactor 0,88/1,00/1,24)]_
- **O motor só recebe 2 respostas do agricultor; o resto está fixo no código ou no notebook**: A API aceita só textura (1–3) e ad (11–16). No financeiro, a área das partes e do baixio é fixa (2/3 ha e 1,0 ha), o preço da raiz entra por MULT_MAND, o custo tem dois níveis (semente e desembolso) e o Garantia-Safra fica fora da conta. No plano, a mandioca entra sempre que é apta. Não existe parâmetro para 'tenho maniva', 'tenho baixio', 'tenho água' ou 'tenho criação'. _[protótipo/app.py:64-66; notebooks/secoes_financeiro/10_familia.py:22, 28, 56-58; motor.py:651 (tampao = 'Mandioca' if 'Mandioca' in ok), 656 (cereal_baixio), 683 (ramo de 3 fases sem mandioca, já pronto)]_
- **Os colegas quase não perguntam nada à família**: O painel Roça Certa do João Pedro só mostra leituras do satélite (solo SMAP, ENSO); a única entrada é a busca de município. A interface inicial do Vicente também só tem a busca. As perguntas de verdade estão no PercolaCampo: terreno em figuras, cultura, semente crioula ou comercial, espaçamento, 'como fica a terra quando chove', mata em volta (%) e maior preocupação (praga, doença, aliados). O protótipo de celular do Vicente tem ainda 'Pluviômetro do vizinho' (mm de hoje) e 'Monte a sua combinação'. _[grep de input/select em colegas/joao-pedro/site-nasa/templates e static/js (só busca e botões; rocacerta.js:206-236 = solo do satélite); colegas/vicente/interface-inicial-vicente/fonte/pagina.html (só #busca); percolacampo_v3...html:440-479 (terreno), 523 (semente), 891-901 (appState), 1539-1546 (assistente de 4 passos); interface-inicial-vicente/prototipo-celular/pagina.html:321-325 (pluviômetro) e 392-398 (comparação com 'Hoje: milho + feijão')]_
- **O Censo Agro 2017 dá valores padrão locais para área, água e semente**: Dado medido, IBGE 2017, por município. Roçado típico da família (a maior entre a área colhida de milho e a de caupi por estabelecimento familiar que planta): mediana do NE 0,78 ha (P10 0,30; P90 1,49); Quixadá 1,03 ha de milho e 0,95 ha de caupi. Irrigação (% das famílias): mediana 5,45%; Quixadá 2,78%; Petrolina 60,2%; 148 municípios ≥ 30% e 41 ≥ 50%. Cisterna: Quixadá 83,2%; 731 municípios ≥ 50%. Semente guardada de milho ≥ 50% da área em 1.107 de 1.495 municípios (Quixadá 73,5%; caupi 81,4%). Orientação técnica: mediana de 5,6% das famílias (Quixadá 7,3%), então a família vai usar a tela quase sempre sem técnico. O Censo não tem rebanho (não está no parquet). _[Scripts scratchpad/analise10/perguntas/defaults.py e defaults2.py sobre dados_resumo/derivados/ibge_ne_censo2017_praticas_mun.parquet (1.793 municípios, 79 colunas)]_
- **Área típica do Censo (~1 ha) é bem menor que a família da demo (3 ha)**: Dona Francisca (3 ha, 1 ha de baixio) é ficção da proposta. Em Quixadá, a área colhida típica por família é ~1 ha. O ano de referência do Censo (2016/17) caiu na seca de 2012–2017, então a área colhida subestima a plantada. Mesmo assim, a pergunta de área muda a escala do R$ em cerca de 3 vezes, e o padrão precisa avisar que é 'área colhida em 2017, ano seco'. _[proposta/PROPOSTA_FINAL_v3.md:787; 10_familia.py:4, 56; saída do defaults.py (Quixadá milho_ha_por_estab_fam 1,03)]_
- **Água: a cisterna de beber não muda o plano; o barreiro e a irrigação mudam**: Segundo a proposta, a cisterna é de beber (Marengo 2022), e o salvamento só existe com barreiro ou açude: 62 mm na floração do milho, ou 620 m³/ha. A cisterna-calçadão de 52 m³ salvaria cerca de 0,08 ha, um volume de grau D (suposição). Na tábua do ZARC do NE, o manejo 'Irrigado' só existe para o 'Feijão' (21.418 linhas, todas de feijão), e o motor filtra só o sequeiro. O GAEZ com insumo alto já vem em aptidao_alta. _[PROPOSTA_FINAL_v3.md:674 e 761; motor.py:148 (filtro Sequeiro), 404-406 (aptidao_alta); script zarc_manejo.py: Nome_Outros_Manejos Sequeiro 219.531 / Irrigado 21.418, só Feijão]_
- **A mandioca já plantada muda o ano caro de 2027**: O plano avisa que, sem mandioca no chão hoje, o tampão só protege a partir de 2028. No financeiro, 2027 é o ano caro: no cenário B, o plano fatura R$ 1.064 e a S0, R$ 1.532, e no desembolso fica em −R$ 6.080. Se a família já tem mandioca de 2026, a Parte A colhe em 2027. Fiz uma conta rápida com os números do notebook, sem rodar: R$ 6.937/ha (mandioca em El Niño forte) × 2/3 ha ≈ +R$ 4.600 em 2027. Sem maniva, o plano tem de usar o giro sem mandioca. _[motor.py:716-718 e 683; 10_familia.py:229-233]_
- **O Garantia-Safra só entra como regra e lembrete, nunca como R$**: Conferido na lei: perda ≥ 40%, área plantada máxima de 5 ha, renda até 1,5 salário mínimo, até 4 módulos fiscais. O valor do benefício e o que acontece com quem planta fora do ZARC não foram conferidos, e o notebook deixa o Garantia-Safra fora da conta. A resposta só pode mudar a elegibilidade (com a área), o item do checklist do P1 e o rigor do aviso 'fora do ZARC'. _[PROPOSTA_FINAL_v3.md:761 e 1256; 10_familia.py:28; motor.py:825 e 963]_
- **A proposta já previa as perguntas da primeira visita**: Na tabela 3.3, a primeira visita diz: 'Confirma a prática atual (o Censo 2017 sugere; 1 pergunta confirma). Pergunta o solo do roçado… Registra rebanho, semente guardada, maniva, mão de obra e água guardada.' A data de plantio é perguntada só no P2 (jan–fev). Isso confirma a separação entre as perguntas de cadastro (agora) e as da temporada (depois). _[PROPOSTA_FINAL_v3.md:369-371]_

## Reaproveitar
- colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html:556-567 (cartões 'Como fica a terra quando chove?') e 884-888 (SOIL_TYPES) → site-versao-final, tela 'Sua terra': Copiar o texto e os ícones como pergunta 1. A mesma resposta preenche textura e AD do ZARC e o soilId do PercolaCampo.
- percolacampo_v3...html:440-479 (cartões de terreno: plano com riacho no fundo / encosta inclinada / misto) → tela 'Sua terra': Adaptar como figuras do formato do roçado (pergunta 2b: baixio, ladeira, plano). Ladeira põe as bordas em curva de nível em destaque.
- percolacampo_v3...html:1539-1560 (setWizardStep: 'Passo x de 4', barra de progresso, Voltar/Próximo) → componente de perguntas do site-versao-final: Usar a mesma navegação para os 3 passos das perguntas.
- percolacampo_v3...html:523 e 891-901 (semente crioula/comercial, espaçamento, mata em volta) → tela 4 (plantação e distribuição): Ficam como controles dentro da tela de distribuição do Vicente, não como perguntas. Padrão 'crioula' quando o Censo dá semente guardada ≥ 50% da área.
- colegas/vicente/interface-inicial-vicente/prototipo-celular/pagina.html:321-325 (Pluviômetro do vizinho) → tela 6 (calendário e portões): Pergunta da temporada no P3/P4 do calendário. Fica para depois.
- colegas/vicente/interface-inicial-vicente/prototipo-celular/pagina.html:392-398 ('Hoje: milho + feijão' × 'Sua escolha', média, 3 piores anos, após El Niño) → tela 5 (dinheiro e segurança): Formato visual da comparação com a S0 no financeiro, com a área da pergunta 2a.
- protótipo/static/app.js:169-176 (seletoresSolo AD1–AD6) → modo técnico do cardápio: Manter só no 'modo técnico', atrás de um 'ver detalhes'.
- protótipo/motor.py:683-687 (giro de 3 fases sem mandioca) → motor (cópia em site-versao-final): Ligar com maniva=nao, sem escrever lógica nova.
- dados_resumo/derivados/ibge_ne_censo2017_praticas_mun.parquet → site-versao-final/dados/padroes_censo2017.json: Exportar um JSON de padrões por município (roçado, irrigação, cisterna, semente guardada, % familiar).
- notebooks/secoes_financeiro/10_familia.py:56-77 (ano_plano com A_F, A_B, KS_, KD_) → cálculo do financeiro no site: Trocar as constantes pela área e a fração de baixio respondidas. A chave semente/diária escolhe entre KS_, KD_ e o custo operacional.

## Proposta detalhada
## 1. Quando perguntar

```
[1 Abrir] → [2 Escolher o lugar] → [3 O que cabe aqui]  → (BLOCO A+B: 5 perguntas, 2 telas, ~40 s) → [4 Como plantar e distribuir]
                                       ↑ padrões do Censo,                                                   (José: Parte A/B/C, baixio, bordas
                                         "não sei" = seguro                                                   + PercolaCampo do Vicente)
                                                                            → (BLOCO C: 2 perguntas, 1 tela, ~15 s) → [5 Dinheiro e segurança]
                                                                                                                   → [6 Calendário e portões]
                                                                                                                       (perguntas da temporada: P2 data de plantio; P3/P4 pluviômetro)
```

Regras:
1. Nenhuma pergunta antes da tela 3. O lugar já basta e os padrões têm fonte.
2. Cada pergunta entra logo antes da tela que ela muda.
3. No máximo 3 perguntas por tela, com 1 toque cada; o "não sei" é sempre a primeira opção visível.
4. Botão "Pular: usar o padrão de <município>".
5. Depois, cada resposta vira um selo editável no topo das telas 4–6 (ex.: "Terra: arenosa ✎ · 1,0 ha · baixio ⅓ · só chuva"). Quando a resposta muda, o aviso diz o que mudou (ex.: "caupi: 11/03–20/04 → 11/03–20/03").

## 2. O formulário (7 perguntas)

```
┌─ Sua terra ─────────────────────────── 1 de 3 ─┐
│ 1. Quando chove forte, como fica a terra do    │
│    seu roçado?                                 │
│  [🏜 Seca rápido, a água some]  (arenosa)      │
│  [🌤 Segura a umidade, não empoça] (misturada) │
│  [💧 Encharca, gruda no pé]  (barro)           │
│  [?  Não sei → mostro as datas que valem em    │
│      qualquer terra]                           │
│ 2. Seu roçado: tamanho e formato               │
│   Tamanho: [-]  1,0 ha  [+]  (ha | tarefas)    │
│   "Padrão: área típica de Quixadá, Censo 2017  │
│    (ano seco)"                                 │
│   [plano com baixio] [ladeira] [plano, sem     │
│    baixio] [não sei]                           │
│   Se baixio: quanto? [um pedaço ¼] [⅓ ou mais] │
│ 3. Além da chuva, que água você tem para a     │
│    roça? (pode marcar mais de uma)             │
│  [só a chuva] [cisterna de placa, de beber]    │
│  [barreiro/açude/calçadão → tamanho: ~50 m³ /  │
│   ~500 m³ / ≥2.000 m³ / sei: ___ m³]           │
│  [poço ou irrigação]                           │
│                     [Pular]   [Próximo →]      │
└────────────────────────────────────────────────┘
┌─ Sua roça ──────────────────────────── 2 de 3 ─┐
│ 4. Tem criação?                                │
│  [nenhuma] [cabras/ovelhas: 1–5 | 6–20 | >20]  │
│  [gado: 1–5 | >5]  [não quero dizer]           │
│ 5. Mandioca: o que você tem hoje?              │
│  [já tenho mandioca plantada]                  │
│  [não tenho, mas consigo maniva até fev]       │
│  [não consigo maniva]                          │
│              [← Voltar]  [Ver como plantar →]  │
└────────────────────────────────────────────────┘
          … tela 4 (plantação e distribuição) …
┌─ Seu bolso (abre a tela 5) ─────────── 3 de 3 ─┐
│ 6. O que vale mais para você neste ano?        │
│  [🛡 Garantir a comida e a criação, mesmo      │
│      ganhando menos]  ← padrão em ano de       │
│      alerta de El Niño (e a tela diz por quê)  │
│  [⚖ Equilibrar]                                │
│  [💰 Vender e ganhar mais; aceito mais risco]  │
│ 7. Você está inscrito no Garantia-Safra?       │
│  [sim] [não] [não sei]                         │
│  → "Com 1,0 ha você cabe no limite de 5 ha."   │
│               [Ver o dinheiro e a segurança →] │
└────────────────────────────────────────────────┘
```

Não são perguntas, são chaves no financeiro com padrão do Censo: "Guardo a minha semente" (padrão: sim, quando a semente guardada de milho é ≥ 50% da área, como em Quixadá, com 73%) e "Pago diária?" (padrão: não, só a família). O "Compare com o que você planta hoje: milho + feijão ✎" é a S0 da proposta 3.3, também editável.

## 3. Pergunta → parâmetro → efeito

| # | Resposta | Parâmetro exato | Onde | Padrão ("não sei") e fonte | Efeito medido ou esperado |
|---|---|---|---|---|---|
| 1 | Seca rápido / Segura / Encharca | textura = 1/2/3 (Cod_Solo do ZARC); ad = 12/13/15 (suposição de mapeamento); PercolaCampo soilId = arenosa/mista/argilosa | API /api/local (app.py:64), _decs (motor.py:600-605), janela(), plano() (data da maniva), agenda() | NOVO: interseção dos solos (a janela que vale em todos) + barra "depende da terra" até o solo mais permissivo. Hoje = melhor caso (motor.py:969) | Medido, API, Quixadá: caupi 11/03–20/03 (arenosa), 31/03 (média), 20/04 (barro); maniva 11/02–28/02 (arenosa) contra 01/02–10/03. Barreiras, milho do baixio: AD2 10 dias contra 82 no "não sei" de hoje |
| 2a | Tamanho (ha) | A_F = (ha − A_B)/3; A_B = ha × fração do baixio (troca os 2/3 e 1,0 fixos de 10_familia.py:56); R$ × área | Financeiro; PercolaCampo (número de plantas e faixas na grade) | Censo 2017: máximo entre o milho e o caupi colhidos por estabelecimento familiar (Quixadá ~1,0 ha; mediana NE 0,78). Medido, mas de ano seco | Tudo em R$ escala linear: a demo de 3 ha fica ~3× acima do típico |
| 2b | Formato: baixio / ladeira / plano | baixio = 0/1 (linha "Baixio" do plano e da agenda; cereal_baixio, motor.py:656); ad_baixio = 15 (suposição); ladeira → texto das bordas "em curva de nível" em destaque | plano(), agenda() | Não sei = linha do baixio com o selo "se você tiver um baixio" | Sem baixio: sai o milho do baixio. Em Quixadá, o milho só chega a 30% de risco e só em AD5–AD6 (estrutura_gaez_zarc.md:137) |
| 3 | Só chuva / cisterna de beber / barreiro (V m³) / poço-irrigação | regime = sequeiro (atual, motor.py:148); cisterna → nada muda (texto "é água da casa"); barreiro → area_salvavel_ha = V/620 no P4; irrigação → aviso + aptidao_alta do GAEZ (motor.py:405) e, depois, ZARC "Feijão / Irrigado" | Agenda (marco P4), cardápio (rótulo), financeiro (milho do baixio salvável: depois) | "Só a chuva". Se pct_irrigacao_fam ≥ 30% (148 municípios; Petrolina 60%), a pergunta abre com "aqui X% das famílias irrigam" | 50 m³ ≈ 0,08 ha; 500 m³ ≈ 0,8 ha (62 mm na floração; volumes de cisterna grau D, proposta:674) |
| 4 | Criação | criacao = 0/pequenos/gado: papel da Parte C (forr, motor.py:652) e das bordas; P4 "segurar a venda dos animais"; financeiro: linha de valor de uso (qualitativa) | plano() (textos), agenda (P4), financeiro | Sem base de rebanho no projeto: padrão "cabras/ovelhas 1–5", marcado como suposição | Sem criação: Parte C vira palhada/cobertura e a forragem passa a "pode vender" (número na P2) |
| 5 | Mandioca plantada / tem maniva / sem maniva | maniva = plantada/tem/nao. nao → tampao = None (ramo motor.py:683); plantada → Parte A 2027 = colheita do tampão e sai a nota de motor.py:716-718 | plano(), agenda(), financeiro (ano_plano 2027) | "Tem maniva" (= família da proposta) | Plantada: 2027 deixa de ser o ano caro (conta rápida ≈ +R$ 4.600 com 2/3 ha, cenário B, 10_familia.py:229-233) |
| 6 | Garantir / Equilibrar / Vender | modo = seguranca/equilibrio/renda: número de destaque (pior ano em 10 e cenário El Niño, ou mediana, ou mediana com preço); unidade (kg/meses de comida, ou R$); MULT_MAND em destaque no modo renda | Financeiro e ordem dos cartões | "Garantir" se nivel_alerta == "alerta" (ONI +2,46); senão "Equilibrar". A tela mostra o motivo | Modo renda mostra plano − S0: R$ 13.978 (preço de Quixadá) → R$ 4.009 (P25 do CE), 10_familia.py:241-243 |
| 7 | Garantia-Safra sim/não/não sei | gs = sim/nao: elegível = área ≤ 5 ha (Lei 12.766/2012, art. 10, IV); não + elegível → item do P1 em destaque (motor.py:963); sim → aviso "fora do ZARC" em vermelho; linha "perda ≥ 40% aciona" sem R$ | Checklist P1, agenda, financeiro (texto) | "Não sei" → mostra a regra e o lembrete | Nenhum R$: o valor e a regra de plantio fora do ZARC não foram conferidos (10_familia.py:28) |

## 4. Contrato da API (mudança mínima)

`GET /api/local?lat=&lon=&textura=1-3|vazio&ad=11-16|vazio&ad_baixio=11-16|vazio&baixio=0|1|vazio&maniva=plantada|tem|nao&agua=chuva|cisterna|barreiro|irriga&vol_m3=N`

O financeiro (área, modo, gs, semente, diária) pode rodar no navegador, a partir de um JSON por município com R$/ha por cultura e cenário. Isso é tarefa do ângulo do financeiro. O JSON de padrões do Censo segue o formato `{cod: {rocado_ha, pct_irrig, pct_cisterna, pct_sem_milho, pct_sem_caupi, pct_familiar}}`.

## 5. O que cabe até amanhã (uma pessoa + IA)

P0, cerca de 7,5 h:
- "Não sei" seguro: 1,5 h.
- Pergunta 1 com as palavras do Vicente: 1 h.
- Ficha e blocos de perguntas: 3 h.
- JSON do Censo: 0,5 h.
- Área e baixio no financeiro: 1 h.
- Maniva "não": 0,5 h.

P1, cerca de 6 h:
- Mandioca plantada.
- Água (área salvável e aviso de irrigado).
- Modo do financeiro.
- ad_baixio.

Fica para depois: criação com número de forragem, irrigado completo, solo por SoilGrids, pesos da família reordenando os cartões, e as perguntas da temporada (data de plantio, pluviômetro).

## Riscos
- Trocar o 'não sei' pela janela segura muda as datas da demo de Quixadá (caupi passa a terminar em 20/03, e não em 20/04, com 'até 20/04 se a terra for de barro'). É preciso alinhar o texto do pitch e da proposta.
- O mapeamento textura→AD (arenosa 12, média 13, barro 15; baixio 15) é suposição. O ZARC classifica a AD pela granulometria e pela profundidade, e o técnico precisa confirmar. Rotular na tela.
- O roçado padrão do Censo 2017 é área colhida no ano agrícola 2016/17, no meio da seca de 2012–2017, e subestima a área plantada. Rotular 'área colhida em 2017, ano seco' e deixar o slider à mão.
- Em Quixadá, 83% das famílias têm cisterna. Se a pergunta de água não disser que a cisterna de beber não muda o plano, a família pode achar que tem água para salvar a lavoura.
- Os volumes de cisterna e calçadão (16 e 52 m³) e a regra de 620 m³/ha são grau C/D. A área salvável deve aparecer como estimativa, nunca como garantia.
- Garantia-Safra: o valor do benefício e a regra para quem planta fora do ZARC não foram conferidos. Não pôr R$ nem prometer cobertura.
- O padrão 'garantir' ligado ao El Niño pode parecer manipulação. A tela precisa mostrar o motivo e deixar trocar com 1 toque.
- Tarefa não é a mesma unidade em todo o NE: a área da tarefa muda de estado para estado e precisa ser conferida. Se não der tempo de conferir, perguntar só em hectares, com uma comparação visual.
- Os fatores do PercolaCampo (smapFactor, seedFactor etc.) são parâmetros do modelo do Vicente, não dados do SMAP. Ao juntar as duas telas, rotular como modelo para não misturar com o que é medido.
- Cada troca de resposta refaz a chamada à API. Para um município já visto, a assinatura do POWER vem do cache. Não disparar chamadas em laço ao mudar sliders (debounce), para não bater no limite de 429 do POWER.

## Perguntas abertas
- Quem usa a tela: a família sozinha ou o técnico de ATER? A proposta diz técnico, mas o Censo mostra que só 5,6% das famílias (mediana) têm orientação. Isso decide se o AD e o 'modo técnico' aparecem.
- O José aceita que o 'não sei' passe a mostrar a janela segura (comum a todos os solos) em vez do melhor caso, mesmo mudando as datas de Quixadá na demo?
- O Garantia-Safra fica como 7ª pergunta ou vira só um item do checklist do P1, abrindo espaço para outra pergunta (ex.: 'paga diária?')?
- Área em hectares ou em tarefas? Se for tarefa, quem confere quanto vale a tarefa em cada estado até amanhã?
- Há base de rebanho por município (IBGE PPM) em algum lugar do E:? Não está no parquet do Censo. Sem ela, o padrão da criação é suposição.
- O padrão da prioridade deve depender do alerta de El Niño do município, ou ser sempre 'Equilibrar'?