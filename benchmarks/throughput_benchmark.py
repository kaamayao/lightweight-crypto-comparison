"""
Benchmark de Rendimiento (Throughput) para Algoritmos de Criptografía Ligera
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


def cargar_datos_prueba(nombre_archivo="medium_message.txt"):
    with open(RUTA_RAIZ_PROYECTO / "data" / nombre_archivo, "r", encoding="utf-8") as archivo:
        return archivo.read()


def medir_rendimiento(funcion_cifrado, funcion_descifrado, texto_plano, clave, numero_iteraciones=5000):
    tamanio_datos_bytes = len(texto_plano.encode("utf-8"))

    # Calentamiento previo
    texto_cifrado = funcion_cifrado(texto_plano, clave)
    funcion_descifrado(texto_cifrado, clave)

    # Medir tiempo de cifrado
    tiempo_inicio = time.perf_counter()
    for _ in range(numero_iteraciones):
        texto_cifrado = funcion_cifrado(texto_plano, clave)
    tiempo_cifrado_total = time.perf_counter() - tiempo_inicio

    # Medir tiempo de descifrado
    tiempo_inicio = time.perf_counter()
    for _ in range(numero_iteraciones):
        funcion_descifrado(texto_cifrado, clave)
    tiempo_descifrado_total = time.perf_counter() - tiempo_inicio

    total_bytes_procesados = numero_iteraciones * tamanio_datos_bytes
    return {
        "rendimiento_cifrado_kb_por_segundo": (total_bytes_procesados / tiempo_cifrado_total) / 1024,
        "rendimiento_descifrado_kb_por_segundo": (total_bytes_procesados / tiempo_descifrado_total) / 1024,
    }


def generar_grafico(resultados_benchmark):
    lista_algoritmos = ["AES-128", "DES", "PRESENT-80"]
    rendimiento_cifrado = [resultados_benchmark[algoritmo]["rendimiento_cifrado_kb_por_segundo"] for algoritmo in lista_algoritmos]
    rendimiento_descifrado = [resultados_benchmark[algoritmo]["rendimiento_descifrado_kb_por_segundo"] for algoritmo in lista_algoritmos]

    posiciones_eje_x = np.arange(len(lista_algoritmos))
    ancho_barra = 0.35

    figura, ejes = plt.subplots(figsize=(10, 6))
    barras_cifrado = ejes.bar(posiciones_eje_x - ancho_barra/2, rendimiento_cifrado, ancho_barra, label="Cifrado", color="#3498db")
    barras_descifrado = ejes.bar(posiciones_eje_x + ancho_barra/2, rendimiento_descifrado, ancho_barra, label="Descifrado", color="#e74c3c")

    ejes.set_xlabel("Algoritmo", fontsize=12)
    ejes.set_ylabel("Rendimiento (KB/s)", fontsize=12)
    ejes.set_title("Rendimiento (KB/s) - Mayor es Mejor", fontsize=14)
    ejes.set_xticks(posiciones_eje_x)
    ejes.set_xticklabels(lista_algoritmos, fontsize=11)
    ejes.legend(loc="upper right")

    for grupo_barras in [barras_cifrado, barras_descifrado]:
        for barra in grupo_barras:
            altura_barra = barra.get_height()
            ejes.annotate(f"{altura_barra:.2f}", xy=(barra.get_x() + barra.get_width()/2, altura_barra),
                       xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    ruta_archivo_salida = RUTA_RAIZ_PROYECTO / "results" / "throughput_benchmark.png"
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
    for nombre_algoritmo, funcion_cifrado, funcion_descifrado, clave in configuracion_algoritmos:
        resultados_benchmark[nombre_algoritmo] = medir_rendimiento(funcion_cifrado, funcion_descifrado, texto_plano, clave)

    generar_grafico(resultados_benchmark)
    print("SUCCESS")


if __name__ == "__main__":
    ejecutar_benchmark()
