"""
Benchmark script for simulating resource-constrained IoT devices
Uses CPU throttling, memory limits, and frequency scaling to simulate low-spec hardware
"""

import os
import sys
import subprocess
import psutil

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from algorithms.DES.index import DES_cifrar, DES_descifrar
from algorithms.AES.index import AES_cifrar, AES_descifrar


class EntornoRestringido:
    """Gestor de contexto para simular entorno con recursos restringidos"""

    def __init__(self, porcentaje_cpu=50, limite_memoria_mb=32, nombre="default"):
        """
        Args:
            porcentaje_cpu: Porcentaje de CPU a permitir (ej., 50 = 50% de un núcleo)
            limite_memoria_mb: Límite de memoria en MB
            nombre: Nombre del perfil para visualización
        """
        self.porcentaje_cpu = porcentaje_cpu
        self.limite_memoria_mb = limite_memoria_mb
        self.nombre = nombre
        self.pid = os.getpid()

    def __enter__(self):
        print(f"\n{'='*80}")
        print(f"Simulating: {self.nombre}")
        print(f"CPU Limit: {self.porcentaje_cpu}% | Memory Limit: {self.limite_memoria_mb}MB")
        print(f"{'='*80}")

        # Establecer afinidad de CPU a un solo núcleo para consistencia
        try:
            p = psutil.Process(self.pid)
            p.cpu_affinity([0])  # Usar solo el primer núcleo de CPU
        except (AttributeError, PermissionError):
            print("Warning: Could not set CPU affinity")

        # Establecer prioridad del proceso para simular CPU más lenta
        try:
            os.nice(10)  # Prioridad más baja (valor nice más alto = prioridad más baja)
        except PermissionError:
            print("Warning: Could not set process priority")

        return self

    def __exit__(self, tipo_exc, valor_exc, tb_exc):
        # Restablecer prioridad
        try:
            os.nice(-10)
        except PermissionError:
            pass


def obtener_perfiles_dispositivo():
    """Definir perfiles de recursos para diferentes clases de dispositivos IoT"""
    return {
        "high_end_pc": {
            "porcentaje_cpu": 100,
            "limite_memoria_mb": 2048,
            "descripcion": "High-end PC / Server (baseline)",
            "ejemplos": "Desktop, Server, Raspberry Pi 4"
        },
        "mid_range_iot": {
            "porcentaje_cpu": 50,
            "limite_memoria_mb": 256,
            "descripcion": "Mid-range IoT Device",
            "ejemplos": "ESP32, Arduino Due, STM32F4"
        },
        "low_end_iot": {
            "porcentaje_cpu": 25,
            "limite_memoria_mb": 64,
            "descripcion": "Low-end IoT Device",
            "ejemplos": "ESP8266, Arduino Uno, ATmega328"
        },
        "ultra_constrained": {
            "porcentaje_cpu": 10,
            "limite_memoria_mb": 16,
            "descripcion": "Ultra-constrained Device",
            "ejemplos": "Sensor nodes, RFID tags, MSP430"
        }
    }


