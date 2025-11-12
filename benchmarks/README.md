# Benchmarks - Criptografía Ligera

Este directorio contiene scripts de benchmarking para comparar DES, AES-128 y PRESENT-80 en múltiples escenarios.

## Scripts Disponibles

### 1. `ejecutar_todos.py` - Script Maestro ⭐
**Recomendado para uso general**

Ejecuta todos los benchmarks secuencialmente y ofrece generar un reporte PDF al final.

```bash
python benchmarks/ejecutar_todos.py
```

Este script ejecutará:
1. Benchmark estándar (PC sin restricciones)
2. Benchmark con restricciones (ESP32, Arduino, sensores)
3. Benchmark de hardware de 4 bits (RFID)
4. Al finalizar, preguntará si deseas generar un reporte PDF completo

**Salidas:**
- `results/benchmark_charts.png` - Gráficos del benchmark estándar
- `results/chart_4bit_hardware.png` - Gráficos del benchmark de 4 bits
- `results/reporte_completo.pdf` - Reporte PDF completo (si se solicita)

---

### 2. `generar_reporte_pdf.py` - Generador de Reporte PDF
Ejecuta todos los benchmarks y genera un reporte PDF completo con:
- Resumen ejecutivo
- Tablas de resultados de todos los benchmarks
- Todos los gráficos generados
- Recomendaciones por caso de uso
- Conclusiones técnicas

```bash
# Opción 1: Usando el script helper (recomendado)
./benchmarks/run_pdf_generator.sh

# Opción 2: Activando el entorno virtual manualmente
source venv_pdf/bin/activate
python benchmarks/generar_reporte_pdf.py
deactivate
```

**Salida:**
- `results/reporte_completo.pdf`

---

### 3. Benchmarks Individuales

#### `benchmark.py` - Benchmark Estándar
Mide el rendimiento máximo en PC/servidor sin restricciones.

```bash
python benchmarks/benchmark.py
```

**Salida:**
- `results/benchmark_charts.png` - Gráficos de rendimiento

---

#### `benchmark_constrained.py` - Benchmark con Restricciones
Simula dispositivos IoT con recursos limitados (ESP32, ESP8266, Arduino, sensores).

```bash
python benchmarks/benchmark_constrained.py
```

**Características:**
- Simula perfiles de 4 clases de dispositivos
- Limita CPU y memoria para emular hardware restringido
- Compara rendimiento en cada perfil

---

#### `benchmark_4bit_hardware.py` - Benchmark de Hardware de 4 Bits
Simula procesadores de 4 bits para RFID tags y sensores ultra-ligeros.

```bash
python benchmarks/benchmark_4bit_hardware.py
```

**Métricas:**
- Ciclos de reloj
- Operaciones nibble (4 bits)
- Consumo energético estimado
- Ciclos por byte

**Salida:**
- `results/chart_4bit_hardware.png` - Gráficos de hardware

---

## Requisitos

### Para ejecutar benchmarks básicos:
```bash
# Solo requiere las bibliotecas estándar de Python
python 3.x
matplotlib
psutil
```

### Para generar reportes PDF:
```bash
# Crear entorno virtual e instalar reportlab
python -m venv venv_pdf
source venv_pdf/bin/activate
pip install reportlab
```

---

## Estructura de Resultados

Todos los resultados se guardan en el directorio `results/`:

```
results/
├── benchmark_charts.png           # Gráficos del benchmark estándar
├── chart_4bit_hardware.png        # Gráficos del benchmark de 4 bits
└── reporte_completo.pdf           # Reporte PDF completo (opcional)
```

---

## Mensajes de Prueba

Los benchmarks utilizan mensajes de tres tamaños:
- **Corto** (`data/short_message.txt`): ~64 bytes
- **Mediano** (`data/medium_message.txt`): ~512 bytes
- **Largo** (`data/long_message.txt`): ~4096 bytes

---

## Notas de Implementación

### Métricas Medidas

Todos los benchmarks miden tanto **CIFRADO** como **DESCIFRADO** por separado:

**Benchmark Estándar y Restringido:**
- Tiempo de preparación de clave
- Tiempo de cifrado (CIFRADO)
- Tiempo de descifrado (DESCIFRADO)
- Uso de memoria
- Throughput (rendimiento)

**Benchmark de 4 Bits:**
- Ciclos de reloj (cifrado y descifrado)
- Operaciones nibble
- Consumo energético
- Ciclos por byte

### Simulación de Hardware Restringido

El benchmark con restricciones (`benchmark_constrained.py`) utiliza:
- Afinidad de CPU (single core)
- Prioridad de proceso reducida (nice +10)
- Perfiles de 4 clases de dispositivos

**Nota:** Esta es una simulación en software. Para resultados precisos en hardware IoT real, se recomienda ejecutar en el dispositivo físico o usar emuladores.

---

## Interpretación de Resultados

### Recomendaciones Generales:

**Servidores/PCs de Alto Rendimiento:**
- ✅ **AES-128**: Mejor balance seguridad/rendimiento
- Beneficio de aceleración por hardware (AES-NI)

**Dispositivos IoT de Rango Medio (ESP32):**
- ✅ **AES-128**: Para compatibilidad estándar
- ✅ **PRESENT-80**: Cuando se prioriza bajo consumo

**Dispositivos IoT de Bajo Consumo (ESP8266, Arduino):**
- ✅ **PRESENT-80**: Optimizado para recursos limitados

**Tags RFID y Sensores Ultra-Ligeros:**
- ✅ **PRESENT-80**: Diseñado específicamente para hardware de 4 bits

**Sistemas Legacy:**
- ⚠️ **DES está obsoleto** - Migrar a AES-128 o superior

---

## Troubleshooting

### Error: ModuleNotFoundError
Asegúrate de ejecutar desde el directorio raíz del proyecto:
```bash
cd /ruta/al/lightweight-crypto-comparison
python benchmarks/benchmark.py
```

### Error al generar PDF: reportlab no encontrado
Instala reportlab en el entorno virtual:
```bash
python -m venv venv_pdf
source venv_pdf/bin/activate
pip install reportlab
```

### Permisos denegados al ejecutar scripts .sh
Dale permisos de ejecución:
```bash
chmod +x benchmarks/*.sh
```

---

## Traducción

Todos los scripts, variables, funciones y comentarios están en español para mantener consistencia con la implementación de los algoritmos.

**Términos clave:**
- **CIFRADO** = Encryption
- **DESCIFRADO** = Decryption
- **Rendimiento** = Throughput
- **Prueba** = Benchmark/Test

---

## Contacto y Contribuciones

Para reportar problemas o sugerencias, abre un issue en el repositorio del proyecto.
