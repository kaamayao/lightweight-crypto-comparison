#!/usr/bin/env python3
"""
Wrapper para ejecutar el generador de PDF con el entorno virtual correcto
Este script NO requiere que reportlab esté instalado globalmente
"""

import os
import sys
import subprocess

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)
VENV_DIR = os.path.join(RAIZ_PROYECTO, "venv_pdf")
PYTHON_VENV = os.path.join(VENV_DIR, "bin", "python")

def main():
    """Ejecutar el generador de PDF usando el entorno virtual"""

    # Verificar si existe el entorno virtual
    if not os.path.exists(VENV_DIR):
        print("❌ Error: Entorno virtual no encontrado")
        print(f"\nNo se encontró el entorno virtual en: {VENV_DIR}")
        print("\nPara crear el entorno virtual e instalar reportlab:")
        print("  python -m venv venv_pdf")
        print("  source venv_pdf/bin/activate")
        print("  pip install reportlab")
        print("  deactivate")
        return 1

    if not os.path.exists(PYTHON_VENV):
        print("❌ Error: Python del entorno virtual no encontrado")
        print(f"\nNo se encontró: {PYTHON_VENV}")
        return 1

    # Ejecutar el generador de PDF usando el Python del entorno virtual
    script_generador = os.path.join(DIRECTORIO_SCRIPT, "generar_reporte_pdf.py")

    try:
        resultado = subprocess.run(
            [PYTHON_VENV, script_generador],
            check=True
        )
        return resultado.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar el generador de PDF: {e}")
        return e.returncode
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
