"""
Benchmark de Potencia y Energía para Algoritmos de Criptografía Ligera
Basado en la metodología de Soto-Cruz et al. (2024)
"""

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RUTA_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RUTA_RAIZ_PROYECTO))

from algorithms.AES.index import AES_cifrar, AES_descifrar  # noqa: E402
from algorithms.DES.index import DES_cifrar, DES_descifrar  # noqa: E402
from algorithms.PRESENT.index import PRESENT_cifrar, PRESENT_descifrar  # noqa: E402

POTENCIA_BASE_REPOSO_VATIOS = 5.0
POTENCIA_CPU_ACTIVO_VATIOS = 15.0
VOLTAJE_REFERENCIA_VOLTIOS = 5.0


def cargar_datos_prueba(nombre_archivo="medium_message.txt"):
    with open(
        RUTA_RAIZ_PROYECTO / "data" / nombre_archivo, "r", encoding="utf-8"
    ) as archivo:
        return archivo.read()


def medir_potencia(
    funcion_cifrado, funcion_descifrado, texto_plano, clave, numero_iteraciones=5000
):
    tamanio_datos_bytes = len(texto_plano.encode("utf-8"))

    texto_cifrado = funcion_cifrado(texto_plano, clave)
    funcion_descifrado(texto_cifrado, clave)

    # Cifrado
    tiempo_real_inicio = time.perf_counter()
    tiempo_cpu_inicio = time.process_time()
    for _ in range(numero_iteraciones):
        texto_cifrado = funcion_cifrado(texto_plano, clave)
    tiempo_cpu_cifrado = time.process_time() - tiempo_cpu_inicio
    tiempo_real_cifrado = time.perf_counter() - tiempo_real_inicio

    # Descifrado
    tiempo_real_inicio = time.perf_counter()
    tiempo_cpu_inicio = time.process_time()
    for _ in range(numero_iteraciones):
        funcion_descifrado(texto_cifrado, clave)
    tiempo_cpu_descifrado = time.process_time() - tiempo_cpu_inicio
    tiempo_real_descifrado = time.perf_counter() - tiempo_real_inicio

    utilizacion_cpu_cifrado = (
        min(tiempo_cpu_cifrado / tiempo_real_cifrado, 1.0)
        if tiempo_real_cifrado > 0
        else 0
    )
    utilizacion_cpu_descifrado = (
        min(tiempo_cpu_descifrado / tiempo_real_descifrado, 1.0)
        if tiempo_real_descifrado > 0
        else 0
    )

    potencia_cifrado = POTENCIA_BASE_REPOSO_VATIOS + (
        POTENCIA_CPU_ACTIVO_VATIOS * utilizacion_cpu_cifrado
    )
    potencia_descifrado = POTENCIA_BASE_REPOSO_VATIOS + (
        POTENCIA_CPU_ACTIVO_VATIOS * utilizacion_cpu_descifrado
    )

    latencia_cifrado_por_byte = tiempo_real_cifrado / (
        numero_iteraciones * tamanio_datos_bytes
    )
    latencia_descifrado_por_byte = tiempo_real_descifrado / (
        numero_iteraciones * tamanio_datos_bytes
    )

    return {
        "potencia_cifrado_miliwatios": potencia_cifrado * 1000,
        "potencia_descifrado_miliwatios": potencia_descifrado * 1000,
        "energia_cifrado_microjulios_por_byte": potencia_cifrado
        * latencia_cifrado_por_byte
        * 1_000_000,
        "energia_descifrado_microjulios_por_byte": potencia_descifrado
        * latencia_descifrado_por_byte
        * 1_000_000,
    }


