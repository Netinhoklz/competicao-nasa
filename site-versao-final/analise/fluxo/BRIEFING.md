# Briefing: revisão do fluxo do QUADRA (14/11/2026, noite)

## O pedido do José (dono do projeto)

> "Não estou gostando do fluxo, está parecendo nenhum pouco profissional e em muitos aspectos ele parece ter perguntas
> desnecessárias. Coloque 10 agentes opus que irão discutir sobre o melhor fluxo mais otimizado e preciso, faça algo bem
> intuitivo!"

Pedidos anteriores dele que continuam valendo:
- "Um agricultor vai ver isso, preciso que seja mais intuitivo para o usuário, menos texto e tudo mais intuitivo! Faça com que as
  outras telas sigam também o estilo da tela inicial, algo chamativo e bonito."
- "O site precisa ser intuitivo e enxuto, não quero nada muito cheio e transbordante com coisas desnecessárias."
- "Quero que o usuário tenha a oportunidade de colocar as configurações que ele trabalha hoje para otimizar o que ele já faz e
  também o que seria o ideal máximo para ele." (módulo `extras/hoje_ideal.js`: Hoje → Melhor → Ideal)
- "Acrescentar opção por hectare ou tamanho do terreno." (`extras/area.js`)
- "Saber o que ele já plantou anteriormente no solo, entender melhor o que ele já faz e as suas experiências." (`extras/historico.js`)
- Atender os 16 pontos do desafio por completo, sobretudo o 16 (lembrar que a ferramenta apoia e não substitui o saber local).

Esses três pedidos (jeito de hoje, área, histórico) **ficam no produto**, mas a forma, o lugar, o número de telas e se são
obrigatórios ou opcionais estão abertos. Ex.: podem virar uma tela só, ficar depois do resultado como "afinar o plano", ter
padrão do Censo e só um toque para confirmar etc.

## O produto

NASA Space Apps 2026, desafio "Field Shift". QUADRA: apoio à rotação de culturas para o agricultor familiar do Nordeste
semiárido com dados da NASA (POWER, SMAP, GPM, MODIS, GRACE, ECOSTRESS...), ZARC/MAPA, GAEZ/FAO, IBGE (PAM, Censo Agro 2017).
Entrega: **15/11/2026, 23:59** (amanhã). Vídeo de 30 s e apresentação ao júri.

Jornada de hoje (o que você vai revisar):
- `web/index.html`: globo 3D (João Pedro), mergulho até o Nordeste, mapa dos 1.794 municípios com camadas no zoom e painel
  "Roça Certa". Botão "Montar o plano do meu roçado" → `roca.html#/<cod>/<passo>`.
- `web/roca.html` + `web/js/roca.js` (roteador, respostas no hash da URL, chave `PADRAO`) e um módulo por passo em
  `web/js/passos/`:
  1. `lugar.js` "O seu lugar": El Niño 2027, mar, chuva, meses de chuva, solo hoje, ano da chuva, tendência, cardápio de 18
     culturas, confiança dos dados. **4.550 px de altura a 390 px.**
  2. `perguntas.js` "Sua roça": 11 telas de pergunta + resumo. Jeito de hoje (3 telas: culturas e divisão %, arranjo, manejo),
     histórico (3 telas: o que plantou em 2026/2025, o que deu certo/quebrou, o que já faz), 5 perguntas (terra, tamanho,
     baixio, água, mandioca), resumo "Pronto".
  3. `plantio.js` "Como plantar": roçado visto de cima em faixas A-B-C, calendário, o que fazer agora. **5.625 px.**
  4. `dinheiro.js` "Quanto rende": Hoje → Melhor → Ideal, caixa, El Niño. **6.629 px.**
  5. `seguranca.js` "Segurança": leque por colheita, grade de 10 roças, memória. **6.377 px.**
- Extras em `web/js/extras/*.js` (um por ponto do desafio), estilos em `web/css/quadra.css`, `web/css/passos/`, `web/css/extras/`.
- Regras visuais atuais: `web/js/passos/LEIA-ME.md`. Decisões de dados: `PLANO_INTEGRACAO.md`. Análises antigas: `analise/*.md`.
- Núcleo: `nucleo/motor.py` (`consultar(lat, lon, textura, ad, ad_baixio, maniva, baixio, hoje)`), servidor `servidor.py`.

## Material para olhar (já pronto, não precisa gerar de novo)

