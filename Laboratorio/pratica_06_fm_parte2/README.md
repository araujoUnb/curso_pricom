# Prática 06 — Demodulação FM: Detector de Inclinação e Discriminador (50 min)

## Alinhamento com cronograma

- Semanas 12–13
- Tópicos: demodulação FM, conversão FM-AM, robustez ao ruído

## Objetivo

Construir dois demoduladores FM baseados em conversão FM-AM, o detector de
inclinação simples e o discriminador balanceado, e comparar ambos com o bloco
`WBFM Receive` usado como referência.

## Pré-requisitos

- Prática 05 — modulador FM montado e funcionando
- Frequência instantânea e desvio de frequência
- Resposta em frequência de filtros passa-faixa

## Roteiro (50 min)

1. **(0–6 min)** Reaproveitar o transmissor FM da Prática 05.
2. **(6–22 min)** Montar o detector de inclinação simples com filtro passa-faixa
   deslocado seguido de detector de envelope e bloqueio CC.
3. **(22–36 min)** Montar o discriminador balanceado com dois filtros sintonizados
   em $f_c \pm \Delta f$ e subtração das envoltórias.
4. **(36–44 min)** Comparar as duas saídas com o `WBFM Receive` no `Time Sink`.
5. **(44–50 min)** Avaliar a robustez ao ruído variando `noise_amp` e registrar
   o limiar de cada demodulador.

## Entregáveis

- Captura do `Time Sink` com mensagem original, detector de inclinação e
  discriminador balanceado.
- Captura do `Time Sink` com as quatro formas de onda, incluindo `WBFM Receive`.
- Tabela com os limiares de `noise_amp` para cada demodulador.
- Relatório em PDF.

## Critérios de avaliação

- Funcionamento dos dois demoduladores construídos
- Coerência da comparação com o demodulador de referência
- Organização dos dados e das capturas
