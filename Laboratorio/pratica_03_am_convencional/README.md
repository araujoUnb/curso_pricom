# Prática 03 — Modulação AM Convencional (DSB+C) (50 min)

## Alinhamento com cronograma

- Semanas 6–7
- Tópicos: AM com portadora, índice de modulação

## Objetivo

Implementar AM convencional (DSB+C), analisar envelope e testar demodulação por detector de envoltória.

## Pré-requisitos

- Conceito de índice de modulação ($\mu$)
- Relação entre sobre-modulação e distorção

## Roteiro (50 min)

1. **(0–10 min)** Montar gerador AM DSB+C: $s(t)=A_c[1+\mu m(t)]\cos(2\pi f_ct)$.
2. **(10–20 min)** Variar $\mu$ em três casos: submodulação, modulação ideal, sobre-modulação.
3. **(20–30 min)** Observar tempo/espectro e identificar componente de portadora e bandas laterais.
4. **(30–40 min)** Implementar detector de envoltória e comparar saída com mensagem original.
5. **(40–48 min)** Quantificar qualitativamente a distorção para $\mu>1$.
6. **(48–50 min)** Registrar conclusões.

## Entregáveis

- Prints para $\mu<1$, $\mu=1$, $\mu>1$.
- Discussão breve sobre sobre-modulação.
- Comparação entre demodulação coerente (Prática 2) e por envoltória.

## Critérios de avaliação

- Escolha correta de parâmetros
- Interpretação do índice de modulação
- Qualidade da análise comparativa
