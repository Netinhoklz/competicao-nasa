# QUADRA: o fluxo da rodada 2 (15/11/2026, manhã)

O pedido do José está na íntegra em `BRIEFING.md`, seção 1. As decisões D1–D8 do orquestrador estão na seção 2 do mesmo arquivo.
Os relatórios de cada agente ficam em `implementacao/*.md`. Este arquivo mostra o resultado colado: a jornada em uma página, as
decisões, onde ficou cada um dos 16 pontos do desafio e o aceite.

## 1. Em 5 linhas

1. A jornada agora é **Sua roça → O plano → Quanto rende → Relatório**. O "Se secar" saiu, e o "Do espaço" foi para o mapa e o painel.
2. Sua roça pergunta o jeito de hoje com as 18 culturas do cardápio, o tamanho em metros, o baixio explicado, a maniva e o ano passado.
   Tudo tem padrão, então 1 toque ainda leva ao plano.
3. O plano abre no **jeito dele, melhorado**: só as culturas que ele planta, girando em faixas. Um controle grande mostra **o ideal**,
   e dentro dele "O que vale mais para você?" redesenha o roçado e os números na hora.
4. "O que você ganha" compara Hoje → Melhorado → Ideal com 8 números selados. O que não dá para medir aparece como "não medido".
   Quanto rende mostra os mesmos números.
5. O **Relatório** dá a lista do que fazer, com datas dd/mm/aaaa tiradas da agenda e o "como" de cada tarefa. Depois vêm o desenho do
   roçado, o material e o "Leve para o técnico". O verde manda tudo no WhatsApp, e o PDF A4 sai com até 4 páginas.

## 2. A jornada, tela a tela (390 px)

```
Globo (index.html)                       Painel do município (painel.html, no globo e sozinho)
 zoom no município → cartão com 3         Inverno 2027 · Plantar · Solo e clima · E se chover · Os dados
 números (milho quebra, chuva típica,     (as 3 últimas são o antigo "Do espaço" + o "E se chover…")
 solo agora), cada um liga a camada       verde "Montar o plano do meu roçado" ─┐
                                                                                 ▼
#/<cod>/2  SUA ROÇA  (verde "Ver o meu plano →")
  O que planta hoje? (as comuns daqui + "Ver todas as culturas (19)")   Tamanho: chips de ha | largura × comprimento (m)
  Na chuva forte, a sua terra…   Tem baixio? (desenho de lado + 1 frase)   Tem maniva?*   No ano passado, o que plantou? (2025)
                                                                                 ▼
#/<cod>/3  O PLANO  (verde "Quanto rende →")
  Agora: …   [Seu jeito, melhorado | O ideal]   (lado ideal: O que vale mais? Água · Renda · Solo · Um pouco de cada)
  roçado larg × comp, anos 2027–2029, "por quê" de cada parte   ▸ Seu terreno em metros (espaçamento, covas, material, 5 × 5 m)
  O que você ganha: Hoje → Melhorado → Ideal (4 números à vista, + 4)   O que fazer e quando   ▸ Por que este plano
                                                                                 ▼
#/<cod>/4  QUANTO RENDE  (verde "Ver o relatório →")
  sobra em 3 anos (Hoje · Melhorado · Ideal, o escolhido marcado)   uma linha por caminho (o ideal diz a prioridade · mudar)
  ano normal · 2027 · anos de quebra   "Em 8 de 10 anos já vistos aqui…"   ▸ 10 roças ▸ Ajustar ▸ 4 jeitos ▸ Ver como calculamos
                                                                                 ▼
#/<cod>/5  RELATÓRIO  (verde "Mandar no WhatsApp"; secundário "Imprimir / salvar PDF")
  cabeçalho com "Mudar" em cada linha   O que fazer e quando (dd/mm/aaaa, onde, o quê, como, condição)   2028 e 2029
  O que juntar para 2027 (desenho + material)   Leve para o técnico   (frase do ponto 16)
```
\* A linha da maniva só aparece quando a mandioca está no jeito dele ou no plano daqui.

