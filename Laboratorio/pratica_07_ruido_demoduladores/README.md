# Prática 07 — Ruído em Demoduladores AM/FM (50 min)

## Alinhamento com cronograma

- Semanas 15–16
- Tópicos: ruído em sistemas analógicos, relação sinal-ruído

## Objetivo

Comparar desempenho de demoduladores AM e FM sob diferentes níveis de ruído aditivo.

## Pré-requisitos

- Conceito de SNR
- Cadeias básicas AM e FM já implementadas

## Roteiro (50 min)

1. **(0–8 min)** Preparar dois fluxos: AM + demod e FM + demod.
2. **(8–18 min)** Inserir canal com ruído branco (`Add` + `Noise Source`) e definir nível inicial.
3. **(18–30 min)** Varredura de 3 níveis de ruído e observação da saída demodulada AM.
4. **(30–42 min)** Repetir varredura para FM com mesmos níveis.
5. **(42–48 min)** Comparar qualitativamente inteligibilidade/distorção AM vs FM.
6. **(48–50 min)** Fechamento.

## Entregáveis

- Tabela com níveis de ruído e percepção de qualidade para AM e FM.
- Evidências (prints) em pelo menos dois níveis de ruído.
- Conclusão técnica sobre robustez relativa AM/FM no experimento.

## Critérios de avaliação

- Procedimento comparativo justo
- Registro organizado dos cenários
- Conclusão consistente com observações
