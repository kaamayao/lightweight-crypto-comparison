# Guía de Uso Rápida - Benchmarks de Criptografía Ligera

## Opción Recomendada: Ejecutar Todo con PDF 🎯

```bash
# Desde el directorio raíz del proyecto
python benchmarks/ejecutar_todos.py
```

Este comando:
1. ✅ Ejecuta los 3 benchmarks completos
2. ✅ Genera todos los gráficos (PNG)
3. ✅ Al finalizar, te preguntará si deseas generar el reporte PDF
4. ✅ Si aceptas, genera un PDF completo con todos los resultados

**Tiempo estimado:** 2-5 minutos (dependiendo de tu hardware)

---

## Alternativas

### Solo generar PDF (sin ejecutar benchmarks nuevamente)

Si ya tienes resultados guardados y solo quieres generar el PDF:

```bash
./benchmarks/run_pdf_generator.sh
```

O manualmente:

```bash
source venv_pdf/bin/activate
python benchmarks/generar_reporte_pdf.py
deactivate
```

### Ejecutar benchmarks individuales

```bash
# Solo PC estándar
python benchmarks/benchmark.py

# Solo dispositivos restringidos (IoT)
python benchmarks/benchmark_constrained.py

# Solo hardware de 4 bits (RFID)
python benchmarks/benchmark_4bit_hardware.py
```

---

## Resultados Generados

Después de ejecutar, encontrarás en `results/`:

| Archivo | Descripción |
|---------|-------------|
| `benchmark_charts.png` | Gráficos del benchmark estándar (9 gráficos en 3x3) |
| `chart_4bit_hardware.png` | Gráficos del benchmark de 4 bits |
| `reporte_completo.pdf` | **Reporte PDF completo con todo** ⭐ |

---

## Contenido del Reporte PDF

El reporte PDF incluye:

📄 **Portada**
- Título del proyecto
- Fecha de generación

📊 **Resumen Ejecutivo**
- Descripción de los 3 escenarios de benchmark
- Estado de ejecución

📈 **Benchmark Estándar (PC)**
- Tabla de resultados detallada
- Gráficos de rendimiento
- Comparación de cifrado vs descifrado

📱 **Benchmark de Dispositivos Restringidos (IoT)**
- Perfiles de dispositivos simulados
- Resultados por perfil (ESP32, ESP8266, etc.)
- Comparación de throughput

🏷️ **Benchmark de Hardware de 4 Bits (RFID)**
- Simulación de ciclos de reloj
- Operaciones nibble
- Consumo energético estimado
- Gráficos de eficiencia

💡 **Recomendaciones por Caso de Uso**
- Servidores y PCs
- IoT de rango medio
- IoT de bajo consumo
- Tags RFID
- Sistemas legacy

🎯 **Conclusiones Técnicas**
- Análisis comparativo
- Guía de selección de algoritmos

---

## Requisitos de Instalación

### Primera vez: Configurar entorno para PDF

```bash
# Crear entorno virtual
python -m venv venv_pdf

# Activar entorno
source venv_pdf/bin/activate

# Instalar reportlab
pip install reportlab

# Desactivar (cuando termines)
deactivate
```

**Nota:** Solo necesitas hacer esto UNA VEZ. Después, los scripts activarán automáticamente el entorno.

---

## Ejemplos de Uso

### Uso típico: Todo de una vez

```bash
# Ejecutar todo y generar PDF
python benchmarks/ejecutar_todos.py
# [Presionar ENTER para comenzar]
# [Esperar 2-5 minutos]
# [Cuando pregunte si generar PDF, escribir: s]
# ✅ Listo! Abre results/reporte_completo.pdf
```

### Uso avanzado: Solo actualizar PDF

Si modificaste los algoritmos y quieres ver nuevos resultados:

```bash
# Re-ejecutar solo benchmark estándar
python benchmarks/benchmark.py

# Ahora generar PDF con los nuevos datos
source venv_pdf/bin/activate
python benchmarks/generar_reporte_pdf.py
deactivate
```

---

## Interpretación de Resultados

### Métricas Clave

**CIFRADO (Encryption):**
- Tiempo que toma convertir texto plano → texto cifrado
- Menor tiempo = mejor rendimiento

