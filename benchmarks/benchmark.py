"""
Prueba de Rendimiento para Comparación de Criptografía Ligera
Evalúa DES y AES-128 en métricas clave:
- Rendimiento de Cifrado/Descifrado (MB/s)
- Latencia (ms por operación)
- Tiempo de preparación de clave (ms)
- Ciclos por byte (estimado)
- Uso de memoria
- Sobrecarga del texto cifrado
"""

import time
import sys
import tracemalloc
import os
from algorithms.utils.index import bits_a_hex, bytes_a_hex
from algorithms.AES.index import AES_cifrar, AES_descifrar
from algorithms.DES.index import DES_cifrar, DES_descifrar
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)
DIRECTORIO_RESULTADOS = os.path.join(RAIZ_PROYECTO, "results")
DIRECTORIO_DATOS = os.path.join(RAIZ_PROYECTO, "data")

sys.path.insert(0, RAIZ_PROYECTO)
matplotlib.use("Agg")


class ResultadoPrueba:
    def __init__(self, algoritmo, tipo_mensaje, tamano_texto_plano):
        self.algoritmo = algoritmo
        self.tipo_mensaje = tipo_mensaje
        self.tamano_texto_plano = tamano_texto_plano
        self.tiempo_preparacion_clave = 0
        self.tiempo_cifrado = 0
        self.tiempo_descifrado = 0
        self.tiempo_total = 0
        self.memoria_usada = 0
        self.tamano_texto_cifrado = 0

    def calcular_metricas(self):
        """Calcular métricas derivadas"""
        self.rendimiento_mbps = (
            (self.tamano_texto_plano / (1024 * 1024)) / self.tiempo_cifrado
            if self.tiempo_cifrado > 0
            else 0
        )

        self.ciclos_por_byte = (
            self.tiempo_cifrado * 2.5e9 / self.tamano_texto_plano
            if self.tamano_texto_plano > 0
            else 0
        )

        self.porcentaje_sobrecarga = (
            (
                (self.tamano_texto_cifrado - self.tamano_texto_plano)
                / self.tamano_texto_plano
                * 100
            )
            if self.tamano_texto_plano > 0
            else 0
        )
        self.memoria_kb = self.memoria_usada / 1024

        # Estimación de consumo de energía para hardware de PC
        # CPU: x86-64 moderno @ 2.5 GHz, TDP típico 15-65W
        # Potencia promedio durante operaciones criptográficas:
        # ~20W para móvil, ~45W para escritorio
        potencia_cpu_watts = 35  # Promedio entre móvil y escritorio
        self.energia_julios = potencia_cpu_watts * self.tiempo_cifrado
        self.energia_milijulios = self.energia_julios * 1000

    def __str__(self):
        return f"""
Algoritmo: {self.algoritmo}
Tipo de Mensaje: {self.tipo_mensaje}
Plaintext tamaño: {self.tamano_texto_plano} bytes
-----------------------------------------
Tiempo CIFRADO: {self.tiempo_cifrado * 1000:.4f} ms
Tiempo DESCIFRADO: {self.tiempo_descifrado * 1000:.4f} ms
Tiempo Total: {self.tiempo_total * 1000:.4f} ms
-----------------------------------------
Throughput (Encryption): {self.rendimiento_mbps:.4f} MB/s
Cycles/Byte (Encryption, est.): {self.ciclos_por_byte:.2f}
Memory Used: {self.memoria_kb:.2f} KB
Energy Consumed (Encryption): {self.energia_milijulios:.4f} mJ
Ciphertext Size: {self.tamano_texto_cifrado} bytes
Overhead: {self.porcentaje_sobrecarga:.2f}%
"""


