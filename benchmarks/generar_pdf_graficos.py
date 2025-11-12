#!/usr/bin/env python3
"""
Generador de PDF Simple - Solo Gráficos
Combina todos los gráficos PNG en un PDF sin texto adicional
Usa Pillow (PIL) en lugar de reportlab para simplicidad
"""

import os
import sys
from PIL import Image

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)
DIRECTORIO_RESULTADOS = os.path.join(RAIZ_PROYECTO, "results")

sys.path.insert(0, RAIZ_PROYECTO)


def generar_pdf_graficos():
    """Generar PDF con solo los gráficos, sin texto adicional"""

    # Asegurar que existe el directorio de resultados
    os.makedirs(DIRECTORIO_RESULTADOS, exist_ok=True)

    ruta_pdf = os.path.join(DIRECTORIO_RESULTADOS, "reporte_completo.pdf")

    # Lista de gráficos en orden
    graficos = [
        # Benchmark estándar - Dashboard combinado
        "benchmark_charts.png",
        # Gráficos individuales
        "chart_encryption_time.png",
        "chart_decryption_time.png",
        "chart_throughput.png",
        "chart_scalability.png",
        "chart_scalability_decryption.png",
        "chart_memory_usage.png",
        "chart_memory_decryption.png",
        "chart_energy_consumption.png",
        "chart_cpu_cycles.png",
        "chart_overall_performance.png",
    ]

    print("\n" + "="*80)
    print("GENERANDO PDF DE GRÁFICOS")
    print("="*80)

    # Cargar imágenes que existen
    imagenes = []
    graficos_incluidos = 0

    for grafico in graficos:
        ruta = os.path.join(DIRECTORIO_RESULTADOS, grafico)
        if os.path.exists(ruta):
            print(f"[OK] Incluyendo: {grafico}")
            try:
                img = Image.open(ruta)
                # Convertir a RGB si es necesario (PDF no soporta RGBA)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                imagenes.append(img)
                graficos_incluidos += 1
            except Exception as e:
                print(f"[SKIP] Error al cargar {grafico}: {e}")
        else:
            print(f"[SKIP] No encontrado: {grafico}")

    if graficos_incluidos == 0:
        print("\n[ERROR] No se encontraron gráficos para incluir en el PDF")
        return None

    # Generar PDF
    print(f"\nGenerando PDF con {graficos_incluidos} gráficos...")

    # La primera imagen es la base, las demás se agregan con save()
    imagenes[0].save(
        ruta_pdf,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=imagenes[1:]
    )

    print(f"\n[OK] PDF generado exitosamente: {ruta_pdf}")
    print(f"   Gráficos incluidos: {graficos_incluidos}/{len(graficos)}")
    print("="*80 + "\n")

    return ruta_pdf


if __name__ == "__main__":
    try:
        generar_pdf_graficos()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
