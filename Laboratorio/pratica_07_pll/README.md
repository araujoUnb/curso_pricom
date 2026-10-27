# Prática 07 — PLL como demodulador FM (50 min)

## Alinhamento com cronograma

- Semanas 14–15
- Tópicos: PLL de 2.ª ordem, frequência natural, resposta ao degrau, limite do VCO, ruído

## Arquivos

- `enunciado_pratica_07.tex` / `.pdf`: enunciado
- `pratica_07_pll.grc`: flowgraph de referência
- `figuras/`: flowgraph e janelas de parâmetros capturados do GNU Radio Companion

## Cadeia

Signal Source (48 kHz) → Frequency Mod (2π·max_dev/samp_rate) → Throttle → Add (+ Noise Source) →
- PLL Frequency Detector (loop_bw, ±2π·f_lim/samp_rate, f_lim = 500 Hz) → Multiply Const samp_rate/(2π·max_dev)
- Quadrature Demod (samp_rate/(2π·max_dev)): referência da Prática 05

O bloco usa ζ = √2/2 e f_n ≈ loop_bw·f_s/π. A saída do PLL é a mensagem filtrada por
|H(f)|² = 1/(1 + (f/f_n)⁴).

## Roteiro (50 min)

1. **(0–10 min)** Montagem do transmissor e dos dois demoduladores.
2. **(10–22 min)** Resposta em frequência: A = L_PLL − L_Q em f_m contra −10log[1 + (f_m/f_n)⁴].
3. **(22–34 min)** Degrau de frequência com mensagem quadrada: sobressinal contra 4,32 % e tempo de pico contra 1/(√2 f_n).
4. **(34–40 min)** Limite do VCO: pico da saída contra min(1, f_lim/Δf).
5. **(40–50 min)** Ruído: ganho de relação tom-piso G = R_PLL − R_Q contra 10log[(1 + (f_r/f_n)⁴)/(1 + (f_m/f_n)⁴)].

## Entregáveis

Relatório no modelo do SIGAA com as Tabelas 2 a 5, capturas do Time Sink na Etapa 3 e do Frequency Sink na Etapa 5 e respostas numéricas Q1 a Q6.
