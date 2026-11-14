# Revisão do protótipo QUADRA por 10 agentes

Consolidado em 14/11/2026, 15:26. São 10 revisões independentes, com 124 problemas relatados. Depois de juntar as repetições, ficaram 83 itens. Para cada crítico e alto, tentei refutar o achado rodando o código, a API ou a fonte. Dos 59 médios e baixos, conferi 55. No total, 79 dos 83 itens foram conferidos.

Os scripts e as saídas do consolidador estão em `E:/campeonato-nasa/tmp/revisao_prototipo/consolidador/`:

| Script | O que confere |
|---|---|
| c01 | portarias em PDF |
| c02 | ZARC |
| c03 | motor real com o CACHE desviado |
| c04 | corrida no cache |
| c05 | Tmax do POWER |
| c06 | classes do GAEZ |
| c07 | amostragem |
| c08 | safras e início da chuva |

Cada script tem a sua saída em `.saida.txt`.

## Resumo

- **A mecânica central está certa.**
  - O motor lê o pixel certo do GAEZ.
  - Recalculei a tábua do ZARC a partir do arquivo bruto: ela bate com a página em 1.656 de 1.656 pares.
  - Reproduzi a fórmula dos análogos, o +36% de Quixadá, o ONI +2,46 e o ranking do SMAP.
  - O servidor não serve arquivos de fora de `static/` e escapa o HTML.
- **Dois dados de base estão errados.**
  - A Tmax e a Tmin da climatologia do POWER são extremos do mês, não médias. Em janeiro, em Quixadá, a climatologia dá 39,3 °C e a média diária dá 34,9 °C.
  - O ZARC do caupi e da mamona soma grupos de ciclo sem cultivar indicada. Em Quixadá, a janela de 20% do caupi começa em 11/03, e não em 21/02.
- **Faltam fundamentos.**
  - As portarias plurianuais do ZARC (mandioca, milheto, palma e gergelim) não entram.
  - Os limiares de classe do GAEZ não são os da camada oficial de classes.
  - A página não mostra a faixa por solo que a regra decidida pede.
- **A apresentação fere regras escritas pelo próprio projeto:**
  - números de cartões T2/T3 e de efeitos não significativos aparecem em negrito;
  - um "+8%" aparece ao lado de uma "regra negativa";
  - o interruptor depende do portão de 30/abr;
  - a chuva da estação seca aparece em "% do normal";
  - o alerta do CE vale para os 9 estados;
  - aparece o rótulo "Sobral — Primo 2023".
- **O software cai com consultas simultâneas.**
  - O cache JSON não tem trava: no meu teste, 107 a 120 de 240 chamadas deram `JSONDecodeError`.
  - A UF vem de uma malha grosseira: a orla de Fortaleza sai "fora do Nordeste" e a sede de Penaforte sai como PE.
- **Veredito: ainda não está implementado corretamente sobre uma base sólida.**
  - Nenhum dos 24 críticos e altos foi refutado.
  - Uns 15 deles se corrigem com mudanças pequenas antes da demo.
  - Os de base (Tmax, limiares do GAEZ, portarias plurianuais, janela por solo) exigem regerar dados e números canônicos.

## Placar

**Por severidade (depois de juntar):**

| Severidade | Itens | Confirmados | dos quais com ressalva | Refutados | Não conferidos |
|---|---|---|---|---|---|
| Crítico | 5 | 5 | 1 | 0 | 0 |
| Alto | 19 | 19 | 4 | 0 | 0 |
| Médio | 35 | 32 | 3 | 0 | 3 |
| Baixo | 24 | 23 | 0 | 0 | 1 |
| **Total** | **83** | **79** | **8** | **0** | **4** |

**Por área (problemas relatados → onde foram parar):**

| Área | Relatados | Críticos / altos relatados | Itens consolidados | Não conferidos |
|---|---|---|---|---|
| GAEZ | 9 | 0 / 2 | C1, A3, A4, M1, M2, M9, M10, B1, B2 | 0 |
| ZARC | 12 | 2 / 3 | C3, C5, A1, A5, A6, A7, M3–M7, B3, B4 | 0 |
| Localização e malhas | 10 | 0 / 2 | A4, A5, M7–M11, B5–B7 | 0 |
| POWER e análogos | 9 | 1 / 2 | C1, C2, A2, M12–M16, M19 | 2 |
| Catálogo e evidência | 11 | 0 / 4 | C4, A8, A9, A18, M17–M19, B8–B11 | 0 |
| Plano de rotação | 13 | 0 / 3 | C4, A8–A13, M2, M18, M20–M23, B12 | 0 |
| Este ano | 15 | 0 / 4 | A6, A10, A13, A14, A17, M23–M28, M35, B7, B13–B15 | 0 |
| Proveniência | 14 | 2 / 3 | C1, C2, A4, A6, A15, A16, M24, M26, M29–M31, B7, B11, B13, B16–B19 | 0 |
| Robustez | 12 | 1 / 1 | C1, A12, A19, M9–M11, M24, M32, B5, B20–B23 | 2 |
| Solidez dos textos | 19 | 1 / 8 | C4, A6–A14, A17, A18, M2, M18, M19, M22, M23, M30, M31, M33–M35, B24 | 0 |
| **Total** | **124** | **7 / 32** | 83 itens | 4 |

## Problemas confirmados: críticos e altos

