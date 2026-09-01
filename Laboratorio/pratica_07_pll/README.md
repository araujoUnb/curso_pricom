# Prática 07 — Phase-Locked Loop (PLL) (50 min)

## Alinhamento com cronograma

- Semanas 14–15
- Tópicos: PLL e sincronismo

## Objetivo

Simular um PLL para recuperação de fase/frequência e analisar condições de captura e rastreamento.

## Pré-requisitos

- Conceito de erro de fase
- Noção de malha de realimentação

## Roteiro (50 min)

1. **(0–8 min)** Apresentar estrutura do PLL (detector de fase, filtro de malha, VCO/NCO).
2. **(8–20 min)** Montar modelo simplificado no GNU Radio com NCO controlado.
3. **(20–30 min)** Introduzir offset de frequência e observar aquisição (lock).
4. **(30–40 min)** Variar ganho/largura da malha e comparar tempo de captura e estabilidade.
5. **(40–47 min)** Inserir ruído e avaliar robustez do lock.
6. **(47–50 min)** Registro dos resultados.

## Entregáveis

- Evidência temporal do erro de fase convergindo (quando houver lock).
- Tabela curta com parâmetros de malha e comportamento observado.
- Discussão: compromisso entre rapidez de captura e sensibilidade a ruído.

## Critérios de avaliação

- Implementação funcional da malha
- Interpretação correta de lock/unlock
- Qualidade da análise paramétrica
