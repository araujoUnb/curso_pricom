# Prática 05 — Modulação FM: desvio, funções de Bessel e regra de Carson (50 min)

## Alinhamento com cronograma

- Semanas 10–11
- Tópicos: FM com tom, espectro de Bessel, nulos de J0, regra de Carson, discriminador

## Arquivos

- `enunciado_pratica_05.tex` / `.pdf`: enunciado
- `pratica_05_fm.grc`: flowgraph de referência
- `figuras/`: flowgraph e janelas de parâmetros capturados do GNU Radio Companion

## Cadeia

Signal Source (cos, samp_rate = 96 kHz) → Frequency Mod (2π·max_dev/samp_rate) → Throttle →
QT GUI Frequency Sink (FFT 8192, flat-top) e Quadrature Demod (samp_rate/2π, saída em Hz) → QT GUI Time Sink

`Frequency Mod` substitui o `WBFM Transmit`: a pré-ênfase do WBFM Transmit aumenta o desvio real
(cerca de +50 % em f_m = 2 kHz com τ = 75 µs) e o desvio dele não muda com o slider durante a execução.

## Roteiro (50 min)

1. **(0–12 min)** Montagem e níveis das componentes para β = 2,5, relativos à portadora sem modulação.
2. **(12–20 min)** Nulos da portadora: Δf = 2,405 f_m e 5,520 f_m.
3. **(20–36 min)** Banda medida pelo critério de −20 dB e erro da regra de Carson, 7 casos.
4. **(36–46 min)** Pico e período de f_i(t) − f_c na saída do discriminador.
5. **(46–50 min)** Síntese.

## Entregáveis

Relatório em PDF com as Tabelas 2 a 5 preenchidas, capturas do espectro e do Time Sink e respostas
numéricas às perguntas Q1 a Q6.
