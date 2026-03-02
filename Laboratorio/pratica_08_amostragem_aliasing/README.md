# Prática 08 — Amostragem e Aliasing (50 min)

## Alinhamento com cronograma

- Semanas 17–18
- Tópicos: amostragem, Nyquist, aliasing

## Objetivo

Demonstrar aliasing no GNU Radio ao variar taxa de amostragem em relação à banda do sinal de entrada.

## Pré-requisitos

- Teorema de Nyquist
- Interpretação de espectros discretizados

## Roteiro (50 min)

1. **(0–8 min)** Configurar sinal de teste (tom único e, opcionalmente, multitom).
2. **(8–18 min)** Cenário A: amostragem acima de Nyquist (referência sem aliasing).
3. **(18–28 min)** Cenário B: amostragem próxima de Nyquist (limite prático).
4. **(28–38 min)** Cenário C: abaixo de Nyquist (aliasing evidente no espectro).
5. **(38–45 min)** Inserir filtro anti-aliasing antes da amostragem e repetir cenário C.
6. **(45–50 min)** Consolidar evidências e conclusões.

## Entregáveis

- Três capturas espectrais (A, B, C) e uma com anti-aliasing.
- Tabela de frequências reais vs frequências aparentes após aliasing.
- Resposta: “Como o filtro anti-aliasing alterou o resultado?”

## Critérios de avaliação

- Correta configuração dos cenários de amostragem
- Evidência clara do aliasing
- Relação entre experimento e teorema
