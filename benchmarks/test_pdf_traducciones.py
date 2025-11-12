#!/usr/bin/env python3
"""
Script para verificar que todas las traducciones en el PDF funcionan correctamente
"""

import os
import sys

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(DIRECTORIO_SCRIPT)
sys.path.insert(0, RAIZ_PROYECTO)

from benchmarks.generar_reporte_pdf import traducir_tipo_mensaje, traducir_perfil_dispositivo

print("="*80)
print("VERIFICACIÓN DE TRADUCCIONES PARA PDF")
print("="*80)

# Verificar tipos de mensaje (ambos inglés y español)
print("\n1. TIPOS DE MENSAJE:")
print("-" * 80)
tipos_mensaje = [
    'tiny', 'small', 'medium', 'large', 'short', 'long', 'very_long', 'extreme_iot',
    'minúsculo', 'pequeño', 'mediano', 'grande', 'corto', 'largo', 'muy_largo', 'extremo_iot'
]

for tipo in tipos_mensaje:
    traducido = traducir_tipo_mensaje(tipo)
    # Verificar que no hay inglés en el resultado
    tiene_ingles = any(palabra in traducido.lower() for palabra in ['tiny', 'small', 'large', 'short', 'long', 'medium'])
    estado = "❌" if tiene_ingles else "✅"
    print(f"  {estado} {tipo:<15} -> {traducido}")

# Verificar perfiles de dispositivo
print("\n2. PERFILES DE DISPOSITIVO:")
print("-" * 80)
perfiles = [
    'High-end PC / Server (baseline)',
    'Mid-range IoT Device',
    'Low-end IoT Device',
    'Ultra-constrained Device'
]

for perfil in perfiles:
    traducido = traducir_perfil_dispositivo(perfil)
    # Verificar que no hay inglés en el resultado (excepto nombres propios como IoT, PC)
    palabras_ingles = ['high-end', 'mid-range', 'low-end', 'ultra-constrained', 'device', 'server', 'baseline']
    tiene_ingles = any(palabra in traducido.lower() for palabra in palabras_ingles)
    estado = "❌" if tiene_ingles else "✅"
    print(f"  {estado} {perfil}")
    print(f"     -> {traducido}")

print("\n" + "="*80)
print("RESUMEN")
print("="*80)

# Verificar que todas las traducciones están en español
todos_tipos_ok = all(
    not any(palabra in traducir_tipo_mensaje(tipo).lower()
            for palabra in ['tiny', 'small', 'large', 'short', 'long', 'medium'])
    for tipo in tipos_mensaje
)

todos_perfiles_ok = all(
    not any(palabra in traducir_perfil_dispositivo(perfil).lower()
            for palabra in ['high-end', 'mid-range', 'low-end', 'ultra-constrained', 'device', 'server', 'baseline'])
    for perfil in perfiles
)

if todos_tipos_ok and todos_perfiles_ok:
    print("\n✅ ¡Todas las traducciones están correctas!")
    print("   El PDF se generará completamente en español.")
else:
    print("\n⚠️  Algunas traducciones aún tienen texto en inglés.")
    if not todos_tipos_ok:
        print("   - Revisar tipos de mensaje")
    if not todos_perfiles_ok:
        print("   - Revisar perfiles de dispositivo")

print("\n" + "="*80 + "\n")
