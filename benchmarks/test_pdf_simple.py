#!/usr/bin/env python3
"""
Test simple para verificar que reportlab funciona correctamente
"""

import os
import sys

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)
DIRECTORIO_RESULTADOS = os.path.join(RAIZ_PROYECTO, "results")

sys.path.insert(0, RAIZ_PROYECTO)

print("Testing PDF generation with reportlab...")
print(f"Results directory: {DIRECTORIO_RESULTADOS}")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch

    print("✅ reportlab imported successfully")

    # Crear directorio de resultados si no existe
    os.makedirs(DIRECTORIO_RESULTADOS, exist_ok=True)

    # Crear PDF de prueba
    ruta_pdf = os.path.join(DIRECTORIO_RESULTADOS, "test.pdf")
    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)

    story = []
    styles = getSampleStyleSheet()

    story.append(Paragraph("Test PDF - Criptografía Ligera", styles['Title']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Este es un PDF de prueba generado con reportlab.", styles['Normal']))

    doc.build(story)

    print(f"✅ PDF de prueba generado exitosamente: {ruta_pdf}")

    # Verificar que el archivo existe y tiene contenido
    if os.path.exists(ruta_pdf) and os.path.getsize(ruta_pdf) > 0:
        print(f"✅ Archivo PDF válido (tamaño: {os.path.getsize(ruta_pdf)} bytes)")
        print("\n🎉 ¡Todo funciona correctamente!")
    else:
        print("❌ El archivo PDF se creó pero está vacío o corrupto")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\nPara instalar reportlab:")
    print("  python -m venv venv_pdf")
    print("  source venv_pdf/bin/activate")
    print("  pip install reportlab")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
