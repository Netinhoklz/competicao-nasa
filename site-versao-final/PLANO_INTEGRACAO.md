# QUADRA, versão final: plano de integração

14/11/2026, 18h. Base: análise de 10 agentes (pasta `analise/`, um relatório por ângulo e `00_resumos_e_recomendacoes.md`).
Entrega: 15/11/2026, 23:59.

## O que entra de cada um

| Parte | Origem | O que entra no site final |
|---|---|---|
| José | `protótipo/` (branch `estudo-jose`, commit e7a23b5) e `notebooks/estudo_financeiro` | O núcleo: motor (GAEZ + ZARC + POWER + catálogo + El Niño + SMAP), cardápio, plano A/B/C + baixio + bordas, calendário até dez/2027, base do financeiro |
| João Pedro | `colegas/joao-pedro/site-nasa` (branch `estudo-jp`, 29f81f6) | A casca: globo 3D, mergulho até o Nordeste, mapa dos 1.794 municípios, painel "Roça Certa" ao lado do mapa (aba Inverno 2027) |
| Vicente | `colegas/vicente/pesquisa_vicente` e `interface-inicial-vicente` (branch `estudo-vicente`, 18fd0e3) | A distribuição no roçado: faixas intercaladas no lugar de blocos (limiar de percolação), a pergunta do solo com as palavras dele ("seca rápido / segura / encharca") e o simulador PercolaCampo como modelo teórico ilustrativo |

## Decisões (resolvem as divergências entre os agentes)

1. **Uma pilha só.** Um servidor Python só com a biblioteca padrão (`servidor.py`, porta 8090) serve o site estático (`web/`) e a
   API (`/api/local`, `/api/municipios`). O núcleo é uma cópia do motor do protótipo (`nucleo/motor.py`, com a origem no cabeçalho),
   porque o site final muda o motor (solo "não sei", maniva, financeiro, projeção) e o protótipo fica como registro da versão
   revisada. Nada de Flask nem de Node no produto.
2. **Um globo só: o do João Pedro**, convertido para estático (sem Flask), com a busca local dos 1.794 municípios. O `site-nasa-v2/`
   (JS puro, autor não confirmado) fica de fora; só as bibliotecas de terceiros da pasta `vendor/` podem ser reaproveitadas.
3. **Uma definição de El Niño:** a do motor. ONI de out–dez/nov–jan ≥ 1,5 → quadras de 1998, 2010, 2016 e 2024. O painel do João
   Pedro (que usava ONI ≥ 0,5, 6 anos) e a projeção (que usava 3 anos) passam a usar essa. O estado é a manchete, em frequência
   ("em X de 10 municípios do CE..."); o município é o detalhe ("o que aconteceu aqui, não é previsão").
4. **As perguntas entram depois das opções e antes do plano.** O lugar sozinho já dá o cardápio, as janelas e o El Niño, e os padrões
   saem do Censo Agro 2017. Bloco 1 ("Sua roça", antes da distribuição): terra, tamanho e baixio, água, mandioca/maniva, criação.
   Bloco 2 ("Seu bolso", na entrada do dinheiro): prioridade, preço da raiz e nível de custo. Toda pergunta tem "não sei".
5. **Do PercolaCampo entram a ideia e a geometria, não os números.** O R_eff, o "% de plantas protegidas" e as constantes do motor do
   Vicente não estão nos artigos da pasta dele (grau D; ver `analise/vicente.md`). O que tem fonte: o limiar de percolação
   (0,593 em malha quadrada) e a ideia de que faixas intercaladas separam o hospedeiro em pedaços. O site calcula a conectividade
   de verdade sobre o desenho do roçado (blocos de gramínea, se descem até o baixio) e diz o limite: não segura praga que voa
   (lagarta-do-cartucho, bicudo).
6. **Solo "não sei" = a janela que vale em todos os solos** (interseção), com o trecho que depende da terra à parte. Hoje o motor usa
   o melhor caso, o que contraria a regra 3.5 da proposta.
7. **Financeiro = refazer o plano nos anos que já aconteceram no município** (PAM 1998–2025, R$ de 2025): 2027 entre os 4 El Niños
   fortes, 2028 e 2029 entre os 28 anos, o mesmo ano para todas as culturas (3.136 sequências). Plano contra o jeito de hoje
   (milho + feijão). Só milho, feijão e mandioca têm série; forragem e perenes ficam sem R$.
8. **Projeção por ciclo = quantis do município encolhidos para a mesorregião, com 2027 condicionado ao El Niño e alargamento
   conforme** (backtest em 1.783 municípios: cobertura de 80% em 0,78; ver `analise/projecao.md`). Na tela: "em 8 de 10 anos
   parecidos você colhe pelo menos X", a grade de 10 roças e o que o município colheu de fato nos anos de El Niño forte.
   Não dá para projetar: seca de vários anos, a roça de uma família, o efeito da rotação, preço futuro.
9. **Todo número leva um selo:** MEDIDO, SUPOSIÇÃO ou PROJEÇÃO, com a fonte ao passar o mouse.