| # | Sev. | Área(s) | Título | Arquivo:linha | Evidência (o que rodei) | Correção sugerida | Veredito |
|---|---|---|---|---|---|---|---|
| C1 | crítico | Robustez, Proveniência, GAEZ, POWER | O cache JSON não tem trava nem gravação atômica: consultas simultâneas dão HTTP 500 e perdem entradas | protótipo/motor.py:124-126, 167-171, 176-181; protótipo/app.py:65 | c04: motor real com o CACHE desviado, 40 threads × 6 pontos novos, 3 rodadas. Deram `JSONDecodeError` 107, 120 e 107 de 240 chamadas. O arquivo ficou com 239 chaves, contra 473 esperadas. O revisor de Robustez viu o arquivo ficar inválido de vez ("Extra data") com só 2 pedidos simultâneos. | Cache em dicionário na memória com `threading.Lock`; gravar em `.tmp` e trocar com `os.replace`; tratar `JSONDecodeError` como cache vazio. Ou tirar o cache do GAEZ (0,08 s por ponto). | Confirmado |
| C2 | crítico | POWER, Proveniência | Tmax e Tmin da assinatura são extremos do mês, não médias. O chip mostra "Tmax na estação úmida 39,2 °C" em Quixadá, e a ET0 sai inflada | scripts/analogos_climaticos_artigos.py:81-88; protótipo/static/app.js:87 | c05: API do POWER em Quixadá (−4,9113; −39,0277).<br>• T2M_MAX de janeiro na climatologia: 39,30 °C, igual ao recorde da série diária 2001–2025 (39,30 °C). A média diária é 34,94 °C.<br>• Março: 40,18 contra 32,13 °C.<br>• T2M_MIN de janeiro: 20,04 °C (o mínimo absoluto). A média diária é 23,65 °C.<br>• Harare, janeiro: 35,94 contra 27,11 °C. | Usar a média mensal de T2M_MAX e T2M_MIN da série diária 2001–2025 (ou T2M ± T2M_RANGE/2). Regerar as 4 tabelas de assinatura e o cache_power.json. Antes da demo, tirar o chip ou chamá-lo de "máxima recorde do mês". | Confirmado |
| C3 | crítico | ZARC | A janela do caupi e da mamona soma grupos de ciclo sem cultivar indicada na portaria | scripts/gaez_zarc_municipio.py:81-84 e 103-105 (lido em protótipo/motor.py:208) | • No dicionário da tábua, Cod_Ciclo 20 = Grupo I.<br>• Port. SPA/MAPA 121/2026 (caupi, CE), item 4.1.1: "nenhuma das cultivares... nos Grupos II e III".<br>• Port. 143/2026 (mamona): "nenhuma... no Grupo I".<br>• c02, caupi em Quixadá: com todos os ciclos, 21/02–11/04 a 20% e 11/02–11/04 a ≤ 30%. Só com o Grupo I, 11/03–11/04 e 01/03–11/04.<br>• A janela muda em 183 de 184 municípios no caupi e em 184 de 184 na mamona. | Filtrar os ciclos que têm cultivar: `{"Feijão Caupi": [20], "Sorgo Forrageiro": [20], "Mamona": [21, 22, 24]}`, com a portaria como fonte. Regerar ceara_2026-2027.csv. Corrigir a v3 9.7 (l. 1219: "caupi 20% em 9 de 9 solos × ciclos"). | Confirmado |
| C4 | crítico | Catálogo, Textos, Plano | Regras negativas e de "sem bônus" saem com ganho positivo em negrito. O 0,92 → 0,49, que vem da simulação do balde, aparece com o DOI de da Luz 2023 | protótipo/motor.py:63-65, 261-281, 320-327; protótipo/static/app.js:167, 179 | c03, em Quixadá:<br>• Regra da luz: "+8% · C·T0". O cartão diz "T0 para área irrigada; NÃO no sequeiro" (milho irrigado, 370/322 mm).<br>• Melo: "+8%". O cartão diz "letras bAB e bAB, ns" e "não um ganho".<br>• Pacheco 2013: "+3%" (mesma letra).<br>• O 0,919 → 0,489 está em conselho/analises/v3_agronomo_cobertura_janelas.saida.txt:81-83. | Criar `mostrar_efeito=False` para luz, melo, pacheco13 e ne_s0. Escrever "sem bônus de grão (ns)". Na luz: "no balde do QUADRA (simulação, grau C)...; o ensaio de da Luz foi irrigado". | Confirmado. Subi de alto para crítico: o número contradiz a regra que acompanha. |
| C5 | crítico | ZARC | O plano diz "maniva de fev a abr", mas abril fica fora do ZARC da mandioca (Port. 11/2020) na maior parte do CE | protótipo/motor.py:302, 308, 311 | • PDF da Port. 11/2020 (mandioca, CE), linha de Quixadá: "5 a 6 \| 4 + 7 \| 3 \| 4 a 7 \| 3 + 8 \| … 8 \| 9 + 3". O último período é o 9 (21–31/mar), e abril (períodos 10–12) não aparece.<br>• Na tabela do revisor, abril fica fora em 159 de 183 municípios. | Agora: "maniva de fev até o fim da janela ZARC da mandioca (em geral março)". Depois, uma tábua complementar da Port. 11/2020. | Confirmado com ressalva: não conferi no SISZARC se a portaria vale em 2026/27. Ela "entra em vigor na data de publicação", sem prazo de safra. |
| A1 | alto | ZARC | "Sem ZARC no CE" é falso para mandioca, milheto, palma e gergelim | protótipo/motor.py:38, 43-44, 210-212; scripts/gaez_zarc_municipio.py:38; proposta/estrutura_gaez_zarc.md:62 | • Li os PDFs de quatro portarias do CE: 11/2020 (mandioca), 330/2020 (milheto), 284/2019 (palma) e 198/2023 (gergelim, em vigor desde 01/06/2023).<br>• c02: nenhuma dessas culturas está na tábua aberta 2026/27, que tem 12 nomes de cultura no sequeiro. | Criar uma tábua complementar com essas portarias e dar a essas culturas uma entrada do ZARC no cardápio (o campo `z`). Trocar "sem ZARC no CE" por "ZARC em portaria plurianual". | Confirmado com ressalva (vigência, como em C5) |
| A2 | alto | POWER | Com a Tmax média, os análogos e os números canônicos mudam: Harare deixa de ser análogo do sertão e a RMF deixa de ser o ponto fraco | protótipo/motor.py:185-191; proposta/PROPOSTA_FINAL_v3.md:35-37, 382, 968-969; proposta/estrutura_gaez_zarc.md:43 | • c05 confirma a causa. Em janeiro, Harare tem recorde de 35,9 °C e média de 27,1 °C; Quixadá, 39,3 e 34,9 °C. A diferença entre os dois lugares passa de 3,4 para 7,8 °C.<br>• Os números vêm do recálculo do revisor (municipios_corrigido.saida.txt), que li mas não refiz: melhor w ≥ 0,6 vai de 154 para 182 municípios; Harare como melhor análogo, de 53 para 13; Quixadá, de +36% para +28%. | Depois de C2, rodar de novo secoes_analogos e secoes_prototipo/05. Atualizar a v3 e a estrutura. | Confirmado com ressalva |
| A3 | alto | GAEZ | Os limiares de classe 75/63/50/35/20/10 não são os da camada oficial de classes do GAEZ v4 (85/70/55/40/25/10) | protótipo/motor.py:132; scripts/gaez_zarc_municipio.py:8, 42; proposta/estrutura_gaez_zarc.md:34; notebooks/secoes_prototipo/01_gaez.py:12-13 | • c06 cruzou siLr_mze (classes da FAO) com sxLr_mze (índice), na mesma grade. As faixas são: classe 1 = 8500–10000; 2 = 7000–8500; 3 = 5500–7000; 4 = 4000–5500; 5 = 2500–4000; 6 = 1000–2500.<br>• O 75/63/50/35 só aparece no texto da legenda do portal (legendas_gaez.json).<br>• O rótulo do motor difere da classe v4 em 26% dos pixels do mundo com SI > 0. | Usar 85/70/55/40/25/10 (ou amostrar siLr e siHr). Registrar o corte APTA (35 ou 40) como decisão. Regerar a tábua. | Confirmado com ressalva: duas fontes da FAO discordam. O corte > 35 é escolha do projeto, mas a frase "legenda oficial" não se sustenta. |
| A4 | alto | GAEZ, Localização, Proveniência | A chave do cache do GAEZ, com 0,01°, devolve o valor de outro pixel | protótipo/motor.py:177 | c03: A (−5,04; −39,004) e B (−5,04; −38,996) têm a mesma chave "-5.04,-39.00". Depois de consultar A, B devolve milho 41 com insumo alto e 28 com insumo baixo. O raster em B dá 66 e 37. | Usar o pixel como chave (floor((90−lat)·12), floor((lon+180)·12)) ou tirar o cache. Apagar o cache_gaez.json atual: o revisor de Proveniência achou 18 de 233 chaves trocadas. | Confirmado |
| A5 | alto | Localização, ZARC | A UF vem de uma malha grosseira. Na costa, o município do CE fica sem UF (alerta apagado e "fora do Nordeste"); na divisa, ele recebe a UF vizinha | protótipo/motor.py:155 | c03, com motor.localizar:<br>• Orla de Fortaleza (−3,72; −38,51), Jericoacoara e Cumbuco: uf None, com o código do município do CE.<br>• Sede de Penaforte (−7,829; −39,071): PE.<br>• Crateús (−5,425; −40,935): PI. | Quando houver município, usar `out["uf"] = UF[cod[:2]]`. Fora do CE, usar a malha de municípios do NE. | Confirmado |
| A6 | alto | ZARC, Este ano, Proveniência, Textos | O aviso "nenhuma cultura é indicada antes de X" conta o risco de 40%, mas no cardápio "indicada" significa 20% | protótipo/motor.py:239; protótipo/static/app.js:114-115 | c02, Quixadá: em 21/01 só há risco de 40% (algodão, amendoim, caupi e sorgo granífero). O 1º decêndio com ≤ 30% é 01/02, e o 1º com 20% é 11/02. | Mostrar as duas datas: "zoneada (até 40%) desde 21/01; risco de 20% só a partir de 11/02". Contar só as culturas do cardápio. | Confirmado |
| A7 | alto | ZARC, Textos | A página mostra só a união de solos e ciclos; a regra decidida pede a faixa do solo mais restritivo ao mais permissivo | protótipo/motor.py:208; protótipo/static/app.js:137-138; proposta/estrutura_gaez_zarc.md:140-141 | c02, milho em Quixadá:<br>• ≤ 30% de 11/02 a 01/03 só nos solos 15 e 16 do Grupo I;<br>• no solo 14, só em 21/02;<br>• nos solos 12 e 13, só 40%;<br>• o solo 11 (AD1) não é zoneado.<br>A página mostra "11/02–01/03 (≤ 30%)" sem dizer o solo. | Calcular a janela por solo em tabela(). Mostrar, por exemplo, "em AD5–AD6; fora em AD1", com um seletor de solo. | Confirmado |
| A8 | alto | Catálogo, Plano, Textos | Cartões T2/T3 saem com número em negrito nas regras, nos princípios e em "clima parecido" | protótipo/motor.py:274-281, 371-372; protótipo/static/app.js:167, 179 | c03, Quixadá:<br>• Em "perto": +140% (+127 a +167) C·T3, +12% C·T3, −3% C·T3, −2% C·T2 e +3% C·T2.<br>• Nos princípios: +31% C·T2 e −32% C·T2. O intervalo do −32% é de energia da sequência, não de rendimento.<br>• A convenção do catálogo diz: "numero so com T0 ou T1; T2 so direcao". | Em cartao(), devolver efeito = None para T2/T3, com o rótulo "só direção" ou "não transfere". Mostrar a variável junto do número. | Confirmado |
| A9 | alto | Catálogo, Plano, Textos | Onde o milho é "com risco" (30 municípios, Quixadá entre eles), a faixa 2 de 2028 vira sorgo granífero. A página usa o +24% e o +36% do milho e diverge da tabela 6.4 | protótipo/motor.py:290, 321, 391 | • c03: em Quixadá, a faixa 2 de 2028 diz "Sorgo granífero · ano bom: Sorgo granífero depois da leguminosa".<br>• 30 municípios têm o milho "com risco".<br>• v3:915 diz "Sorgo forrageiro; em ano bom, milho".<br>• v3:1213 diz "sorgo na metade inferior da faixa". | Seguir a 6.4: sorgo forrageiro e, em ano bom, milho no solo que guarda água. Ou mostrar a faixa do sorgo (+2% a +24%). Escrever "contra cereal solteiro". | Confirmado |
| A10 | alto | Plano, Este ano, Textos | O interruptor faz a faixa 2 de 2028 depender do portão de 30/abr, onde a proposta diz que só cabe salvar | protótipo/motor.py:338-340 | • API: "se o portão de 30/abr acender, a faixa 2 de 2028 vai para forragem ou pousio".<br>• v3:117 e :945: "em 30/abr só cabe salvar".<br>• v3:924: "A escolha é feita no plantio, com o oceano (P1) e a chuva desde 1/fev". | "Em 2028, a faixa 2 decide no plantio (P1 e chuva desde 1/fev). Em 30/abr só cabe salvar." | Confirmado |
| A11 | alto | Plano, Textos | plano() não se adapta quando falta leguminosa ou mandioca: o plano fica todo em pousio e os textos citam culturas que não estão lá | protótipo/motor.py:287-315 | c03:<br>• Picos-PI (−7,08; −41,47): as 15 células ficam em pousio, com "precoce; metade guardada até ~10/mar" e "+ leguminosa em revezamento".<br>• Limoeiro do Norte: "Feijão-caupi · precoce, na terra que foi mandioca", sem mandioca no plano.<br>• A mandioca fica "fora" em 20 municípios do CE. | Montar o texto a partir da cultura do ano anterior. Sem leguminosa, avisar "sem rotação possível com o cardápio". Sem mandioca, tirar o "tampão" do por_que e avisar que falta o tampão. | Confirmado |
| A12 | alto | Plano, Textos, Robustez | Fora do NE, o plano usa as bordas, o número e as regras do sertão: palma + gliricídia em Iowa e em Saskatoon | protótipo/motor.py:316-318, 391; protótipo/static/app.js:155-157 | • c03: Iowa e Saskatoon recebem "Palma + gliricídia · em nível" nos 3 anos.<br>• A página diz "o motor usa +24%", que vem do cartão de "sequeiro quente-seco".<br>• O aviso diz "as culturas são do lugar (GAEZ)". | Pôr as bordas de palma + gliricídia só no NE; fora, "perene local, a definir". Usar o cartão do sertão só no estrato T1. Corrigir o aviso. | Confirmado |
| A13 | alto | Este ano, Textos, Plano | O alerta do El Niño e o calendário do CE valem nos 9 estados do NE, inclusive onde os análogos não mostram sinal | protótipo/motor.py:353, 388 | • Código: `alerta = oni >= 1.5 and uf is not None`; `modelo_ne = uf is None`.<br>• perspectiva_uf.csv: PE, AL, SE e BA têm 2 de 4 no tercil inferior.<br>• c03: Recife e o Oeste da Bahia saem com alerta True, modelo_ne False e "metade guardada até ~10/mar". | Alerta pleno só no CE (ou nas UF com 3 de 4); nas outras, "sinal fraco, não calibrado". Mostrar o aviso das datas do CE em todo ponto sem município do CE. | Confirmado |
| A14 | alto | Este ano, Textos | A chuva da estação seca aparece em "% do normal" (CE "40%"), contra o fundamento, que manda usar o percentil (39 = normal) | protótipo/motor.py:365 | • c03: "Chuva de ago a nov/2026 em CE: 6 mm (40% do normal; é a estação seca)".<br>• estado_atual_uf.csv dá percentil 39.<br>• pesquisa/el_nino_2026_nordeste.md:37: "use o percentil: o '% do normal' engana". | "6 mm, percentil 39 (normal para a época). A chuva da estação seca não prevê a quadra." | Confirmado |
| A15 | alto | Proveniência | O valor atual da chuva (IMERG Late/Early) é comparado com uma normal feita de outro produto (IMERG Final, via POWER) | scripts/el_nino_2026.py:112-132; protótipo/motor.py:363-365 | • Código: o valor atual soma Late e Early; a normal vem de imerg_ne_mensal (POWER).<br>• CMR: o último grânulo do Final V07 é de 30/09/2025.<br>• O fator Late/Final de 2 a 3 vezes (ago–set/2025) é do revisor, medido por OPeNDAP. Não refiz essa medida. | Fazer a normal com o mesmo produto (GPM_3IMERGDL, desde 2000). Ou mostrar só os mm, com o rótulo "preliminar". | Confirmado com ressalva (magnitude não reproduzida) |
| A16 | alto | Proveniência | Os documentos de base dizem "IMERG Final até 14/09/2026", mas o Final V07 termina em 30/09/2025 | pesquisa/bases_ibge_e_complementares.md:26, 111, 155; pesquisa/viabilidade_artigos_nordeste.md:294, 370 | • CMR (GPM_3IMERGDF V07): último grânulo 20250930 V07B. O Late vai até 13/11/2026.<br>• O MANIFESTO do IMERG registra "Final ate 2025-09". | Corrigir para "Final até 30/09/2025; Late depois". Marcar 2026 como preliminar no início da chuva. | Confirmado |
| A17 | alto | Este ano, Textos | "24 dias depois do típico" aparece em negrito em Quixadá com n = 3, e não se separa do acaso | protótipo/motor.py:226-230; protótipo/static/app.js:106-111 | • c03: permutação exata em Quixadá, com 2.300 triplas de anos sem El Niño forte. 14% delas dão diferença ≥ 24 dias.<br>• v3:1218 proíbe dizer "o El Niño atrasa o início". | Mostrar os 3 anos (2010: 19/03; 2016: 06/01; 2024: 12/02) e a frase "com 3 anos, não se separa do acaso". Tirar o negrito. | Confirmado |
| A18 | alto | Textos, Catálogo, Proveniência | A página usa rótulos que a errata da v3 proíbe: "Sobral-CE — Primo 2023" e "Franke: efeito da leguminosa MENOR/MAIOR" | scripts/analogos_climaticos_artigos.py:29, 32-37 (gravados em dados/analogos_artigos/assinaturas.csv); protótipo/static/app.js:90 | • c03: Juazeiro (w 0,86) e Fortaleza (w 0,33) mostram "Sobral-CE — Primo 2023".<br>• O Sahel mostra "Franke 2017: efeito da leguminosa MENOR".<br>• v3:59 e :1239: o Primo é simulação (grau D).<br>• v3:31: "Sai 'efeito menor na zona árida'". | Sobral: "Sacramento 2013 (carbono medido; C)". Franke sem adjetivo e como "Franke 2018". Regerar assinaturas.csv. | Confirmado |
| A19 | alto | Robustez | Corrida no front-end: uma resposta lenta sobrescreve a consulta mais nova | protótipo/static/app.js:34-55 | • Pelo código, consultar() não numera os pedidos nem cancela o anterior. O `finally` esconde o "Consultando…" na primeira resposta.<br>• Um ponto fora do CE leva cerca de 1 s (POWER ao vivo); um ponto do CE, 0,01–0,15 s.<br>• O revisor reproduziu no Edge: o marcador ficou em Quixadá e o painel mostrou AL. | `let seq`; em cada chamada, `const meu = ++seq`; depois do `await`, `if (meu !== seq) return`. Ou usar AbortController. | Confirmado pelo código; a reprodução no navegador é do revisor |

