# Capítulo 6 — Demonstrações: Formatação de Pulso, ISI e Diagrama de Olho

Material de apoio para apresentação em sala. A cadeia demonstrada é sempre a
mesma: símbolos 2-PAM → filtro formatador RRC no transmissor → canal com ruído
→ filtro casado RRC no receptor. A combinação RRC × RRC dá um cosseno
levantado, que tem ISI nula nos instantes de símbolo.

## Arquivos

- `demo_pulse_shaping_olho.grc` — flowgraph do GNU Radio (versão 3.10), o
  artefato principal para mostrar ao vivo.
- `demo_pulse_shaping_olho.py` — script Python gerado automaticamente pelo
  GNU Radio a partir do `.grc` (executável direto, sem abrir o Companion).
- `demo_interativo_matplotlib.py` — versão em NumPy/Matplotlib, com dois modos:
  janela interativa com sliders ou geração das figuras dos slides. Útil como
  alternativa caso o GNU Radio não esteja disponível.

## 1. Demonstração no GNU Radio (com sliders)

Abrir no GNU Radio Companion e executar:

```bash
gnuradio-companion demo_pulse_shaping_olho.grc
```

Sliders interativos:

- **Roll-off alpha** — controla a banda ocupada `W = (1+alpha)·Rs/2` e o
  formato do pulso. Reduzir `alpha` estreita a abertura horizontal do olho.
- **Ruído do canal (AWGN)** — adiciona ruído gaussiano; fecha a abertura
  vertical do olho e reduz a margem de decisão.

Janelas exibidas:

- **Formatação de Pulso RRC (tempo)** — forma de onda transmitida.
- **Espectro do sinal formatado** — mostra a banda mudando com `alpha`.
- **Diagrama de Olho (após filtro casado)** — `QT GUI Eye Sink`.

Parâmetro fixo: `sps = 8` amostras por símbolo. Para mudar `sps`, edite a
variável e execute novamente (mudar `sps` em tempo de execução realoca os
filtros).

Para rodar o flowgraph sem abrir o Companion:

```bash
python3 demo_pulse_shaping_olho.py
```

## 2. Demonstração em Python (com sliders)

Janela interativa com sliders de alpha, ruído e amostras por símbolo:

```bash
python3 demo_interativo_matplotlib.py
```

## 3. Regenerar as figuras dos slides

```bash
python3 demo_interativo_matplotlib.py --salvar ../../Latex-slides/figures/cap6
```

Gera `demo_gr_pulse_shaping.pdf`, `demo_gr_eye_alpha.pdf` e
`demo_gr_eye_ruido.pdf`, usados nas seções de formatação de pulso e diagrama
de olho dos slides.

## Roteiro sugerido em sala

1. Iniciar com `alpha = 1` e ruído zero: pulso largo, olho bem aberto.
2. Reduzir `alpha` até `0,2`: a banda encolhe no espectro e o olho fica mais
   estreito na horizontal — conexão direta com a sensibilidade a jitter.
3. Voltar `alpha` a `0,35` e aumentar o ruído: o olho fecha na vertical,
   ilustrando a perda de margem de decisão e o aumento da taxa de erro.