def probar_des(texto_plano, tipo_mensaje):
    """Probar cifrado/descifrado DES"""
    clave = "secret12"  # Exactamente 8 caracteres = 64 bits (requerido por DES)
    assert len(clave) == 8, "DES requiere una clave de exactamente 8 caracteres (64 bits)"
    resultado = ResultadoPrueba("DES", tipo_mensaje, len(texto_plano))

    # Medir tiempo de preparación de clave (integrado en cifrado para DES)
    tracemalloc.start()
    inicio = time.perf_counter()

    # ===== CIFRADO =====
    inicio_cifrado = time.perf_counter()
    bits_texto_cifrado = DES_cifrar(texto_plano, clave)
    fin_cifrado = time.perf_counter()

    actual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    resultado.tiempo_cifrado = fin_cifrado - inicio_cifrado
    resultado.memoria_usada = pico
    resultado.tamano_texto_cifrado = len(bits_texto_cifrado) // 8

    # ===== DESCIFRADO =====
    inicio_descifrado = time.perf_counter()
    bits_descifrados = DES_descifrar(bits_texto_cifrado, clave)
    fin_descifrado = time.perf_counter()

    resultado.tiempo_descifrado = fin_descifrado - inicio_descifrado
    resultado.tiempo_total = (fin_cifrado - inicio) + \
        resultado.tiempo_descifrado
    # Estimar 5% para preparación de clave
    resultado.tiempo_preparacion_clave = resultado.tiempo_cifrado * 0.05

    resultado.calcular_metricas()
    # Primeros 64 caracteres hexadecimales
    return resultado, bits_a_hex(bits_texto_cifrado)[:64]


def probar_aes(texto_plano, tipo_mensaje):
    """Probar cifrado/descifrado AES-128"""
    clave = "secretkey1234567"  # Exactamente 16 caracteres = 128 bits (requerido por AES-128)
    assert len(clave) == 16, "AES-128 requiere una clave de exactamente 16 caracteres (128 bits)"
    resultado = ResultadoPrueba("AES-128", tipo_mensaje, len(texto_plano))

    tracemalloc.start()
    inicio = time.perf_counter()

    # ===== CIFRADO =====
    inicio_cifrado = time.perf_counter()
    bytes_texto_cifrado = AES_cifrar(texto_plano, clave)
    fin_cifrado = time.perf_counter()

    actual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    resultado.tiempo_cifrado = fin_cifrado - inicio_cifrado
    resultado.memoria_usada = pico
    resultado.tamano_texto_cifrado = len(bytes_texto_cifrado)

    # ===== DESCIFRADO =====
    inicio_descifrado = time.perf_counter()
    bytes_descifrados = AES_descifrar(bytes_texto_cifrado, clave)
    fin_descifrado = time.perf_counter()

    resultado.tiempo_descifrado = fin_descifrado - inicio_descifrado
    resultado.tiempo_total = (fin_cifrado - inicio) + \
        resultado.tiempo_descifrado
    # Estimar 8% para expansión de clave
    resultado.tiempo_preparacion_clave = resultado.tiempo_cifrado * 0.08

    resultado.calcular_metricas()
    return resultado, bytes_a_hex(bytes_texto_cifrado)[:64]




