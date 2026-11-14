# Dossiê Técnico e Científico: Projeto PercolaCampo
**Inteligência Espacial Baseada na Teoria da Percolação para Manejo de Pragas na Agricultura Familiar e de Médio Porte (Hackathon NASA)**

---

## Sumário Executivo

Este documento consolida toda a jornada de pesquisa, modelagem matemática, arquitetura de dados e design de experiência do usuário (UX) desenvolvida para o **PercolaCampo**. O objetivo do sistema é traduzir modelos avançados da **Teoria da Percolação** (física estatística e epidemiologia botânica) cruzados com dados de sensoriamento remoto da **NASA** em recomendações práticas, visuais e de baixo custo para agricultores familiares e médios produtores.

---

## 1. Fundamentação Científica: Percolação no Manejo de Pragas

A Teoria da Percolação modela a lavoura como uma rede espacial de nós (plantas ou talhões) conectados por ligações que representam a probabilidade de dispersão de pragas, fitopatógenos ou inimigos naturais.

### 1.1 Mecanismos Principais
* **Limiar Crítico de Percolação ($p_c$ ou $\chi_c$):** Em um monocultivo disposto em malha quadrada regular com transmissão entre vizinhos mais próximos, o limiar crítico teórico de percolação de sítios é $p_c \approx 0{,}5927$. Acima desse valor, forma-se um aglomerado contínuo (*spanning cluster*) que conecta extremos opostos da lavoura, desencadeando um surto epidêmico generalizado.
* **Bloqueio de Conectividade em Policultivos:** Sistemas diversificados típicos da agricultura familiar (como consórcios em faixas ou sistema *Milpa*) inserem plantas não-hospedeiras ou variedades resistentes que atuam como barreiras físicas e químicas, elevando o limiar crítico $\chi_c$ para valores entre $0{,}88$ e $0{,}98$.
* **Paradoxo da Fragmentação para Inimigos Naturais:** Agentes de controle biológico conservativo (joaninhas, crisopídeos, parasitoides) também dependem da conectividade da paisagem. Quando a cobertura de habitat natural ou corredores floridos cai abaixo do limiar de **$40\%$**, os predadores perdem a capacidade de rastrear focos de pragas.
* **Percolação Hídrica no Solo:** A infiltração e drenagem da água no perfil do solo (moduladas por textura e cobertura morta) governam a movimentação de zoósporos (*Phytophthora*), fungos de solo (*Rhizoctonia*), nematoides e a lixiviação de bioinsumos.

### 1.2 Síntese dos Resultados da Literatura

#### Tabela 1: Efeito do desenho espacial da lavoura sobre o limiar crítico ($\chi_c$)
| Configuração Espacial | Tipo de Rede / Sistema | Limiar Crítico ($\chi_c$) | Efeito Epidemiológico | Impacto Produtivo | Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Monocultivo homogêneo** | Malha quadrada 2D (vizinhos próximos) | $\chi_c = 0{,}5927$ | Surto generalizado acima de $59{,}3\%$ de suscetibilidade | Perda severa em cultivares suscetíveis | Ramírez et al. (2018; 2020) |
| **Policultivo aleatório** ($50\%$ resistente) | Mistura ao acaso (*well-mixed*) | $\chi_c \approx 0{,}78\text{--}0{,}85$ | Redução de até $65\%$ no tamanho médio dos focos | Ganho de $18\%\text{--}32\%$ na colheita líquida | Alonso-Tlali et al. (2025) |
| **Consórcio em linhas alternadas** | Rede estruturada periódica (faixas) | $\chi_c \approx 0{,}88\text{--}0{,}92$ | Bloqueio transversal completo da frente de invasão | Ganho de $25\%\text{--}40\%$ sem perda de manejo | Ramírez et al. (2018); Alonso-Tlali et al. (2025) |
| **Consórcio em padrão xadrez** | Malha bipartite intercalada | $\chi_c \to 1{,}00$ (vizinhança ortogonal) | Supressão quase total da transmissão entre vizinhos | Alta estabilidade produtiva | Alonso-Tlali et al. (2025) |
| **Barreiras estratégicas na borda** | Percolação mista (*joint site-bond*) | Deslocamento não-linear (*q*-exponencial) | Economia de $5\%\text{--}10\%$ na área de barreiras | Permite uso de variedades comerciais | González-Martínez et al. (2026) |