## Problemas confirmados: médios

| # | Área(s) | Título | Arquivo:linha | Evidência | Correção | Veredito |
|---|---|---|---|---|---|---|
| M1 | GAEZ | O motor arredonda antes de classificar e de cortar | scripts/gaez_zarc_municipio.py:71; protótipo/motor.py:132, 211 | c03: na mandioca de Palmácia, o raw é 3536 (SI 35,36). O motor arredonda para 35 e a cultura fica "fora". | Usar round(v/100, 1) e arredondar só na tela | Confirmado |
| M2 | GAEZ, Plano, Textos | Fora do CE, "apta com insumo alto" entra no cardápio e no plano sem registro na regra decidida | protótipo/motor.py:213-216, 285, 335-337; protótipo/static/app.js:128-131 | c03, Oeste da Bahia: 5 culturas com SI 32 saem "apta com insumo alto", e o milho entra no plano. A v3 (l. 21 e 40) só prevê insumo alto nos perímetros irrigados. | Registrar a regra ou mostrar o insumo alto só como rótulo, fora do plano | Confirmado |
| M3 | ZARC | Cultura "com risco" só a 40% aparece sem janela, e o plano põe esse milho no baixio | protótipo/static/app.js:137-138; protótipo/motor.py:292, 333-334 | c02: em Icapuí, o milho não tem janela a 20% nem a ≤ 30%; a ≤ 40%, de 11/02 a 01/03 | Mostrar a janela de 40%; exigir ≤ 30% para o baixio | Confirmado |
| M4 | ZARC | A data final da janela é o início do último decêndio | scripts/gaez_zarc_municipio.py:45-61 | janelas() usa data_dec(ant). O caupi "21/02–11/04" vai, na verdade, até 20/04. | Usar o último dia do decêndio na ponta final | Confirmado |
| M5 | ZARC | A janela da mamona junta o "Clima Semiárido" (baixa produtividade) com a mamona tradicional | scripts/gaez_zarc_municipio.py:81 | c02: o código …011 (Semiárido) está em 89 municípios e o …041 em 184. Port. 143/2026, item 1.13. | Separar as duas mamonas | Confirmado |
| M6 | ZARC | "A janela do milho encolheu em 71%" vem da troca do esquema de solo | notebooks/secoes_prototipo/02_zarc.py:109-112; 90_sintese.py:7 | c02 e c08: milho e girassol passaram das classes de solo 1–3 para 11–16. As outras 9 culturas da tábua são idênticas célula a célula. | Reescrever a leitura | Confirmado |
| M7 | Localização, ZARC | Na divisa, há pontos "CE sem município": ficam sem ZARC e com o texto "ZARC só no Brasil" | protótipo/motor.py:154, 213-216 | c03: (−7,34; −39,92) e o vértice comum de Quixadá e Ibaretama dão {uf: CE}, sem município | Usar a malha de municípios do NE ou o município mais próximo (até ~1 km) | Confirmado |
| M8 | Localização | A malha simplificada do mapa não é a mesma que o motor usa | protótipo/motor.py:400 | c07: em (−7,8416; −38,9673), a malha original dá Penaforte e a simplificada, Jati. Outro caso: Ibaretama na original, Morada Nova na simplificada. | Servir a malha original (313 KB) ou simplificar preservando a topologia | Confirmado |
| M9 | Localização, Robustez, GAEZ | Um clique numa cópia do mundo (longitude fora de ±180) dá erro | protótipo/static/app.js:55; protótipo/app.py:47 | c07: o GAEZ devolve None em (260; 40) e 78 em (−100; 40). O código não usa wrap(). | `e.latlng.wrap()`; normalizar a longitude no servidor | Confirmado com ressalva (o erro 422 do POWER foi reproduzido só pelos revisores) |
| M10 | Localização, Robustez, GAEZ | Um ponto no mar recebe cardápio e plano, e o GAEZ sem dado vira "pouco apta" | protótipo/motor.py:214, 284-341, 345 | c03, Atlântico (−10; −25): aptidão None e "pouco apta"; plano todo em pousio, com palma + gliricídia nas bordas | Mostrar "sem dado" quando os dois insumos forem None; não montar plano fora de terra | Confirmado |
| M11 | Robustez, Localização | /api/local não valida a entrada | protótipo/app.py:45-51 | curl lat=abc no servidor 8765: HTTP 500 com {"erro": "ValueError: could not convert string to float: 'abc'"} | Responder 400 com mensagem curta; exigir isfinite e a faixa da latitude | Confirmado |
| M12 | POWER | No CE, a assinatura do município (do ponto interno) substitui a do ponto clicado | protótipo/motor.py:163-166 | c07: Fortaleza no ponto (CE12) tem Tmax úmida de 31,5 °C; o município, 35,0 °C. c03: o atalho de Fortaleza mostra w 0,33, "parecido". | Usar a célula do clique ou escrever "clima do município" | Confirmado |
| M13 | POWER | A chave do cache do POWER (0,1°) pode cair na célula vizinha | protótipo/motor.py:168-170 | — | — | Não conferido |
| M14 | POWER | O pré-cálculo do CE ignora a grade de radiação de 1° | scripts/preparar_analogos_aprofundado.py:40 | — | — | Não conferido |
| M15 | POWER | O freio "rebaixa o grau quando w < 0,3" não foi implementado | protótipo/motor.py:274-281 | c03: em Recife, w 0,15 e "nenhum estudo parecido", com os 11 graus iguais aos de Quixadá. v3:382. | Rebaixar A→B→C→D ou tirar a frase da proposta | Confirmado |
| M16 | POWER | A página mostra w = 0,60 com o texto "parecido" | protótipo/motor.py:384 | c03, Crateús (−5,18; −40,67): {w 0,6, "estudos de clima parecido"} | Classificar pelo valor arredondado | Confirmado |
| M17 | Catálogo | Ensaios irrigados entram em "clima parecido" sem aviso, e o escopo e a variável somem | protótipo/static/app.js:174-181; protótipo/motor.py:274-281 | c03 e c07: em Quixadá aparece nascimento_cobertura_caupi_nulo (Crato, "caupi irrigado 369,4 mm"), com w 0,76 | Marcar "[irrigado]"; mostrar o escopo e a variável | Confirmado |
| M18 | Catálogo, Plano, Textos | O +24% aparece sem "no ano colhido" e sem "contra cereal solteiro" | protótipo/motor.py:321; protótipo/static/app.js:165-168 | c03: o princípio diz "leguminosa num ano e cereal no seguinte", com "+24% (+2 a +49)". v3:1213. | Pôr os dois qualificadores na frase | Confirmado |
| M19 | POWER, Catálogo, Textos | O "ponderado pelo clima" do Franke sai com soma dos pesos perto de 0 | protótipo/motor.py:378; protótipo/static/app.js:186 | c03: Paracuru, soma 0,04 → +41%; Recife, 0,00 → +27%; Atlântico, 0,00 → +42% | Devolver None quando a soma for < 0,3 | Confirmado. Rebaixei de alto para médio, porque a página mostra a soma e "só como sensibilidade". |
| M20 | Plano | O giro da 6.4 tem 4 fases para 3 faixas | proposta/PROPOSTA_FINAL_v3.md:920 | c03, Quixadá: em 2028, as faixas 1–3 são mandioca, sorgo granífero e mandioca (sem leguminosa). Em 2029, caupi, mandioca e mandioca (sem forragem). | Usar 4 faixas ou reescrever a frase | Confirmado com ressalva: o baixio tem caupi em revezamento todos os anos |
| M21 | Plano | O guandu entra como leguminosa "precoce" e em revezamento | protótipo/motor.py:287 | c03, em PE (−8,587; −37,505): "Guandu · precoce; metade guardada" e "Milheto + Guandu em revezamento". O catálogo (md:405) diz "só guandu de ciclo completo ou perene". | Tirar o guandu das anuais e pô-lo em faixa perene | Confirmado |
| M22 | Plano, Textos | "Não trocar sorgo contínuo por milho-sorgo" aparece como veto | protótipo/motor.py:324 | v3:1215 lista "milho-sorgo vetado" entre o que não dizer. O cartão diz "alerta de direção, não veto numérico". | "Alerta (C·T2, n = 10, só direção)" | Confirmado |
| M23 | Plano, Este ano, Textos | Fora do NE, a página diz "Sem alerta", mas o El Niño não foi avaliado ali | protótipo/motor.py:338-340, 353 | c03: Iowa e Harare dizem "Sem alerta", e a mesma resposta diz "só calibrou o Nordeste" | Criar um terceiro estado: "não avaliado aqui" | Confirmado |
| M24 | Este ano, Proveniência, Robustez, Textos | "ONI de set/2026: +2.46" é o trimestre ASO e está com ponto decimal | protótipo/motor.py:355 | c03 mostra o texto. A 9.7 usa "ONI ASO/2026 = +2,46". | "ONI de ago–out/2026 (ASO): +2,46" | Confirmado |
| M25 | Este ano | O início compara o El Niño com todos os anos, e o "dia 6 contra 18" da v3 não se reproduz | protótipo/motor.py:227; proposta/PROPOSTA_FINAL_v3.md:38, 249, 899, 1218 | c08: mediana das medianas anuais, dia 6 contra dia 15 (demais anos); municipal, 6 contra 17. Nunca dá 18. | Comparar com os "demais anos"; corrigir o número | Confirmado |
| M26 | Este ano, Proveniência | Se a última data do SMAP for 29/02, a montagem falha e a página fica em "carregando" | protótipo/motor.py:111 | c07: pd.Timestamp(2015, 2, 29) dá "day is out of range for month" | fim − DateOffset(years=…), com try/except | Confirmado |
| M27 | Este ano | O cache do SMAP só é invalidado pela data final | protótipo/motor.py:104-108 | O código compara só attrs["fim"]. | Guardar também o mtime e o tamanho da fonte | Confirmado pelo código |
| M28 | Este ano | Um ONI negativo sai como "El Niño fraco/neutro" | protótipo/motor.py:355 | Pelo código, oni < 1 dá "fraco/neutro", inclusive −1,6. | Rótulos com sinal (La Niña) | Confirmado pelo código |
| M29 | Proveniência | A página não diz a data nem o período das bases | protótipo/motor.py:355, 365; protótipo/static/app.js:84-92, 99-101 | c03: os textos não trazem a data final da chuva (13/11) nem o produto (preliminar); os chips não trazem o período (POWER 2001–2025; GAEZ 1981–2010). | Datar cada base | Confirmado |
| M30 | Proveniência, Textos | O GAEZ do ponto clicado não é o GAEZ municipal canônico | protótipo/motor.py:349; protótipo/static/index.html:20 | c03 e c07: pelo atalho de Quixadá, mandioca 63 e milho 53; na tábua (ponto interno), 66 e 56. A 9.7 diz "Mandioca: GAEZ 66". | Pôr o atalho no ponto interno ou rotular "no ponto clicado" | Confirmado |
| M31 | Proveniência, Textos | O rodapé credita o MODIS, que não é usado; faltam IIASA, IBGE e licenças | protótipo/static/index.html:48-51 | c07: o rodapé diz "NASA POWER, GPM IMERG V07, SMAP L4, MODIS", e o motor.py não lê nenhum dado MODIS. | Tirar o MODIS; pôr os créditos e as licenças | Confirmado com ressalva (as licenças não foram conferidas) |
| M32 | Robustez | A tabela do cardápio estoura a largura de 390 px | protótipo/static/estilo.css:41, 45 | — | — | Não conferido (sem navegador) |
| M33 | Textos | As justificativas das faixas afirmam causa sem número ("protege", "rende mais"), e "sem mandioca no chão hoje" aparece como fato | protótipo/motor.py:301, 305, 332 | c03: textos de Quixadá | Pôr os números e escrever "se" | Confirmado |
| M34 | Textos | O amendoim aparece como "quebra nematoide", regra que o catálogo rejeitou | protótipo/motor.py:39 | c07: md:204 diz "resultados contraditórios"; md:335, "nenhuma leguminosa é quebra garantida". | "Nematoide só com diagnóstico de solo (C)" | Confirmado |
| M35 | Textos, Este ano | Faltam as ressalvas do El Niño: 2024 foi normal; o Atlântico é desconhecido; o ano está além do recorde | protótipo/static/app.js:99-100, 116; protótipo/motor.py:361-362 | c03: a perspectiva não traz as ressalvas de el_nino_2026_nordeste.md | Acrescentar as 4 ressalvas | Confirmado |

