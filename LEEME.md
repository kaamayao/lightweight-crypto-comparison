# Comparación de Criptografía Ligera

Análisis comparativo de dos algoritmos de criptografía (DES y AES-128), evaluando su rendimiento, eficiencia y nivel de seguridad en diferentes entornos.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Algoritmos Implementados](#algoritmos-implementados)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Benchmarks](#benchmarks)
- [Simulación de Dispositivos Limitados](#simulación-de-dispositivos-limitados)
- [Resultados](#resultados)
- [Documentación](#documentación)

---

## 📖 Descripción

Este proyecto implementa y compara tres algoritmos de criptografía ligera diseñados para dispositivos con recursos limitados (IoT, sistemas embebidos, nodos sensores). El objetivo es evaluar su rendimiento bajo diferentes condiciones y tamaños de mensaje.

### Métricas Evaluadas

- ⏱️ **Tiempo de Cifrado/Descifrado** (ms)
- 📊 **Rendimiento** (MB/s)
- 🔄 **Ciclos por Byte** (estimado)
- 💾 **Uso de Memoria** (KB)
- 📈 **Sobrecarga de Texto Cifrado** (%)
- 🔑 **Tiempo de Configuración de Clave** (ms)

---

## 🔐 Algoritmos Implementados

### 1. DES (Data Encryption Standard)
- **Tamaño de Bloque:** 64 bits
- **Tamaño de Clave:** 64 bits (56 bits efectivos)
- **Rondas:** 16
- **Estado:** Algoritmo legado, considerado inseguro para uso moderno

### 2. AES-128 (Advanced Encryption Standard)
- **Tamaño de Bloque:** 128 bits
- **Tamaño de Clave:** 128 bits
- **Rondas:** 10
- **Estado:** Estándar actual, ampliamente adoptado

### 3. PRESENT-80
- **Tamaño de Bloque:** 64 bits
- **Tamaño de Clave:** 80 bits
- **Rondas:** 32
- **Estado:** Diseñado específicamente para hardware ultra-ligero

---

## 📁 Estructura del Proyecto

```
lightweight-crypto-comparison/
├── algorithms/                  # Implementaciones de algoritmos
│   ├── DES/
│   │   ├── index.py            # Implementación DES
│   │   └── constants.py        # Constantes DES (S-boxes, etc.)
│   ├── AES/
│   │   ├── index.py            # Implementación AES-128
│   │   └── constants.py        # Constantes AES (S-boxes, RCON)
│   └── PRESENT/
│       ├── index.py            # Implementación PRESENT-80
│       └── constants.py        # Constantes PRESENT
├── utils/
│   └── index.py                # Funciones utilitarias
├── data/                        # Mensajes de prueba
│   ├── short_message.txt       # Mensaje corto (12 bytes)
│   ├── medium_message.txt      # Mensaje mediano (339 bytes)
│   ├── long_message.txt        # Mensaje largo (1170 bytes)
│   ├── very_long_message.txt   # Mensaje muy largo (6633 bytes)
│   └── extreme_iot_message.txt # Mensaje extremo IoT (14807 bytes)
├── benchmark.py                 # Script principal de benchmark
├── benchmark_constrained.py     # Benchmark con restricciones simuladas
├── create_pdf.py               # Generador de PDF con gráficos
├── Dockerfile                  # Imagen Docker para pruebas
├── run_docker_benchmarks.sh    # Script automatizado (inglés)
├── ejecutar_benchmarks_docker.sh # Script automatizado (español)
├── docs/
│   └── refList.md              # Referencias académicas
└── resultados/                 # Resultados de benchmarks
    ├── benchmark_results.txt
    ├── constrained_benchmark_results.txt
    ├── benchmark_charts_report.pdf
    └── *.png                   # Gráficos individuales
```

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.11+
- pip (gestor de paquetes de Python)
- Docker (opcional, para simulaciones avanzadas)

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd lightweight-crypto-comparison

# Instalar dependencias de Python
pip install matplotlib numpy Pillow
```

---

## 💻 Uso

### 1. Benchmark Básico

Ejecuta el benchmark completo con todos los algoritmos y tamaños de mensaje:

```bash
python benchmarks/benchmark.py
```

Esto generará:
- Resultados en consola
- Gráficos PNG individuales
- Archivo `benchmark_results.txt`

### 2. Benchmark con Restricciones Simuladas

Simula dispositivos IoT con recursos limitados:

```bash
python benchmarks/benchmark_constrained.py
```

Perfiles incluidos:
- PC de gama alta (línea base)
- Dispositivo IoT de gama media (ESP32)
- Dispositivo IoT de gama baja (ESP8266)
- Dispositivo ultra-restringido (nodos sensores)

### 3. Generar PDF con Gráficos

Combina todos los gráficos en un solo PDF:

```bash
python benchmarks/create_pdf.py
```

Genera: `benchmark_charts_report.pdf`

---

## 🐳 Simulación de Dispositivos Limitados

### Usando Docker (Recomendado)

Docker proporciona límites **reales** de recursos (no aproximaciones):

#### Opción A: Script Automatizado

```bash
# En inglés
./run_docker_benchmarks.sh

# En español
./ejecutar_benchmarks_docker.sh
```

Esto ejecuta automáticamente 4 configuraciones y guarda resultados en `docker_results/` o `resultados_docker/`.

#### Opción B: Manual

```bash
# 1. Construir imagen
docker build -t crypto-benchmark .

# 2. Ejecutar con diferentes restricciones

# ESP32 (gama media: 50% CPU, 256MB RAM)
docker run --rm --cpus=0.5 --memory=256m crypto-benchmark

# ESP8266 (gama baja: 25% CPU, 64MB RAM)
docker run --rm --cpus=0.25 --memory=64m crypto-benchmark

# Nodo sensor (ultra-restringido: 10% CPU, 32MB RAM)
docker run --rm --cpus=0.1 --memory=32m crypto-benchmark

# Guardar resultados
docker run --rm --cpus=0.25 --memory=64m crypto-benchmark > resultados_esp8266.txt
```

### Métodos de Simulación Disponibles

| Método | Precisión | Complejidad | Documentación |
|--------|-----------|-------------|---------------|
| Simulación Python | Baja | Baja | Ver código |
| Docker | Media-Alta | Baja | `GUIA_RAPIDA_DOCKER.md` |
| QEMU | Muy Alta | Alta | `GUIA_SIMULACION_DISPOSITIVOS_LIMITADOS.md` |
| Hardware Real | Exacta | Media | Guías de simulación |

---

## 📊 Benchmarks

### Tipos de Mensajes

1. **Corto** (12 bytes): "¡Hola Mundo!"
2. **Mediano** (339 bytes): Texto con múltiples oraciones
3. **Largo** (1170 bytes): Capítulo de documentación técnica
4. **Muy Largo** (6633 bytes): Documento completo sobre criptografía
5. **Extremo IoT** (14807 bytes): Paquete de actualización de firmware simulado

### Gráficos Generados

1. **benchmark_charts.png** - Panel completo con 6 gráficos
2. **chart_encryption_time.png** - Comparación de tiempo de cifrado
3. **chart_throughput.png** - Comparación de rendimiento
4. **chart_scalability.png** - Escalabilidad (tiempo vs tamaño)
5. **chart_memory_usage.png** - Comparación de uso de memoria

---

## 📈 Resultados

### Hallazgos Clave

#### Rendimiento General (PC de gama alta)

| Algoritmo | Tiempo Cifrado (ms) | Rendimiento (MB/s) | Memoria (KB) |
|-----------|---------------------|-------------------|--------------|
| **AES-128** | 706.29 | 0.0200 | 249.00 |
| **DES** | 734.61 | 0.0192 | 1916.06 |
| **PRESENT-80** | 1864.79 | 0.0076 | 1916.28 |

*Resultados para mensaje extremo IoT (14.8 KB)*

#### Conclusiones

1. ✅ **AES-128**: Mejor rendimiento general para mensajes medianos a grandes
2. ⚡ **DES**: Rendimiento moderado, uso alto de memoria
3. 🔧 **PRESENT-80**: Más lento en software (optimizado para hardware)

#### Notas Importantes

- Estas son implementaciones en **SOFTWARE** en CPU de propósito general
- En **hardware real** (ESP32/STM32 con aceleración AES), AES sería 10-100x más rápido
- **PRESENT-80** está diseñado para implementación en hardware ultra-ligero
- El uso de memoria incluye sobrecarga del intérprete de Python

---

## 📚 Documentación

### Guías en Español

- **LEEME.md** - Este archivo (README en español)
- **GUIA_RAPIDA_DOCKER.md** - Guía rápida de Docker
- **GUIA_SIMULACION_DISPOSITIVOS_LIMITADOS.md** - Métodos de simulación completos
- **TRADUCCION_COMENTARIOS.md** - Traducción de todos los comentarios del código

### Guías en Inglés

- **README.md** - README original
- **DOCKER_QUICKSTART.md** - Docker quickstart guide
- **LOW_SPEC_SIMULATION_GUIDE.md** - Low-spec device simulation guide

### Referencias Académicas

Ver `docs/refList.md` para lista de papers y recursos académicos.

---

## 🛠️ Desarrollo

### Ejecutar Pruebas

```bash
# Benchmark básico
python benchmarks/benchmark.py > resultados.txt

# Benchmark restringido
python benchmarks/benchmark_constrained.py > resultados_restringidos.txt

# Generar PDF
python benchmarks/create_pdf.py
```

### Añadir Nuevos Algoritmos

1. Crear directorio en `algorithms/`
2. Implementar funciones `ALGO_encrypt()` y `ALGO_decrypt()`
3. Añadir constantes en `constants.py`
4. Actualizar `benchmark.py` con nuevo algoritmo

### Añadir Nuevos Mensajes de Prueba

1. Crear archivo en `data/`
2. Actualizar `benchmark.py` para cargar el nuevo mensaje
3. Añadir a lista `test_cases`

---

## 📊 Comparación con Hardware Real

| Entorno | AES-128 | DES | PRESENT-80 |
|---------|---------|-----|------------|
| PC (Software Python) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| ESP32 (HW accel) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| STM32 (HW accel) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| ASIC ultra-ligero | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

⭐ = Rendimiento relativo

---

## 🔬 Casos de Uso

### 1. Investigación Académica
- Comparación de algoritmos de criptografía ligera
- Análisis de rendimiento en entornos restringidos
- Gráficos y datos para papers

### 2. Desarrollo IoT
- Selección de algoritmo apropiado para tu dispositivo
- Estimación de rendimiento antes de implementación en hardware
- Validación de requisitos de recursos

### 3. Educación
- Aprender implementación de algoritmos criptográficos
- Entender trade-offs de rendimiento vs seguridad
- Experimentar con diferentes configuraciones

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

[Especificar licencia aquí]

---

## 👥 Autores

[Nombres de autores]

---

## 🙏 Agradecimientos

- NIST por el estándar de Criptografía Ligera
- Comunidad de código abierto
- Referencias académicas (ver `docs/refList.md`)

---

## 📧 Contacto

[Información de contacto]

---

## 🔗 Enlaces Útiles

- [NIST Lightweight Cryptography](https://csrc.nist.gov/projects/lightweight-cryptography)
- [Embedded Systems Security](https://www.embedded.com/category/security/)
- [IoT Security Foundation](https://www.iotsecurityfoundation.org/)

---

**Nota**: Este proyecto es para fines educativos y de investigación. No usar las implementaciones directamente en producción sin auditoría de seguridad profesional.
