#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los benchmarks
Ejecuta benchmarks con diferentes perfiles de recursos:
1. Benchmark estándar (PC sin restricciones)
2. Benchmark con restricciones (simulación ESP32, Arduino, sensores, etc.)
"""

import os
import sys
import time

# Configuración de rutas
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)

sys.path.insert(0, RAIZ_PROYECTO)


def imprimir_banner(titulo):
    """Imprimir un banner llamativo para cada sección"""
    ancho = 100
    print("\n" + "=" * ancho)
    print("=" * ancho)
    print(f"  {titulo.center(ancho-4)}")
    print("=" * ancho)
    print("=" * ancho + "\n")


def imprimir_resumen_final(resultados_estandar, resultados_restringidos, tiempo_total):
    """Imprimir un resumen final de todos los benchmarks"""
    imprimir_banner("RESUMEN FINAL - TODOS LOS BENCHMARKS")

    print("RESULTADOS GENERALES:\n")

    # Benchmark estándar
    print("1. BENCHMARK ESTÁNDAR (PC SIN RESTRICCIONES):")
    if resultados_estandar:
        num_perfiles = len(resultados_estandar)
        total_pruebas = sum(len(r["resultados"]) for r in resultados_estandar.values())
        print(f"   - Perfiles ejecutados: {num_perfiles}")
        print(f"   - Total de pruebas: {total_pruebas}")
        print("   - Gráficos: results/benchmark_charts_sin_restricciones.png")
        print("   [OK] Completado exitosamente")
    else:
        print("   [ERROR] No completado")

    # Benchmark restringido
    print("\n2. BENCHMARK RESTRINGIDO (DISPOSITIVOS IoT):")
    if resultados_restringidos:
        num_perfiles = len(resultados_restringidos)
        total_pruebas = sum(len(r["resultados"]) for r in resultados_restringidos.values())
        print(f"   - Perfiles simulados: {num_perfiles}")

        # Listar perfiles ejecutados
        perfiles_nombres = [r["config"]["descripcion"] for r in resultados_restringidos.values()]
        print("   - Dispositivos:")
        for nombre in perfiles_nombres:
            print(f"     * {nombre}")

        print(f"   - Total de pruebas: {total_pruebas}")
        print("   - Gráficos: results/benchmark_charts_*.png (uno por perfil)")
        print("   [OK] Completado exitosamente")
    else:
        print("   [ERROR] No completado")

    print("\n" + "=" * 100)
    print("TODOS LOS RESULTADOS GUARDADOS EN: results/")
    print("=" * 100)

    # Contar éxitos
    exitosos = sum([
        1 if resultados_estandar else 0,
        1 if resultados_restringidos else 0
    ])
    total = 2

    print(f"\nESTADO FINAL: {exitosos}/{total} benchmarks completados exitosamente")
    print(f"TIEMPO TOTAL: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")

    if exitosos == total:
        print("\n[OK] TODOS LOS BENCHMARKS COMPLETADOS!")
    else:
        print("\n[WARNING] Algunos benchmarks fallaron. Revisa los errores arriba.")


def generar_pdf_reporte():
    """Generar reporte PDF automáticamente con todos los gráficos"""
    print("\n" + "=" * 100)
    print("GENERACIÓN DE REPORTE PDF")
    print("=" * 100)
    print("\nGenerando reporte PDF con todos los gráficos...")

    try:
        from benchmarks.generar_pdf_graficos import generar_pdf_graficos

        ruta_pdf = generar_pdf_graficos()

        if ruta_pdf:
            print(f"\n[OK] Reporte PDF generado exitosamente: {ruta_pdf}")
            print("     El reporte incluye todos los gráficos generados durante los benchmarks")
            print("     Un gráfico por página para fácil visualización")
        else:
            print("\n[ERROR] Error al generar PDF")

    except ImportError as e:
        print(f"\n[ERROR] Error: Falta la biblioteca Pillow")
        print("\nPara instalar Pillow:")
        print("  pip install Pillow")
        print(f"\nDetalle del error: {e}")
    except Exception as e:
        print(f"\n[ERROR] Error al generar PDF: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal para ejecutar todos los benchmarks"""
    inicio_total = time.time()

    # Banner inicial
    print("\n" + "=" * 100)
    print("=" * 100)
    print("  SUITE COMPLETA DE BENCHMARKS - CRIPTOGRAFÍA LIGERA".center(100))
    print("  DES vs AES-128".center(100))
    print("=" * 100)
    print("=" * 100)

    print("\nSe ejecutarán 2 tipos de benchmarks:")
    print("   1. Rendimiento estándar (PC sin restricciones)")
    print("   2. Dispositivos con restricciones (4 perfiles IoT)")
    print("\nPerfiles de dispositivos a simular:")
    print("   - PC de gama alta / Servidor")
    print("   - Dispositivo IoT gama media (ESP32, Arduino Due)")
    print("   - Dispositivo IoT gama baja (ESP8266, Arduino Uno)")
    print("   - Dispositivo ultra restringido (sensores, RFID)")

    input("\nPresiona ENTER para comenzar...")

    resultados_estandar = None
    resultados_restringidos = None

    # Importar la función de benchmark
    from benchmarks.benchmark import ejecutar_pruebas

    # 1. Benchmark estándar (sin restricciones)
    imprimir_banner("BENCHMARK 1/2: RENDIMIENTO ESTÁNDAR (PC)")
    print("Modo: PC/Servidor sin restricciones de recursos")
    print("Propósito: Medir el rendimiento máximo de los algoritmos\n")

    tiempo_inicio = time.time()
    try:
        resultados_estandar = ejecutar_pruebas(perfiles=None, generar_graficos_flag=True)
        tiempo_transcurrido = time.time() - tiempo_inicio
        print(f"\n[OK] Benchmark estándar completado en {tiempo_transcurrido:.2f} segundos")
    except Exception as e:
        print(f"\n[ERROR] Error en benchmark estándar: {e}")
        import traceback
        traceback.print_exc()

    # 2. Benchmark restringido (4 perfiles IoT)
    imprimir_banner("BENCHMARK 2/2: DISPOSITIVOS CON RESTRICCIONES (IoT)")
    print("Modo: Simulación de 4 perfiles de dispositivos IoT")
    print("Propósito: Evaluar rendimiento en hardware con recursos limitados\n")

    tiempo_inicio = time.time()
    try:
        perfiles = ["high_end_pc", "mid_range_iot", "low_end_iot", "ultra_constrained"]
        resultados_restringidos = ejecutar_pruebas(perfiles=perfiles, generar_graficos_flag=True)
        tiempo_transcurrido = time.time() - tiempo_inicio
        print(f"\n[OK] Benchmark restringido completado en {tiempo_transcurrido:.2f} segundos")
    except Exception as e:
        print(f"\n[ERROR] Error en benchmark restringido: {e}")
        import traceback
        traceback.print_exc()

    # Resumen final
    tiempo_total = time.time() - inicio_total
    imprimir_resumen_final(resultados_estandar, resultados_restringidos, tiempo_total)

    # Generar PDF automáticamente
    generar_pdf_reporte()

    print("\n" + "=" * 100)
    print("SUITE DE BENCHMARKS FINALIZADA")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Benchmarks interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