#### Tabela 2: Evidências empíricas e parâmetros críticos em campo
| Sistema Estudado | Agente / Organismo | Parâmetro Crítico | Resultado Empírico | Aplicação Prática | Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Canteiros de brássicas** (couve-flor) | *Rhizoctonia solani* (tombamento) | Espaçamento: $26\text{ mm}$ vs. $33\text{--}44\text{ mm}$ | A $26\text{ mm}$, focos atingiram $22$ plantas; a $44\text{ mm}$, propagação insignificante | Ajuste simples de espaçamento elimina fungicidas | Poggi et al. (2013) |
| **Agroecossistemas fragmentados** | Pulgão (*A. pisum*) e joaninhas | Limiar de cobertura funcional $\approx 40\%$ | Abaixo de $40\%$, *C. maculata* falha em conter focos | Manter corredores ecológicos interligados | With et al. (2002) |
| **Pomares cítricos** (pequeno/médio) | Vetores de baixa dispersão | Raio médio $2a \approx 5{,}0\text{ m}$ | Densidades $> 300\text{ plantas/ha}$ cruzam o limiar | Poda focal e quebra-ventos na borda | Cunniffe et al. (2014) |

---

## 2. Arquitetura Computacional do Software (Hackathon NASA)

Para operar em tempo real em dispositivos móveis e computadores sem depender de simulações de Monte Carlo lentas, o backend utiliza um **pipeline híbrido em três camadas** alimentado por dados geoespaciais.

### 2.1 Matriz de Roteamento Automático de Modelos

| Método de Percolação | Gatilho de Seleção no Software | Inputs (Produtor + NASA) | Complexidade | Saída Calculada |
| :--- | :--- | :--- | :--- | :--- |
| **Percolação de Sítios** (*Site*) | Pragas caminhantes ou contato direto | Mapa do talhão, suscetibilidade, espaçamento | $O(N)$ via Newman-Ziff | Fração máxima segura de hospedeiros ($p < p_c$) |
| **Percolação de Ligações** (*Bond*) | Vetores voadores curtos, vento ou água livre | Vento (NASA POWER), declive (SRTM), chuva (GPM) | Grafo direcionado ponderado | Probabilidade crítica de salto entre plantas ($T_c$) |
| **Percolação Mista** (*Joint Site-Bond*) | **Padrão para policultivos e consórcios** | Resistência genética + barreiras + geometria | *Surrogate ML* / Espectral | Índice acoplado de risco epidêmico ($R_{\text{eff}}$) |
| **Percolação Contínua** (*Continuum*) | Paisagem no entorno e inimigos naturais | NDVI/EVI (Sentinel-2) + raio de voo | Grafo Geométrico Aleatório | Cobertura mínima ($\ge 40\%$) e corredores |
| **Percolação Hídrica** (*Vadose*) | Encharcamento e lixiviação de bioinsumos | Precipitação (GPM), umidade (SMAP), solo | Solver 1D Darcy-Green-Ampt | Taxa de infiltração e risco de doenças de raiz |

### 2.2 Métodos Rápidos de Predição em Tempo Real
1. **Aproximação Espectral via Autovalor Dominante ($\lambda_{\max}$):** Representando a lavoura como uma matriz de adjacência ponderada $W$, o limiar crítico é obtido em menos de $5\text{ ms}$ por:
   $$p_c \approx \frac{1}{\lambda_{\max}(W)}$$
   O sistema permanece na zona segura (subcrítica) sempre que $T \cdot \lambda_{\max}(W) < 1$.
2. **Algoritmo de Newman-Ziff:** Utiliza estruturas *Union-Find* para calcular toda a curva de transição de fase $P_{\text{perc}}(p)$ para $p \in [0,1]$ em uma única varredura sobre o polígono exato da propriedade.
3. **Surrogate Model (LightGBM / XGBoost):** Treinado offline sobre cenários sintéticos para inferência instantânea offline combinando clima e geometria.

### 2.3 Fluxograma de Dados (Entrada $\to$ Processamento $\to$ Saída)

```text
[1. DADOS DE ENTRADA]
 ├── Produtor / App: Polígono GeoJSON, cultura, semente (crioula/comercial), espaçamento (cm)
 ├── APIs NASA & Satélite:
 │    ├── NASA GPM IMERG (precipitação) & NASA SMAP (umidade do solo)
 │    ├── NASA POWER / MERRA-2 (direção e velocidade do vento)
 │    └── Sentinel-2 NDVI (mata nativa no entorno) & SRTM DEM (declividade)
 └── Base Biológica: Raio de dispersão (d0), transmissibilidade basal (T0) e textura do solo
         │
         ▼
[2. MOTOR DE PROCESSAMENTO]
 ├── Módulo 1 (Roteador): Seleciona Site, Bond, Joint Site-Bond, Continuum ou Hídrico
 ├── Módulo 2 (Grafo Espacial W): Pondera arestas por distância, vento, declive e barreiras
 ├── Módulo 3 (Solver pc): Calcula 1/lambda_max(W), Newman-Ziff e curvas q-exponenciais
 └── Módulo 4 (Otimizador): Testa faixas, padrão xadrez, espaçamento e barreiras de borda
         │
         ▼
[3. DADOS DE SAÍDA ACIONÁVEIS]
 ├── Diagnóstico Semáforo: Estado da lavoura (Protegida / Atenção / Alerta) e % salva
 ├── Mapa Espacial Interativo: Simulação de foco (Dia 1 a 15) e rotas de invasão pelo vento
 ├── Plano Prático em 3 Passos: Espaçamento ideal, planta companheira e posição da barreira
 └── Alerta de Aliados Naturais: Monitoramento da regra >= 40% de cobertura para predadores
```