**Links antigos:** `#/<cod>/1?…` abre Sua roça com as mesmas respostas, na mesma entrada do histórico. `#/<cod>/5?…` abre o
Relatório. **Mudar:** `data-editar` em qualquer passo abre Sua roça na linha certa (`hoje`, `ha`, `terra`, `baixio`, `maniva`,
`antes`), e o verde vira "Voltar a … →". **Uma fonte só:** Plano, Quanto rende e Relatório mostram `ideal.escolhido(r, resp, ef)`,
pelas chaves `plano` e `prioridade`. Trocar o lado ou a prioridade não chama a API de novo.

## 3. Decisões

### Do orquestrador (BRIEFING, seção 2; não reabertas)
D1 a jornada 2 → 3 → 4 → 5 · D2 Sua roça com todas as culturas, metros, baixio explicado, maniva e ano passado · D3 o plano melhorado,
o ideal e as prioridades no Plano · D4 terreno e espaçamento · D5 Quanto rende com a mesma fonte · D6 o "Do espaço" no painel e no mapa ·
D7 o Relatório · D8 sem mudar o núcleo nem o servidor.

### Do integrador (esta fase)
- **O "Melhorado" mudou de definição, e os números de Quixadá também.** Antes, o melhorado punha um pedaço de mandioca de reserva
  que ele não planta. Agora ele usa só as culturas dele (A2.md, seção 3). Com Quixadá padrão, em 3 anos, Quanto rende mostra:

  | | Antes (rodada 1) | Agora |
  |---|---|---|
  | Hoje | R$ 2.480 | R$ 2.480 |
  | Melhorado | R$ 4.190 | R$ 2.550 |
  | Ideal | R$ 4.360 | R$ 3.980 |

  O ideal padrão de 2027, ano de alerta, é "Guardar água". "Um pouco de cada" segue com R$ 4.360. O `calculo.js` não mudou, e o
  `teste_calculo.mjs` dá a mesma saída do HEAD.
- **O revezamento segue a célula do plano.** Um baixio "solteiro" ou "sem revezamento" não ganha a linha "… no milho em pé" na
  agenda (`ideal.js`, `fazerAgenda`), nem a 2ª planta no terreno. O "+ feijão em revezamento" do seu jeito conta o feijão entre as
  carreiras, a 25 cm, como diz o "como" do A1. Antes, o terreno só contava a 2ª planta quando o texto dizia "caupi".
- **Terreno e material:** a gliricídia da cerca agora é contada (perímetro ÷ 5 m). Quando a fonte não dá o kg, como no milho e na
  mucuna, sai o número de sementes (covas × por cova). O `agronomia.json` tem uma nova tentativa em 400 ms.
- **O ponto 4 ganhou casa nova:** "Testamos 7 jeitos de ler o passado" (as barras de acerto em 100) saiu do "Se secar" e foi para o
  "Ver como calculamos" de Quanto rende, ao lado do "Calibrador honesto".
- **"Seu olho" no Relatório:** o das faixas ("Faixas e espaçamento se acertam no chão, em curva de nível.") fica no bloco do material.
  Agora todo passo tem 1 à vista.
- **"Ver as 5 perguntas" virou "Ver as perguntas (5)"**, porque "5 perguntas" é frase banida e o técnico de Crateús tem 5 perguntas.
- **A animação de entrada só roda quando a pessoa chega ao passo.** Um redesenho por uma resposta nova não pula 10 px (`sem-entrada`
  na casca, para todos os passos).
- **Eco do Plano:** fica "Cada ano, outro lugar." (C2). Com o controle novo em cima, o desenho continua em 548 px, e o texto é menor.
- **Feijão × caupi na frente (pedido 7 do C2):** a decisão é chamar o Feijão-caupi de **"feijão"** e o Feijão comum de
  **"feijão comum"**. É a palavra de Sua roça ("Feijão · caupi, de corda") e a do "por quê" do motor; "caupi" fica no glossário e no
  balão. A troca mexe nos nomes curtos de `plantio.js`, `plantio/calendario.js`, `terreno.js`, `relatorio.js` e `leve_ao_tecnico.js`,
  e em cerca de 30 textos fixos. Fica para o Y (fase 5), com o aceite para conferir. Até lá, o desenho e o calendário dizem "caupi".
