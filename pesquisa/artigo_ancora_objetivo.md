# Artigo-âncora para o objetivo do desafio

> **Objetivo do desafio (Field Shift):** "combinar observações da NASA na Terra com informações agrícolas locais para criar
> um aplicativo, modelo, mapa interativo ou outra ferramenta de apoio à decisão [...] ajudar os agricultores a explorar
> opções de rotação de culturas que possam melhorar a saúde do solo e fortalecer a resiliência às mudanças nas condições
> climáticas e hídricas."

Todas as referências abaixo foram conferidas no Crossref em 14/11/2026: título, autores, revista, data e número de citações.

## 1. O artigo principal

**Kluger, D. M.; Di Tommaso, S.; Lobell, D. B. (2025).** *Precrop payoffs: causal machine learning reveals large but
variable yield benefits of crop rotation in major breadbaskets.* **Environmental Research Letters** 20, 114037.
https://doi.org/10.1088/1748-9326/ae0f45 (Stanford; arXiv 2506.02384).

**O que fizeram.** Combinaram mapas de culturas por pixel, satélite (Landsat nos EUA e no Canadá; Sentinel-2 na França e
na China) e clima (TerraClimate) com **florestas causais** (*causal forests*, pacote `grf`). O objetivo foi medir o efeito
da cultura anterior ("precrop") sobre o rendimento da seguinte e **como esse efeito muda com o clima**. Estudaram 4
celeiros: EUA (2008–2021), Canadá (2011–2020), França (2015–2021) e Nordeste da China (2017–2019). O rendimento foi
aproximado pelo pico de um índice de vegetação, calibrado com o rendimento por condado.

**O que acharam.**
- A rotação de 2 culturas traz um ganho mediano de **~4,5%** do rendimento médio nas 36 combinações cultura × país.
- Esse ganho é cerca de **3,7 vezes** o ganho adicional de diversificar ainda mais.
- Os benefícios **variam com o clima**: em geral são maiores com mais chuva na estação.
- A leguminosa como cultura anterior rende menos benefício sob calor.

*Esses números vêm do texto do arXiv (v2); conferir na versão publicada antes de colocar no slide.*

**Por que encaixa no nosso trabalho.** É, em escala mundial, exatamente o que propomos: satélite + mapa de culturas +
clima + IA causal para dizer **qual rotação funciona onde e sob qual clima**.

| Componente | Kluger et al. 2025 | O nosso estudo |
|---|---|---|
| Mapa de culturas por pixel | CDL (EUA) e produtos nacionais | CDL 2023–2025 + frequência 2008–2025 (EUA); IBGE PAM por município (Ceará); MapBiomas é o próximo |
| Satélite óptico | Landsat, Sentinel-2 | Landsat 8/9, Sentinel-2, HLS (Landsat + Sentinel-2 harmonizados pela NASA), MODIS, VIIRS |
| Clima | TerraClimate | NASA POWER, IMERG, ERA5, NEX-GDDP (futuro) |
| Água no solo | — | **SMAP L4 (zona da raiz), GLDAS, GRACE**: dimensão que eles não têm |
| Método | Floresta causal | Floresta causal / ML causal (seção 30 do notebook) |
| Região | 4 celeiros temperados do Norte | **Semiárido tropical (Ceará)**: lacuna que eles deixam |

**A lacuna que nós preenchemos.** O artigo não estuda o Brasil nem o semiárido, não usa dados de água (umidade do solo,
água subterrânea) e mede só rendimento, não resiliência à seca. A nossa ferramenta leva o mesmo método para onde ele faz
mais falta: agricultura de sequeiro, sem mapa de culturas oficial, com **dados de água da NASA** no centro.

## 2. Pilares de apoio (um para cada palavra do objetivo)