def probar_algoritmo_restringido(nombre_algoritmo, func_cifrar, func_descifrar,
                                 texto_plano, clave, perfil):
    """
    Probar un algoritmo bajo restricciones de recursos

    Args:
        nombre_algoritmo: Nombre del algoritmo
        func_cifrar: Función de cifrado
        func_descifrar: Función de descifrado
        texto_plano: Mensaje de prueba
        clave: Clave de cifrado
        perfil: Perfil de restricción de recursos
    """
    import time
    import tracemalloc

    with EntornoRestringido(
        porcentaje_cpu=perfil["porcentaje_cpu"],
        limite_memoria_mb=perfil["limite_memoria_mb"],
        nombre=f"{perfil['descripcion']} - {nombre_algoritmo}"
    ):
        # Calentamiento
        _ = func_cifrar(texto_plano[:64] if len(texto_plano) > 64 else texto_plano, clave)

        # ===== CIFRADO =====
        tracemalloc.start()
        tiempo_inicio = time.perf_counter()

        texto_cifrado = func_cifrar(texto_plano, clave)

        tiempo_cifrado = time.perf_counter() - tiempo_inicio
        actual, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # ===== DESCIFRADO =====
        inicio_descifrado = time.perf_counter()
        descifrado = func_descifrar(texto_cifrado, clave)
        tiempo_descifrado = time.perf_counter() - inicio_descifrado

        resultado = {
            "algoritmo": nombre_algoritmo,
            "perfil": perfil["descripcion"],
            "tamano_texto_plano": len(texto_plano),
            "tiempo_cifrado_ms": tiempo_cifrado * 1000,
            "tiempo_descifrado_ms": tiempo_descifrado * 1000,
            "tiempo_total_ms": (tiempo_cifrado + tiempo_descifrado) * 1000,
            "memoria_kb": pico / 1024,
            "rendimiento_kbps": (len(texto_plano) / 1024) / tiempo_cifrado if tiempo_cifrado > 0 else 0
        }

        return resultado


def ejecutar_pruebas_restringidas():
    """Ejecutar pruebas simulando diferentes clases de dispositivos"""

    print("="*80)
    print("RESOURCE-CONSTRAINED DEVICE SIMULATION BENCHMARK")
    print("Testing DES, AES-128, and PRESENT-80 on simulated IoT devices")
    print("="*80)

    # Cargar mensajes de prueba
    print("\nLoading test messages...")
    mensajes_prueba = {}

    try:
        with open("../data/short_message.txt", "r", encoding="utf-8") as f:
            mensajes_prueba["short"] = f.read()
        with open("../data/medium_message.txt", "r", encoding="utf-8") as f:
            mensajes_prueba["medium"] = f.read()
        with open("../data/long_message.txt", "r", encoding="utf-8") as f:
            mensajes_prueba["long"] = f.read()
    except FileNotFoundError:
        print("Error: Test message files not found!")
        return

    # Definir algoritmos
    algoritmos = [
        {
            "nombre": "DES",
            "cifrar": DES_cifrar,
            "descifrar": DES_descifrar,
            "clave": "secret12"  # Exactamente 8 caracteres = 64 bits (requerido por DES)
        },
        {
            "nombre": "AES-128",
            "cifrar": AES_cifrar,
            "descifrar": AES_descifrar,
            "clave": "secretkey1234567"  # Exactamente 16 caracteres = 128 bits (AES-128)
        }
    ]

    # Validar longitudes de claves
    assert len(algoritmos[0]["clave"]) == 8, "DES requiere clave de 8 caracteres (64 bits)"
    assert len(algoritmos[1]["clave"]) == 16, "AES-128 requiere clave de 16 caracteres (128 bits)"

    perfiles = obtener_perfiles_dispositivo()

    # Imprimir perfiles de dispositivos
    print("\n" + "="*80)
    print("DEVICE PROFILES")
    print("="*80)
    for nombre_perfil, perfil in perfiles.items():
        print(f"\n{perfil['descripcion']}:")
        print(f"  CPU: {perfil['porcentaje_cpu']}% | RAM: {perfil['limite_memoria_mb']}MB")
        print(f"  Examples: {perfil['ejemplos']}")

    # Ejecutar pruebas
    todos_resultados = []

    for tipo_mensaje, mensaje in mensajes_prueba.items():
        print(f"\n\n{'='*80}")
        print(f"Testing {tipo_mensaje.upper()} message ({len(mensaje)} bytes)")
        print(f"{'='*80}")

        for nombre_perfil, perfil in perfiles.items():
            print(f"\n--- {perfil['descripcion']} ---")

            for algo in algoritmos:
                try:
                    resultado = probar_algoritmo_restringido(
                        algo["nombre"],
                        algo["cifrar"],
                        algo["descifrar"],
                        mensaje,
                        algo["clave"],
                        perfil
                    )
                    todos_resultados.append(resultado)

                    print(f"{algo['nombre']:<12}: "
                          f"Enc(CIFRADO)={resultado['tiempo_cifrado_ms']:>8.2f}ms | "
                          f"Dec(DESCIFRADO)={resultado['tiempo_descifrado_ms']:>8.2f}ms | "
                          f"Total={resultado['tiempo_total_ms']:>8.2f}ms | "
                          f"Throughput(Enc)={resultado['rendimiento_kbps']:>6.2f}KB/s")

                except Exception as e:
                    print(f"{algo['nombre']:<12}: ERROR - {str(e)}")

    # Generar reporte resumen
    imprimir_reporte_resumen(todos_resultados, perfiles)

    return todos_resultados