## Problemas confirmados: baixos

| # | Área(s) | Título | Arquivo:linha | Evidência | Veredito |
|---|---|---|---|---|---|
| B1 | GAEZ | O sorgo forrageiro usa a camada do sorgo de grão | protótipo/motor.py:42 | O código usa a camada "sorgo". | Confirmado pelo código |
| B2 | GAEZ | A ficha do notebook diz 13 culturas; a seleção tem 15 | notebooks/secoes_prototipo/01_gaez.py:10-11 | c07 | Confirmado |
| B3 | ZARC | O aviso "antes de 01/01" aparece em 31 municípios | protótipo/static/app.js:114-115 | Pelo código, o aviso sai quando zarc_primeiro existe; 31 municípios têm 01/01. | Confirmado |
| B4 | ZARC | O texto canônico do milho em Quixadá simplifica demais | proposta/PROPOSTA_FINAL_v3.md:1219 | c02: o solo 14 do Grupo I tem 30% em 21/02; o solo 16 do Grupo II, de 11/02 a 21/02. | Confirmado |
| B5 | Localização, Robustez | Um link com ?lat=abc trava a página | protótipo/static/app.js:69-74 | Pelo código: não há isFinite, e SELO e TIPOS são declarados depois. | Confirmado pelo código |
| B6 | Localização | A busca só aceita o nome exato | protótipo/static/app.js:56-58 | Pelo código: municipios[e.target.value]. | Confirmado pelo código |
| B7 | Localização, Este ano, Proveniência | 8 municípios ficam sem o início da chuva (IMERG), mas o README diz 184 | protótipo/motor.py:221-224; protótipo/README.md:38 | c07: onset_sos_mun.csv tem 176 códigos. | Confirmado |
| B8 | Catálogo | O DOI do +24% aponta só para o Zhao 2022 | protótipo/motor.py:280 | c03: ne_lg e ne_s0 devolvem 10.1038/s41467-022-32464-0. | Confirmado |
| B9 | Catálogo | A regra do Melo diz "85 dias"; o plano diz "50–85 dias" | protótipo/motor.py:63 | c03 | Confirmado |
| B10 | Catálogo | O 8,5% vira "+8%" | protótipo/motor.py:264 | c07: o pct do cartão é 8,5. | Confirmado |
| B11 | Catálogo, Proveniência | O mesmo artigo aparece como Franke 2017 e Franke 2018 na mesma tela | dados/analogos_artigos/assinaturas.csv; protótipo/static/app.js:186 | c03 | Confirmado |
| B12 | Plano | A nota do milho "com risco" não diz o solo | protótipo/motor.py:333-334 | c03 | Confirmado |
| B13 | Este ano, Proveniência | 2009/10 é "moderado" no eventos.csv e "forte" na página | scripts/el_nino_2026.py:59 | c07: ONI 1,50 com categoria "moderado"; FORTES usa ≥ 1,5. | Confirmado |
| B14 | Este ano | Dezembro de ano bissexto sai 1 dia atrasado | protótipo/motor.py:146-147 | Pelo código: dayofyear − 365. | Confirmado pelo código |
| B15 | Este ano | "Em novembro" e "2027" estão fixos no texto | protótipo/motor.py:258, 338 | Pelo código. | Confirmado pelo código |
| B16 | Proveniência | Os caches não têm versão, e os dados só se atualizam com reinício | protótipo/motor.py:73-94, 124-182 | Pelo código. | Confirmado pelo código |
| B17 | Proveniência | O SMAP diário tem 4 datas duplicadas | protótipo/motor.py:110-112 | c07: 4.247 tempos e 4.243 únicos (2023-10-09, 2024-04-03, 2024-11-26, 2025-05-22). | Confirmado |
| B18 | Proveniência | `dt.dayofyear` está obsoleto | protótipo/motor.py:147 | c07: o pandas 3.1.1 dá Pandas4Warning. | Confirmado |
| B19 | Proveniência | A proveniência das malhas não está registrada | dados/referencia/ | c07: a pasta não tem MANIFESTO.json. | Confirmado |
| B20 | Robustez | Um byte nulo no caminho derruba a conexão | protótipo/app.py:55 | Não enviei esse pedido ao 8765. | Não conferido |
| B21 | Robustez | Há duas inserções de HTML sem esc() | protótipo/static/app.js:17, 136, 141 | Pelo código. | Confirmado pelo código |
| B22 | Robustez | O GAEZ relê o selecao.csv e abre 30 rasters a cada ponto | scripts/gaez_zarc_municipio.py:64-73 | Pelo código. | Confirmado pelo código |
| B23 | Robustez | O favicon.ico dá 404 | protótipo/static/index.html:4-8 | curl /favicon.ico no 8765: 404. | Confirmado |
| B24 | Textos | Há jargão e rótulos internos sem explicação | protótipo/static/app.js:85, 92, 167-168 | Leitura do app.js. | Confirmado |

