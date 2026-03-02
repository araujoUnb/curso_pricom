# Prática 01 — FFT e Análise Espectral (50 min)

## Alinhamento com cronograma

- Semanas 2–3
- Tópicos: Série/Transformada de Fourier, análise espectral

## Objetivo

Implementar no GNU Radio um fluxo simples para observar o espectro de sinais senoidais e multitonais, relacionando domínio do tempo e da frequência.

## Pré-requisitos

- Noções básicas de senoides (amplitude, frequência, fase)
- Abrir e executar flowgraph no GNU Radio Companion (GRC)

## Roteiro (50 min)

1. **(0–5 min)** Abertura do experimento e revisão dos blocos (`Signal Source`, `Throttle`, `QT GUI Time Sink`, `QT GUI Frequency Sink`).
2. **(5–15 min)** Gerar senoide única, variar frequência e amplitude, observar mudanças no tempo e no espectro.
3. **(15–25 min)** Inserir segunda senoide e analisar composição espectral (dois picos).
4. **(25–35 min)** Ajustar parâmetros de FFT (tamanho da janela, média) e discutir resolução espectral.
5. **(35–45 min)** Inserir ruído (`Noise Source`) e analisar mascaramento de componentes fracas.
6. **(45–50 min)** Registrar capturas e consolidar conclusões.

## Entregáveis

- Captura de tela do sinal no tempo e no espectro em 3 cenários: tom único, multitom, multitom com ruído.
- Tabela curta com parâmetros usados (frequências, amplitudes, nível de ruído, FFT size).
- Resposta: “Como a resolução espectral muda ao variar FFT size?”

## Critérios de avaliação (rápido)

- Montagem funcional do flowgraph
- Coerência entre resultados e teoria
- Clareza das conclusões