---

## 3. Metanálise Quantitativa e Motor Calibrado em 5 Etapas

A partir do cruzamento paramétrico das 9 referências científicas, foi estruturado o motor determinístico-estocástico em 5 etapas que roda sob o capô do aplicativo:

1. **Kernel de Transmissão entre Covas ($T_{\text{bond}}$ — *Poggi et al., 2013; Cunniffe et al., 2014*):**
   $$T_{\text{bond}} = T_0 \cdot \exp\left(-\frac{d}{d_0}\right) \cdot f_{\text{chuva\_SMAP}} \cdot f_{\text{vento\_declive}}$$
   Onde $d$ é o espaçamento real em centímetros e $d_0$ é a escala característica por cultura ($d_0 = 32\text{ cm}$ para hortaliças; $44\text{ cm}$ para feijão; $52\text{ cm}$ para milho; $65\text{ cm}$ para mandioca/perenes).
2. **Limiar Crítico Geométrico ($\chi_c$ — *Ramírez et al., 2018; Alonso-Tlali et al., 2025*):**
   $$\chi_c(p_b) = \min\left(0{,}98,\; 0{,}5927 + k_{\text{geom}} \cdot p_b\right)$$
   Com $k_{\text{mono}} = 0$, $k_{\text{aleatório}} = 0{,}42$, $k_{\text{faixas}} = 0{,}56$ e $k_{\text{xadrez}} = 0{,}72$, onde $p_b$ é a fração de plantas-barreira no talhão.
3. **Atenuação *q*-Exponencial de Barreiras de Borda ($E_q$ — *González-Martínez et al., 2026*):**
   $$E_q(f_b) = \left[1 - (1 - q)\alpha f_b\right]^{\frac{1}{1 - q}}, \quad q = 1{,}35$$
   Concentrar barreiras nas duas primeiras linhas contra o vento predominante ($\alpha = 4{,}8$ vs. $\alpha = 2{,}6$ interna) gera uma economia média de **$8{,}2\%$ de área produtiva** para o mesmo nível de contenção.
4. **Número Efetivo de Percolação Sítio-Ligação ($R_{\text{eff}}$ — *Ramírez et al., 2020*):**
   $$R_{\text{eff}} = \frac{p_{\text{site}} \cdot T_{\text{eff}}}{\chi_c}$$
   Classifica o estado da propriedade em **Zona Subcrítica / Protegida** ($R_{\text{eff}} < 0{,}85$), **Transição Crítica / Atenção** ($0{,}85 \le R_{\text{eff}} \le 1{,}05$) ou **Supercrítica / Alerta** ($R_{\text{eff}} > 1{,}05$).
5. **Classificação das 5 Fases da Paisagem (*With & Crist, 1995; With et al., 2002; Kun et al., 2019*):**
   Monitora a cobertura de mata nativa e corredores floridos no entorno: Fase 1 ($>60\%$, contínua), Fase 2 ($50\%\text{--}60\%$, perfurada), Fase 3 ($40\%\text{--}50\%$, limiar de fragmentação), Fase 4 ($25\%\text{--}40\%$, colapso de inimigos naturais) e Fase 5 ($<25\%$, extinção local de predadores).

---

## 4. Design Centrado no Agricultor (Protótipo `PercolaCampo`)

Na iteração final da interface (`index.html`), a arquitetura visual foi dividida em duas abas com públicos distintos, garantindo comunicação direta e empática com o produtor rural sem perder rigor científico:

### 4.1 Aba Principal: `Minha Lavoura` (100% Linguagem Cotidiana)
* **Eliminação Total de Jargão Técnico:** Nenhuma letra grega ($\chi_c$, $\lambda_{\max}$, $E_q$) ou termo acadêmico aparece na tela principal. Tudo é traduzido em indicadores visuais:
  * **3 Pílulas de Condições de Hoje:** *Vento Hoje* (direção e intensidade), *Chuva & Terra* (umidade do solo) e *Aliados Naturais* (status do abrigo de joaninhas e abelhas).
  * **Semáforo de Diagnóstico:** *Lavoura Protegida* (verde), *Atenção: Risco de Espalhar* (âmbar) ou *Alerta: Risco Alto de Perda* (terracota), acompanhado da barra de **Plantas Protegidas (%)**.
  * **Botão de Otimização em 1 Toque (`✨ Aplicar Melhor Desenho para Minha Roça`):** Calcula automaticamente o espaçamento ideal, insere faixas de planta companheira (ex.: Feijão-guandu no Milho, Cravo-de-defunto nas Hortaliças) e reforça a borda contra o vento, exibindo o ganho percentual antes/depois.
  * **Mapa Espacial Interativo do Terreno:** Polígono topográfico irregular com curvas de nível, riacho animado, mata nativa ao redor e 3 ferramentas grandes ao toque:
    1. `🔍 Apontar Foco de Praga` (dispara simulação animada do **Dia 1 ao Dia 15**).
    2. `🌻 Desenhar Faixa Protetora` (pincel tátil para intercalar linhas de consórcio).
    3. `🌿 Conectar Mata Nativa` (fecha corredores ecológicos na borda para ultrapassar $40\%$ e atrair joaninhas para dentro da roça).
  * **Assistente Guiado (`Configurar Minha Roça`):** Jornada visual em 4 passos (escolha do terreno, cultura/semente com régua visual planta-a-planta de `40 cm` a `100 cm`, comportamento da terra na chuva e objetivo da safra).

### 4.2 Aba Secundária: `Base Científica (Metanálise)`
* Destinada a avaliadores do hackathon, extensionistas rurais e pesquisadores.
* Exibe o pipeline matemático vivo das 5 etapas sincronizado em tempo real com a lavoura configurada, dois gráficos vetoriais interativos (deslocamento de $\chi_c(p_b)$ vs. limiar de $40\%$ de predadores e curva *q*-exponencial de economia de área) e a tabela completa com os parâmetros extraídos dos 9 artigos.

---

## 5. Referências Bibliográficas

1. **Alonso-Tlali, J. A., Ramírez, J. E., et al. (2025).** Applications of Percolation Theory to Prevent the Propagation of Phytopathogens and Pests on Plantations. *Entropy*, 27(4), 386. MDPI.
2. **Cunniffe, N. J., Laranjeira, F. F., Neri, F. M., DeSimone, R. E., & Gilligan, C. A. (2014).** Cost-Effective Control of Plant Disease When Epidemiological Knowledge Is Incomplete: Modelling Bahia Bark Scaling of Citrus. *PLoS Computational Biology*, 10(8), e1003753. (Base de dados Embrapa Mandioca e Fruticultura).
3. **González-Martínez, J. R. A., Ramírez, J. E., et al. (2026).** Assessing the effectiveness of barrier allocation strategies against the propagation of phytopathogens and pests with percolation. *Chaos: An Interdisciplinary Journal of Nonlinear Science*, 36(9), 093144. AIP Publishing.
4. **Kun, Á., Oborny, B., & Dieckmann, U. (2019).** Five main phases of landscape degradation revealed by a dynamic mesoscale model analysing the splitting, shrinking, and disappearing of habitat patches. *Scientific Reports*, 9, 11149.
5. **Poggi, S., Neri, F. M., Deytieux, V., Bates, A., Otten, W., Gilligan, C. A., & Bailey, D. J. (2013).** Percolation-Based Risk Index for Pathogen Invasion: Application to Soilborne Disease in Propagation Systems. *Phytopathology*, 103(10), 1012–1019.
6. **Ramírez, J. E., Molina-Gayosso, E., Lozada-Lechuga, J., Flores-Rojas, L. M., Martínez, M. I., & Fernández Téllez, A. (2018).** Percolation strategy to improve the production of plants with high pathogen susceptibility. *Physical Review E*, 98(6), 062409.
7. **Ramírez, J. E., Pajares, C., Martínez, M. I., Rodríguez Fernández, R., Molina-Gayosso, E., Lozada-Lechuga, J., & Fernández Téllez, A. (2020).** Site-bond percolation solution to preventing the propagation of *Phytophthora* zoospores on plantations. *Physical Review E*, 101(3), 032301.
8. **With, K. A., & Crist, T. O. (1995).** Critical thresholds in species' responses to landscape structure. *Ecology*, 76(8), 2446–2459.
9. **With, K. A., Pavuk, D. M., Worchuck, J. L., Oates, R. K., & Fisher, J. L. (2002).** Threshold effects of landscape structure on biological control in agroecosystems. *Ecological Applications*, 12(1), 52–65.