- **Testes no repositório:** os JSON da API sem respostas (8 municípios) estão em `testes/exemplos/api/`, e as 4 respostas reais
  de Quixadá em `testes/exemplos/api_respostas/`. `teste_dinheiro.mjs` (C3), `teste_relatorio.mjs`, `teste_pdf.py` (C4) e
  `teste_painel.py` (B3) foram para `testes/ferramentas/`, com caminhos relativos.

## 4. Os 16 pontos do desafio: onde ficou cada um

O "Se secar" e o "Do espaço" saíram da jornada. Conferi ponto a ponto: nenhum ficou sem casa.

| Ponto | Onde está agora |
|---|---|
| 1. Temperatura, umidade, chuva, evaporação × vulnerabilidade e solo | Globo (camadas Solo, Calor, Água guardada) e o cartão do município (milho quebra, chuva típica, solo agora); painel › Solo e clima (o solo de hoje pelo SMAP, quando a chuva chega, as tendências); Plano › Por que este plano › "Onde o seu roçado sofre mais" |
| 2. Termos científicos | "o que é?" do glossário em todos os passos e no painel; o glossário inteiro no painel › Os dados; o balão do selo |
| 3. Satélite × medida no chão | Painel › Os dados (`satelite_chao`, satélite × pluviômetro; `harmonizacao`); o selo diz o satélite ("MEDIDO · NASA SMAP" à vista em Sua roça) |
| 4. Comparar abordagens | Quanto rende › Ver como calculamos › "Testamos 7 jeitos de ler o passado" (acerto em 100, trazido do "Se secar") e o "Calibrador honesto"; painel › E se chover (teste deixando cada ano de fora) |
| 5. Transições sazonais, campo despido, estresse | Plano (o "Agora", o mês a mês com descanso, o calendário); "O que você ganha" › meses de chão coberto; Relatório (o que fazer e quando, mês a mês); painel › Solo e clima ("A chuva chega ~18/01") |
| 6. Incerteza e saber local | Selo em todo número; "não medido" onde não dá; Quanto rende › "Em 8 de 10 anos já vistos aqui…" e a grade de 10 roças (o compacto do "Se secar", D5); painel › Os dados (confiança); "seu olho" em todo passo |
| 7. Harmonização numa grade comum | Painel › Os dados › "Ver as grades de cada satélite" (`harmonizacao`) |
| 8. Comparar cenários de rotação | Plano: [Seu jeito melhorado \| O ideal] + as 4 prioridades redesenham o roçado; "O que você ganha" (R$, quebra, comida, forragem, N, chão coberto, caminho da lagarta); Quanto rende › "Os 4 jeitos, lado a lado" |
| 9. Ideias × prioridades do agricultor | Plano › lado "O ideal" › "O que vale mais para você?" (Água · Renda · Solo · Um pouco de cada), que grava `prioridade` e muda o desenho e os números na hora |
| 10. Fixadoras, cobertura, raízes | Plano › Por que este plano › "O que cada planta faz pelo solo"; "Adubo que o feijão deixa" (kg de N, com a fonte) em "O que você ganha"; Relatório › "Como fazer" (adubação verde, palha no chão) |
| 11. Mapas no tempo | Globo (camadas com controle de tempo e "tocar"); painel › Solo e clima (tendências) |
| 12. Vulnerabilidade no campo | Plano › "Onde o seu roçado sofre mais"; Plano › "Seu terreno em metros" (o roçado dele em escala, o baixio embaixo, onde a água desce); Sua roça › o baixio desenhado de lado |
| 13. Controles de cenário | Painel › E se chover (o controle da chuva e "cada ano", que vinha do "Se secar"); Plano › mês a mês; o controle de 2 lados e as prioridades |
| 14. Fácil para quem lê pouco | Uma tela de perguntas com padrão (1 toque), ícones e palavras da roça; um verde por tela; tetos de altura e palavras conferidos no aceite; Relatório com a data à esquerda e o "como" curto, no papel ou no WhatsApp |
| 15. Prioridades e restrições (água, equipamento, mercado) | Água: prioridade "Água" e o baixio. Mercado: prioridade "Renda" e o preço da raiz. Equipamento: o custo "semente, trator, adubo e diária". Terra, tamanho em metros, maniva e ano passado em Sua roça |
| 16. Apoia e não substitui | Rodapé fixo em cada tela (leva ao "Leve para o técnico"); "seu olho" em todo passo; Relatório › "Leve para o técnico" + WhatsApp; a frase no cartão do globo e no painel; "não medido" e os selos |

