#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los benchmarks
Ejecuta secuencialmente:
1. Benchmark estándar (PC sin restricciones)
2. Benchmark con restricciones (simulación ESP32, Arduino, etc.)
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


def ejecutar_benchmark_estandar():
    """Ejecutar benchmark estándar (PC sin restricciones)"""
    imprimir_banner("BENCHMARK 1/2: RENDIMIENTO ESTÁNDAR (PC)")
    print("Hardware: PC/Servidor sin restricciones")
    print("Propósito: Medir rendimiento máximo de los algoritmos\n")

    tiempo_inicio = time.time()

    try:
        from benchmarks.benchmark import ejecutar_pruebas
        resultados = ejecutar_pruebas(perfiles=None, generar_graficos_flag=True)
        tiempo_transcurrido = time.time() - tiempo_inicio

        print(f"\n[OK] Benchmark estándar completado en {tiempo_transcurrido:.2f} segundos")
        return resultados
    except Exception as e:
        print(f"\n[ERROR] Error en benchmark estándar: {e}")
        import traceback
        traceback.print_exc()
        return None


def ejecutar_benchmark_restringido():
    """Ejecutar benchmark con restricciones (ESP32, Arduino, etc.)"""
    imprimir_banner("BENCHMARK 2/2: DISPOSITIVOS CON RESTRICCIONES (IoT)")
    print("Hardware: Simulación de ESP32, ESP8266, Arduino, sensores")
    print("Propósito: Evaluar rendimiento en dispositivos con recursos limitados\n")

    tiempo_inicio = time.time()

    try:
        from benchmarks.benchmark import ejecutar_pruebas
        # Ejecutar con todos los perfiles restringidos
        perfiles = ["high_end_pc", "mid_range_iot", "low_end_iot", "ultra_constrained"]
        resultados = ejecutar_pruebas(perfiles=perfiles, generar_graficos_flag=True)
        tiempo_transcurrido = time.time() - tiempo_inicio

        print(f"\n[OK] Benchmark restringido completado en {tiempo_transcurrido:.2f} segundos")
        return resultados
    except Exception as e:
        print(f"\n[ERROR] Error en benchmark restringido: {e}")
        import traceback
        traceback.print_exc()
        return None


def imprimir_resumen_final(resultados):
    """Imprimir un resumen final de todos los benchmarks"""
    imprimir_banner("RESUMEN FINAL - TODOS LOS BENCHMARKS")

    print("RESULTADOS GENERALES:\n")

    print("1. BENCHMARK ESTÁNDAR (PC):")
    if resultados['estandar']:
        num_perfiles = len(resultados['estandar'])
        print(f"   - Perfiles ejecutados: {num_perfiles}")
        print("   - Gráficos generados en: results/benchmark_charts_*.png")
        print("   - Algoritmos probados: DES, AES-128")
        print("   [OK] Completado exitosamente")
    else:
        print("   [ERROR] No completado")

    print("\n2. BENCHMARK RESTRINGIDO (IoT):")
    if resultados['restringido']:
        num_perfiles = len(resultados['restringido'])
        print(f"   - Perfiles simulados: {num_perfiles} (PC gama alta, ESP32, ESP8266, sensores)")
        print("   - Gráficos generados en: results/benchmark_charts_*.png")
        print("   [OK] Completado exitosamente")
    else:
        print("   [ERROR] No completado")

    print("\n" + "=" * 100)
    print("TODOS LOS RESULTADOS GUARDADOS EN: results/")
    print("=" * 100)

    # Contar éxitos
    exitosos = sum(1 for r in resultados.values() if r is not None)
    total = len(resultados)

    print(f"\nESTADO FINAL: {exitosos}/{total} benchmarks completados exitosamente")

    if exitosos == total:
        print("[OK] TODOS LOS BENCHMARKS COMPLETADOS!")
    else:
        print("[WARNING] Algunos benchmarks fallaron. Revisa los errores arriba.")


def generar_pdf_si_se_desea(resultados):
    """Preguntar al usuario si desea generar reporte PDF"""
    print("\n" + "=" * 100)
    print("GENERACIÓN DE REPORTE PDF")
    print("=" * 100)
    print("\n¿Deseas generar un reporte PDF completo con todos los resultados?")
    print("El reporte incluirá:")
    print("  - Resumen ejecutivo")
    print("  - Tablas de resultados de todos los benchmarks")
    print("  - Todos los gráficos generados")
    print("  - Recomendaciones por caso de uso")
    print("  - Conclusiones técnicas")

    respuesta = input("\nGenerar PDF? (s/n): ").strip().lower()

    if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
        print("\nGenerando reporte PDF...")

        try:
            # Importar y ejecutar directamente (ya no necesita venv separado)
            from benchmarks.generar_pdf_graficos import generar_pdf_graficos

            ruta_pdf = generar_pdf_graficos()

            if ruta_pdf:
                print(f"\n[OK] Reporte PDF generado: {ruta_pdf}")
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
    else:
        print("\nOmitiendo generación de PDF")


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

    print("\nSe ejecutarán 2 benchmarks:")
    print("   1. Rendimiento estándar (PC sin restricciones)")
    print("   2. Dispositivos con restricciones (ESP32, Arduino, sensores)")

    input("\nPresiona ENTER para comenzar...")

    # Ejecutar todos los benchmarks
    resultados = {
        'estandar': None,
        'restringido': None
    }

    # 1. Benchmark estándar
    resultados['estandar'] = ejecutar_benchmark_estandar()

    # 2. Benchmark restringido
    resultados['restringido'] = ejecutar_benchmark_restringido()

    # Resumen final
    tiempo_total = time.time() - inicio_total

    imprimir_resumen_final(resultados)

    print(f"\nTIEMPO TOTAL DE EJECUCIÓN: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")
    print("\n" + "=" * 100)
    print("SUITE DE BENCHMARKS FINALIZADA")
    print("=" * 100 + "\n")

    # Ofrecer generación de PDF
    generar_pdf_si_se_desea(resultados)


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
