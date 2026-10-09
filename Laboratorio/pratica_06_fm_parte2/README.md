# Prática 06 — Demodulação FM: detector de inclinação e discriminador balanceado (50 min)

## Alinhamento com cronograma

- Semanas 12–13
- Tópicos: conversão FM-AM, cancelamento de harmônicas pares, limiar do FM

## Arquivos

- `enunciado_pratica_06.tex` / `.pdf`: enunciado
- `pratica_06_fm_parte2.grc`: flowgraph de referência
- `figuras/`: flowgraph e janelas de parâmetros capturados do GNU Radio Companion

## Cadeia

Signal Source (480 kHz) → Frequency Mod (2π·max_dev/samp_rate) → Throttle → Add (+ Noise Source) →
- `bpf_pos` [Δf, 5Δf], transição 4Δf → Complex to Mag → DC Blocker → Low Pass (decimação 10): detector de inclinação
- `bpf_pos` − `bpf_neg` [−5Δf, −Δf] → DC Blocker → Low Pass: discriminador balanceado
- Quadrature Demod (samp_rate/(2π·max_dev)) → Low Pass: referência da Prática 05

Os filtros foram reprojetados: f_i ∈ [−Δf, Δf] percorre a parte curva da rampa de `bpf_pos`,
de modo que o detector simples gera 2.ª harmônica (−12 dB) e o balanceado a cancela (abaixo de −100 dB),
mantendo a 3.ª em −30 dB e dobrando a amplitude (+6 dB).

## Roteiro (50 min)

1. **(0–6 min)** Transmissor da Prática 05 com ruído.
2. **(6–18 min)** Detector de inclinação: amplitude, H2 − H1, H3 − H1.
3. **(18–28 min)** Discriminador balanceado: mesmas medidas.
4. **(28–34 min)** Referência de quadratura.
5. **(34–48 min)** Relação tom-piso R em função de noise_amp e C/N na banda de Carson.
6. **(48–50 min)** Síntese.

## Entregáveis

Relatório em PDF com as Tabelas 2 e 3, capturas sem ruído e com noise_amp = 1,0 e respostas numéricas Q1 a Q6.

## Gabarito

`Laboratorio/Codigos/pratica_06_gabarito/codigos/pratica_06_gabarito.py`, validado no GNU Radio 3.10.12.
