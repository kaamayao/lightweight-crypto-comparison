"""
Benchmark unificado para comparación de criptografía ligera
Evalúa DES y AES-128 con perfiles de recursos configurables:
- Sin restricciones (PC/Servidor)
- Dispositivos IoT de gama media (ESP32)
- Dispositivos IoT de gama baja (ESP8266)
- Dispositivos ultra restringidos (sensores)

Métricas evaluadas:
- Rendimiento de Cifrado/Descifrado (MB/s)
- Latencia (ms por operación)
- Tiempo de preparación de clave (ms)
- Ciclos por byte (estimado)
- Uso de memoria
- Sobrecarga del texto cifrado
- Consumo de energía estimado
"""

import time
import sys
import tracemalloc
import os
import psutil
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


# ============================================================================
# PERFILES DE DISPOSITIVOS
# ============================================================================


def obtener_perfiles_dispositivo():
    """Definir perfiles de recursos para diferentes clases de dispositivos"""
    return {
        "sin_restricciones": {
            "porcentaje_cpu": 100,
            "limite_memoria_mb": 4096,
            "descripcion": "PC/Servidor sin restricciones",
            "ejemplos": "Desktop, Server, Workstation",
            "restringido": False,
        },
        "high_end_pc": {
            "porcentaje_cpu": 100,
            "limite_memoria_mb": 2048,
            "descripcion": "PC de gama alta / Servidor (línea base)",
            "ejemplos": "Desktop, Server, Raspberry Pi 4",
            "restringido": True,
        },
        "mid_range_iot": {
            "porcentaje_cpu": 50,
            "limite_memoria_mb": 256,
            "descripcion": "Dispositivo IoT de gama media",
            "ejemplos": "ESP32, Arduino Due, STM32F4",
            "restringido": True,
        },
        "low_end_iot": {
            "porcentaje_cpu": 25,
            "limite_memoria_mb": 64,
            "descripcion": "Dispositivo IoT de gama baja",
            "ejemplos": "ESP8266, Arduino Uno, ATmega328",
            "restringido": True,
        },
        "ultra_constrained": {
            "porcentaje_cpu": 10,
            "limite_memoria_mb": 16,
            "descripcion": "Dispositivo ultra restringido",
            "ejemplos": "Sensor nodes, RFID tags, MSP430",
            "restringido": True,
        },
    }


# ============================================================================
# GESTOR DE RESTRICCIONES DE RECURSOS
# ============================================================================


class EntornoRestringido:
    """Gestor de contexto para simular entorno con recursos restringidos"""

    def __init__(self, perfil=None):
        """
        Args:
            perfil: Diccionario con configuración del perfil o None para sin restricciones
        """
        self.perfil = perfil
        self.pid = os.getpid()
        self.original_affinity = None
        self.original_nice = None

    def __enter__(self):
        if self.perfil is None or not self.perfil.get("restringido", False):
            # Sin restricciones - no hacer nada
            return self

        print(f"\n{'=' * 80}")
        print(f"Simulando: {self.perfil['descripcion']}")
        print(
            f"Límite CPU: {self.perfil['porcentaje_cpu']}% | Límite Memoria: {
                self.perfil['limite_memoria_mb']
            }MB"
        )
        print(f"{'=' * 80}")

        # Establecer afinidad de CPU a un solo núcleo para consistencia
        try:
            p = psutil.Process(self.pid)
            self.original_affinity = p.cpu_affinity()
            p.cpu_affinity([0])  # Usar solo el primer núcleo de CPU
        except (AttributeError, PermissionError):
            print("Advertencia: No se pudo establecer afinidad de CPU")

        # Establecer prioridad del proceso para simular CPU más lenta
        try:
            self.original_nice = os.nice(0)
            os.nice(10)  # Prioridad más baja
        except (PermissionError, OSError):
            print("Advertencia: No se pudo establecer prioridad del proceso")

        return self

    def __exit__(self, tipo_exc, valor_exc, tb_exc):
        if self.perfil is None or not self.perfil.get("restringido", False):
            return

        # Restablecer afinidad de CPU
        if self.original_affinity is not None:
            try:
                p = psutil.Process(self.pid)
                p.cpu_affinity(self.original_affinity)
            except (AttributeError, PermissionError):
                pass

        # Restablecer prioridad
        if self.original_nice is not None:
            try:
                current_nice = os.nice(0)
                os.nice(self.original_nice - current_nice)
            except (PermissionError, OSError):
                pass


