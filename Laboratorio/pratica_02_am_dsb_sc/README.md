# Prática 02 — Modulação AM DSB-SC (50 min)

## Alinhamento com cronograma

- Semanas 4–5
- Tópicos: Modulação em amplitude, DSB-SC

## Objetivo

Construir um modulador e um demodulador coerente DSB-SC no GNU Radio, avaliar o
efeito do erro de fase do oscilador local e determinar o intervalo válido de
frequência de corte do filtro passa-baixas.

## Pré-requisitos

- Conceito de portadora e sinal mensagem
- Multiplicação no domínio do tempo
- Identidade do produto de cossenos

## Parâmetros

`samp_rate = 48000`, `fc = 5000`, `fm = 1000`, amplitudes unitárias.

Com esses valores a mensagem fica em 1 kHz, as bandas laterais em 4 e 6 kHz e o
termo de frequência dupla da demodulação em `2*fc ± fm` = 9 e 11 kHz. O critério
do filtro passa-baixas, `fm < f_corte < 2*fc - fm`, corresponde a
`1000 < f_corte < 9000` Hz e é verificável dentro da faixa de amostragem.

## Roteiro (50 min)

1. **(0–12 min)** Etapa 1: modulador DSB-SC e verificação da ausência de
   componente em `fc`.
2. **(12–22 min)** Etapa 2: variação de `fm` e registro das bandas laterais,
   incluindo o caso `fm >= fc`.
3. **(22–38 min)** Etapa 3: demodulador coerente com oscilador local em
   quadratura e varredura do erro de fase de 0° a 90°.
4. **(38–46 min)** Etapa 4: varredura da frequência de corte do filtro em 500,
   1500, 3000, 9500 e 12000 Hz.
5. **(46–50 min)** Etapa 5: capturas de tela e consolidação das tabelas.

## Entregáveis

Relatório em PDF contendo:

- Captura do espectro do sinal modulado, com as bandas laterais identificadas e
  a ausência da portadora.
- Captura do sinal demodulado com fase 0° e com fase 90°.
- Captura da saída demodulada com corte acima de `2*fc - fm`.
- Tabelas 2, 3 e 4 preenchidas.
- Respostas às 5 questões.

## Critérios de avaliação

- Fluxograma corretamente implementado
- Identificação correta das bandas laterais
- Concordância entre a amplitude medida e `0,5·cos(θ)`
- Interpretação do critério de corte do filtro passa-baixas

## Arquivos

- `enunciado_pratica_02.tex` / `.pdf` — enunciado do aluno
- `pratica_02_am_dsbsc.grc` — fluxograma de referência
- `../gabaritos_professor/pratica_02_am_dsb_sc/` — gabarito e critérios
- `../Codigos/pratica_02_gabarito/` — validação numérica sobre o GNU Radio
