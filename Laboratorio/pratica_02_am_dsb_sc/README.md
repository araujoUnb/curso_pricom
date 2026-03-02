# Prática 02 — Modulação AM DSB-SC (50 min)

## Alinhamento com cronograma

- Semanas 4–5
- Tópicos: Modulação em amplitude, DSB-SC

## Objetivo

Construir um modulador e demodulador coerente DSB-SC no GNU Radio e avaliar recuperação de mensagem.

## Pré-requisitos

- Conceito de portadora e sinal mensagem
- Multiplicação no domínio do tempo

## Roteiro (50 min)

1. **(0–8 min)** Configurar mensagem senoidal de baixa frequência e portadora de frequência mais alta.
2. **(8–18 min)** Implementar modulação DSB-SC com bloco de multiplicação.
3. **(18–28 min)** Visualizar espectro e identificar bandas laterais e ausência de linha de portadora.
4. **(28–40 min)** Implementar demodulação coerente (multiplicação por oscilador local + LPF).
5. **(40–47 min)** Testar erro de sincronismo de fase/frequência no oscilador local.
6. **(47–50 min)** Consolidar observações para relatório.

## Entregáveis

- Diagrama do flowgraph (print).
- Comparação entre sinal mensagem original e recuperado.
- Comentário sobre efeito de erro de fase na demodulação coerente.

## Critérios de avaliação

- Fluxo corretamente implementado
- Identificação correta das bandas laterais
- Interpretação dos efeitos de sincronismo