As correções dos baixos estão nas revisões de origem e são diretas: trocar a camada, validar, normalizar, padronizar o ano, aplicar esc(), usar `day_of_year` e acrescentar `<link rel="icon" href="data:,">`.

## O que foi conferido e está certo

- **GAEZ.**
  - A ordem lon/lat, o nodata −9, a divisão por 100 e a camada sx (toda a terra da célula, sequeiro, clima de 1981–2010) estão certos. O mapeamento das culturas também.
  - Como conferido: o revisor comparou a API com a leitura manual do pixel em 10 de 13 pontos, nas 11 culturas e nos 2 insumos. A tábua dá round(raw/100) em 184 de 184 municípios.
  - Eu conferi que siLr e sxLr usam a mesma grade (c06) e que a leitura direta do raster dá o valor esperado no ponto B (c03).
- **ZARC.**
  - O decêndio 1 é 01–10/jan, como nas tabelas das portarias 330/2026 e 11/2020. Os valores da tábua são só 0, 20, 30 e 40.
  - O recálculo independente deu 0 diferenças em 1.656 pares, e a API bate com a tábua bruta nos 184 municípios.
  - Há uma portaria por cultura (11). A 245 vale só para o milho com braquiária, e a tábua da braquiária é idêntica à do milho.
  - Conferi nos PDFs que o feijão de 2ª safra é Phaseolus (Port. 354/2026). Também li as portarias 121, 143, 218, 270, 297, 97, 73 e 169 de 2026.
