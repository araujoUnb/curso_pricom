# Prática 04 — Modulação SSB (50 min)

## Alinhamento com cronograma

- Semanas 8–9
- Tópicos: SSB e eficiência espectral

## Objetivo

Gerar sinal SSB por filtragem e pela transformada de Hilbert no GNU Radio,
comparar a ocupação de banda com o DSB-SC e medir o efeito de um erro de
frequência no oscilador local.

## Parâmetros (2026/2)

| Variável | Valor | Observação |
|---|---|---|
| `samp_rate` | 64 000 Hz | |
| `fc` | 16 000 Hz | |
| `fm` | 3 000 Hz | slider de 1 500 a 6 000 Hz, passo 500 |
| `delta_f` | 0 Hz | slider de −500 a 500 Hz, passo 25 |
| `bw_trans` | 800 Hz | banda de transição dos passa-banda |
| `bw_trans_lp` | 600 Hz | banda de transição do passa-baixas |
| `n_hilb` | 101 | coeficientes do filtro de Hilbert |
| `d_align` | 224 | atraso de grupo BPF + LPF, em amostras |

Componentes esperadas: LSB em 13 kHz, USB em 19 kHz, sem componente em 16 kHz.

## Pré-requisitos

- Conceito de banda lateral superior/inferior
- Noção de filtro passa-faixa e do método de Hilbert

## Roteiro (50 min)

1. **(0–10 min)** Gerar DSB-SC e identificar as bandas laterais no espectro.
2. **(10–18 min)** Filtro passa-banda para a banda lateral superior.
3. **(18–24 min)** Filtro passa-banda para a banda lateral inferior.
4. **(24–34 min)** Demodulação coerente com compensação do atraso de grupo.
5. **(34–40 min)** Varredura de `delta_f` e medida do deslocamento espectral.
6. **(40–50 min)** Geração por Hilbert e comparação da supressão.

## Entregáveis

- Evidência espectral das bandas laterais superior e inferior.
- Comparação objetiva de banda ocupada entre DSB-SC e SSB.
- Tabela do efeito de `delta_f` sobre a frequência recuperada.
- Comparação numérica da supressão obtida por filtragem e por Hilbert.

## Critérios de avaliação

- Geração correta de SSB pelos dois métodos
- Validação espectral consistente, com níveis em dB
- Discussão técnica objetiva

## Pontos de atenção do professor

- O ramo em fase do método de Hilbert deve sair da saída `re` do bloco
  `Complex To Float`, e não da fonte da mensagem. Ligando na fonte, o
  cancelamento falha por completo e as duas bandas laterais permanecem.
- A `QT GUI Time Sink` da Etapa 4 deve ficar com `Autoscale = No`, caso
  contrário o fator de escala 0,5 da demodulação coerente não fica visível.
- Sem o bloco `Delay` de 224 amostras, as curvas da Time Sink aparecem
  deslocadas horizontalmente. Vários relatórios de 2026/1 atribuíram esse
  deslocamento a "erro de fase" em vez de atraso de grupo.

## Valores de referência medidos no GNU Radio

| Grandeza | Valor |
|---|---|
| Supressão da banda indesejada por filtragem | −65,9 dB |
| Supressão da banda indesejada por Hilbert | −74,2 dB |
| Amplitude do sinal demodulado | 0,4998 |
| Pico demodulado com `delta_f` = 100 Hz | 2 900 Hz |
| Pico demodulado com `delta_f` = 300 Hz | 2 700 Hz |
