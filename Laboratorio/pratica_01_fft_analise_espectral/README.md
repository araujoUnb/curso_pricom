# Prática 01 — FFT e Análise Espectral (50 min)

## Alinhamento com cronograma

- Semanas 2–3
- Tópicos: Série/Transformada de Fourier, análise espectral

## Objetivo

Implementar no GNU Radio um fluxo simples para observar o espectro de sinais senoidais e multitonais, medindo com critérios numéricos a resolução espectral, o efeito do ruído e o vazamento produzido por diferentes janelas.

## Pré-requisitos

- Noções básicas de senoides (amplitude, frequência, fase)
- Abrir e executar flowgraph no GNU Radio Companion (GRC)

## Roteiro (50 min)

1. **(0–8 min)** Flowgraph base: `Signal Source`, `Throttle`, `QT GUI Time Sink`, `QT GUI Frequency Sink`, sliders `freq1`/`amp1`/`freq2`/`amp2`.
2. **(8–16 min)** Tom único: variar `freq1` e conferir a posição do pico contra `f_k = k·fs/N`.
3. **(16–24 min)** Segundo tom e bloco `Add`: verificar a diferença de 6 dB entre os picos.
4. **(24–34 min)** Resolução espectral com tons de **1000 e 1200 Hz e amplitudes iguais**: varrer o *FFT Size* e medir a profundidade do vale `D = A_min − V`, com critério `D ≥ 3 dB`.
5. **(34–42 min)** Ruído gaussiano: calcular a SNR de banda larga e medir `SNR_disp = A_pico − P`, com critério de visibilidade de 6 dB.
6. **(42–50 min)** Janelas com tom **fora do índice, em 1050 Hz**: medir supressão `S = A_pico − L` e largura a −3 dB.

## Pontos que não podem ser trocados

- A Etapa 4 exige `freq2 = 1200` e `amp1 = amp2`. Com os tons de 1000 e 2500 Hz da Etapa 3 os picos já se separam em todos os *FFT Size* e a tabela perde o sentido.
- A Etapa 6 exige `freq1 = 1050`. Em 1000 Hz o tom cai exatamente sobre o índice `k = 32`, não há vazamento e as quatro janelas ficam indistinguíveis.
- A Etapa 6 exige `noise_amp = 0` e `amp2 = 0`.

## Medições na tela

O `QT GUI Frequency Sink` está configurado com *Control Panel* habilitado e *Spectrum Width: Half*. O painel permite mudar *FFT Size*, *FFT Window* e *Average* com o flowgraph em execução. Ajustar *Average* para *High* antes de qualquer leitura de nível. O eixo é *Relative Gain (dB)*, de referência arbitrária: só diferenças de níveis têm significado.

## Entregáveis

- Relatório em PDF no modelo do SIGAA, com fundamentação teórica.
- Capturas no tempo e na frequência em 3 cenários: tom único, dois tons, dois tons com ruído.
- Cinco tabelas do enunciado preenchidas com valores medidos.
- Respostas às 5 questões, cada uma citando os valores obtidos.

## Critérios de avaliação

- Montagem funcional do flowgraph
- Valores medidos coerentes com a teoria, dentro de ±2 dB
- Respostas apoiadas em números, não em impressões visuais

## Arquivos

- `enunciado_pratica_01.tex` / `.pdf` — enunciado do aluno
- `pratica_01_fft_analise_espectral.grc` — flowgraph de referência
- Gabarito do professor: `../gabaritos_professor/pratica_01_fft_analise_espectral/`
- Script que gera os valores de referência: `../Codigos/pratica_01_gabarito/codigos/pratica_01_gabarito.py`