- **Localização.**
  - Os 184 nomes da busca levam ao município certo, tanto pela API quanto pelo motor.
  - Os códigos de UF 21–29 batem com o IBGE. Nenhum ponto cai em 2 municípios. A auto-interseção de Barbalha não afeta o resultado.
- **POWER e análogos.**
  - As equações FAO-56 e as unidades da API conferem. A padronização é igual à dos notebooks, e o peso é w = exp(−d²/2).
  - Com os dados de hoje, os números 154/23/7, Sobral 78, Harare 53 e RMF 0,31 se reproduzem.
  - No c03, os análogos de Quixadá saíram iguais aos do notebook: Bom Jesus 0,82, Serra Talhada 0,58, Sobral 0,49 e Harare 0,40.
- **Catálogo.**
  - Os 14 cartões fixos têm grau e transferência iguais aos do JSON e aos do .md, e os DOIs estão no índice. Os 18 DOIs mostrados resolvem em doi.org.
  - O +36% com soma dos pesos 0,62 foi refeito do zero, e o c03 deu o mesmo resultado.
  - Os textos de uso de mudare22, zhao, hospedeiro e martins batem com o catálogo.
- **Plano no CE.**
  - Nenhuma cultura "fora" entra no plano, e nenhuma gramínea segue outra gramínea fora do baixio.
  - A leguminosa vem antes do cereal na faixa 2 nos 184 municípios. O milho "com risco" fica só no baixio, nos 30 municípios em que isso acontece.
  - A metade guardada até ~10/mar cabe no ZARC do caupi nos 184 municípios (a ≤ 30% em 183). Isso continua valendo só com o Grupo I.
  - As notas da lagarta e da cobertura aparecem em todas as respostas.