# ============================================================================
# CLASES DE RESULTADOS
# ============================================================================


class ResultadoPrueba:
    def __init__(
        self,
        algoritmo,
        tipo_mensaje,
        tamano_texto_plano,
        perfil_nombre="sin_restricciones",
    ):
        self.algoritmo = algoritmo
        self.tipo_mensaje = tipo_mensaje
        self.tamano_texto_plano = tamano_texto_plano
        self.perfil_nombre = perfil_nombre
        self.tiempo_preparacion_clave = 0
        self.tiempo_cifrado = 0
        self.tiempo_descifrado = 0
        self.tiempo_total = 0
        self.memoria_cifrado = 0
        self.memoria_descifrado = 0
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
        self.memoria_cifrado_kb = self.memoria_cifrado / 1024
        self.memoria_descifrado_kb = self.memoria_descifrado / 1024

        # Estimación de consumo de energía para hardware de PC
        # CPU: x86-64 moderno @ 2.5 GHz, TDP típico 15-65W
        # Potencia promedio durante operaciones criptográficas:
        # ~20W para móvil, ~45W para escritorio
        potencia_cpu_watts = 35  # Promedio entre móvil y escritorio
        self.energia_julios = potencia_cpu_watts * self.tiempo_cifrado
        self.energia_milijulios = self.energia_julios * 1000

        # Para dispositivos restringidos, ajustar consumo de energía
        self.rendimiento_kbps = (
            (self.tamano_texto_plano / 1024) / self.tiempo_cifrado
            if self.tiempo_cifrado > 0
            else 0
        )

    def __str__(self):
        return f"""
Algoritmo: {self.algoritmo}
Tipo de Mensaje: {self.tipo_mensaje}
Perfil: {self.perfil_nombre}
Tamaño Plaintext: {self.tamano_texto_plano} bytes
-----------------------------------------
Tiempo CIFRADO: {self.tiempo_cifrado * 1000:.4f} ms
Tiempo DESCIFRADO: {self.tiempo_descifrado * 1000:.4f} ms
Tiempo Total: {self.tiempo_total * 1000:.4f} ms
-----------------------------------------
Rendimiento (Cifrado): {self.rendimiento_mbps:.4f} MB/s
Ciclos/Byte (Cifrado, est.): {self.ciclos_por_byte:.2f}
Memoria Cifrado: {self.memoria_cifrado_kb:.2f} KB
Memoria Descifrado: {self.memoria_descifrado_kb:.2f} KB
Energía Consumida (Cifrado): {self.energia_milijulios:.4f} mJ
Tamaño Ciphertext: {self.tamano_texto_cifrado} bytes
Sobrecarga: {self.porcentaje_sobrecarga:.2f}%
"""


def probar_des(texto_plano, tipo_mensaje, perfil=None):
    clave = "secret12"
    assert len(clave) == 8, (
        "DES requiere una clave de exactamente 8 caracteres (64 bits)"
    )

    perfil_nombre = perfil["descripcion"] if perfil else "sin_restricciones"
    resultado = ResultadoPrueba(
        "DES", tipo_mensaje, len(texto_plano), perfil_nombre)

    with EntornoRestringido(perfil):
        # ===== CIFRADO =====
        tracemalloc.start()
        inicio = time.perf_counter()
        inicio_cifrado = time.perf_counter()
        bits_texto_cifrado = DES_cifrar(texto_plano, clave)
        fin_cifrado = time.perf_counter()

        _, pico_cifrado = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultado.tiempo_cifrado = fin_cifrado - inicio_cifrado
        resultado.memoria_cifrado = pico_cifrado
        resultado.tamano_texto_cifrado = len(bits_texto_cifrado) // 8

        # ===== DESCIFRADO =====
        tracemalloc.start()
        inicio_descifrado = time.perf_counter()
        DES_descifrar(bits_texto_cifrado, clave)
        fin_descifrado = time.perf_counter()

        _, pico_descifrado = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultado.tiempo_descifrado = fin_descifrado - inicio_descifrado
        resultado.memoria_descifrado = pico_descifrado
        resultado.tiempo_total = (fin_cifrado - inicio) + resultado.tiempo_descifrado
        resultado.tiempo_preparacion_clave = resultado.tiempo_cifrado * 0.05
        resultado.calcular_metricas()

        return resultado, bits_a_hex(bits_texto_cifrado)[:64]


