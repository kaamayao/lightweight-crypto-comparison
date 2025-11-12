# Cómo Generar el Reporte PDF

## Solución Simple ✅

El reporte PDF usa **Pillow (PIL)** para combinar los gráficos PNG en un PDF. Pillow ya está instalado como dependencia de matplotlib.

## Método Automático (Recomendado)

Ejecuta el script maestro:

```bash
python benchmarks/ejecutar_todos.py
```

Cuando termine de ejecutar los 3 benchmarks, te preguntará:

```
¿Deseas generar un reporte PDF completo con todos los resultados?
Generar PDF? (s/n):
```

**Responde "s" (sí)** y el script generará automáticamente el PDF.

**Resultado**: `results/reporte_completo.pdf`

---

## Método Manual

Si ya ejecutaste los benchmarks y solo quieres generar el PDF:

```bash
python benchmarks/generar_pdf_graficos.py
```

---

## Requisitos

Solo necesitas **Pillow**, que probablemente ya está instalado:

```bash
# Verificar si Pillow está instalado
python -c "from PIL import Image; print('✅ Pillow disponible')"

# Si no está instalado:
pip install Pillow
```

**Nota**: Pillow es una dependencia de matplotlib, así que probablemente ya lo tienes.

---

## Contenido del PDF Generado

El PDF incluye **solo los gráficos** (sin texto adicional):

**Benchmark Estándar (10 gráficos)**
1. Dashboard principal con 8 gráficos combinados
2. Tiempo de cifrado por tipo de mensaje
3. Tiempo de descifrado por tipo de mensaje
4. Rendimiento (throughput)
5. Escalabilidad - Cifrado
6. Escalabilidad - Descifrado
7. Uso de memoria
8. Consumo energético
9. Ciclos de CPU por byte
10. Comparación general de rendimiento

**Total: 10 páginas (una por gráfico)**

---

## Todas las Etiquetas en Español ✅

Todos los gráficos están **completamente en español**, incluyendo:

- ✅ Tipos de mensaje: corto, mediano, largo, muy largo, extremo IoT
- ✅ Títulos de gráficos
- ✅ Etiquetas de ejes
- ✅ Leyendas

---

## Troubleshooting

### Error: "No module named 'PIL'"

**Causa**: Pillow no está instalado.

**Solución**:
```bash
pip install Pillow
```

### El PDF está vacío o tiene pocos gráficos

**Causa**: Los gráficos PNG no se han generado.

**Solución**: Ejecuta primero los benchmarks:
```bash
python benchmarks/benchmark.py
```

O ejecuta todo junto:
```bash
python benchmarks/ejecutar_todos.py
```

---

## Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `benchmarks/ejecutar_todos.py` | Script maestro que ofrece generar PDF al final |
| `benchmarks/generar_pdf_graficos.py` | Generador de PDF simple con Pillow |
| `results/reporte_completo.pdf` | PDF generado (salida) |
| `results/*.png` | Gráficos individuales incluidos en el PDF |

---

**¿Preguntas?** Revisa `benchmarks/README.md` o `benchmarks/USAGE.md` para más información.
