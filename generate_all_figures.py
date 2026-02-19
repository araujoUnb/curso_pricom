#!/usr/bin/env python3
"""
generate_all_figures.py

Script para gerar todas as figuras dos slides dos módulos.
Executa todos os scripts Python encontrados em Modulo*/Code/cap*/scripts/

Uso:
    python generate_all_figures.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.absolute()

# Padrão dos diretórios de scripts
SCRIPTS_PATTERN = "Modulo*/Code/cap*/scripts/*.py"


def find_figure_scripts():
    """Encontra todos os scripts de geração de figuras."""
    scripts = []
    for modulo_dir in PROJECT_ROOT.glob("Modulo*"):
        if not modulo_dir.is_dir():
            continue
        
        code_dir = modulo_dir / "Code"
        if not code_dir.exists():
            continue
        
        for cap_dir in code_dir.glob("cap*"):
            if not cap_dir.is_dir():
                continue
            
            scripts_dir = cap_dir / "scripts"
            if not scripts_dir.exists():
                continue
            
            for script in scripts_dir.glob("*.py"):
                # Ignorar README e __pycache__
                if script.name != "README.md" and not script.name.startswith("_"):
                    scripts.append(script)
    
    return sorted(scripts)


def run_script(script_path):
    """Executa um script Python e retorna True se bem-sucedido."""
    print(f"\n{'='*70}")
    print(f"Gerando figuras: {script_path.relative_to(PROJECT_ROOT)}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            capture_output=False,
            timeout=300  # 5 minutos por script
        )
        
        if result.returncode == 0:
            print(f"✓ Sucesso: {script_path.name}")
            return True
        else:
            print(f"✗ Erro: {script_path.name} (código {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout: {script_path.name} demorou mais de 5 minutos")
        return False
    except Exception as e:
        print(f"✗ Exceção: {script_path.name}\n{e}")
        return False


def main():
    """Função principal."""
    print("\n" + "="*70)
    print("GERADOR DE FIGURAS - CURSO PRICOM")
    print("="*70)
    
    scripts = find_figure_scripts()
    
    if not scripts:
        print("\n⚠ Nenhum script de geração de figuras encontrado.")
        print("   Verifique a estrutura: Modulo*/Code/cap*/scripts/*.py")
        return 1
    
    print(f"\nEncontrados {len(scripts)} script(s) de geração:\n")
    for script in scripts:
        print(f"  - {script.relative_to(PROJECT_ROOT)}")
    
    # Executar scripts
    successful = 0
    failed = 0
    
    for script in scripts:
        if run_script(script):
            successful += 1
        else:
            failed += 1
    
    # Resumo
    print(f"\n{'='*70}")
    print(f"RESUMO:")
    print(f"  ✓ Sucesso: {successful}")
    print(f"  ✗ Falhas: {failed}")
    print(f"  Total: {len(scripts)}")
    print(f"{'='*70}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