**DESCIFRADO (Decryption):**
- Tiempo que toma convertir texto cifrado → texto plano
- Menor tiempo = mejor rendimiento

**Throughput (Rendimiento):**
- KB/s de datos procesados
- Mayor throughput = mejor rendimiento

**Ciclos por Byte:**
- Ciclos de reloj necesarios por byte (solo 4-bit hardware)
- Menor = más eficiente

**Energía (μJ):**
- Consumo energético estimado (solo 4-bit hardware)
- Menor = mejor para baterías

### ¿Qué Algoritmo Elegir?

| Escenario | Recomendación | Razón |
|-----------|---------------|-------|
| Servidor web | **AES-128** | Aceleración de hardware, estándar industrial |
| ESP32 | **AES-128** o **PRESENT-80** | AES para compatibilidad, PRESENT para batería |
| Arduino Uno | **PRESENT-80** | Diseñado para bajo consumo |
| RFID tag | **PRESENT-80** | Optimizado para hardware de 4 bits |
| Sistema legacy con DES | **Migrar a AES-128** | DES está obsoleto y vulnerable |

---

## FAQ

**P: ¿Cuánto tarda en ejecutar todos los benchmarks?**
R: Entre 2-5 minutos dependiendo de tu hardware.

**P: ¿Puedo ejecutar los benchmarks sin generar PDF?**
R: Sí, cuando `ejecutar_todos.py` pregunte, simplemente escribe "n".

**P: ¿Los resultados son determinísticos?**
R: No exactamente. Los tiempos varían ligeramente según la carga del sistema, pero las tendencias son consistentes.

**P: ¿El benchmark con restricciones es preciso para mi ESP32 real?**
R: Es una aproximación. Para resultados precisos, ejecuta en el hardware real.

**P: ¿Qué significan los gráficos 3x3 del benchmark estándar?**
R:
- Columnas: Cifrado, Descifrado, Comparaciones diversas
- Cada fila: Diferentes métricas (tiempo, throughput, memoria)

**P: ¿Puedo cambiar los mensajes de prueba?**
R: Sí, edita los archivos en `data/` (short_message.txt, medium_message.txt, long_message.txt).

**P: ¿Cómo comparto los resultados?**
R: Simplemente comparte el archivo `results/reporte_completo.pdf`.

---

## Troubleshooting

### Error: "reportlab not found"
```bash
# Solución: Instalar en entorno virtual
python -m venv venv_pdf
source venv_pdf/bin/activate
pip install reportlab
```

### Error: "ModuleNotFoundError: algorithms"
```bash
# Solución: Ejecutar desde el directorio raíz
cd /ruta/al/lightweight-crypto-comparison
python benchmarks/ejecutar_todos.py
```

### Error: "Permission denied" al ejecutar .sh
```bash
# Solución: Dar permisos de ejecución
chmod +x benchmarks/*.sh
```

### Los gráficos no aparecen en el PDF
- Asegúrate de ejecutar los benchmarks ANTES de generar el PDF
- Los archivos PNG deben existir en `results/`

---

## Para Desarrolladores

Si quieres modificar el reporte PDF, edita `benchmarks/generar_reporte_pdf.py`:

- `crear_portada()`: Modifica la portada
- `crear_seccion_*()`: Modifica cada sección
- `crear_seccion_recomendaciones()`: Añade/modifica recomendaciones
- `crear_seccion_conclusiones()`: Añade/modifica conclusiones

Para añadir nuevos gráficos al PDF:
```python
# En generar_reporte_pdf.py
from reportlab.platypus import Image

ruta_nuevo_grafico = os.path.join(DIRECTORIO_RESULTADOS, "mi_grafico.png")
if os.path.exists(ruta_nuevo_grafico):
    img = Image(ruta_nuevo_grafico, width=7*inch, height=5*inch)
    story.append(img)
```

---

## Recursos Adicionales

- **README.md**: Documentación completa de todos los scripts
- **benchmark.py**: Código del benchmark estándar
- **benchmark_constrained.py**: Código del benchmark con restricciones
- **benchmark_4bit_hardware.py**: Código del benchmark de 4 bits
- **generar_reporte_pdf.py**: Código del generador de PDF

---

**¿Preguntas?** Consulta README.md o abre un issue en el repositorio.