## A jornada

```
index.html (globo do João Pedro) ─ escolhe o município ─ mergulho ─ mapa + painel Roça Certa
        └─ botão "Montar o plano do meu roçado" ─► roca.html#/<cod>/<passo>
              1 O lugar        o que os dados permitem, sem perguntar nada (hoje medido, El Niño, cardápio, janela aberta agora)
              2 Sua roça       5 perguntas, todas com "não sei" (padrão do Censo)
              3 Como plantar   roçado visto de cima em escala, faixas A-B-C-A-B-C (Vicente), ano 2027/28/29, mês a mês,
                               calendário de plantio e colheita, o que fazer agora
              4 Quanto rende   plano × jeito de hoje, caixa mês a mês, "se 2027 for como 1998/2010/2016/2024"
              5 Segurança      leque por colheita (2027, 2028, 2029), grade de 10 roças, o que já aconteceu aqui
```

## Pastas

```
site-versao-final/
  servidor.py                 servidor stdlib: web/ + /api
  nucleo/motor.py             cópia do motor do protótipo, com as mudanças do site final
  dados/                      JSON gerados (financeiro, projeção, padrões do Censo) que a API serve por município
  ferramentas/                scripts que geram dados/ (e origem_analise/: os scripts dos agentes)
  web/index.html              globo, mergulho, mapa e painel (João Pedro)
  web/roca.html               a jornada em 5 passos
  web/js/passos/*.js          um arquivo por passo
  web/dados/                  dados estáticos lidos pelo navegador (malha, El Niño por estado)
  web/modulos/percolacampo/   simulador do Vicente (modelo teórico, ilustrativo)
  analise/                    os 10 relatórios
  CREDITOS.md                 arquivo → autor → branch@commit → o que mudou
```

## Contrato da API (`GET /api/local?lat=&lon=` ou `?cod=`)

O JSON do protótipo (local, clima, analogos, confianca, cardapio, este_ano, plano, agenda, evidencia, fontes) mais:
- parâmetros novos: `textura` (1–3), `ad` (11–16), `ad_baixio` (11–16), `maniva` (tem | nao | plantada), `hoje` (AAAA-MM-DD);
- `financeiro`: série e faixas por cultura do município (contrato em `analise/financeiro.md`, seção 3);
- `projecao`: quantis por cultura e ano 2027–2029 (contrato em `analise/projecao.md`, seção 7);
- `padroes`: padrões do Censo 2017 para as perguntas (`rocado_ha`, `pct_irrig`, `pct_cisterna`, `pct_semente_milho`, ...);
- `el_nino_uf`: a manchete do estado com a definição única.

## O que fica para depois da entrega

Publicação estática para o júri (repositório público: decisão do José), modo sem internet completo, versão em inglês dos rótulos,
vento e declive no desenho do roçado, perguntas da temporada (data de plantio, pluviômetro), portarias plurianuais fora do CE.

## Pedidos aos colegas

- João Pedro: subir `conselho/analises/jp_analogos_atlantico.py` e `pesquisa/embasamento_painel_nordeste.md`, citados no README dele
  e ausentes do branch. Até lá, o "AUC ≈ 0,5" não aparece no site.
- Vicente: dizer de onde vêm as constantes do PercolaCampo (k das faixas e do xadrez, χc 0,88–0,92, q, α, d0) e conferir o DOI do
  González-Martínez 2026. Até lá, esses números não aparecem.

## Rodada de 14/11 (noite): os 16 pontos, o jeito de hoje e as perenes

- **16 pontos do desafio:** 10 módulos em `web/js/extras/`, um por ponto, encaixados nos passos por um integrador e conferidos por
  dois revisores. Relatórios em `integracao/*.md`.
  - Ponto 16: frase fixa na barra de baixo, "seu olho" nos momentos de decisão, confiança dos dados e "Leve para o técnico".
  - Mapa: camadas leves no zoom do globo, entre elas quebra 2027, solo, calor, água guardada e confiança.
- **O jeito de hoje e a experiência** (pedido do José): `extras/hoje_ideal.js`, `extras/historico.js` e `extras/area.js`.
  - Passo 2: começa por "Como você planta hoje?" e "O que plantou e o que deu certo". A área aceita hectares, tarefas ou a medida
    do terreno.
  - Passo 3: "Por onde começar o seu giro".
  - Passo 4: Hoje → Melhor → Ideal. O "jeito de hoje" da conta passa a ser o informado.
  - Passo 5: "A sua memória e os dados".
- **Perenes: caju, banana e cana** (a jaca fica de fora, sem dado). Não giram nas partes A/B/C; ficam nas bordas ou num pedaço fixo.
  - ZARC dos perenes do NE em `scripts/zarc_perenes_ne.py`: caju Port. 403–411/2020 (9 UFs); banana de sequeiro Port. 260–268/2019
    (AL, BA, MA, PB, PE, SE); cana "outros fins" Port. 5/2026.
  - GAEZ: banana e cana.
  - Financeiro: série do caju (castanha) por município e banana/cana no CE (`scripts/preparar_perenes_financeiro.py`; rodar depois
    de `ferramentas/preparar_financeiro_site.py`).