| Palavra do objetivo | Artigo | Achado | Citações |
|---|---|---|---|
| **resiliência** a condições adversas | Bowles et al. 2020, *One Earth* 2:284–293, https://doi.org/10.1016/j.oneear.2020.02.007 | 11 experimentos de longo prazo na América do Norte: rotação diversa dá +28% no milho e reduz a perda em ano seco de 14% a 90% | 501 |
| **saúde do solo** → resistência à seca | Renwick et al. 2021, *Environ. Res. Lett.* 16:084067, https://doi.org/10.1088/1748-9326/ac1468 | Experimento de 36 anos com abrigos de exclusão de chuva: a diversificação reduziu a perda do milho na seca em ~17%; a matéria orgânica do solo se associou a menos estresse hídrico | 89 |
| **mudanças** climáticas | Zhou et al. 2024, *Global Change Biology*, https://doi.org/10.1111/gcb.17556 | Satélite + floresta causal no Corn Belt: o benefício da rotação milho-soja é "extremamente sensível ao clima" e muda com o aquecimento. **A rotação certa de hoje pode não ser a de amanhã** | 15 |
| **observações da NASA** substituem o campo | Beal Cohen, Seifert, Azzari, Lobell 2019, *Agronomy Journal*, https://doi.org/10.2134/agronj2019.03.0157 (destacado pela NASA Harvest) | Dados de satélite reproduziram o efeito da rotação medido em campo, mesmo sem dado de chão | 13 |
| diversidade **estabiliza** a produção | Renard & Tilman 2019, *Nature*, https://doi.org/10.1038/s41586-019-1316-y | Em escala nacional, maior diversidade de culturas = produção mais estável entre anos | 599 |

## 3. A mesma evidência nos nossos dados do Ceará

Script: `pesquisa/analise_diversidade_resiliencia.py`. Saídas: `.saida.txt` e `.csv`.

- **Pergunta:** os municípios com mais diversidade de lavouras antes da seca (2004–2011) perderam menos rendimento na seca
  de 2012–2016?
- **Dados:** IBGE PAM (184 municípios), com chuva de fev–mai do IMERG por município e relevo do SRTM.
- **Métrica:** rendimento relativo (2012–16 ÷ 2004–11).

| Teste | Resultado | Leitura |
|---|---|---|
| Portfólio de lavouras × diversidade (Spearman) | ρ = +0,49, p < 0,0001 | mais diverso = perdeu menos |
| Portfólio, controlando chuva do IMERG, relevo e **efeito fixo de mesorregião** | **+6,6 p.p.** de rendimento preservado do 1º ao 3º quartil de diversidade (p = 0,002) | **robusto** |
| Só o milho, mesmos controles | +6,6 a +9,3 p.p. (p = 0,19–0,27) | mesmo sinal e tamanho de Bowles/Renwick, mas **não significativo** dentro das mesorregiões: sugestivo, não prova |
| Perda por área (plantada − colhida) | ~0 na maioria dos municípios | métrica inadequada: após 2000 o IBGE registra a seca no rendimento, não na área |

**Como contar isso sem exagero.** É uma associação **municipal** (diversidade da paisagem/portfólio), não um experimento
de rotação no talhão. Ela mostra que o padrão dos artigos aparece também no semiárido cearense. A ferramenta usa a
mesma lógica e mostra a incerteza.

> **⚠️ Atualização (rodada 2 do conselho, 14/11): o +6,6 p.p. NÃO deve ir para o pitch.**
> O cético refez o teste separando a **composição** do portfólio, que tem menos milho e feijão e mais culturas tolerantes
> ou irrigadas (`conselho/analises/v2_cetico_diversidade_composicao.py`). **Só com lavouras de sequeiro, o efeito cai
> para +1,4 p.p., não significativo.**
> - **Leitura correta:** os municípios diversos perderam menos porque plantam mais culturas que aguentam a seca ou que
>   são irrigadas, não por um efeito da diversidade em si.
> - Isso conversa com Kluger et al. 2025, que também acha pouco ganho em diversificar além de uma rotação simples. O
>   valor da rotação está em **qual** cultura entra, não no número de culturas.

## 4. Frases prontas para o pitch

- **PT:** "Stanford mostrou, com satélite e IA causal, que o benefício da rotação depende do clima de cada lugar, mas
  estudou só celeiros temperados (Kluger et al., ERL 2025). Nós levamos esse método ao semiárido, com os dados de água
  da NASA no centro."
- **EN:** "Stanford researchers showed, with satellites and causal AI, that crop-rotation benefits depend on local climate,
  but only in temperate breadbaskets (Kluger et al., ERL 2025). We bring that method to the semi-arid tropics, with NASA
  water data at its core."
- **Número do Ceará:** não usar o +6,6 p.p. (ver a atualização acima). Os números de vitrine que se reproduzem estão
  na `proposta/PROPOSTA_FINAL_v2.md` (tabela de números canônicos) e no El Niño (`pesquisa/el_nino_2026_nordeste.md`).