## 5. O que cada número quer dizer em "O que você ganha"

São 8 números (`ideal.beneficios`). Cada um tem selo e fonte, e quando falta o dado o valor é `null`, mostrado como "não medido":
- **R$:** sobra num ano normal, sobra em 2027 (El Niño) e anos de quebra em 10. Vêm de `calculo.js`, numa base pareada para hoje, o
  melhorado e os 4 ideais.
- **Comida colhida** (kg/ano).
- **Comida do gado** (t de matéria seca/ano) e **adubo que o feijão deixa** (kg de N/ano): coeficientes do `agronomia.json` × área,
  com selo SUPOSIÇÃO ou PROJEÇÃO pelo lugar da medida.
- **Meses de chão coberto.**
- **Caminho da lagarta cortado** (anos em 3), pelo `desenho.js`.

## 6. Aceite

`testes/ferramentas/aceite_fluxo.py` roda tudo em série, um Edge por vez, a 390 × 844. Os critérios:

| # | Critério | Como |
|---|---|---|
| N1 | `calculo.js` igual ao HEAD e `teste_calculo.mjs` com saída idêntica (diff vazio) | git + node numa árvore temporária com o `calculo.js` do HEAD |
| N2–N4 | `teste_ideal.mjs`, `teste_dinheiro.mjs` e `teste_relatorio.mjs` com 0 falha (no N4, toda data do relatório existe na agenda, em 168 casos) | node |
| Telas | Nos 7 municípios: Sua roça ≤ 1.800 px e ≤ 190 palavras; Plano (os 2 lados) ≤ 3.600 px e ≤ 430; Quanto rende ≤ 2.600 px e ≤ 300; Relatório sem teto. Também: 1 verde por tela, "seu olho" ≤ 2, nenhuma frase banida (à vista e nos "ver mais"), nada rolando de lado (também com tudo aberto), selo ≥ 11 px, "ver mais" ≥ 44 px, 0 erro no console. E o que cada tela precisa ter: as 5–6 linhas, "Ver todas", os metros, o baixio desenhado e um selo NASA em Sua roça; o controle, as 4 prioridades, "O que você ganha", sem maniva nem giro no meio, "Agora" ≤ 400 px e desenho ≤ 550 px no Plano; o gráfico ≤ 450 px e a tabela em Quanto rende; tarefas com datas, o técnico e o WhatsApp no Relatório | script por tela |
| C1 | Só "Ver o meu plano": hash sem parâmetros, ficha "(típico)", "(o comum daqui)" | toques |
| C2 | Quixadá padrão, Quanto rende: R$ 2.480 · 2.550 · 3.980 | toques |
| C3 | O controle de 2 lados e as 4 prioridades mudam o desenho e os números (4 de 4) e gravam `plano`/`prioridade`; voltar ao seu jeito desenha igual | toques |
| C4 | O mesmo plano e os mesmos números no Plano, em Quanto rende e no Relatório (Seu Antônio, 40 × 100 m, o ideal com Água) | toques |
| C5 | Voltar do navegador 4 → 3 → 2 → globo | toques |
| C6 | "Mudar" da ficha (passo 4) e do baixio (Relatório) abre a linha certa, com "Voltar a …", e volta | toques |
| C7 | Terra "não sei": o aviso da areia só para culturas do plano à vista (Piritiba; Petrolina, ideal); com barro some; nada em Quixadá | toques |
| C8 | Maniva em Sua roça: "Não tenho" grava `maniva=nao` e a mandioca sai do desenho, com aviso | toques |
| C9 | Ano passado em Sua roça: "Milho" grava `antes=2025:milho` e o Plano diz "ali teve milho em 2025 e 2026" | toques |
| C10 | Relatório: toda data dd/mm/aaaa (com todo detalhe aberto) existe na agenda do plano escolhido; WhatsApp com o plano e as próximas tarefas; nenhum verde no técnico | toques + motor na página |
| C11 | Selo "MEDIDO · NASA …" à vista em Sua roça, e o toque mostra a fonte | toques |
| C12 | Links antigos: `/1` → Sua roça com as mesmas respostas; `/5` → Relatório; ⅓ de baixio desenha | toques |
| C13 | A frase do ponto 16 leva ao "Leve para o técnico" do Relatório | toques |
| P1 | Painel: Solo e clima (`tendencias`), E se chover (`cenario_chuva`), Os dados (`confianca`, `glossario`, `satelite_chao`, `harmonizacao`), com selos, sem rolar de lado e sem erro | painel.html |
| P2 | O verde do painel vai a `#/<cod>/2`; o cartão do mapa tem 3 números-chave (`numerosChave`) | painel.html |
| F1 | Do globo ao plano em 2 toques | `percorrer_fluxo.py` |
| F2 | Percurso 2 → 3 → 4 → 5 com o verde certo | `percorrer_fluxo.py` |
| F3 | Seu Antônio: o hash tem só `hoje=milho:34,feijao:33,mandioca:33`, `maniva=plantada`, `ha=3`, `terra=barro`, `baixio=pouco` | `percorrer_fluxo.py` |
| F4 | 40 × 100 m: `ha=0.4&area_un=medida:100x40&larg=40&comp=100`; o desenho, o terreno e o Relatório mostram 40 × 100 | `percorrer_fluxo.py` |
| F5 | O ideal com Água: `plano=ideal&prioridade=garantir`; Quanto rende marca o ideal; o Relatório diz "O ideal" e "Guardar água" | `percorrer_fluxo.py` |
| F6–F7 | PDF A4 do Relatório com até 4 páginas (Seu Antônio com Água; Quixadá "Um pouco de cada", o caso mais pesado) | `msedge --print-to-pdf` |

