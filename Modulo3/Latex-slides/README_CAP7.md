# Slides do Capítulo 7: Conversão Analógico-Digital

## Visão Geral

Este conjunto de slides cobre o capítulo de Conversão Analógico-Digital com foco em:
- Amostragem e Teorema de Nyquist-Shannon
- Quantização uniforme e ruído de quantização
- PCM (Pulse Code Modulation)
- Companding (A-law e $\mu$-law)

## Estrutura dos Arquivos

### Arquivo principal
- `main.tex`: arquivo principal do Beamer

### Organização do capítulo
- `cap7_analog_to_digital_conversion.tex`: agrega as seções do capítulo

### Seções individuais
1. `sec7_1_sampling.tex`
   - Teorema da amostragem
   - Derivação espectral
   - Aliasing

2. `sec7_2_quantization.tex`
   - Quantização uniforme
   - Ruído de quantização
   - Derivação de $P_q=\Delta^2/12$
   - Relação $\SQNR \approx 1.76 + 6.02n$

3. `sec7_3_pcm_companding.tex`
   - Cadeia PCM
   - Taxa de bits
   - Companding ($\mu$-law e A-law)

## Compilação

```bash
cd Modulo3/Latex-slides
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

ou com latexmk:

```bash
cd Modulo3/Latex-slides
latexmk -pdf -interaction=nonstopmode main.tex
```

## Observação

O conteúdo detalhado das derivações matemáticas está em:
- `../derivacoes_matematicas.md`

Esse arquivo foi preparado para servir de base para evolução didática dos slides.
