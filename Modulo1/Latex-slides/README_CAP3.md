# Slides do Capítulo 3: Análise e Transmissão de Sinais

## Visão Geral

Este conjunto de slides cobre de forma completa e detalhada o Capítulo 3 sobre Análise e Transmissão de Sinais, focando em:
- Transformada de Fourier e suas propriedades
- Sistemas LTI e análise espectral
- Filtros e distorção em canais
- Energia e potência de sinais
- DFT e FFT

## Estrutura dos Arquivos

### Arquivo Principal
- **`main.tex`**: Arquivo principal do Beamer, configurado para o Capítulo 3

### Organização do Capítulo
- **`cap3_analise_transmissao_sinais.tex`**: Estrutura modular que inclui todas as 9 seções

### Seções Individuais (9 arquivos)

1. **`sec3_1_fourier_transform.tex`** (~18 slides)
   - Derivação da Transformada de Fourier
   - Exemplos: pulso retangular, exponencial
   - Interpretação física e princípio de incerteza

2. **`sec3_2_useful_transforms.tex`** (~16 slides)
   - Transformadas de funções fundamentais
   - Delta de Dirac, constantes, exponenciais
   - Pulsos, degraus, Gaussianas, trens de impulsos

3. **`sec3_3_fourier_properties.tex`** (~20 slides)
   - 11 propriedades com demonstrações completas
   - Linearidade, deslocamentos, escala, convolução
   - Derivação, integração, dualidade, Parseval

4. **`sec3_4_lti_systems.tex`** (~17 slides)
   - Resposta ao impulso e função de transferência
   - Causalidade e estabilidade
   - Transmissão sem distorção
   - Exemplos: filtro RC, filtros ideais

5. **`sec3_5_ideal_vs_practical_filters.tex`** (~15 slides)
   - Filtros ideais e problema da causalidade
   - Critério de Paley-Wiener
   - Filtros práticos: Butterworth, Chebyshev, Bessel, Elíptico
   - Projeto e determinação de ordem

6. **`sec3_6_signal_distortion.tex`** (~14 slides)
   - Modelo de canal de comunicação
   - Distorção de amplitude e fase
   - Atraso de grupo
   - Equalização e exemplos práticos

7. **`sec3_7_energy_spectral_density.tex`** (~16 slides)
   - Energia de sinais
   - Teorema de Parseval (demonstração)
   - Densidade espectral de energia
   - Largura de banda e relação de incerteza

8. **`sec3_8_power_spectral_density.tex`** (~18 slides)
   - Potência média de sinais
   - Densidade espectral de potência
   - Teorema de Wiener-Khinchin
   - Ruído branco e SNR

9. **`sec3_9_dft.tex`** (~17 slides)
   - Amostragem e Teorema de Nyquist
   - Transformada Discreta de Fourier
   - Fast Fourier Transform (FFT)
   - Fenômenos: aliasing, vazamento, janelamento

## Estatísticas

- **Total de seções**: 9
- **Total estimado de slides**: ~150 slides
- **Referências bibliográficas**: 12 livros e artigos clássicos
- **Scripts Python**: 5 scripts principais + README

## Figuras e Visualizações

### Diretório: `figures/cap3/`

#### Scripts Python (`figures/cap3/scripts/`)

1. **`01_rect_fourier.py`**
   - Pulso retangular e transformada sinc
   - Ilustra relação tempo-frequência

2. **`02_exponential_fourier.py`**
   - Exponencial causal e espectro Lorentziano
   - Magnitude e fase

3. **`03_filters_comparison.py`**
   - Comparação Butterworth vs Chebyshev vs Bessel
   - Respostas em magnitude e fase

4. **`04_convolution_example.py`**
   - Demonstração da propriedade de convolução
   - Convolução no tempo ↔ multiplicação na frequência

5. **`05_dft_windowing.py`**
   - Efeito de diferentes janelas
   - Redução de vazamento espectral

#### Como Gerar as Figuras

```bash
cd figures/cap3/scripts
python 01_rect_fourier.py
python 02_exponential_fourier.py
python 03_filters_comparison.py
python 04_convolution_example.py
python 05_dft_windowing.py
```

Ou executar todos de uma vez (Windows):
```cmd
cd figures\cap3\scripts
for %f in (*.py) do python %f
```

**Requisitos**: `numpy`, `matplotlib`, `scipy`

```bash
pip install numpy matplotlib scipy
```

## Compilação

### Compilar os Slides