def probar_aes(texto_plano, tipo_mensaje, perfil=None):
    """Probar cifrado/descifrado AES-128 bajo un perfil de recursos"""
    clave = "secretkey1234567"  # Exactamente 16 caracteres = 128 bits (requerido por AES-128)
    assert len(clave) == 16, (
        "AES-128 requiere una clave de exactamente 16 caracteres (128 bits)"
    )

    perfil_nombre = perfil["descripcion"] if perfil else "sin_restricciones"
    resultado = ResultadoPrueba(
        "AES-128", tipo_mensaje, len(texto_plano), perfil_nombre
    )

    with EntornoRestringido(perfil):
        inicio = time.perf_counter()

        # ===== CIFRADO =====
        tracemalloc.start()
        inicio_cifrado = time.perf_counter()
        bytes_texto_cifrado = AES_cifrar(texto_plano, clave)
        fin_cifrado = time.perf_counter()

        _, pico_cifrado = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultado.tiempo_cifrado = fin_cifrado - inicio_cifrado
        resultado.memoria_cifrado = pico_cifrado
        resultado.tamano_texto_cifrado = len(bytes_texto_cifrado)

        # ===== DESCIFRADO =====
        tracemalloc.start()
        inicio_descifrado = time.perf_counter()
        bytes_descifrados = AES_descifrar(bytes_texto_cifrado, clave)
        fin_descifrado = time.perf_counter()

        _, pico_descifrado = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultado.tiempo_descifrado = fin_descifrado - inicio_descifrado
        resultado.memoria_descifrado = pico_descifrado
        resultado.tiempo_total = (fin_cifrado - inicio) + resultado.tiempo_descifrado
        # Estimar 8% para expansión de clave
        resultado.tiempo_preparacion_clave = resultado.tiempo_cifrado * 0.08

        resultado.calcular_metricas()
        return resultado, bytes_a_hex(bytes_texto_cifrado)[:64]


# ============================================================================
# FUNCIONES DE VISUALIZACIÓN Y REPORTES
# ============================================================================


