# Scripts Cap 5: Ruído em Sistemas de Comunicação

Scripts Python para gerar figuras do Capítulo 5 (Efeito do Ruído).

## Requisitos

```bash
pip install numpy matplotlib
```

## Scripts

| Script | Figura | Descrição |
|--------|--------|-----------|
| `11_snr_comparison.py` | snr_comparison.pdf | $(S/N)_o$ vs. $\gamma$ (banda base, DSB-SC, SSB, AM, FM) |
| `12_noise_figure_cascade.py` | noise_figure_cascade.pdf | $F_{tot}$ vs. $G_1$ e ordem dos estágios (Friis) |
| `13_preemphasis_deemphasis.py` | preemphasis_deemphasis.pdf | Filtros pré/pós-ênfase FM |
| `14_fm_threshold.py` | fm_threshold.pdf | Efeito de limiar em FM |
| `15_thermal_noise_psd.py` | thermal_noise_psd.pdf | PSD do ruído térmico |

## Execução

Use o ambiente virtual do projeto (`.venv` na raiz do repositório):

**Windows (PowerShell):**
```powershell
& "..\..\..\..\.venv\Scripts\python.exe" 11_snr_comparison.py
& "..\..\..\..\.venv\Scripts\python.exe" 12_noise_figure_cascade.py
& "..\..\..\..\.venv\Scripts\python.exe" 13_preemphasis_deemphasis.py
& "..\..\..\..\.venv\Scripts\python.exe" 14_fm_threshold.py
& "..\..\..\..\.venv\Scripts\python.exe" 15_thermal_noise_psd.py
```

Ou, a partir da raiz PRICOM com `.venv` ativado:
```powershell
.venv\Scripts\Activate.ps1
cd Modulo2\tpl-slides-main\figures\cap5\scripts
python 11_snr_comparison.py
python 12_noise_figure_cascade.py
python 13_preemphasis_deemphasis.py
python 14_fm_threshold.py
python 15_thermal_noise_psd.py
```

As figuras são salvas em `../` (figures/cap5/). Os slides usam essas figuras quando os PDFs existem; caso contrário exibem um placeholder.