```bash
cd Modulo1/tpl-slides-main
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Ou use seu editor LaTeX preferido (TeXstudio, Overleaf, etc.)

### Arquivos Gerados

- **`main.pdf`**: Slides completos em PDF
- Figuras em `figures/cap3/`: `.pdf` e `.png` de alta resolução

## Características dos Slides

### Conteúdo Pedagógico

✅ **Derivações matemáticas passo a passo**
- Cada manipulação algébrica justificada
- Sem "pulos" nas demonstrações
- Clareza nas transições lógicas

✅ **Exemplos numéricos completos**
- Pelo menos 2 exemplos por seção
- Dados realistas e interpretações físicas
- Solução detalhada visível

✅ **Visualizações**
- Figuras Python de alta qualidade
- Diagramas TikZ para conceitos
- Gráficos comparativos

### Estilo de Apresentação

✅ **Uso moderado de blocos**
- Máximo 2 blocos por slide
- Apenas para definições e teoremas principais
- Derivações em texto normal (não em blocos)

✅ **Notação consistente**
- Comandos customizados: `\FT{}`, `\IFT{}`, `\sinc`, `\rect`
- Vetores em negrito
- Operadores bem definidos

✅ **Slides de transição**
- Slide colorido separando capítulo
- Sumário no início
- Resumo ao final de cada seção

## Conteúdo por Seção (Detalhado)

### 3.1 Transformada de Fourier
- Motivação e necessidade
- Derivação da TF a partir da Série de Fourier (4 etapas)
- Par transformada direta/inversa
- Condições de existência (Dirichlet)
- Espectro de magnitude e fase
- 3 exemplos completos: retangular, exponencial unilateral, exponencial bilateral

### 3.2 Funções Úteis
- 9 pares fundamentais de transformadas
- Delta de Dirac (propriedade de amostragem)
- Constante (via dualidade)
- Exponencial complexa e senoidais
- Degrau e função sinal (derivações)
- Pulsos: retangular, triangular
- Gaussiana (demonstração completa)
- Trem de impulsos periódico
- Tabelas resumo

### 3.3 Propriedades
- 11 propriedades com demonstrações:
  1. Linearidade
  2. Deslocamento temporal
  3. Deslocamento em frequência (modulação)
  4. Escala temporal
  5. Convolução no tempo
  6. Multiplicação no tempo
  7. Derivação
  8. Integração
  9. Dualidade
  10. Simetrias (Hermitiana, par/ímpar)
  11. Teorema de Parseval
- Exemplos de aplicação
- Tabela resumo completa

### 3.4 Sistemas LTI
- Caracterização: linearidade e invariância
- Resposta ao impulso h(t)
- Função de transferência H(ω)
- Relação Y(ω) = H(ω)X(ω)
- Causalidade e critérios
- Estabilidade BIBO
- Transmissão sem distorção: H(ω) = Ke^(-jωt_d)
- Distorção de amplitude e fase
- Atraso de grupo
- Largura de banda
- Exemplos: filtro RC, filtro ideal

### 3.5 Filtros
- 4 tipos ideais: LP, HP, BP, BS
- Problema da causalidade
- Critério de Paley-Wiener
- Aproximações práticas:
  - Butterworth (maximally flat)
  - Chebyshev I e II (ripple)
  - Bessel (fase linear)
  - Elíptico (ordem mínima)
- Comparação detalhada
- Cálculo de ordem necessária
- Exemplo numérico de projeto
- Implementação (analógica e digital)

### 3.6 Distorção em Canais
- Modelo Y(ω) = H_c(ω)X(ω)
- Distorção de amplitude: |H_c(ω)| variável
- Distorção de fase: φ(ω) não-linear
- Atraso de grupo: τ_g(ω)
- Distorção linear vs não-linear
- Equalização: H_eq(ω) = 1/H_c(ω)
- Tipos de equalizadores (fixo, adaptativo, DFE)
- Exemplos: canal telefônico, cabo coaxial, multipercurso
- Compromisso equalização vs ruído

### 3.7 Energia e DEE
- Classificação: sinais de energia vs potência
- Energia: E = ∫|f(t)|²dt
- Teorema de Parseval (demonstração completa)
- Densidade Espectral de Energia: Ψ(ω) = |F(ω)|²
- Largura de banda (definições: absoluta, 3dB, ruído, X%)
- Relação de incerteza Δt·Δω ≥ 1/2
- Gaussiana ótima
- Energia em sistemas LTI
- Energia em banda limitada
- Autocorrelação: R(τ) ↔ Ψ(ω)

### 3.8 Potência e PSD
- Potência média: P = lim(1/T)∫|f(t)|²dt
- PSD: S(ω) = lim|F_T(ω)|²/T
- PSD de sinais periódicos (impulsos)
- Teorema de Wiener-Khinchin: R(τ) ↔ S(ω)
- Demonstração do teorema
- PSD em sistemas LTI: S_y = |H|²S_x
- Ruído branco: S_n = N_0/2
- Ruído filtrado
- SNR = P_s/(N_0B)
- Exemplo integrado

### 3.9 DFT e FFT
- Limitações da TF contínua
- Teorema de Nyquist: f_s ≥ 2f_max
- Aliasing (causa, efeito, prevenção)
- Definição da DFT
- Interpretação: frequências discretas
- Resolução: Δf = f_s/N
- Propriedades: periodicidade, simetria
- Relação DFT-TF contínua
- Complexidade: O(N²) para DFT direta
- FFT: algoritmo Cooley-Tukey, O(N log N)
- Ganho de velocidade
- Vazamento espectral (leakage)
- Janelamento: Hanning, Hamming, Blackman, Kaiser
- Efeito cerca (picket fence)
- Zero-padding
- Exemplos práticos: senoide, áudio, espectrograma
- Implementação (Python, MATLAB, C)

## Referências Bibliográficas

O arquivo `references.bib` inclui 12 referências principais:

1. **Lathi & Ding** (2019) - Modern Digital and Analog Communication Systems, 5ª ed.
2. **Proakis & Salehi** (2007) - Fundamentals of Communication Systems
3. **Oppenheim et al.** (2010) - Signals and Systems
4. **Haykin & Moher** (2009) - Communication Systems
5. **Couch** (2013) - Digital and Analog Communication Systems
6. **Bracewell** (2000) - The Fourier Transform and Its Applications
7. **Proakis & Manolakis** (2001) - Digital Signal Processing
8. **Cooley & Tukey** (1965) - FFT Algorithm
9. **Papoulis & Pillai** (2002) - Probability and Stochastic Processes
10. **Carlson & Crilly** (2002) - Communication Systems
11. **Shannon** (1948) - A Mathematical Theory of Communication
12. **Ziemer & Tranter** (2015) - Principles of Communications

## Comandos Customizados

Definidos em `main.tex`:

```latex
\newcommand{\FT}[1]{\mathcal{F}\{#1\}}        % Transformada
\newcommand{\IFT}[1]{\mathcal{F}^{-1}\{#1\}}  % Inversa
\newcommand{\ft}{\mathcal{F}}                  % Operador
\newcommand{\conv}{\ast}                        % Convolução
\newcommand{\sinc}{\text{sinc}}                 % Sinc
\newcommand{\rect}{\text{rect}}                 % Retângulo
\newcommand{\tri}{\text{tri}}                   % Triângulo
\newcommand{\sgn}{\text{sgn}}                   % Sinal
\DeclareMathOperator{\Real}{Re}                 % Parte real
\DeclareMathOperator{\Imag}{Im}                 % Parte imaginária
```

## Observações Importantes

### Para o Professor

1. **Flexibilidade**: Cada seção é modular e pode ser apresentada independentemente
2. **Profundidade**: Derivações completas permitem diferentes níveis de detalhamento
3. **Exemplos**: Múltiplos exemplos por seção facilitam compreensão
4. **Visualizações**: Scripts Python podem ser executados ao vivo durante a aula

### Para os Alunos

1. **Acompanhamento**: Derivações passo a passo facilitam estudo individual
2. **Prática**: Scripts Python disponíveis para experimentação
3. **Referências**: Bibliografia extensa para aprofundamento
4. **Resumos**: Cada seção termina com resumo dos conceitos principais

## Customização

### Ajustar Conteúdo

- Comentar/descomentar seções em `cap3_analise_transmissao_sinais.tex`
- Modificar ordem de apresentação
- Adicionar slides extras em qualquer seção

### Modificar Figuras

- Editar parâmetros nos scripts Python
- Regenerar figuras com novos valores
- Adicionar novas visualizações

### Estilo Visual

- Cores e tema definidos em `template/beamertheme-unb.sty`
- Tamanhos de figura: `\figFull`, `\figHalf`, `\figHalfV`
- Fontes e espaçamento ajustáveis

## Contato e Suporte

Para questões, sugestões ou correções:
- Professor: daniel.araujo@unb.br
- Laboratório de Telecomunicações - UnB

## Licença

Material didático para uso acadêmico na Universidade de Brasília.

---

**Última atualização**: Fevereiro 2026  
**Versão**: 1.0  
**Total de páginas estimadas**: ~150 slides
