#!/usr/bin/env python3
"""
Generador de Reporte PDF Completo
Ejecuta todos los benchmarks y genera un PDF con resultados, gráficos y recomendaciones
"""

import os
import sys
import time
from datetime import datetime

# Configuración de rutas
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)
DIRECTORIO_RESULTADOS = os.path.join(RAIZ_PROYECTO, "results")

sys.path.insert(0, RAIZ_PROYECTO)

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def traducir_tipo_mensaje(tipo_mensaje):
    """Traducir tipos de mensaje de inglés a español (o mantener si ya está en español)"""
    traducciones = {
        # Inglés -> Español
        'tiny': 'minúsculo',
        'small': 'pequeño',
        'medium': 'mediano',
        'large': 'grande',
        'very_long': 'muy largo',
        'short': 'corto',
        'long': 'largo',
        'extreme_iot': 'extremo iot',
        # Mantener español tal cual
        'minúsculo': 'minúsculo',
        'pequeño': 'pequeño',
        'mediano': 'mediano',
        'grande': 'grande',
        'muy_largo': 'muy largo',
        'corto': 'corto',
        'largo': 'largo',
        'extremo_iot': 'extremo iot'
    }
    return traducciones.get(tipo_mensaje.lower(), tipo_mensaje)


def traducir_perfil_dispositivo(perfil):
    """Traducir nombres de perfiles de dispositivo de inglés a español"""
    traducciones = {
        'High-end PC / Server (baseline)': 'PC de Alto Rendimiento / Servidor',
        'Mid-range IoT Device': 'Dispositivo IoT de Rango Medio',
        'Low-end IoT Device': 'Dispositivo IoT de Bajo Consumo',
        'Ultra-constrained Device': 'Dispositivo Ultra-Restringido'
    }
    return traducciones.get(perfil, perfil)


def crear_portada(story, styles):
    """Crear portada del reporte"""
    titulo_style = ParagraphStyle(
        'TituloPortada',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitulo_style = ParagraphStyle(
        'SubtituloPortada',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Reporte Comparativo de Criptografía Ligera", titulo_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("DES vs AES-128 vs PRESENT-80", subtitulo_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Análisis de Rendimiento en Múltiples Escenarios", subtitulo_style))
    story.append(Spacer(1, inch))

    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    story.append(Paragraph(f"Fecha de generación: {fecha_actual}", subtitulo_style))

    story.append(PageBreak())