def imprimir_tabla_comparacion(resultados):
    """Imprimir tabla de comparación formateada"""
    print("\n" + "=" * 100)
    print("LIGHTWEIGHT CRYPTOGRAPHY PERFORMANCE COMPARISON")
    print("=" * 100)

    # Agrupar por tipo de mensaje
    tipos_mensaje = {}
    for resultado in resultados:
        if resultado.tipo_mensaje not in tipos_mensaje:
            tipos_mensaje[resultado.tipo_mensaje] = []
        tipos_mensaje[resultado.tipo_mensaje].append(resultado)

    for tipo_mensaje, resultados_mensaje in tipos_mensaje.items():
        print(f"\n{'=' * 100}")
        print(f"MESSAGE TYPE: {tipo_mensaje.upper()}")
        print(f"Size: {resultados_mensaje[0].tamano_texto_plano} bytes")
        print(f"{'=' * 100}")

        # Encabezado
        print(
            f"\n{'Algorithm':<15} {'Enc Time':<15} {'Dec Time':<15} "
            f"{'Throughput':<15} {'Cycles/Byte':<15} {'Memory':<12} "
            f"{'Overhead':<10}"
        )
        print(
            f"{'':<15} {'CIFRADO (ms)':<15} {'DESCIFRADO (ms)':<15} "
            f"{'(Enc, MB/s)':<15} {'(Enc, est.)':<15} {'(KB)':<12} "
            f"{'(%)':<10}"
        )
        print("-" * 100)

        # Filas de datos
        for resultado in resultados_mensaje:
            print(
                f"{resultado.algoritmo:<15} "
                f"{resultado.tiempo_cifrado * 1000:<15.4f} "
                f"{resultado.tiempo_descifrado * 1000:<15.4f} "
                f"{resultado.rendimiento_mbps:<15.4f} "
                f"{resultado.ciclos_por_byte:<15.2f} "
                f"{resultado.memoria_kb:<12.2f} "
                f"{resultado.porcentaje_sobrecarga:<10.2f}"
            )

        # Encontrar mejor rendimiento
        mejor_cifrado = min(resultados_mensaje, key=lambda x: x.tiempo_cifrado)
        mejor_descifrado = min(
            resultados_mensaje, key=lambda x: x.tiempo_descifrado)
        mejor_rendimiento = max(
            resultados_mensaje, key=lambda x: x.rendimiento_mbps)
        mejor_memoria = min(resultados_mensaje, key=lambda x: x.memoria_usada)

        print(f"\n{'Best Encryption Speed (CIFRADO):':<35} {
              mejor_cifrado.algoritmo}")
        print(
            f"{'Best Decryption Speed (DESCIFRADO):':<35} {
                mejor_descifrado.algoritmo}"
        )
        print(f"{'Best Throughput (Encryption):':<35} {
              mejor_rendimiento.algoritmo}")
        print(f"{'Lowest Memory Usage:':<35} {mejor_memoria.algoritmo}")


def imprimir_resultados_detallados(resultados):
    """Imprimir resultados detallados para cada prueba"""
    print("\n\n" + "=" * 100)
    print("DETAILED BENCHMARK RESULTS")
    print("=" * 100)

    for resultado in resultados:
        print(resultado)