### Resultado (rodada final do integrador)

Rodada de 15/11/2026, 10:24–10:34, com `aceite_fluxo.py --prints`: **tudo ok** (saída 0). Resultado em
`E:/campeonato-nasa/tmp/fluxo2/final/aceite.json` e prints em `E:/campeonato-nasa/tmp/fluxo2/final/`.

| Parte | Resultado |
|---|---|
| Node | N1 ok (16 linhas iguais ao HEAD; `calculo.js` sem mudança) · N2 143.084 conferências, 0 falha · N3 21.413, 0 falha · N4 19.258 em 168 casos, 0 falha |
| Telas (35 = 5 × 7 municípios) | 0 falha. Sua roça 1.522–1.661 px e 160–184 palavras · Plano, seu jeito, 2.699–2.828 px e 323–356 · Plano, ideal, 2.975–3.131 px e 353–415 · Quanto rende 1.925–2.163 px e 213–291 · Relatório 3.789–5.627 px, 5–16 tarefas. 1 verde em todas; "seu olho" 1–2; 0 erro no console; nada rolando de lado |
| Toques | C1–C13 ok. Quixadá padrão: R$ 2.480 · 2.550 · 3.980. Prioridades: 4 desenhos e 4 tabelas diferentes. Seu Antônio com Água: Plano e Quanto rende com os mesmos R$ 703 / 949 / 903 (ano normal), 345 / 511 / 452 (2027) e 1 em 10; Relatório "O ideal · Guardar água" com 44 datas, 0 fora da agenda |
| Painel | P1 ok (as 6 peças do antigo "Do espaço" nas 3 abas, 7–16 selos por aba, 0 erro) · P2 ok (verde → `#/2311306/2`; cartão: milho quebra 6 em 10, chuva 590 mm, solo normal) |
| Percurso e PDF | F1–F5 ok (o globo abriu de verdade e levou ao plano em 2 toques) · F6 e F7: PDF A4 com 4 páginas cada |