def crear_seccion_resumen_ejecutivo(story, styles, resultados):
    """Crear sección de resumen ejecutivo"""
    story.append(Paragraph("Resumen Ejecutivo", styles['CustomHeading1']))
    story.append(Spacer(1, 0.2*inch))

    texto_resumen = """
    Este reporte presenta un análisis comparativo exhaustivo de tres algoritmos
    criptográficos: DES (Data Encryption Standard), AES-128 (Advanced Encryption Standard)
    y PRESENT-80 (algoritmo de criptografía ligera). Los benchmarks evalúan el rendimiento
    de estos algoritmos en tres escenarios distintos:
    """
    story.append(Paragraph(texto_resumen, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    # Lista de escenarios
    escenarios = [
        "<b>1. Rendimiento Estándar (PC):</b> Evaluación en hardware sin restricciones para establecer línea base",
        "<b>2. Dispositivos Restringidos (IoT):</b> Simulación de ESP32, ESP8266, Arduino y sensores",
        "<b>3. Hardware de 4 bits (RFID):</b> Simulación de procesadores ultra-ligeros para tags RFID"
    ]

    for escenario in escenarios:
        story.append(Paragraph(escenario, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    story.append(Spacer(1, 0.3*inch))

    # Estado de benchmarks
    exitosos = sum(1 for r in resultados.values() if r is not None)
    total = len(resultados)

    estado_texto = f"""
    <b>Estado de Ejecución:</b> {exitosos}/{total} benchmarks completados exitosamente
    """
    story.append(Paragraph(estado_texto, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(PageBreak())


def crear_seccion_benchmark_estandar(story, styles, resultados):
    """Crear sección de benchmark estándar"""
    story.append(Paragraph("1. Benchmark Estándar (PC sin restricciones)", styles['CustomHeading1']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(
        "Este benchmark mide el rendimiento máximo de los algoritmos en hardware moderno sin restricciones.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))

    # Crear tabla de resultados (solo si hay datos)
    if resultados:
        story.append(Paragraph("Resultados de Rendimiento:", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        # Tabla de métricas por algoritmo
        datos_tabla = [
            ['Algoritmo', 'Mensaje', 'Cifrado (ms)', 'Descifrado (ms)', 'Total (ms)', 'Throughput (KB/s)']
        ]

        for resultado in resultados[:9]:  # Primeros 9 resultados (3 algoritmos x 3 mensajes)
            datos_tabla.append([
                resultado.algoritmo,
                traducir_tipo_mensaje(resultado.tipo_mensaje),
                f"{resultado.tiempo_cifrado * 1000:.2f}",
                f"{resultado.tiempo_descifrado * 1000:.2f}",
                f"{resultado.tiempo_total * 1000:.2f}",
                f"{resultado.rendimiento:.2f}"
            ])

        tabla = Table(datos_tabla, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        story.append(tabla)
        story.append(Spacer(1, 0.3*inch))

    # Incluir gráficos - Dashboard principal
    ruta_grafico = os.path.join(DIRECTORIO_RESULTADOS, "benchmark_charts.png")
    if os.path.exists(ruta_grafico):
        story.append(Paragraph("Dashboard Principal de Resultados", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        img = Image(ruta_grafico, width=7*inch, height=7*inch)
        story.append(img)
        story.append(PageBreak())

    # Gráficos individuales del benchmark estándar
    graficos_individuales = [
        ("chart_encryption_time.png", "Tiempo de Cifrado (CIFRADO)", 6.5, 5),
        ("chart_throughput.png", "Rendimiento (Throughput)", 6.5, 5),
        ("chart_scalability.png", "Escalabilidad", 6.5, 5),
        ("chart_memory_usage.png", "Uso de Memoria", 6.5, 5),
        ("chart_energy_consumption.png", "Consumo Energético", 6.5, 5),
    ]

    for nombre_archivo, titulo, ancho, alto in graficos_individuales:
        ruta = os.path.join(DIRECTORIO_RESULTADOS, nombre_archivo)
        if os.path.exists(ruta):
            story.append(Paragraph(titulo, styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            img = Image(ruta, width=ancho*inch, height=alto*inch)
            story.append(img)
            story.append(PageBreak())


def crear_seccion_benchmark_restringido(story, styles, resultados):
    """Crear sección de benchmark con restricciones"""
    story.append(Paragraph("2. Benchmark de Dispositivos Restringidos (IoT)", styles['CustomHeading1']))
    story.append(Spacer(1, 0.2*inch))

    if not resultados:
        story.append(Paragraph("❌ No se completó este benchmark", styles['Normal']))
        return

    story.append(Paragraph(
        "Este benchmark simula el rendimiento en dispositivos IoT con recursos limitados, "
        "incluyendo ESP32, ESP8266, Arduino y sensores ultra-ligeros.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))

    # Perfiles de dispositivos
    story.append(Paragraph("Perfiles de Dispositivos Simulados:", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))

    perfiles_data = [
        ['Perfil', 'CPU', 'RAM', 'Ejemplos'],
        ['PC de Alto Rendimiento', '100%', '2048 MB', 'Desktop, Server, Raspberry Pi 4'],
        ['IoT de Rango Medio', '50%', '256 MB', 'ESP32, Arduino Due, STM32F4'],
        ['IoT de Bajo Consumo', '25%', '64 MB', 'ESP8266, Arduino Uno, ATmega328'],
        ['Ultra-Restringido', '10%', '16 MB', 'Nodos sensores, tags RFID, MSP430']
    ]

    tabla_perfiles = Table(perfiles_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 3.5*inch])
    tabla_perfiles.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    story.append(tabla_perfiles)
    story.append(Spacer(1, 0.3*inch))

    # Muestra de resultados representativos
    story.append(Paragraph("Resultados Representativos (Mensaje Mediano):", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))

    # Filtrar resultados de mensaje mediano
    resultados_mediano = [r for r in resultados if r.get('tamano_texto_plano', 0) > 100][:12]

    datos_tabla = [
        ['Perfil', 'Algoritmo', 'Cifrado (ms)', 'Descifrado (ms)', 'Throughput (KB/s)']
    ]

    for resultado in resultados_mediano:
        datos_tabla.append([
            traducir_perfil_dispositivo(resultado.get('perfil', 'N/A'))[:30],
            resultado.get('algoritmo', 'N/A'),
            f"{resultado.get('tiempo_cifrado_ms', 0):.2f}",
            f"{resultado.get('tiempo_descifrado_ms', 0):.2f}",
            f"{resultado.get('rendimiento_kbps', 0):.2f}"
        ])

    tabla_resultados = Table(datos_tabla, colWidths=[2*inch, 1*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    tabla_resultados.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    story.append(tabla_resultados)
    story.append(Spacer(1, 0.2*inch))

    story.append(PageBreak())


def crear_seccion_benchmark_4bits(story, styles, resultados):
    """Crear sección de benchmark de 4 bits"""
    story.append(Paragraph("3. Benchmark de Hardware de 4 Bits (RFID/Sensores)", styles['CustomHeading1']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(
        "Este benchmark simula procesadores de 4 bits encontrados en tags RFID, sensores inalámbricos "
        "y dispositivos implantables. Mide ciclos de reloj, operaciones nibble y consumo energético estimado.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))

    # Tabla de resultados (solo si hay datos)
    if resultados:
        story.append(Paragraph("Resultados de Simulación de Hardware:", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        datos_tabla = [
            ['Algoritmo', 'Mensaje', 'Ciclos', 'Ops Nibble', 'Energía (μJ)', 'Ciclos/Byte']
        ]

        for resultado in resultados[:9]:  # Primeros 9 resultados
            datos_tabla.append([
                resultado.get('algoritmo', 'N/A'),
                traducir_tipo_mensaje(resultado.get('tipo_mensaje', 'N/A')),
                f"{resultado.get('ciclos', 0):,}",
                f"{resultado.get('operaciones_nibble', 0):,}",
                f"{resultado.get('energia_uj', 0):.2f}",
                f"{resultado.get('ciclos_por_byte', 0):.1f}"
            ])

        tabla = Table(datos_tabla, colWidths=[1*inch, 1*inch, 1.2*inch, 1.2*inch, 1*inch, 1.2*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        story.append(tabla)
        story.append(Spacer(1, 0.3*inch))

    # Incluir gráfico principal de 4 bits
    ruta_grafico = os.path.join(DIRECTORIO_RESULTADOS, "chart_4bit_hardware.png")
    if os.path.exists(ruta_grafico):
        story.append(Paragraph("Dashboard de Hardware de 4 Bits", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        img = Image(ruta_grafico, width=7*inch, height=5*inch)
        story.append(img)
        story.append(PageBreak())

    # Gráficos individuales de 4 bits
    graficos_4bit = [
        ("chart_4bit_cycles.png", "Ciclos de Reloj por Algoritmo", 6.5, 5),
        ("chart_4bit_time.png", "Tiempo Absoluto de Cifrado", 6.5, 5),
        ("chart_4bit_speedup.png", "Aceleración Relativa (Speedup)", 6.5, 5),
        ("chart_4bit_efficiency.png", "Eficiencia por Byte", 6.5, 5),
        ("chart_4bit_hardware_size.png", "Tamaño de Hardware Estimado", 6.5, 5),
        ("chart_4bit_energy.png", "Consumo Energético Estimado", 6.5, 5),
    ]

    for nombre_archivo, titulo, ancho, alto in graficos_4bit:
        ruta = os.path.join(DIRECTORIO_RESULTADOS, nombre_archivo)
        if os.path.exists(ruta):
            story.append(Paragraph(titulo, styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            img = Image(ruta, width=ancho*inch, height=alto*inch)
            story.append(img)
            story.append(PageBreak())


def crear_seccion_recomendaciones(story, styles):
    """Crear sección de recomendaciones"""
    story.append(Paragraph("Recomendaciones por Caso de Uso", styles['CustomHeading1']))
    story.append(Spacer(1, 0.2*inch))

    recomendaciones = [
        {
            'titulo': 'Servidores y PCs de Alto Rendimiento',
            'recomendacion': 'AES-128',
            'razon': 'Ofrece el mejor balance entre seguridad y rendimiento en hardware moderno. '
                     'Ampliamente soportado por aceleración de hardware (AES-NI).'
        },
        {
            'titulo': 'Dispositivos IoT de Rango Medio (ESP32)',
            'recomendacion': 'AES-128 o PRESENT-80',
            'razon': 'AES-128 para compatibilidad estándar. PRESENT-80 cuando se prioriza bajo consumo '
                     'energético y se cuenta con implementación de hardware.'
        },
        {
            'titulo': 'Dispositivos IoT de Bajo Consumo (ESP8266, Arduino)',
            'recomendacion': 'PRESENT-80',
            'razon': 'Diseñado específicamente para dispositivos con recursos limitados. Menor consumo '
                     'de memoria y energía comparado con AES.'
        },
        {
            'titulo': 'Tags RFID y Sensores Ultra-Ligeros',
            'recomendacion': 'PRESENT-80',
            'razon': 'Arquitectura optimizada para implementación en hardware de 4 bits. Significativamente '
                     'menos ciclos y menor consumo energético que DES o AES.'
        },
        {
            'titulo': 'Sistemas Legacy',
            'recomendacion': 'Migrar de DES a AES-128',
            'razon': 'DES está obsoleto y es vulnerable a ataques de fuerza bruta. Se recomienda migración '
                     'inmediata a AES-128 o superior.'
        }
    ]

    for rec in recomendaciones:
        story.append(Paragraph(f"<b>{rec['titulo']}</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Recomendación:</b> {rec['recomendacion']}", styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(f"<b>Razón:</b> {rec['razon']}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

    story.append(PageBreak())


def crear_seccion_conclusiones(story, styles):
    """Crear sección de conclusiones"""
    story.append(Paragraph("Conclusiones", styles['CustomHeading1']))
    story.append(Spacer(1, 0.2*inch))

    conclusiones = """
    <b>1. AES-128</b> se mantiene como el estándar de oro para aplicaciones de propósito general,
    ofreciendo excelente seguridad y rendimiento en hardware moderno.<br/><br/>

    <b>2. PRESENT-80</b> demuestra ventajas significativas en dispositivos con recursos extremadamente
    limitados, particularmente en implementaciones de hardware de 4 bits donde supera a DES y AES
    en eficiencia energética y ciclos de reloj.<br/><br/>

    <b>3. DES</b> debe considerarse obsoleto para nuevas implementaciones debido a su vulnerable
    tamaño de clave de 56 bits efectivos. Solo debe mantenerse en sistemas legacy con plan de migración.<br/><br/>

    <b>4.</b> La selección del algoritmo correcto depende críticamente del contexto de implementación:
    capacidades de hardware, restricciones de energía, requisitos de seguridad y compatibilidad con
    estándares existentes.<br/><br/>

    <b>5.</b> Para IoT y dispositivos embebidos, el análisis del ciclo de vida completo (incluyendo
    consumo energético y reemplazo de baterías) favorece a PRESENT-80 sobre alternativas más pesadas.
    """

    story.append(Paragraph(conclusiones, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))


def generar_reporte_pdf(resultados):
    """
    Generar reporte PDF completo con todos los resultados

    Args:
        resultados: Dict con claves 'estandar', 'restringido', '4bits'
    """
    # Asegurar que existe el directorio de resultados
    os.makedirs(DIRECTORIO_RESULTADOS, exist_ok=True)

    ruta_pdf = os.path.join(DIRECTORIO_RESULTADOS, "reporte_completo.pdf")

    # Crear documento
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Contenedor de elementos
    story = []

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo personalizado para encabezados
    styles.add(ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    # Usar CustomHeading1 como Heading1
    # No podemos reasignar directamente, así que usaremos CustomHeading1 en su lugar

    print("\n" + "="*80)
    print("GENERANDO REPORTE PDF")
    print("="*80)

    # Construir reporte
    print("\n[1/7] Creando portada...")
    crear_portada(story, styles)

    print("[2/7] Creando resumen ejecutivo...")
    crear_seccion_resumen_ejecutivo(story, styles, resultados)

    print("[3/7] Creando sección de benchmark estándar...")
    crear_seccion_benchmark_estandar(story, styles, resultados.get('estandar'))

    print("[4/7] Creando sección de benchmark restringido...")
    crear_seccion_benchmark_restringido(story, styles, resultados.get('restringido'))

    print("[5/7] Creando sección de benchmark de 4 bits...")
    crear_seccion_benchmark_4bits(story, styles, resultados.get('4bits'))

    print("[6/7] Creando recomendaciones...")
    crear_seccion_recomendaciones(story, styles)

    print("[7/7] Creando conclusiones...")
    crear_seccion_conclusiones(story, styles)

    # Generar PDF
    print("\nGenerando archivo PDF...")
    doc.build(story)

    print(f"\n✅ Reporte PDF generado exitosamente: {ruta_pdf}")
    print("="*80 + "\n")

    return ruta_pdf


def main():
    """Función principal: ejecutar todos los benchmarks y generar PDF"""
    import pickle

    # Verificar si hay resultados temporales guardados (llamado desde ejecutar_todos.py)
    ruta_resultados_temp = os.path.join(RAIZ_PROYECTO, "results", ".resultados_temp.pkl")

    if os.path.exists(ruta_resultados_temp):
        print("\n" + "="*80)
        print("GENERANDO REPORTE PDF CON RESULTADOS EXISTENTES")
        print("="*80)

        try:
            with open(ruta_resultados_temp, 'rb') as f:
                resultados = pickle.load(f)

            # Generar PDF
            generar_reporte_pdf(resultados)

            return
        except Exception as e:
            print(f"❌ Error al cargar resultados temporales: {e}")
            print("Ejecutando benchmarks desde cero...")

    # Si no hay resultados temporales, ejecutar benchmarks
    print("\n" + "="*80)
    print("GENERADOR DE REPORTE PDF COMPLETO")
    print("="*80)
    print("\nEste script ejecutará todos los benchmarks y generará un reporte PDF completo.")
    print("El proceso puede tomar varios minutos...\n")

    try:
        input("⏸️  Presiona ENTER para comenzar...")
    except EOFError:
        # Si no hay terminal interactiva, continuar automáticamente
        print("(Ejecutando en modo no-interactivo)")

    tiempo_inicio = time.time()

    # Ejecutar todos los benchmarks
    print("\n" + "="*80)
    print("EJECUTANDO BENCHMARKS")
    print("="*80)

    resultados = {
        'estandar': None,
        'restringido': None,
        '4bits': None
    }

    # 1. Benchmark estándar
    print("\n[1/3] Ejecutando benchmark estándar...")
    try:
        from benchmarks.benchmark import ejecutar_pruebas
        resultados['estandar'] = ejecutar_pruebas()
        print("✅ Benchmark estándar completado")
    except Exception as e:
        print(f"❌ Error en benchmark estándar: {e}")

    # 2. Benchmark restringido
    print("\n[2/3] Ejecutando benchmark restringido...")
    try:
        from benchmarks.benchmark_constrained import ejecutar_pruebas_restringidas
        resultados['restringido'] = ejecutar_pruebas_restringidas()
        print("✅ Benchmark restringido completado")
    except Exception as e:
        print(f"❌ Error en benchmark restringido: {e}")

    # 3. Benchmark de 4 bits
    print("\n[3/3] Ejecutando benchmark de 4 bits...")
    try:
        from benchmarks.benchmark_4bit_hardware import ejecutar_benchmark_hardware_4bits
        resultados['4bits'] = ejecutar_benchmark_hardware_4bits()
        print("✅ Benchmark de 4 bits completado")
    except Exception as e:
        print(f"❌ Error en benchmark de 4 bits: {e}")

    # Generar PDF
    ruta_pdf = generar_reporte_pdf(resultados)

    tiempo_total = time.time() - tiempo_inicio

    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)
    print(f"\n⏱️  Tiempo total: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")
    print(f"📄 Reporte PDF: {ruta_pdf}")
    print(f"📁 Todos los resultados en: {DIRECTORIO_RESULTADOS}/")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