`E:/campeonato-nasa/tmp/fluxo_atual/`: um PNG e um TXT (texto da tela) por tela da jornada, Quixadá-CE (cód. 2311306), a 390 px:
`01_passo1_lugar`, `02`–`13` (as 11 telas do passo 2 + resumo), `14_passo3_plantio`, `15_passo4_dinheiro`, `16_passo5_seguranca`.
Os PNG longos são altos (até 6.600 px); leia o TXT primeiro e abra o PNG para ver a cara.

O servidor está rodando em `http://127.0.0.1:8090` (**não pare nem reinicie**). API: `GET /api/local?cod=2311306` com
parâmetros opcionais `textura` (1–3), `ad` (11–16), `ad_baixio`, `maniva` (tem|nao|plantada), `baixio` (0|1), `hoje`.
Para medir o efeito de uma resposta, compare o JSON com e sem o parâmetro (ex.: `curl -s "http://127.0.0.1:8090/api/local?cod=2311306&textura=1"`).
Se precisar de um print novo: `MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/testes/ferramentas/print_url.py <saida.png> 390 "<url>" 6`
(salve em `E:/campeonato-nasa/tmp/`, nunca no C:, que está quase cheio). Nunca mate python.exe em massa.

## Restrições

- Nesta rodada **ninguém edita o site**: só ler, medir e propor. Cada agente escreve apenas o seu arquivo em `analise/fluxo/`.
- O produto precisa continuar cobrindo os 16 pontos (lista abaixo), com o selo MEDIDO/SUPOSIÇÃO/PROJEÇÃO nos números.
- Pilha: módulos ES estáticos + servidor Python stdlib; sem framework; tema escuro do globo.
- A proposta precisa caber em **4–6 horas de implementação** por poucos agentes, reaproveitando os módulos que já existem.
- Público: agricultor familiar, pouca leitura, celular Android simples, internet fraca; e o júri da NASA (demo curta).
- Escrever em português do Brasil.

## Os 16 pontos do desafio ("Considerações Potenciais")

Entendendo Condições e Dados
1. Explore como as mudanças de temperatura, umidade do solo, chuva, evaporação e estresse vegetal se relacionam com a
   vulnerabilidade das culturas e a saúde do solo.
2. Considere explicar termos científicos como evapotranspiração, anomalias de umidade do solo, índices de vegetação (NDVI),
   risco de geada e indicadores de balanço hídrico.
3. Esclareça como as observações de satélite diferem das medições terrestres e como a combinação de ambas pode melhorar a precisão.

SI, Modelagem e Fusão de Dados
4. Compare diferentes abordagens de IA ou estatísticas para identificar padrões em condições climáticas e do solo históricos.
5. Considere como a IA pode destacar transições sazonais, períodos de campo despido ou momentos em que as culturas atuais
   apresentam maior estresse.
6. Explique como o modelo interpreta a incerteza e onde a expertise local seria necessária para validar os resultados.
7. Harmonizar conjuntos de dados com diferentes resoluções espaciais e temporais (SMAP, ECOSTRESS, GPM, Landsat/MODIS, GEDI,
   solo) numa grade comum para comparações claras e explicáveis de estratégia de rotação.

Exploração da Estratégia de Rotação
8. Compare cenários de rotação: ciclo de nutrientes, risco de erosão, matéria orgânica, ciclo de pragas, uso de água,
   potencial de forragem ou mercado.
9. Mapear quais ideias de rotação melhor se alinham com as prioridades do agricultor (conservar água, renda suplementar,
   estrutura do solo).
10. Breves explicações de como fixadoras de nitrogênio, culturas de cobertura, raízes profundas ou tolerantes à seca
    contribuem para a saúde do solo a longo prazo.

Mapeamento Geoespacial e Visualização
11. Mapas interativos para explorar tendências ao longo do tempo (umidade do solo, ondas de calor, queda no armazenamento de água).
12. Visualizar vulnerabilidades em nível de campo (zonas de erosão, pontos de estresse hídrico, áreas com geada).
13. Complementos opcionais: linhas do tempo, sobreposições comparando dados, controles deslizantes de cenários de chuva ou temperatura.

Design Centrado no Agricultor
14. Tornar a ferramenta facilmente interpretável para agricultores com pouca experiência técnica ou geoespacial.
15. Permitir que os agricultores introduzam suas prioridades ou restrições (água, equipamentos, mercado).
16. Lembrar que a ferramenta apoia, e não substitui, a expertise local, e destacar onde o julgamento humano é mais importante.
