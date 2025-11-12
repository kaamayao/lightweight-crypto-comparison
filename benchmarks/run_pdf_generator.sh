#!/bin/bash
# Script para ejecutar el generador de PDF con el entorno virtual

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/venv_pdf"

# Verificar si existe el entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Entorno virtual no encontrado en $VENV_DIR"
    echo "Ejecuta primero: python -m venv venv_pdf && source venv_pdf/bin/activate && pip install reportlab"
    exit 1
fi

# Activar entorno virtual y ejecutar
source "$VENV_DIR/bin/activate"
python "$SCRIPT_DIR/generar_reporte_pdf.py"
deactivate
