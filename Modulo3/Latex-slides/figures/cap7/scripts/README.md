# Scripts Python - Capítulo 7: Conversão Analógico-Digital

Este diretório é reservado para scripts Python de geração de figuras dos slides do Capítulo 7.

## Requisitos

```bash
pip install numpy matplotlib scipy
```

## Convenção sugerida de scripts

| Script | Descrição | Figuras esperadas |
|--------|-----------|-------------------|
| `01_sampling_aliasing.py` | Réplicas espectrais e aliasing | sampling_aliasing.pdf/png |
| `02_quantization_noise.py` | Quantização uniforme e erro | quantization_noise.pdf/png |
| `03_sqnr_vs_bits.py` | Curva SQNR vs número de bits | sqnr_vs_bits.pdf/png |
| `04_companding_curves.py` | Curvas A-law e \mu-law | companding_curves.pdf/png |

## Execução

### Linux/Mac
```bash
for script in *.py; do python "$script"; done
```

### Windows (PowerShell)
```powershell
Get-ChildItem *.py | ForEach-Object { python $_.Name }
```

As figuras devem ser salvas no diretório pai (`../`) em PDF e PNG.