- **Este ano.**
  - O ONI de ASO/2026 é +2,46, o maior de ago–out desde 1950. O arquivo local é idêntico ao do CPC baixado hoje.
  - A perspectiva por UF confere, e a chuva recente do CE dá 5,7 mm contra 14,3 mm.
  - A janela de 30 dias e o ranking do SMAP por UF batem com a 9.7.
  - O início de Quixadá confere: 20/01, com p10 em 02/01 e p90 em 15/02 (o c03 deu o mesmo). O cache do SMAP se regrava sem erro no Windows.
- **Proveniência.**
  - O ZARC foi baixado depois da atualização do CKAN (13/11, 07:11).
  - O SMAP vai até 10/11/2026, que é o último grânulo no CMR. O IMERG Late vai até 12/11 e o Early até 13/11.
  - As assinaturas pré-calculadas batem com a API ao vivo, e a atribuição do OpenStreetMap está certa.
- **Robustez.**
  - Testadas 18 variantes, nenhuma serviu arquivo de fora de `static/`. O servidor escuta só em 127.0.0.1, e o esc() cobre todas as strings que vêm dele.
  - Não há vazamento de memória em 200 consultas.
  - Tempos medidos: CE 0,13 s; NE 1,1 s; consultas repetidas 0,01–0,06 s.
- **Textos.**
  - O ONI não aparece como "o mais forte da história", e o texto do SMAP traz a ressalva ρ +0,01.
  - O cardápio de Quixadá bate com a seção 5 da estrutura. A página diz "+36% só como sensibilidade" e "nunca foi medida".
  - Não aparece "Portaria 245" nem "nada em janeiro" como regra do estado.

## Problemas refutados e ajustes

- **Nenhum crítico ou alto foi refutado.**
- **Mudei a severidade de 4 grupos:**
  - Subi C4 (regras negativas com ganho) de alto para crítico.
  - O cache sem trava estava como médio no GAEZ e baixo no POWER. Juntei como crítico (C1), porque derruba a página.
  - Rebaixei o ponderado do Franke (M19) de alto para médio, porque a página mostra a soma dos pesos.
  - O interruptor estava como médio em Este ano. Ficou alto (A10), como no Plano e nos Textos.
- **Parte de alguns achados não se reproduziu ou precisa de ressalva:**
  - A corrupção permanente do cache não se repetiu nas minhas 3 rodadas: o arquivo terminou válido. O HTTP 500 e a perda de entradas se repetiram.
  - O revisor contou "78 de 104 cartões T2/T3 com número". Contei 61 com percentual e não recontei os que vêm em t/ha ou LER.
  - "2028 fica sem leguminosa" vale só para as faixas 1–3, porque o baixio tem caupi em revezamento todo ano.
  - Não refiz o fator Late/Final de 2 a 3 vezes nem os números exatos dos análogos corrigidos (154 → 182, Harare 53 → 13).
- **Não conferi** M13, M14, M32, B20 e as licenças do GAEZ e do ZARC.

## Ordem recomendada de correção

