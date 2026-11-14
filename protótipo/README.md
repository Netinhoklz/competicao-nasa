# QUADRA: protótipo "escolha o lugar" (Nordeste)

Clique num ponto do mapa (ou digite um dos 1.794 municípios do Nordeste). A ferramenta mostra o que aquele lugar permite:

1. **Local e clima:**
   - a estação chuvosa típica do município (IMERG);
   - a assinatura climática do NASA POWER (com Tmax e Tmin médias diárias);
   - o estudo de clima mais parecido, com o peso de transferência w = exp(−d²/2).
2. **Este ano:**
   - o ONI (NOAA);
   - o El Niño medido no próprio município (chuva da estação nos El Niños fortes da série IMERG);
   - a chuva recente (em percentil, preliminar);
   - o solo agora (NASA SMAP L4, posição entre 12 anos);
   - o início típico da chuva e o dos anos de El Niño forte;
   - as duas datas do ZARC: zoneada (até 40%) e risco de 20%.
3. **O que plantar:** cardápio de 15 culturas (7 alimentos, 5 de forragem e cobertura, 3 de renda) com a aptidão do FAO
   GAEZ v4 e a janela e o risco do ZARC 2026/27.
   - Regra: se a cultura tem ZARC no município, o ZARC decide e o GAEZ vira rótulo; senão, o GAEZ decide (aptidão > 40,
     pouco insumo).
4. **Calendário (de hoje até dez/2027):** para cada parte do roçado, quando preparar, plantar e colher.
   - "O que fazer agora": janelas abertas, as que abrem nos próximos 75 dias e as ações sem arrependimento.
   - Gantt por parte: na pista de cima, o plantio (janela do ZARC no melhor risco que houver, e o trecho de até 40%); na de
     baixo, a cultura na roça e a colheita (janela + ciclo da cultura, tabela `CICLO` do motor, igual à do notebook
     financeiro).
   - Sem ZARC, a janela é estimada pelo início típico da chuva (IMERG) até 40 dias depois (suposição).
   - Marcos do ano: os portões da proposta v3 (P1 a P5; 19/mar e 30/abr) só onde a estação é de quadra e alguma janela do
     ZARC do plano abre até 19/mar. Nos outros lugares, os marcos vêm do ZARC e do IMERG.
   - A estação de 2028 (plantios até dez/2027, como no Cerrado) repete as datas do ZARC 2026/27.
   - O solo escolhido no cardápio muda as janelas (`/api/local?...&textura=1–3&ad=11–16`).
5. **Rotação 2027–2029:** o roçado dividido em 3 partes de tamanho parecido (A, B e C) que trocam de cultura a cada ano
   (mandioca → leguminosa → cereal/forragem → mandioca), mais o baixio (parte mais úmida, cereal) e as bordas (perenes em
   curva de nível). Desenho do roçado visto de cima, ano a ano, com as culturas que existem no lugar, e o interruptor do ano.
6. **De onde vem cada regra:**
   - cartões do catálogo de rotações; o número só aparece para cartões T0 ou T1;
   - os estudos de clima parecido com o lugar;
   - fontes e datas de cada base.

## Como rodar

```bash
cd "protótipo"
E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 app.py        # abre em http://localhost:8765
```

- Link direto já consultado: `http://localhost:8765/?lat=-4.9113&lon=-39.0277` (Quixadá).
- Precisa de internet para o mapa (OpenStreetMap, Leaflet pelo cdnjs) e para o clima do POWER fora do Nordeste. Se o
  POWER recusar pedidos (erro 429), a página segue sem os análogos e avisa.

## Cobertura

| Camada | Onde funciona |
|---|---|
| GAEZ v4, catálogo, análogos (POWER ao vivo) | mundo inteiro |
| ZARC 2026/27, regime e início da chuva (IMERG), El Niño por município, clima pré-calculado | 1.794 municípios do Nordeste |
| SMAP L4 agora | recorte do Nordeste (o SMAP é global; só baixamos o NE) |

Fora do Nordeste o plano usa o modelo do sertão e avisa: as culturas são do lugar (GAEZ, pouco insumo), mas as datas,
as bordas e o alerta do ano foram calibrados no NE.

## Dados (gerados por scripts do projeto)

- `scripts/preparar_prototipo_nordeste.py`: ZARC do NE (dados abertos do MAPA), assinaturas do POWER por município,
  regime e início da chuva (IMERG) e a tabela GAEZ × ZARC (`E:/campeonato-nasa/dados/gaez_zarc/nordeste_2026-2027.csv`).
- `scripts/completar_assinaturas_ne.py`: completa as células que o POWER recusou.
- `scripts/gaez_zarc_municipio.py`: regras do GAEZ (classes oficiais da v4) e do ZARC (só os ciclos com cultivar,
  quando conferidos; janela até o fim do decêndio).
- `scripts/analogos_climaticos_artigos.py`: assinatura do POWER. Tmax e Tmin são as médias diárias de 2001–2024, porque a
  climatologia do POWER traz o recorde do mês.

## Arquivos

- `motor.py`: junta as camadas e devolve um JSON por ponto. Usa caches com trava e gravação atômica em
  `E:/campeonato-nasa/dados/prototipo/`.
- `app.py`: servidor só com a biblioteca padrão. Rotas: `/`, `/api/local?lat=&lon=[&textura=&ad=]` (valida a entrada) e
  `/api/municipios` (a mesma malha do motor).
- `static/`: a página (`index.html`, `app.js`, `estilo.css`).
- `REVISAO_10_AGENTES.md`: revisão por 10 agentes (14/11/2026) e o que já foi corrigido.

Base de decisão: `proposta/estrutura_gaez_zarc.md`, `pesquisa/catalogo_rotacoes_comprovadas.md` e `proposta/PROPOSTA_FINAL_v3.md`.
