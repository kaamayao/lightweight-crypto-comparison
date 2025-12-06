"""
Benchmark de Memoria para Algoritmos de Criptografía Ligera
Basado en la metodología de Soto-Cruz et al. (2024)
"""

import sys
import tracemalloc
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RUTA_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RUTA_RAIZ_PROYECTO))

from algorithms.AES import constants as constantes_aes  # noqa: E402
from algorithms.AES.index import AES_cifrar, AES_descifrar  # noqa: E402
from algorithms.DES import constants as constantes_des  # noqa: E402
from algorithms.DES.index import DES_cifrar, DES_descifrar  # noqa: E402
from algorithms.PRESENT import constants as constantes_present  # noqa: E402
from algorithms.PRESENT.index import PRESENT_cifrar, PRESENT_descifrar  # noqa: E402


def cargar_datos_prueba(nombre_archivo="medium_message.txt"):
    with open(RUTA_RAIZ_PROYECTO / "data" / nombre_archivo, "r", encoding="utf-8") as archivo:
        return archivo.read()


def medir_memoria_estatica(modulo_constantes):
    memoria_total = 0
    for nombre_atributo in dir(modulo_constantes):
        if not nombre_atributo.startswith("_"):
            objeto = getattr(modulo_constantes, nombre_atributo)
            tamanio_objeto = sys.getsizeof(objeto)
            if isinstance(objeto, (list, tuple)):
                for elemento in objeto:
                    if isinstance(elemento, (list, tuple)):
                        tamanio_objeto += sys.getsizeof(elemento)
                        for subelemento in elemento:
                            if isinstance(subelemento, (list, tuple)):
                                tamanio_objeto += sys.getsizeof(subelemento)
            memoria_total += tamanio_objeto
    return memoria_total


def medir_memoria_tiempo_ejecucion(funcion_cifrado, funcion_descifrado, texto_plano, clave, numero_iteraciones=100):
    tracemalloc.start()
    for _ in range(numero_iteraciones):
        texto_cifrado = funcion_cifrado(texto_plano, clave)
    _, pico_memoria_cifrado = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    for _ in range(numero_iteraciones):
        funcion_descifrado(texto_cifrado, clave)
    _, pico_memoria_descifrado = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return pico_memoria_cifrado, pico_memoria_descifrado


def generar_grafico(totales_memoria_estatica, resultados_tiempo_ejecucion):
    lista_algoritmos = ["AES-128", "DES", "PRESENT-80"]

    memoria_estatica_kb = [totales_memoria_estatica[algoritmo] / 1024 for algoritmo in lista_algoritmos]
    pico_cifrado_kb = [resultados_tiempo_ejecucion[algoritmo][0] / 1024 for algoritmo in lista_algoritmos]
    pico_descifrado_kb = [resultados_tiempo_ejecucion[algoritmo][1] / 1024 for algoritmo in lista_algoritmos]

    posiciones_eje_x = np.arange(len(lista_algoritmos))
    ancho_barra = 0.25

    figura, ejes = plt.subplots(figsize=(10, 6))
    barras_memoria_estatica = ejes.bar(posiciones_eje_x - ancho_barra, memoria_estatica_kb, ancho_barra, label="Memoria Estática (Constantes)", color="#2ecc71")
    barras_pico_cifrado = ejes.bar(posiciones_eje_x, pico_cifrado_kb, ancho_barra, label="Pico Cifrado", color="#3498db")
    barras_pico_descifrado = ejes.bar(posiciones_eje_x + ancho_barra, pico_descifrado_kb, ancho_barra, label="Pico Descifrado", color="#e74c3c")

    ejes.set_xlabel("Algoritmo", fontsize=12)
    ejes.set_ylabel("Memoria (KB)", fontsize=12)
    ejes.set_title("Comparación de Uso de Memoria - Algoritmos de Criptografía Ligera", fontsize=14)
    ejes.set_xticks(posiciones_eje_x)
    ejes.set_xticklabels(lista_algoritmos, fontsize=11)
    ejes.legend(loc="upper right")

    for grupo_barras in [barras_memoria_estatica, barras_pico_cifrado, barras_pico_descifrado]:
        for barra in grupo_barras:
            altura_barra = barra.get_height()
            ejes.annotate(f"{altura_barra:.2f}", xy=(barra.get_x() + barra.get_width()/2, altura_barra),
                       xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    ruta_archivo_salida = RUTA_RAIZ_PROYECTO / "results" / "memory_benchmark.png"
    ruta_archivo_salida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ruta_archivo_salida, dpi=150)
    plt.close()


def ejecutar_benchmark():
    texto_plano = cargar_datos_prueba()

    configuracion_constantes_algoritmos = [
        ("AES-128", constantes_aes),
        ("DES", constantes_des),
        ("PRESENT-80", constantes_present),
    ]

    configuracion_funciones_algoritmos = [
        ("AES-128", AES_cifrar, AES_descifrar, "ClaveSecreta1234"),
        ("DES", DES_cifrar, DES_descifrar, "Clave123"),
        ("PRESENT-80", PRESENT_cifrar, PRESENT_descifrar, "ClavePresent"),
    ]

    totales_memoria_estatica = {}
    for nombre_algoritmo, modulo_constantes in configuracion_constantes_algoritmos:
        totales_memoria_estatica[nombre_algoritmo] = medir_memoria_estatica(modulo_constantes)

    resultados_tiempo_ejecucion = {}
    for nombre_algoritmo, funcion_cifrado, funcion_descifrado, clave in configuracion_funciones_algoritmos:
        resultados_tiempo_ejecucion[nombre_algoritmo] = medir_memoria_tiempo_ejecucion(funcion_cifrado, funcion_descifrado, texto_plano, clave)

    generar_grafico(totales_memoria_estatica, resultados_tiempo_ejecucion)
    print("SUCCESS")


if __name__ == "__main__":
    ejecutar_benchmark()