## Rodada de 15/11 (madrugada): o fluxo novo

- 10 lentes propuseram e debateram o fluxo (`analise/fluxo/01..10_*.md` e `debate/`); o fechamento está em `analise/fluxo/00_FLUXO_FINAL.md`.
- O globo leva direto a **Sua roça** (`#/<cod>/2`): uma tela, 4 linhas já marcadas com o comum daqui (o que planta, tamanho, terra, baixio).
  Do painel ao plano são 2 toques (eram 14); respondendo tudo, 6.
- O resto é perguntado onde age: maniva no plano, 2025 no giro, o ano que quebrou na memória, prioridade nas abas do dinheiro;
  custo, raiz e arranjo em "Ajustar a conta". Saem água (vai ao "Leve para o técnico"), manejo, "deu bem", "o que já faz" e Garantia-Safra.
- Um indicador (pílulas Roça · Plano · Dinheiro · Seca · Espaço, ordem [2,3,4,5,1]) e um verde por tela. O passo 1 vira "Do espaço".
- Conferência: `testes/ferramentas/aceite_fluxo.py` (21 critérios, 7 municípios) e `percorrer_fluxo.py`. Relatórios em `analise/fluxo/implementacao/`.

## Rodada de 15/11 (manhã): o jeito de hoje × o ideal, o terreno em metros e o relatório

- Pedido do José e decisões D1–D8: `analise/fluxo2/BRIEFING.md`. Fluxo colado, os 16 pontos e o aceite: `analise/fluxo2/00_FLUXO_V2.md`.
  Relatórios dos agentes: `analise/fluxo2/implementacao/`.
- **Jornada:** Sua roça (`#/<cod>/2`) → O plano (`/3`) → Quanto rende (`/4`) → **Relatório** (`/5`), pílulas Roça · Plano · Dinheiro ·
  Relatório (`ORDEM = [2, 3, 4, 5]`). O "Se secar" saiu (`seguranca.js` fica no disco). O "Do espaço" foi para o painel (abas Solo e
  clima, E se chover, Os dados) e para o cartão do mapa (3 números-chave). `#/<cod>/1` abre Sua roça.
- **Sua roça:** as 18 culturas do cardápio + "Outra" (`extras/culturas.js`, barra "Ver todas as culturas"), o tamanho em metros
  (`larg`, `comp`), o baixio explicado com um desenho, a maniva e o ano passado (saíram do Plano).
- **O plano:** abre em "Seu jeito, melhorado" (só as culturas dele, girando). O controle [Seu jeito melhorado | O ideal] grava `plano`;
  no ideal, "O que vale mais para você?" grava `prioridade`. "O que você ganha" compara Hoje → Melhorado → Ideal com 8 números
  selados, e "Seu terreno em metros" mostra o espaçamento, as covas, o material e o zoom de 5 × 5 m (`dados/agronomia.json`, ~30
  publicações da Embrapa e 5 artigos).
- **Uma fonte só:** `extras/ideal.js` (`escolhido`, `comparar3`, `agendaDe`), sem DOM, roda no node. Plano, Quanto rende e Relatório
  mostram o mesmo plano e os mesmos números. O Melhorado mudou de definição: Quixadá padrão em 3 anos é Hoje R$ 2.480, Melhorado
  R$ 2.550 e Ideal (Guardar água) R$ 3.980. O "Um pouco de cada" segue com R$ 4.360. `calculo.js` não mudou.
- **Revisão e correção (tarde):** os 3 revisores mostraram que o "Guardar água", então padrão de 2027, dava sobra negativa justo no
  ano de El Niño (Quixadá −R$ 33). Agora a prioridade padrão sai dos números (`ideal.escolhaPadrao`): nunca uma que perde para outra
  em ano normal, 2027 e quebra; em ano de alerta, a que mais sobra em 2027. Em 6 dos 7 municípios é "Mais renda" (Quixadá: Ideal
  R$ 6.640 em 3 anos). Em Picos, Arapiraca e Barreiras nenhum ideal rende mais que o jeito de hoje, e a tela diz isso. Também:
  grão e raiz de mandioca em números separados; mandioca marcada em "O que planta hoje" já está no chão; perenes num pedaço próprio
  do desenho; palma com 10 t MS/ha/ano (SUPOSIÇÃO); a manchete do ideal compara com o seu jeito (`hoje_ideal.mancheteIdeal`).
- **Relatório:** datas dd/mm/aaaa só da agenda (ZARC e as regras do núcleo), o "como" de cada tarefa, o material, "Leve para o
  técnico", WhatsApp com as próximas tarefas e PDF A4 com até 4 páginas.
- **Conferência:** `testes/ferramentas/aceite_fluxo.py` (node + telas nos 7 municípios + 13 toques + painel + percurso + PDF) e
  `percorrer_fluxo.py`. Os JSON da API para os testes do node estão em `testes/exemplos/api/`.