**Antes da demo (15/11/2026).** São mudanças pequenas, sem regerar os dados de base:
1. **C1 e A4:** pôr a trava e a gravação atômica no cache (ou tirar o cache do GAEZ) e usar o pixel como chave. Apagar o cache_gaez.json, que já tem entradas trocadas. Sem isso, dois cliques simultâneos derrubam a página da demo.
2. **A5:** `UF[cod[:2]]` quando houver município. É uma linha e conserta a orla de Fortaleza, Jericoacoara e Penaforte.
3. **C4, A8, M18 e M22:** mostrar `_efeito` só para T0/T1 significativos e usar `mostrar_efeito=False` em luz, melo, pacheco13 e ne_s0. Usar os textos canônicos da 9.7: "+24% no ano colhido, contra cereal solteiro" e "milho-sorgo: alerta".
4. **C3:** filtrar os ciclos com cultivar (caupi no Grupo I; mamona nos Grupos II–IV) e regerar ceara_2026-2027.csv com `python -I scripts/gaez_zarc_municipio.py --ceara`. Atualizar a linha de Quixadá na 9.7. Se não der tempo, a saída mínima é uma nota: "janela de todos os grupos; com as cultivares registradas (Grupo I), a partir de 11/03".
5. **C5:** trocar "maniva de fev a abr" por "maniva de fev até o fim da janela ZARC da mandioca (em geral março)".
6. **C2 (parcial):** tirar o chip "Tmax na estação úmida" ou chamá-lo de "máxima recorde do mês".
7. **Textos (A6, A10, A14, A17 e M24):**
   - duas datas no aviso do ZARC;
   - interruptor no plantio;
   - percentil da chuva;
   - início com os 3 anos e sem negrito;
   - "ONI ago–out/2026 (ASO): +2,46".
8. **A9:** a faixa 2 de 2028 como na 6.4: sorgo forrageiro e, em ano bom, milho.
9. **A18 e B11:** rótulos dos análogos, com Sacramento 2013 no lugar do Primo e "Franke 2018" sem adjetivo. Pode ser feito mapeando na saída de analogos(), sem regerar.
10. **A13, M23 e A12:**
    - alerta pleno só no CE e "não calibrado" fora dele;
    - `modelo_ne = not cod`;
    - palma + gliricídia só no NE.
11. **M19, A19 e M30:**
    - ponderado None quando a soma for < 0,3;
    - número de pedido no app.js;
    - atalho de Quixadá no ponto interno (−4,9113; −39,0277).
12. **A11 (mínimo):** textos que dependem da cultura efetiva. "Na terra que foi mandioca" só aparece se houver mandioca.

**Depois da demo.** Estes pedem regerar dados e números canônicos:
- **C2 completo e A2:** assinatura com Tmax e Tmin médias. Depois, refazer os análogos, os notebooks, a v3 e a estrutura.
- **A3 e M1:** limiares do GAEZ v4 e SI com uma casa decimal. Regerar a tábua e as contagens 164/135/121.
- **A1 e C5 completos:** tábua complementar das portarias plurianuais, depois de conferir a vigência no SISZARC.
- **A7, M3, M4 e M5:** janela por solo, janela de 40%, fim do decêndio e as duas mamonas.
- **A15 e A16:** normal com o IMERG Late e correção dos documentos sobre o IMERG Final.
- **A11 completo, M20 e M21:** fallback do plano, giro com 4 faixas e guandu em faixa perene.
- **Demais médios e baixos:** malhas, validação de entrada, mar, celular, licenças, SMAP e cache com versão.

## Notas de método

- Não parei nem reiniciei o servidor da 8765. Fiz três consultas a ele, nenhuma das quais grava cache: `GET /`, `GET /favicon.ico` e `GET /api/local?lat=abc`, que falha antes do motor.
- Os testes do motor rodaram no próprio processo, com `motor.CACHE` desviado para `E:/campeonato-nasa/tmp/revisao_prototipo/consolidador/cache*`.
- Ao importar o motor, o Python regravou `protótipo/__pycache__/motor.cpython-313.pyc`, que é só o cache de bytecode. Este relatório é o único arquivo do projeto que criei.
- As portarias foram lidas nos PDFs que os revisores baixaram, na pasta tool-results da sessão. Para o IMERG, consultei o CMR. Para a Tmax, consultei a API do POWER: climatologia e série diária de 2001–2025.

## Correções aplicadas em 14/11/2026 (tarde), junto com a extensão para o Nordeste

- **Corrigidos no código e nos dados:**
  - C1: cache com trava e gravação atômica; o cache do SMAP também é gravado de forma atômica.
  - C2: Tmax e Tmin médias diárias de 2001–2024. Todas as assinaturas foram regeradas: 32 pontos de referência, 31 lugares do catálogo, 1.794 municípios do NE e a grade global.
  - C3: só os ciclos com cultivar no CE (caupi e sorgo forrageiro no Grupo I; mamona nos Grupos II–IV).
  - C4, A8, M18 e M22: número só em cartões T0/T1; as regras negativas saem sem ganho.
  - C5: "maniva de fev até o fim da janela ZARC da mandioca".
  - A3 e M1: classes oficiais da v4, corte de aptidão em 40 e uma casa decimal.
  - A4: o cache do GAEZ usa o pixel como chave.
  - A5 e M7: a UF vem do código IBGE; na costa e nas divisas, o município mais próximo até ~2 km.
  - A6: duas datas no aviso do ZARC.
  - A9: a faixa 2 de 2028 segue a seção 6.4.
  - A10: o interruptor decide no plantio.
  - A11: textos dependem da cultura efetiva; sem mandioca, o giro tem 3 fases.
  - A12: palma + gliricídia só no NE.
  - A13 e M23: El Niño medido no próprio município, com o estado "não avaliado" fora do NE.
  - A14 e A15: chuva recente em percentil, marcada como preliminar.
  - A17 e M25: início com os anos de El Niño e sem negrito; a comparação é com os "demais anos".
  - A18: rótulos de Sacramento 2013 e Franke 2018.
  - A19: a página só desenha a resposta do pedido mais novo.
  - M2: insumo alto só como rótulo.
  - M3: janela de 40%; o baixio só recebe milho com risco até 30%.
  - M4: a janela termina no último dia do decêndio.
  - M8: o mapa usa a mesma malha do motor.
  - M9, M10 e M11: longitude normalizada, mar sem plano e entrada validada (400).
  - M13: a chave do POWER é a célula nativa.
  - M16 e M19: w classificado pelo valor arredondado; ponderado só com soma dos pesos ≥ 0,3.
  - M21: guandu como perene.
  - M24 e M28: rótulo do ONI corrigido, com La Niña.
  - M26 e M27: SMAP sem erro em 29/02 e cache invalidado pela fonte.
  - M29 e M31: cartão de fontes e datas; o MODIS saiu do rodapé.
  - M32: a tabela rola dentro do cartão no celular.
  - M33, M34 e M35: textos com condicional, regra do nematoide e ressalvas do El Niño.
- **Pendentes:**
  - A1: tábua complementar das portarias plurianuais da mandioca, do milheto, da palma e do gergelim (hoje o cartão cita a portaria e usa o GAEZ).
  - A2: atualizar os números dos análogos na proposta v3, na estrutura e nos notebooks com as assinaturas novas.
  - A7: seletor de solo.
  - A16: corrigir nos documentos o "IMERG Final até 14/09/2026".
  - M5: separar as duas mamonas.
  - M6: leitura do notebook sobre a janela do milho.
  - M12, M14, M15, M17, M20 e M30: parcialmente tratados.
  - Ciclos com cultivar fora do CE: não conferidos; o cartão avisa.