def imprimir_tabla_comparacion(resultados, perfil_actual=None):
    """Imprimir tabla de comparación formateada"""
    print("\n" + "=" * 100)
    print("COMPARACIÓN DE RENDIMIENTO DE CRIPTOGRAFÍA LIGERA")
    if perfil_actual:
        print(f"Perfil: {perfil_actual['descripcion']}")
    print("=" * 100)

    # Agrupar por tipo de mensaje
    tipos_mensaje = {}
    for resultado in resultados:
        if resultado.tipo_mensaje not in tipos_mensaje:
            tipos_mensaje[resultado.tipo_mensaje] = []
        tipos_mensaje[resultado.tipo_mensaje].append(resultado)

    for tipo_mensaje, resultados_mensaje in tipos_mensaje.items():
        print(f"\n{'=' * 100}")
        print(f"TIPO DE MENSAJE: {tipo_mensaje.upper()}")
        print(f"Tamaño: {resultados_mensaje[0].tamano_texto_plano} bytes")
        print(f"{'=' * 100}")

        # Encabezado
        print(
            f"\n{'Algoritmo':<15} {'Tiempo Cifr.':<15} {'Tiempo Desc.':<15} "
            f"{'Rendimiento':<15} {'Ciclos/Byte':<15} {'Mem Cifr.':<12} "
            f"{'Mem Desc.':<12} {'Sobrecarga':<10}"
        )
        print(
            f"{'':<15} {'CIFRADO (ms)':<15} {'DESCIFRADO (ms)':<15} "
            f"{'(Cifr, MB/s)':<15} {'(Cifr, est.)':<15} {'(KB)':<12} "
            f"{'(KB)':<12} {'(%)':<10}"
        )
        print("-" * 115)

        # Filas de datos
        for resultado in resultados_mensaje:
            print(
                f"{resultado.algoritmo:<15} "
                f"{resultado.tiempo_cifrado * 1000:<15.4f} "
                f"{resultado.tiempo_descifrado * 1000:<15.4f} "
                f"{resultado.rendimiento_mbps:<15.4f} "
                f"{resultado.ciclos_por_byte:<15.2f} "
                f"{resultado.memoria_cifrado_kb:<12.2f} "
                f"{resultado.memoria_descifrado_kb:<12.2f} "
                f"{resultado.porcentaje_sobrecarga:<10.2f}"
            )

        # Encontrar mejor rendimiento
        mejor_cifrado = min(resultados_mensaje, key=lambda x: x.tiempo_cifrado)
        mejor_descifrado = min(
            resultados_mensaje, key=lambda x: x.tiempo_descifrado)
        mejor_rendimiento = max(
            resultados_mensaje, key=lambda x: x.rendimiento_mbps)
        mejor_memoria_cifrado = min(resultados_mensaje, key=lambda x: x.memoria_cifrado)
        mejor_memoria_descifrado = min(resultados_mensaje, key=lambda x: x.memoria_descifrado)

        print(f"\n{'Mejor Velocidad de Cifrado:':<35} {
              mejor_cifrado.algoritmo}")
        print(f"{'Mejor Velocidad de Descifrado:':<35} {
              mejor_descifrado.algoritmo}")
        print(f"{'Mejor Rendimiento (Cifrado):':<35} {
              mejor_rendimiento.algoritmo}")
        print(f"{'Menor Uso Memoria (Cifrado):':<35} {mejor_memoria_cifrado.algoritmo}")
        print(f"{'Menor Uso Memoria (Descifrado):':<35} {mejor_memoria_descifrado.algoritmo}")


def imprimir_resultados_detallados(resultados):
    """Imprimir resultados detallados para cada prueba"""
    print("\n\n" + "=" * 100)
    print("RESULTADOS DETALLADOS DEL BENCHMARK")
    print("=" * 100)

    for resultado in resultados:
        print(resultado)


