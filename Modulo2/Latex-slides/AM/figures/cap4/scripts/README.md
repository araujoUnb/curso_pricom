# Scripts Python - Capítulo 4: Modulações Analógicas

Este diretório contém 10 scripts Python para geração de figuras didáticas de alta qualidade para os slides de Modulações Analógicas.

## Requisitos

```bash
pip install numpy matplotlib scipy
```

Versões testadas:
- Python: 3.8+
- NumPy: 1.20+
- Matplotlib: 3.3+
- SciPy: 1.6+

## Estrutura

### Scripts AM (01-05)

| Script | Descrição | Figuras Geradas |
|--------|-----------|-----------------|
| `01_am_dsb_sc.py` | Modulação DSB-SC completa | am_dsb_sc.pdf/png |
| `02_am_conventional.py` | AM convencional (múltiplos μ) | am_conventional.pdf/png, am_efficiency.pdf/png |
| `03_am_ssb.py` | SSB e transformada de Hilbert | am_ssb.pdf/png |
| `04_am_vsb.py` | Filtro VSB | am_vsb.pdf/png |
| `05_am_comparison.py` | Comparação completa | am_comparison.pdf/png, am_radar_comparison.pdf/png |

### Scripts FM (06-10)

| Script | Descrição | Figuras Geradas |
|--------|-----------|-----------------|
| `06_fm_bessel.py` | Funções de Bessel | fm_bessel_functions.pdf/png, fm_spectrum_beta.pdf/png, fm_bessel_table.pdf/png |
| `07_fm_bandwidth.py` | Largura de banda FM | fm_carson_rule.pdf/png, fm_nbfm_vs_wbfm.pdf/png, fm_broadcast_bandwidth.pdf/png |
| `08_fm_demodulation.py` | Discriminador FM | fm_discriminator.pdf/png, fm_discriminator_response.pdf/png |
| `09_pll_analysis.py` | Análise do PLL | pll_analysis.pdf/png, pll_locking.pdf/png |
| `10_superheterodyne.py` | Receptor superheterodino | superheterodyne_conversion.pdf/png, superheterodyne_image.pdf/png, superheterodyne_filter.pdf/png |

## Execução

### Individual

```bash
python 01_am_dsb_sc.py
```

### Todos os Scripts

**Linux/Mac:**
```bash
for script in *.py; do python "$script"; done
```

**Windows (PowerShell):**
```powershell
Get-ChildItem *.py | ForEach-Object { python $_.Name }
```

**Windows (CMD):**
```cmd
for %f in (*.py) do python "%f"
```

## Saída

Todas as figuras são salvas em `../` (diretório pai) em dois formatos:
- **PDF:** Para inclusão nos slides LaTeX (alta qualidade vetorial)
- **PNG:** Para visualização rápida (300 DPI)

## Detalhes dos Scripts

### 01_am_dsb_sc.py

**Conceitos ilustrados:**
- Sinal modulante m(t)
- Portadora cos(2πfct)
- Sinal modulado AM DSB-SC
- Envelope do sinal
- Espectros: mensagem, portadora, sinal modulado
- Identificação de USB e LSB

**Parâmetros:**
- fm = 1000 Hz
- fc = 10000 Hz
- Ac = 1.0
- Am = 0.8

**Figuras:** 1 arquivo com 6 subplots

---

### 02_am_conventional.py

**Conceitos ilustrados:**
- Envelopes para μ = 0.5, 1.0, 1.5
- Supermodulação visual
- Espectros comparativos
- Eficiência de potência vs μ

**Figuras:** 2 arquivos
1. Comparação de sinais (3×2 grid)
2. Gráfico de eficiência

---

### 03_am_ssb.py

**Conceitos ilustrados:**
- Transformada de Hilbert
- Relação m(t) ↔ m̂(t)
- Geração SSB-USB e SSB-LSB
- Cancelamento espectral

**Técnicas:**
- Usa scipy.signal.hilbert()
- Comparação temporal e espectral

**Figuras:** 1 arquivo com 5 subplots

---

### 04_am_vsb.py

**Conceitos ilustrados:**
- Filtro VSB com transição gradual
- Simetria vestigial em fc
- Comparação DSB/SSB/VSB
- Economia de banda

**Parâmetros:**
- W = 4200 Hz (vídeo típico)
- fc = 50000 Hz
- f_vest = 1250 Hz