def imprimir_reporte_resumen(resultados, perfiles):
    """Imprimir reporte de comparación resumido"""

    print("\n\n" + "="*80)
    print("SUMMARY: PERFORMANCE ACROSS DEVICE CLASSES")
    print("="*80)

    # Agrupar por perfil y algoritmo
    for nombre_perfil, perfil in perfiles.items():
        descripcion_perfil = perfil["descripcion"]
        resultados_perfil = [r for r in resultados if r["perfil"] == descripcion_perfil]

        if not resultados_perfil:
            continue

        print(f"\n{descripcion_perfil}")
        print("-" * 80)
        print(f"{'Algorithm':<15} {'Avg Enc':<18} {'Avg Dec':<18} "
              f"{'Avg Throughput':<20}")
        print(f"{'':<15} {'CIFRADO (ms)':<18} {'DESCIFRADO (ms)':<18} "
              f"{'(Enc, KB/s)':<20}")
        print("-" * 80)

        # Calcular promedios por algoritmo
        for nombre_algoritmo in ["DES", "AES-128", "PRESENT-80"]:
            resultados_algo = [r for r in resultados_perfil if r["algoritmo"] == nombre_algoritmo]

            if resultados_algo:
                promedio_cifrado = sum(r["tiempo_cifrado_ms"] for r in resultados_algo) / len(resultados_algo)
                promedio_descifrado = sum(r["tiempo_descifrado_ms"] for r in resultados_algo) / len(resultados_algo)
                promedio_rendimiento = sum(r["rendimiento_kbps"] for r in resultados_algo) / len(resultados_algo)

                print(f"{nombre_algoritmo:<15} {promedio_cifrado:<18.2f} {promedio_descifrado:<18.2f} "
                      f"{promedio_rendimiento:<20.2f}")

    # Mejor algoritmo por perfil
    print("\n\n" + "="*80)
    print("RECOMMENDATIONS BY DEVICE CLASS")
    print("="*80)

    for nombre_perfil, perfil in perfiles.items():
        descripcion_perfil = perfil["descripcion"]
        resultados_perfil = [r for r in resultados if r["perfil"] == descripcion_perfil]

        if not resultados_perfil:
            continue

        # Encontrar el algoritmo con mejor rendimiento (cifrado más rápido)
        mejor = min(resultados_perfil, key=lambda x: x["tiempo_cifrado_ms"])

        print(f"\n{descripcion_perfil}:")
        print(f"  Best Algorithm: {mejor['algoritmo']}")
        print(f"  Encryption Time (CIFRADO): {mejor['tiempo_cifrado_ms']:.2f}ms")
        print(f"  Decryption Time (DESCIFRADO): {mejor['tiempo_descifrado_ms']:.2f}ms")
        print(f"  Throughput (Encryption): {mejor['rendimiento_kbps']:.2f}KB/s")


if __name__ == "__main__":
    print("\nNOTE: This simulation uses software-based resource limiting.")
    print("Results are approximations of constrained hardware behavior.")
    print("For accurate IoT device testing, use actual hardware or emulators.")
    print()

    resultados = ejecutar_pruebas_restringidas()

    print("\n" + "="*80)
    print("CONSTRAINED BENCHMARK COMPLETE")
    print("="*80)