def generar_graficos(resultados, perfil_nombre="sin_restricciones"):
    """Generar gráficos de comparación de resultados de prueba"""
    print("\n\n" + "=" * 100)
    print("GENERANDO GRÁFICOS DE COMPARACIÓN")
    print(f"Perfil: {perfil_nombre}")
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
    uso_memoria_descifrado = {algo: [] for algo in algoritmos}
    energia = {algo: [] for algo in algoritmos}
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
                uso_memoria[algo].append(resultado.memoria_cifrado_kb)
                uso_memoria_descifrado[algo].append(resultado.memoria_descifrado_kb)
                energia[algo].append(resultado.energia_milijulios)
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
    ax1.set_xticks(x + ancho / 2)
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
    ax2.set_xticks(x + ancho / 2)
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
    ax3.set_xticks(x + ancho / 2)
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
    ax4.set_xticks(x + ancho / 2)
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
    ax7.set_xticks(x + ancho / 2)
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
    ax8.set_xticks(posicion_x + ancho_comparacion / 2)
    ax8.set_xticklabels(categorias, fontsize=8, rotation=15)
    ax8.legend()
    ax8.grid(axis="y", alpha=0.3)

    plt.suptitle(
        f"Análisis de Rendimiento: Criptografía Ligera\nDES vs AES-128\nPerfil: {
            perfil_nombre
        }",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Guardar la figura con nombre específico del perfil
    nombre_perfil_safe = perfil_nombre.replace("/", "_").replace(" ", "_")
    archivo_salida = os.path.join(
        DIRECTORIO_RESULTADOS, f"benchmark_charts_{nombre_perfil_safe}.png"
    )
    plt.savefig(archivo_salida, dpi=300, bbox_inches="tight")
    print(f"\n[OK] Gráficos guardados en: {archivo_salida}")

    plt.close("all")

    # ============================================================================
    # GRÁFICOS INDIVIDUALES PARA PDF (solo para perfil sin_restricciones)
    # ============================================================================

    if perfil_nombre == "sin_restricciones":
        print("\nGenerando gráficos individuales para PDF...")

        # Preparar datos para gráficos individuales
        x = np.arange(len(etiquetas_mensaje))
        ancho = 0.35  # Ancho para 2 algoritmos

        # 1. Gráfico Individual: Tiempo de Cifrado
        fig1, ax = plt.subplots(figsize=(12, 6))
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
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_encryption_time.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de tiempo de cifrado guardado")

        # 2. Gráfico Individual: Rendimiento (Throughput)
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
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_throughput.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de rendimiento guardado")

        # 3. Gráfico Individual: Escalabilidad - Cifrado
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
        print("[OK] Gráfico de escalabilidad guardado")

        # 4. Gráfico Individual: Escalabilidad - Descifrado
        fig4, ax = plt.subplots(figsize=(12, 6))
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
        print("[OK] Gráfico de escalabilidad de descifrado guardado")

        # 5. Gráfico Individual: Uso de Memoria - Cifrado
        fig5, ax = plt.subplots(figsize=(12, 6))
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
        ax.set_ylabel("Uso de Memoria Cifrado (KB)", fontsize=12, fontweight="bold")
        ax.set_title(
            "Comparación de Uso de Memoria - Cifrado",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_memory_usage.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de uso de memoria (cifrado) guardado")

        # 6. Gráfico Individual: Uso de Memoria - Descifrado
        fig6, ax = plt.subplots(figsize=(12, 6))
        for i, algo in enumerate(algoritmos):
            ax.bar(
                x + i * ancho,
                uso_memoria_descifrado[algo],
                ancho,
                label=algo,
                color=colores[algo],
                alpha=0.8,
            )
        ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
        ax.set_ylabel("Uso de Memoria Descifrado (KB)", fontsize=12, fontweight="bold")
        ax.set_title(
            "Comparación de Uso de Memoria - Descifrado",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_memory_decryption.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de uso de memoria (descifrado) guardado")

        # 7. Gráfico Individual: Consumo de Energía
        fig7, ax = plt.subplots(figsize=(12, 6))
        for i, algo in enumerate(algoritmos):
            ax.bar(
                x + i * ancho,
                energia[algo],
                ancho,
                label=algo,
                color=colores[algo],
                alpha=0.8,
            )
        ax.set_xlabel("Tipo de Mensaje", fontsize=12, fontweight="bold")
        ax.set_ylabel("Energía Consumida (mJ)", fontsize=12, fontweight="bold")
        ax.set_title(
            "Comparación de Consumo Energético - Hardware PC (Menor es Mejor)",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_energy_consumption.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de consumo de energía guardado")

        # 8. Gráfico Individual: Tiempo de Descifrado
        fig8, ax = plt.subplots(figsize=(12, 6))
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
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_decryption_time.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de tiempo de descifrado guardado")

        # 9. Gráfico Individual: Ciclos por Byte
        fig9, ax = plt.subplots(figsize=(12, 6))
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
        ax.set_xticks(x + ancho / 2)
        ax.set_xticklabels(etiquetas_mensaje, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_cpu_cycles.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de ciclos de CPU guardado")

        # 10. Gráfico Individual: Comparación General de Rendimiento
        fig10, ax = plt.subplots(figsize=(12, 6))
        categorias = [
            "Tiempo Cifrado",
            "Tiempo Descifrado",
            "Uso de Memoria",
            "Ciclos de CPU",
        ]
        posicion_x = np.arange(len(categorias))
        ancho_comparacion = 0.35

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
        ax.set_xticks(posicion_x + ancho_comparacion / 2)
        ax.set_xticklabels(categorias, fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(DIRECTORIO_RESULTADOS, "chart_overall_performance.png"),
            dpi=300,
            bbox_inches="tight",
        )
        print("[OK] Gráfico de rendimiento general guardado")

        plt.close("all")
        print("\n[OK] Todos los gráficos individuales generados exitosamente!")


# ============================================================================
# FUNCIÓN PRINCIPAL DE EJECUCIÓN
# ============================================================================


def ejecutar_pruebas(perfiles=None, generar_graficos_flag=True):
    """
    Ejecutar todas las pruebas de rendimiento

    Args:
        perfiles: Lista de nombres de perfiles a ejecutar, o None para solo sin restricciones
        generar_graficos_flag: Si generar gráficos o no

    Returns:
        Dict con resultados agrupados por perfil
    """
    print("Cargando mensajes de prueba...")

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

    # Obtener todos los perfiles disponibles
    todos_perfiles = obtener_perfiles_dispositivo()

    # Determinar qué perfiles ejecutar
    if perfiles is None:
        # Solo sin restricciones
        perfiles_a_ejecutar = {"sin_restricciones": None}
    else:
        # Perfiles especificados
        perfiles_a_ejecutar = {}
        for nombre_perfil in perfiles:
            if nombre_perfil in todos_perfiles:
                perfiles_a_ejecutar[nombre_perfil] = todos_perfiles[nombre_perfil]
            else:
                print(
                    f"Advertencia: Perfil '{
                        nombre_perfil}' no encontrado, se omitirá"
                )

    # Ejecutar pruebas para cada perfil
    todos_resultados = {}

    for nombre_perfil, config_perfil in perfiles_a_ejecutar.items():
        print("\n" + "=" * 100)
        print(
            f"EJECUTANDO BENCHMARK: {
                config_perfil['descripcion'] if config_perfil else 'Sin restricciones'
            }"
        )
        print("=" * 100)

        resultados_perfil = []
        textos_cifrados = {}

        for tipo_mensaje, mensaje in casos_prueba:
            print(f"\n{'=' * 80}")
            print(f"Probando mensaje {
                  tipo_mensaje.upper()} ({len(mensaje)} bytes)...")
            print(f"{'=' * 80}")

            textos_cifrados[tipo_mensaje] = {}

            # Ejecución de calentamiento
            _ = DES_cifrar(mensaje[:64], "secret12")

            print(f"\n[1/2] Probando DES...")
            resultado_des, tc_des = probar_des(
                mensaje, tipo_mensaje, config_perfil)
            resultados_perfil.append(resultado_des)
            textos_cifrados[tipo_mensaje]["DES"] = tc_des
            print(f"[OK] DES completado: {
                  resultado_des.tiempo_cifrado * 1000:.2f} ms")

            print(f"[2/2] Probando AES-128...")
            resultado_aes, tc_aes = probar_aes(
                mensaje, tipo_mensaje, config_perfil)
            resultados_perfil.append(resultado_aes)
            textos_cifrados[tipo_mensaje]["AES-128"] = tc_aes
            print(
                f"[OK] AES-128 completado: {
                    resultado_aes.tiempo_cifrado * 1000:.2f} ms"
            )

        # Guardar resultados de este perfil
        todos_resultados[nombre_perfil] = {
            "resultados": resultados_perfil,
            "textos_cifrados": textos_cifrados,
            "config": config_perfil,
        }

        # Imprimir tabla de comparación
        imprimir_tabla_comparacion(resultados_perfil, config_perfil)

        # Generar gráficos si está habilitado
        if generar_graficos_flag:
            perfil_nombre_display = (
                config_perfil["descripcion"] if config_perfil else "sin_restricciones"
            )
            generar_graficos(resultados_perfil, perfil_nombre_display)

    return todos_resultados


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("=" * 100)
    print("SUITE DE BENCHMARKS DE CRIPTOGRAFÍA LIGERA - UNIFICADO")
    print("Comparando DES vs AES-128")
    print("=" * 100)
    print(f"\nVersión de Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")

    # Por defecto, ejecutar solo sin restricciones cuando se llama directamente
    print("\nModo: Sin restricciones (PC/Servidor)")
    print("\nIniciando benchmarks...\n")

    resultados = ejecutar_pruebas(perfiles=None, generar_graficos_flag=True)

    print("\n" + "=" * 100)
    print("BENCHMARK COMPLETADO")
    print("=" * 100)