**Figuras:** 1 arquivo com 4 subplots

---

### 05_am_comparison.py

**Conceitos ilustrados:**
- Espectros lado a lado
- Comparação sobreposta
- Gráfico radar de características
- Trade-offs visualizados

**Características comparadas:**
- Eficiência de banda
- Eficiência de potência
- Simplicidade TX/RX
- Robustez

**Figuras:** 2 arquivos
1. Comparação espectral (2×2 grid)
2. Gráfico radar polar

---

### 06_fm_bessel.py

**Conceitos ilustrados:**
- Funções de Bessel J₀ a J₅
- Espectros FM para β = 0.5, 1.0, 2.0, 5.0
- Componentes significativas (>1%)
- Tabela de valores

**Técnicas:**
- Usa scipy.special.jv()
- Cálculo de potência por componente

**Figuras:** 3 arquivos
1. Jn(β) vs β
2. Espectros para diferentes β (2×2 grid)
3. Tabela de valores

---

### 07_fm_bandwidth.py

**Conceitos ilustrados:**
- Regra de Carson: B ≈ 2(Δf + fm)
- Largura precisa (98% potência)
- Erro da regra de Carson
- NBFM vs WBFM
- FM broadcast (Δf = 75 kHz)

**Análises:**
- Comparação Carson vs precisa
- Espectros temporais e frequenciais
- Aplicação prática

**Figuras:** 3 arquivos

---

### 08_fm_demodulation.py

**Conceitos ilustrados:**
- Discriminador de frequência
- Conversão FM → AM
- Derivada do sinal FM
- Envelope e detecção
- Características de transferência

**Técnicas:**
- Diferenciação numérica
- Detector de envelope com scipy.signal.hilbert()
- Filtragem passa-baixas

**Figuras:** 2 arquivos

---

### 09_pll_analysis.py

**Conceitos ilustrados:**
- Detector de fase (sin(Δφ))
- Resposta em frequência (1ª e 2ª ordem)
- Resposta ao degrau
- Faixas de captura e lock
- Simulação de travamento

**Técnicas:**
- Usa scipy.signal para funções de transferência
- Simulação temporal simplificada
- Análise de sistemas de controle

**Figuras:** 2 arquivos

---

### 10_superheterodyne.py

**Conceitos ilustrados:**
- Conversão RF → IF
- Produtos de mistura
- Problema da frequência imagem
- Filtro de RF
- Rejeição de imagem

**Parâmetros realistas:**
- fRF = 100 MHz
- fLO = 110.7 MHz
- fIF = 10.7 MHz (padrão FM)

**Figuras:** 3 arquivos

---

## Customização

### Modificar Parâmetros

Edite as constantes no início de cada script:

```python
# Exemplo: 01_am_dsb_sc.py
fm = 1000  # Frequência da mensagem
fc = 10000  # Frequência da portadora
Ac = 1.0   # Amplitude
```

### Alterar Resolução

```python
# Para PNG
plt.savefig('figura.png', dpi=300)  # Altere dpi

# Para PDF (vetorial, sempre alta qualidade)
plt.savefig('figura.pdf')
```

### Estilo de Plots

```python
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
# Adicione mais customizações...
```

## Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
pip install numpy matplotlib scipy
```

### Figuras não aparecem
- Certifique-se de que o diretório pai `../` é gravável
- Verifique permissões de arquivo

### Avisos do Matplotlib
- Avisos sobre backend são normais
- Para evitar: `export MPLBACKEND=Agg` (Linux/Mac)

### Memória insuficiente
- Reduza `fs` (taxa de amostragem) nos scripts
- Reduza `T` (duração) da simulação

## Estatísticas

- **Total de linhas:** ~2500
- **Tempo de execução:** ~3-6s por script
- **Espaço em disco:** ~15-20 MB (todas figuras)
- **Figuras totais:** 20-25

## Contribuições

Para melhorias ou correções:
1. Mantenha o estilo consistente
2. Adicione comentários explicativos
3. Teste antes de submeter
4. Documente alterações

## Licença

© 2026 Daniel Costa Araújo - UnB

Para fins educacionais.

---

**Autor:** Prof. Daniel Costa Araújo  
**Contato:** daniel.araujo@unb.br  
**Última atualização:** Fevereiro 2026