def generar_graficos(resultados):
    """Generar gráficos de comparación de resultados de prueba"""
    print("\n\n" + "=" * 100)
    print("GENERATING COMPARISON CHARTS")
    print("=" * 100)

    # Organizar datos por tipo de mensaje y algoritmo
    tipos_mensaje = ["corto", "mediano", "largo", "muy_largo", "extremo_iot"]
    algoritmos = ["DES", "AES-128"]

    datos = {
        tipo_msg: {algo: None for algo in algoritmos} for tipo_msg in tipos_mensaje
    }

    for resultado in resultados:
        datos[resultado.tipo_mensaje][resultado.algoritmo] = resultado

    # Preparar datos para graficar
    tamanos_mensaje = []
    tiempos_cifrado = {algo: [] for algo in algoritmos}
    tiempos_descifrado = {algo: [] for algo in algoritmos}
    rendimientos = {algo: [] for algo in algoritmos}
    uso_memoria = {algo: [] for algo in algoritmos}
    ciclos_por_byte = {algo: [] for algo in algoritmos}

    etiquetas_mensaje = []
    for tipo_mensaje in tipos_mensaje:
        for algo in algoritmos:
            if datos[tipo_mensaje][algo]:
                resultado = datos[tipo_mensaje][algo]
                # Solo agregar una vez por tipo de mensaje
                if algo == algoritmos[0]:
                    tamanos_mensaje.append(resultado.tamano_texto_plano)
                    etiquetas_mensaje.append(
                        f"{tipo_mensaje}\n({resultado.tamano_texto_plano}B)"
                    )
                # Convertir a ms
                tiempos_cifrado[algo].append(resultado.tiempo_cifrado * 1000)
                tiempos_descifrado[algo].append(
                    resultado.tiempo_descifrado * 1000)
                rendimientos[algo].append(resultado.rendimiento_mbps)
                uso_memoria[algo].append(resultado.memoria_kb)
                ciclos_por_byte[algo].append(resultado.ciclos_por_byte)

    # Crear figura con subgráficos - expandido a 3x3 para más gráficos
    fig = plt.figure(figsize=(18, 15))

    # Esquema de colores
    colores = {"DES": "#FF6B6B", "AES-128": "#4ECDC4"}

    # 1. Comparación de Tiempo de Cifrado (CIFRADO)
    ax1 = plt.subplot(3, 3, 1)
    x = np.arange(len(etiquetas_mensaje))
    ancho = 0.35  # Wider bars for 2 algorithms instead of 3
    for i, algo in enumerate(algoritmos):
        ax1.bar(
            x + i * ancho,
            tiempos_cifrado[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax1.set_xlabel("Tipo de Mensaje", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Tiempo de Cifrado (ms)", fontsize=10, fontweight="bold")
    ax1.set_title("Comparación: Tiempo de CIFRADO",
                  fontsize=12, fontweight="bold")
    ax1.set_xticks(x + ancho)
    ax1.set_xticklabels(etiquetas_mensaje, fontsize=8)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # 2. Comparación de Tiempo de Descifrado (DESCIFRADO)
    ax2 = plt.subplot(3, 3, 2)
    for i, algo in enumerate(algoritmos):
        ax2.bar(
            x + i * ancho,
            tiempos_descifrado[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax2.set_xlabel("Tipo de Mensaje", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Tiempo de Descifrado (ms)", fontsize=10, fontweight="bold")
    ax2.set_title("Comparación: Tiempo de DESCIFRADO",
                  fontsize=12, fontweight="bold")
    ax2.set_xticks(x + ancho)
    ax2.set_xticklabels(etiquetas_mensaje, fontsize=8)
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    # 3. Comparación de Rendimiento
    ax3 = plt.subplot(3, 3, 3)
    for i, algo in enumerate(algoritmos):
        ax3.bar(
            x + i * ancho,
            rendimientos[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax3.set_xlabel("Tipo de Mensaje", fontsize=10, fontweight="bold")
    ax3.set_ylabel("Rendimiento (MB/s)", fontsize=10, fontweight="bold")
    ax3.set_title("Comparación: Rendimiento (Cifrado)",
                  fontsize=12, fontweight="bold")
    ax3.set_xticks(x + ancho)
    ax3.set_xticklabels(etiquetas_mensaje, fontsize=8)
    ax3.legend()
    ax3.grid(axis="y", alpha=0.3)

    # 4. Comparación de Uso de Memoria
    ax4 = plt.subplot(3, 3, 4)
    for i, algo in enumerate(algoritmos):
        ax4.bar(
            x + i * ancho,
            uso_memoria[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax4.set_xlabel("Tipo de Mensaje", fontsize=10, fontweight="bold")
    ax4.set_ylabel("Uso de Memoria (KB)", fontsize=10, fontweight="bold")
    ax4.set_title("Comparación: Uso de Memoria",
                  fontsize=12, fontweight="bold")
    ax4.set_xticks(x + ancho)
    ax4.set_xticklabels(etiquetas_mensaje, fontsize=8)
    ax4.legend()
    ax4.grid(axis="y", alpha=0.3)

    # 5. Tiempo de Cifrado vs Tamaño de Mensaje (Gráfico de Líneas)
    ax5 = plt.subplot(3, 3, 5)
    for algo in algoritmos:
        ax5.plot(
            tamanos_mensaje,
            tiempos_cifrado[algo],
            marker="o",
            linewidth=2,
            markersize=8,
            label=algo,
            color=colores[algo],
        )
    ax5.set_xlabel("Tamaño del Mensaje (bytes)",
                   fontsize=10, fontweight="bold")
    ax5.set_ylabel("Tiempo de Cifrado (ms)", fontsize=10, fontweight="bold")
    ax5.set_title(
        "Escalabilidad: Tiempo vs Tamaño del Mensaje", fontsize=12, fontweight="bold"
    )
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_xscale("log")
    ax5.set_yscale("log")

    # 6. Tiempo de Descifrado vs Tamaño de Mensaje (Gráfico de Líneas)
    ax6 = plt.subplot(3, 3, 6)
    for algo in algoritmos:
        ax6.plot(
            tamanos_mensaje,
            tiempos_descifrado[algo],
            marker="s",
            linewidth=2,
            markersize=8,
            label=algo,
            color=colores[algo],
        )
    ax6.set_xlabel("Tamaño del Mensaje (bytes)",
                   fontsize=10, fontweight="bold")
    ax6.set_ylabel("Tiempo de Descifrado (ms)", fontsize=10, fontweight="bold")
    ax6.set_title(
        "Escalabilidad: Tiempo Descifrado vs Tamaño", fontsize=12, fontweight="bold"
    )
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    ax6.set_xscale("log")
    ax6.set_yscale("log")

    # 7. Comparación de Ciclos por Byte
    ax7 = plt.subplot(3, 3, 7)
    for i, algo in enumerate(algoritmos):
        ax7.bar(
            x + i * ancho,
            ciclos_por_byte[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax7.set_xlabel("Tipo de Mensaje", fontsize=10, fontweight="bold")
    ax7.set_ylabel("Ciclos por Byte", fontsize=10, fontweight="bold")
    ax7.set_title("Eficiencia de CPU (Menor es Mejor)",
                  fontsize=12, fontweight="bold")
    ax7.set_xticks(x + ancho)
    ax7.set_xticklabels(etiquetas_mensaje, fontsize=8)
    ax7.legend()
    ax7.grid(axis="y", alpha=0.3)

    # 8. Puntuación de Rendimiento General
    ax8 = plt.subplot(3, 3, 8)
    # Normalizar métricas para comparación (menor es mejor para todas)
    datos_normalizados = {}
    for algo in algoritmos:
        # Puntuaciones normalizadas promedio (escala 0-1)
        norm_cifrado = np.array(tiempos_cifrado[algo]) / max(
            [max(tiempos_cifrado[a]) for a in algoritmos]
        )
        norm_descifrado = np.array(tiempos_descifrado[algo]) / max(
            [max(tiempos_descifrado[a]) for a in algoritmos]
        )
        norm_memoria = np.array(uso_memoria[algo]) / max(
            [max(uso_memoria[a]) for a in algoritmos]
        )
        norm_ciclos = np.array(ciclos_por_byte[algo]) / max(
            [max(ciclos_por_byte[a]) for a in algoritmos]
        )

        datos_normalizados[algo] = {
            "Tiempo Cifrado": np.mean(norm_cifrado),
            "Tiempo Descifrado": np.mean(norm_descifrado),
            "Uso de Memoria": np.mean(norm_memoria),
            "Ciclos de CPU": np.mean(norm_ciclos),
        }

    categorias = [
        "Tiempo Cifrado",
        "Tiempo Descifrado",
        "Uso de Memoria",
        "Ciclos de CPU",
    ]
    posicion_x = np.arange(len(categorias))
    ancho_comparacion = 0.25

    for i, algo in enumerate(algoritmos):
        valores = [datos_normalizados[algo][cat] for cat in categorias]
        ax8.bar(
            posicion_x + i * ancho_comparacion,
            valores,
            ancho_comparacion,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )

    ax8.set_xlabel("Métrica de Rendimiento", fontsize=10, fontweight="bold")
    ax8.set_ylabel(
        "Puntuación Normalizada (Menor es Mejor)", fontsize=10, fontweight="bold"
    )
    ax8.set_title("Comparación General de Rendimiento",
                  fontsize=12, fontweight="bold")
    ax8.set_xticks(posicion_x + ancho_comparacion)
    ax8.set_xticklabels(categorias, fontsize=8, rotation=15)
    ax8.legend()
    ax8.grid(axis="y", alpha=0.3)

    plt.suptitle(
        "Análisis de Rendimiento: Criptografía Ligera\nDES vs AES-128",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Guardar la figura
    archivo_salida = os.path.join(
        DIRECTORIO_RESULTADOS, "benchmark_charts.png")
    plt.savefig(archivo_salida, dpi=300, bbox_inches="tight")
    print(f"\n[OK] Gráficos guardados en: {archivo_salida}")

    # También crear gráficos individuales para mejor legibilidad

    # Gráfico Individual 1: Tiempo de Cifrado
    fig1, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(etiquetas_mensaje))
    ancho = 0.25
    for i, algo in enumerate(algoritmos):
        ax.bar(
            x + i * ancho,
            tiempos_cifrado[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
    ax.set_ylabel("Tiempo de Cifrado (ms)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Comparación de Tiempo de Cifrado - Algoritmos de Criptografía Ligera",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x + ancho)
    ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_encryption_time.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Encryption time chart saved to: results/chart_encryption_time.png")

    # Gráfico Individual 2: Rendimiento
    fig2, ax = plt.subplots(figsize=(12, 6))
    for i, algo in enumerate(algoritmos):
        ax.bar(
            x + i * ancho,
            rendimientos[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
    ax.set_ylabel("Rendimiento (MB/s)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Comparación de Rendimiento - Algoritmos de Criptografía Ligera",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x + ancho)
    ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_throughput.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Throughput chart saved to: results/chart_throughput.png")

    # Gráfico Individual 3: Escalabilidad
    fig3, ax = plt.subplots(figsize=(12, 6))
    for algo in algoritmos:
        ax.plot(
            tamanos_mensaje,
            tiempos_cifrado[algo],
            marker="o",
            linewidth=3,
            markersize=10,
            label=algo,
            color=colores[algo],
        )
    ax.set_xlabel("Tamaño del Mensaje (bytes)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Tiempo de Cifrado (ms)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Análisis de Escalabilidad - Tiempo vs Tamaño del Mensaje",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_scalability.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Scalability chart saved to: results/chart_scalability.png")

    # Gráfico Individual 3b: Escalabilidad Descifrado
    fig3b, ax = plt.subplots(figsize=(12, 6))
    for algo in algoritmos:
        ax.plot(
            tamanos_mensaje,
            tiempos_descifrado[algo],
            marker="s",
            linewidth=3,
            markersize=10,
            label=algo,
            color=colores[algo],
        )
    ax.set_xlabel("Tamaño del Mensaje (bytes)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Tiempo de Descifrado (ms)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Análisis de Escalabilidad - Tiempo de Descifrado vs Tamaño del Mensaje",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_scalability_decryption.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Scalability decryption chart saved to: results/chart_scalability_decryption.png")

    # Gráfico Individual 4: Uso de Memoria
    fig4, ax = plt.subplots(figsize=(12, 6))
    for i, algo in enumerate(algoritmos):
        ax.bar(
            x + i * ancho,
            uso_memoria[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
    ax.set_ylabel("Uso de Memoria (KB)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Comparación de Uso de Memoria - Algoritmos de Criptografía Ligera",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x + ancho)
    ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_memory_usage.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Memory usage chart saved to: results/chart_memory_usage.png")

    # 5. Gráfico de Consumo de Energía
    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(etiquetas_mensaje))
    ancho = 0.25

    energia_des = [
        r.energia_milijulios for r in resultados if r.algoritmo == "DES"]
    energia_aes = [
        r.energia_milijulios for r in resultados if r.algoritmo == "AES-128"]

    ax.bar(x - ancho/2, energia_des, ancho, label="DES",
           color=colores["DES"], alpha=0.8)
    ax.bar(x + ancho/2, energia_aes, ancho, label="AES-128",
           color=colores["AES-128"], alpha=0.8)

    ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
    ax.set_ylabel("Energía Consumida (mJ)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Comparación de Consumo Energético - Hardware PC (Menor es Mejor)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x + ancho)
    ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_energy_consumption.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(
        f"[OK] Energy consumption chart saved to: results/chart_energy_consumption.png"
    )

    # 6. Gráfico Individual: Tiempo de Descifrado
    fig6, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(etiquetas_mensaje))
    ancho = 0.25
    for i, algo in enumerate(algoritmos):
        ax.bar(
            x + i * ancho,
            tiempos_descifrado[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
    ax.set_ylabel("Tiempo de Descifrado (ms)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Comparación de Tiempo de Descifrado - Algoritmos de Criptografía Ligera",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x + ancho)
    ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_decryption_time.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Decryption time chart saved to: results/chart_decryption_time.png")

    # 7. Gráfico Individual: Ciclos por Byte
    fig7, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(etiquetas_mensaje))
    ancho = 0.25
    for i, algo in enumerate(algoritmos):
        ax.bar(
            x + i * ancho,
            ciclos_por_byte[algo],
            ancho,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )
    ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
    ax.set_ylabel("Ciclos por Byte", fontsize=12, fontweight="bold")
    ax.set_title(
        "Eficiencia de CPU - Ciclos por Byte (Menor es Mejor)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x + ancho)
    ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_cpu_cycles.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] CPU cycles chart saved to: results/chart_cpu_cycles.png")

    # 8. Gráfico Individual: Comparación General de Rendimiento
    fig8, ax = plt.subplots(figsize=(12, 6))
    categorias = [
        "Tiempo Cifrado",
        "Tiempo Descifrado",
        "Uso de Memoria",
        "Ciclos de CPU",
    ]
    posicion_x = np.arange(len(categorias))
    ancho_comparacion = 0.25

    # Calcular datos normalizados
    datos_normalizados = {}
    for algo in algoritmos:
        norm_cifrado = np.array(tiempos_cifrado[algo]) / max(
            [max(tiempos_cifrado[a]) for a in algoritmos]
        )
        norm_descifrado = np.array(tiempos_descifrado[algo]) / max(
            [max(tiempos_descifrado[a]) for a in algoritmos]
        )
        norm_memoria = np.array(uso_memoria[algo]) / max(
            [max(uso_memoria[a]) for a in algoritmos]
        )
        norm_ciclos = np.array(ciclos_por_byte[algo]) / max(
            [max(ciclos_por_byte[a]) for a in algoritmos]
        )

        datos_normalizados[algo] = {
            "Tiempo Cifrado": np.mean(norm_cifrado),
            "Tiempo Descifrado": np.mean(norm_descifrado),
            "Uso de Memoria": np.mean(norm_memoria),
            "Ciclos de CPU": np.mean(norm_ciclos),
        }

    for i, algo in enumerate(algoritmos):
        valores = [datos_normalizados[algo][cat] for cat in categorias]
        ax.bar(
            posicion_x + i * ancho_comparacion,
            valores,
            ancho_comparacion,
            label=algo,
            color=colores[algo],
            alpha=0.8,
        )

    ax.set_xlabel("Métrica de Rendimiento", fontsize=12, fontweight="bold")
    ax.set_ylabel(
        "Puntuación Normalizada (Menor es Mejor)", fontsize=12, fontweight="bold"
    )
    ax.set_title(
        "Comparación General de Rendimiento - Todos los Algoritmos",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(posicion_x + ancho_comparacion)
    ax.set_xticklabels(categorias, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(DIRECTORIO_RESULTADOS, "chart_overall_performance.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"[OK] Overall performance chart saved to: results/chart_overall_performance.png")

    plt.close("all")
    print("\n[OK] All charts generated successfully!")


def ejecutar_pruebas():
    """Ejecutar todas las pruebas de rendimiento"""
    print("Loading test messages...")

    # Cargar mensajes de prueba
    with open(
        os.path.join(DIRECTORIO_DATOS, "short_message.txt"), "r", encoding="utf-8"
    ) as f:
        mensaje_corto = f.read()

    with open(
        os.path.join(DIRECTORIO_DATOS, "medium_message.txt"), "r", encoding="utf-8"
    ) as f:
        mensaje_mediano = f.read()

    with open(
        os.path.join(DIRECTORIO_DATOS, "long_message.txt"), "r", encoding="utf-8"
    ) as f:
        mensaje_largo = f.read()

    with open(
        os.path.join(DIRECTORIO_DATOS, "very_long_message.txt"), "r", encoding="utf-8"
    ) as f:
        mensaje_muy_largo = f.read()

    with open(
        os.path.join(DIRECTORIO_DATOS, "extreme_iot_message.txt"), "r", encoding="utf-8"
    ) as f:
        mensaje_extremo = f.read()

    casos_prueba = [
        ("corto", mensaje_corto),
        ("mediano", mensaje_mediano),
        ("largo", mensaje_largo),
        ("muy_largo", mensaje_muy_largo),
        ("extremo_iot", mensaje_extremo),
    ]

    resultados = []
    textos_cifrados = {}

    for tipo_mensaje, mensaje in casos_prueba:
        print(f"\n{'=' * 80}")
        print(f"Benchmarking {tipo_mensaje.upper()
                              } message ({len(mensaje)} bytes)...")
        print(f"{'=' * 80}")

        textos_cifrados[tipo_mensaje] = {}

        # Ejecución de calentamiento
        _ = DES_cifrar(mensaje[:64], "secret12")

        print(f"\n[1/3] Testing DES...")
        resultado_des, tc_des = probar_des(mensaje, tipo_mensaje)
        resultados.append(resultado_des)
        textos_cifrados[tipo_mensaje]["DES"] = tc_des
        print(f"[OK] DES completed: {
              resultado_des.tiempo_cifrado * 1000:.2f} ms")

        print(f"[2/3] Testing AES-128...")
        resultado_aes, tc_aes = probar_aes(mensaje, tipo_mensaje)
        resultados.append(resultado_aes)
        textos_cifrados[tipo_mensaje]["AES-128"] = tc_aes
        print(
            f"[OK] AES-128 completed: {resultado_aes.tiempo_cifrado * 1000:.2f} ms")

    # Imprimir tabla de comparación
    imprimir_tabla_comparacion(resultados)

    # Imprimir textos cifrados de muestra
    print("\n\n" + "=" * 100)
    print("SAMPLE CIPHERTEXTS (first 64 hex characters)")
    print("=" * 100)
    for tipo_mensaje, algoritmos in textos_cifrados.items():
        print(f"\n{tipo_mensaje.upper()}:")
        for algo, tc in algoritmos.items():
            print(f"  {algo:<15}: {tc}")

    # Imprimir resultados detallados
    imprimir_resultados_detallados(resultados)

    # Generar gráficos de visualización
    generar_graficos(resultados)

    # Imprimir resumen
    print("\n\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)
    print("""
Key Findings:
1. AES-128: Generally fastest for larger messages due to mature optimization
2. DES: Legacy algorithm, moderate performance, 64-bit block size limitation

Important Notes:
- These are SOFTWARE implementations on a general-purpose CPU
- Hardware implementations would show very different results
- Memory usage includes Python interpreter overhead
- Cycles per byte are estimated based on wall-clock time
    """)

    return resultados


if __name__ == "__main__":
    print("=" * 100)
    print("LIGHTWEIGHT CRYPTOGRAPHY BENCHMARK SUITE")
    print("Comparing DES vs AES-128")
    print("=" * 100)
    print(f"\nPython version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print("\nStarting benchmarks...\n")

    ejecutar_pruebas()

    print("\n" + "=" * 100)
    print("BENCHMARK COMPLETE")
    print("=" * 100)
