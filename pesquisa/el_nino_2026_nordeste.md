# El Niño 2026–27 e o Nordeste — resumo para a proposta e o pitch

Dados baixados em 14/11/2026. Análise: `scripts/el_nino_2026.py`; notebook: seção 17
(`notebooks/secoes/17_el_nino_2026.py`); saídas em `E:/campeonato-nasa/dados/el_nino_2026/`.

## Agora (NOAA)
- **ONI de ago–set–out/2026: +2,46 °C.**
- **Semana de 04/11/2026:**
  - Niño 3.4: +3,3 °C;
  - Niño 3: +4,4 °C;
  - Niño 1+2: +5,6 °C.
- **Boletim do CPC de 12/11/2026, "El Niño Advisory":**
  - chance **maior que 79%** de El Niño forte a muito forte até jan–mar/2027;
  - chance de **~60%** de evento histórico (≥ +2,5 °C) em out–dez e nov–jan.
- **Atlântico tropical em set/2026:** TNA +0,64 e TSA +0,57 (NOAA PSL), ambos quentes, com gradiente quase neutro. O
  estado que importa é o de fev–abr/2027, que ainda não é previsível com segurança.

## O que El Niños fortes fizeram (5 eventos com dado NASA)

| Evento | ONI (out–jan) | Quadra do Ceará (POWER, % do normal) | Milho CE (desvio da tendência) | Feijão CE | Mandioca CE |
|---|---|---|---|---|---|
| 1982/83 | +2,12 | 53% | −60% | −28% | −33% |
| 1997/98 | +2,37 | 44% | −64% | −51% | −17% |
| 2009/10 | +1,50 | 64% | −40% | −19% | −14% |
| 2015/16 | +2,59 | 58% | −64% | −45% | −16% |
| 2023/24 | +1,99 | 93% | 0% | 0% | +1% |

- **Ceará:** quadra no tercil inferior em **4 de 5**; mediana de **58% do normal**. Nos anos sem El Niño forte, o
  rendimento do milho fica em média +7,5% acima da tendência.
- **Por estado (IMERG, 4 eventos: 1998, 2010, 2016 e 2024):**
  - MA, PI, CE, RN e PB ficaram abaixo do normal em **3 de 4**;
  - PE, AL, SE e BA ficaram abaixo em 2 de 4.
- **2023/24 foi a exceção:** quadra e safra normais.

## Como o Nordeste entra em 2027 (NASA)
- **Chuva de 01/08 a 13/11/2026 (IMERG V07 Late e Early, preliminar; o Final V07 só vai até 30/09/2025):** baixa no MA (percentil 11) e no PI (25); normal no CE (39), RN, PB e PE
  (54); acima do normal em AL, SE e BA. É a estação seca, então use o percentil: o "% do normal" engana com totais tão
  pequenos.
- **Umidade da zona da raiz (SMAP L4, 30 dias até 10/11, posição entre 12 anos; 1 = o mais seco):**
  - **Maranhão e Sergipe: 1º**, o novembro mais seco da série;
  - **Piauí e Pernambuco: 2º**;
  - AL e BA: 3º; PB e RN: 4º;
  - **Ceará: 5º, normal.** Mais úmido que a entrada de 2015 (2º) e mais seco que a de 2023 (7º).
- **Ressalva importante:** a umidade do solo de novembro **não prevê a quadra**, porque a memória dela não chega a
  fevereiro (rodada 2 do conselho). O risco de 2027 vem do **oceano**.
- **Correção (14/11):** a 1ª versão deste resumo dizia "CE 18 contra 25 e 28" pelo percentil pronto do SMAP. Esse
  campo quase não existe no Nordeste de out a jan (menos de 0,5% das células do Ceará). Estava errado.
- **Água total (GRACE, set/2026):** Ceará −9,7 cm, entre 2023 (−3,5) e 2015 (−16,7).
- **Vegetação (VIIRS NDVI, nov/2026):** Ceará 0,403, perto da climatologia (0,393).

## Frase para o pitch
- **PT:** "O Pacífico está no El Niño mais forte em décadas (+2,46 °C, NOAA). Nos últimos cinco El Niños fortes, o Ceará
  perdeu chuva em quatro e o milho caiu de 40% a 64%. O SMAP da NASA mostra o Maranhão e Sergipe com o novembro mais
  seco da série. A QUADRA transforma isso numa decisão de rotação agora, em novembro, e reavalia em março e abril,
  quando o solo começa a falar."
- **EN:** "The Pacific is in its strongest El Niño in decades (+2.46 °C, NOAA). In four of the last five strong El Niños,
  Ceará's rainy season failed and maize fell 40–64%. NASA's SMAP shows Maranhão and Sergipe at their driest November on
  record. QUADRA turns that into a rotation decision today, in November, and re-checks in March and April, when the soil
  starts to speak."

## Ressalvas obrigatórias
- n = 5 eventos.
- O ONI de out–jan ainda não foi observado.
- O Atlântico de fev–abr/2027 é desconhecido.
- 2027 pode ficar fora da faixa histórica.
- Por tudo isso, falar em **probabilidade e alerta**, não em previsão certa. Reavaliar nos portões de janeiro e de 19/mar.

## Referências do nosso acervo sobre o mecanismo
- Moura et al. 1981 (*J. Atmos. Sci.*)
- Nobre et al. 1996 (*J. Climate*)
- Kayano et al. 2006 (*JGR*)
- Andreoli et al. 2006 (*Int. J. Climatol.*)
- **Alves et al. 2009 (*Climate Research*):** oceanos × milho e feijão do Ceará, 1952–2000
- Marengo et al. 2017: seca de 2010–2016

Ver `pesquisa/artigos_nordeste.md`.
