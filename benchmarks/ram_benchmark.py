"""
Benchmark de Memoria RAM para Algoritmos de Criptografía Ligera
Basado en la metodología de Soto-Cruz et al. (2024)
"""

import sys
import tracemalloc
import gc
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


def medir_uso_ram(funcion, texto_plano, clave, numero_iteraciones=100):
    gc.collect()
    funcion(texto_plano, clave)

    gc.collect()
    tracemalloc.start()
    for _ in range(numero_iteraciones):
        funcion(texto_plano, clave)
    _, pico_memoria = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return pico_memoria


def medir_consumo_ram(funcion_cifrado, funcion_descifrado, texto_plano, clave):
    texto_cifrado = funcion_cifrado(texto_plano, clave)

    ram_cifrado = medir_uso_ram(funcion_cifrado, texto_plano, clave)
    ram_descifrado = medir_uso_ram(lambda texto, clave_desc: funcion_descifrado(texto_cifrado, clave_desc), texto_plano, clave)

    return {
        "ram_cifrado_bytes": ram_cifrado,
        "ram_descifrado_bytes": ram_descifrado,
        "ram_cifrado_kilobytes": ram_cifrado / 1024,
        "ram_descifrado_kilobytes": ram_descifrado / 1024,
    }


def generar_grafico(resultados_benchmark):
    lista_algoritmos = ["AES-128", "DES", "PRESENT-80"]

    figura, ejes_subgraficos = plt.subplots(2, 1, figsize=(10, 10))
    posiciones_eje_x = np.arange(len(lista_algoritmos))
    ancho_barra = 0.35

    # RAM en Bytes
    ejes_bytes = ejes_subgraficos[0]
    ram_cifrado_bytes = [resultados_benchmark[algoritmo]["ram_cifrado_bytes"] for algoritmo in lista_algoritmos]
    ram_descifrado_bytes = [resultados_benchmark[algoritmo]["ram_descifrado_bytes"] for algoritmo in lista_algoritmos]

    barras_cifrado_bytes = ejes_bytes.bar(posiciones_eje_x - ancho_barra/2, ram_cifrado_bytes, ancho_barra, label="Cifrado", color="#3498db")
    barras_descifrado_bytes = ejes_bytes.bar(posiciones_eje_x + ancho_barra/2, ram_descifrado_bytes, ancho_barra, label="Descifrado", color="#e74c3c")

    ejes_bytes.set_xlabel("Algoritmo", fontsize=12)
    ejes_bytes.set_ylabel("RAM (bytes)", fontsize=12)
    ejes_bytes.set_title("Uso de RAM (bytes) - Menor es Mejor", fontsize=14)
    ejes_bytes.set_xticks(posiciones_eje_x)
    ejes_bytes.set_xticklabels(lista_algoritmos, fontsize=11)
    ejes_bytes.legend(loc="upper right")
    ejes_bytes.set_ylim(bottom=0)

    for grupo_barras in [barras_cifrado_bytes, barras_descifrado_bytes]:
        for barra in grupo_barras:
            altura_barra = barra.get_height()
            ejes_bytes.annotate(f"{altura_barra:.0f}", xy=(barra.get_x() + barra.get_width()/2, altura_barra),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    # RAM en KB
    ejes_kilobytes = ejes_subgraficos[1]
    ram_cifrado_kb = [resultados_benchmark[algoritmo]["ram_cifrado_kilobytes"] for algoritmo in lista_algoritmos]
    ram_descifrado_kb = [resultados_benchmark[algoritmo]["ram_descifrado_kilobytes"] for algoritmo in lista_algoritmos]

    barras_cifrado_kb = ejes_kilobytes.bar(posiciones_eje_x - ancho_barra/2, ram_cifrado_kb, ancho_barra, label="Cifrado", color="#27ae60")
    barras_descifrado_kb = ejes_kilobytes.bar(posiciones_eje_x + ancho_barra/2, ram_descifrado_kb, ancho_barra, label="Descifrado", color="#f39c12")

    ejes_kilobytes.set_xlabel("Algoritmo", fontsize=12)
    ejes_kilobytes.set_ylabel("RAM (KB)", fontsize=12)
    ejes_kilobytes.set_title("Uso de RAM (KB) - Menor es Mejor para IoT", fontsize=14)
    ejes_kilobytes.set_xticks(posiciones_eje_x)
    ejes_kilobytes.set_xticklabels(lista_algoritmos, fontsize=11)
    ejes_kilobytes.legend(loc="upper right")
    ejes_kilobytes.set_ylim(bottom=0)

    for grupo_barras in [barras_cifrado_kb, barras_descifrado_kb]:
        for barra in grupo_barras:
            altura_barra = barra.get_height()
            ejes_kilobytes.annotate(f"{altura_barra:.2f}", xy=(barra.get_x() + barra.get_width()/2, altura_barra),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    ruta_archivo_salida = RUTA_RAIZ_PROYECTO / "results" / "ram_benchmark.png"
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
        resultados_benchmark[nombre_algoritmo] = medir_consumo_ram(funcion_cifrado, funcion_descifrado, texto_plano, clave)

    generar_grafico(resultados_benchmark)
    print("SUCCESS")


if __name__ == "__main__":
    ejecutar_benchmark()
