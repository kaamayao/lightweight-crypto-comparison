# Lightweight Cryptography Comparison: DES vs AES-128

Comparación de rendimiento entre algoritmos de criptografía ligera DES y AES-128 en diferentes perfiles de hardware.

## Requisitos

- **Python**: 3.9.6 o superior
- **Dependencias**: Ver `requirements.txt`

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Ejecutar todos los benchmarks

```bash
python3 benchmarks/ejecutar_todos.py
```

Este comando ejecutará:
1. Benchmark estándar (PC sin restricciones)
2. Benchmarks con restricciones (4 perfiles IoT simulados)
3. Generación automática de gráficos
4. Generación automática de PDF con todos los resultados

### Resultados

Los resultados se guardan en el directorio `results/`:
- `benchmark_charts_*.png`: Dashboards con 9 gráficos comparativos
- `chart_*.png`: Gráficos individuales para cada métrica
- `reporte_completo.pdf`: Reporte PDF con todos los gráficos (11 páginas)

## Estructura del Proyecto

```
lightweight-crypto-comparison/
├── algorithms/           # Implementaciones de algoritmos
│   ├── AES/             # AES-128
│   ├── DES/             # DES
│   └── utils/           # Utilidades comunes
├── benchmarks/          # Scripts de benchmarking
│   ├── benchmark.py     # Sistema unificado de benchmarks
│   ├── ejecutar_todos.py # Script principal
│   └── generar_pdf_graficos.py # Generador de PDF
├── data/                # Mensajes de prueba
└── results/             # Resultados generados (gitignored)
```

## Algoritmos Implementados

- **DES**: Data Encryption Standard (clave de 64 bits)
- **AES-128**: Advanced Encryption Standard (clave de 128 bits)

## Métricas Evaluadas

- Tiempo de cifrado y descifrado
- Rendimiento (throughput en MB/s)
- Uso de memoria (cifrado y descifrado por separado)
- Consumo energético estimado
- Ciclos de CPU por byte
- Escalabilidad vs tamaño de mensaje

## Perfiles de Hardware Simulados

1. **Sin restricciones**: PC/Servidor de gama alta
2. **PC de gama alta**: Línea base para comparación
3. **IoT gama media**: ESP32, Arduino Due (50% CPU, 512 MB RAM)
4. **IoT gama baja**: ESP8266, Arduino Uno (25% CPU, 256 MB RAM)
5. **Ultra restringido**: Sensores, RFID (10% CPU, 128 MB RAM)

## Licencia

[Especificar licencia aquí]
