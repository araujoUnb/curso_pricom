# Prática 08 — Conversão A/D: Amostragem, Aliasing e Quantização PCM (100 min)

## Alinhamento com cronograma

- Semanas 17–18
- Módulo 3 — conversão analógico-digital: amostragem, Nyquist, aliasing e quantização PCM

## Objetivo

Cobrir a cadeia completa de conversão A/D no GNU Radio: demonstrar aliasing ao variar a taxa de amostragem (Parte I) e implementar um quantizador PCM medindo o SQNR em função do número de bits (Parte II).

## Pré-requisitos

- Teorema de Nyquist e interpretação de espectros discretizados
- Quantização uniforme: passo `Delta = Vpp/2^n`, ruído `Pq = Delta^2/12`, regra `SQNR = 1,76 + 6,02n` dB

## Flowgraphs

- `Codigos/pratica_08_amostragem_aliasing.grc` — Parte I (decimação com e sem filtro anti-aliasing)
- `Codigos/pratica_08_quantizacao_pcm.grc` — Parte II (quantizador + medição de SQNR)
- `Codigos/quantizer_epy.py` — código do Embedded Python Block (quantizador uniforme mid-rise)

## Roteiro (100 min)

### Parte I — Amostragem e aliasing (0–50 min)
1. Flowgraph base com `Keep 1 in N`.
2. Verificação de Nyquist nos cenários A–F.
3. Cálculo e confirmação da frequência de aliasing.
4. Filtro anti-aliasing antes da decimação.
5. Sinal multitonal.

### Parte II — Quantização PCM (50–100 min)
6. Montagem do quantizador com Embedded Python Block; formas de onda original, quantizada e erro.
7. Medição do SQNR no GNU Radio com a cadeia Multiply → Moving Average → Divide → Log10 → Number Sink.
8. Espectro do ruído de quantização (piso sobe ~6 dB a cada bit removido).

## Entregáveis

- Capturas espectrais dos cenários A e C e antes/depois do filtro anti-aliasing.
- Tabela de frequências reais vs aparentes (aliasing).
- Capturas das formas de onda quantizadas para n = 3 e n = 8 bits.
- Tabela de SQNR teórico vs medido.
- Respostas numéricas às 6 questões.

## Critérios de avaliação

- Configuração correta dos cenários de amostragem e do quantizador
- Evidência clara do aliasing e do ruído de quantização
- Concordância entre experimento e teoria (Nyquist e regra dos 6 dB/bit)

## Validação automática

`/usr/bin/python3 Codigos/pratica_08_gabarito.py` reproduz as duas partes em modo headless (GNU Radio 3.10), gerando figuras, CSVs e `relatorio.txt`.