def generar_grafico(resultados_benchmark):
    lista_algoritmos = ["AES-128", "DES", "PRESENT-80"]

    figura, ejes_subgraficos = plt.subplots(2, 1, figsize=(10, 10))
    posiciones_eje_x = np.arange(len(lista_algoritmos))
    ancho_barra = 0.35

    # Consumo de Potencia
    ejes_potencia = ejes_subgraficos[0]
    potencia_cifrado = [
        resultados_benchmark[algoritmo]["potencia_cifrado_miliwatios"]
        for algoritmo in lista_algoritmos
    ]
    potencia_descifrado = [
        resultados_benchmark[algoritmo]["potencia_descifrado_miliwatios"]
        for algoritmo in lista_algoritmos
    ]

    barras_potencia_cifrado = ejes_potencia.bar(
        posiciones_eje_x - ancho_barra / 2,
        potencia_cifrado,
        ancho_barra,
        label="Cifrado",
        color="#3498db",
    )
    barras_potencia_descifrado = ejes_potencia.bar(
        posiciones_eje_x + ancho_barra / 2,
        potencia_descifrado,
        ancho_barra,
        label="Descifrado",
        color="#e74c3c",
    )

    ejes_potencia.set_xlabel("Algoritmo", fontsize=12)
    ejes_potencia.set_ylabel("Potencia (mW)", fontsize=12)
    ejes_potencia.set_title("Consumo de Potencia (mW)", fontsize=14)
    ejes_potencia.set_xticks(posiciones_eje_x)
    ejes_potencia.set_xticklabels(lista_algoritmos, fontsize=11)
    ejes_potencia.legend(loc="upper right")
    ejes_potencia.set_ylim(bottom=0)

    for grupo_barras in [barras_potencia_cifrado, barras_potencia_descifrado]:
        for barra in grupo_barras:
            altura_barra = barra.get_height()
            ejes_potencia.annotate(
                f"{altura_barra:.1f}",
                xy=(barra.get_x() + barra.get_width() / 2, altura_barra),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # Energía por Byte
    ejes_energia = ejes_subgraficos[1]
    energia_cifrado = [
        resultados_benchmark[algoritmo]["energia_cifrado_microjulios_por_byte"]
        for algoritmo in lista_algoritmos
    ]
    energia_descifrado = [
        resultados_benchmark[algoritmo]["energia_descifrado_microjulios_por_byte"]
        for algoritmo in lista_algoritmos
    ]

    barras_energia_cifrado = ejes_energia.bar(
        posiciones_eje_x - ancho_barra / 2,
        energia_cifrado,
        ancho_barra,
        label="Cifrado",
        color="#27ae60",
    )
    barras_energia_descifrado = ejes_energia.bar(
        posiciones_eje_x + ancho_barra / 2,
        energia_descifrado,
        ancho_barra,
        label="Descifrado",
        color="#f39c12",
    )

    ejes_energia.set_xlabel("Algoritmo", fontsize=12)
    ejes_energia.set_ylabel("Energía (µJ/byte)", fontsize=12)
    ejes_energia.set_title(
        "Energía por Byte (µJ/byte) - Menor es Mejor", fontsize=14)
    ejes_energia.set_xticks(posiciones_eje_x)
    ejes_energia.set_xticklabels(lista_algoritmos, fontsize=11)
    ejes_energia.legend(loc="upper right")

    for grupo_barras in [barras_energia_cifrado, barras_energia_descifrado]:
        for barra in grupo_barras:
            altura_barra = barra.get_height()
            ejes_energia.annotate(
                f"{altura_barra:.2f}",
                xy=(barra.get_x() + barra.get_width() / 2, altura_barra),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    ruta_archivo_salida = RUTA_RAIZ_PROYECTO / "results" / "power_benchmark.png"
    ruta_archivo_salida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ruta_archivo_salida, dpi=150)
    plt.close()


def ejecutar_benchmark():
    texto_plano = cargar_datos_prueba()

    configuracion_algoritmos = [
        ("AES-128", AES_cifrar, AES_descifrar, "ClaveSecreta1234"),
        ("DES", DES_cifrar, DES_descifrar, "Clave123"),
        ("PRESENT-80", PRESENT_cifrar, PRESENT_descifrar, "ClavePresent"),
    ]

    resultados_benchmark = {}
    for (
        nombre_algoritmo,
        funcion_cifrado,
        funcion_descifrado,
        clave,
    ) in configuracion_algoritmos:
        resultados_benchmark[nombre_algoritmo] = medir_potencia(
            funcion_cifrado, funcion_descifrado, texto_plano, clave
        )

    generar_grafico(resultados_benchmark)
    print("SUCCESS")


if __name__ == "__main__":
    ejecutar_benchmark()
