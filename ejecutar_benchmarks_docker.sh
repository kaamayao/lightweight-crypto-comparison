#!/bin/bash

# Script auxiliar para ejecutar benchmarks en Docker con diferentes restricciones de recursos

echo "================================================================================"
echo "EJECUTOR DE BENCHMARKS RESTRINGIDOS BASADOS EN DOCKER"
echo "================================================================================"
echo ""

# Verificar si existe la imagen de Docker
if ! docker images | grep -q crypto-benchmark; then
    echo "Construyendo imagen de Docker 'crypto-benchmark'..."
    docker build -t crypto-benchmark .
    echo ""
fi

# Crear directorio de salida
mkdir -p resultados_docker

echo "Ejecutando benchmarks con diferentes restricciones de recursos..."
echo ""

# 1. Gama alta (línea base - sin restricciones)
echo "[1/4] PC de gama alta / Servidor (sin restricciones)..."
docker run --rm \
    crypto-benchmark \
    > resultados_docker/gama_alta.txt 2>&1
echo "  ✓ Resultados guardados en: resultados_docker/gama_alta.txt"

# 2. IoT de gama media (similar a ESP32: 50% CPU, 256MB RAM)
echo "[2/4] Dispositivo IoT de gama media (ESP32: 50% CPU, 256MB RAM)..."
docker run --rm \
    --cpus=0.5 \
    --memory=256m \
    crypto-benchmark \
    > resultados_docker/iot_gama_media.txt 2>&1
echo "  ✓ Resultados guardados en: resultados_docker/iot_gama_media.txt"

# 3. IoT de gama baja (similar a ESP8266: 25% CPU, 64MB RAM)
echo "[3/4] Dispositivo IoT de gama baja (ESP8266: 25% CPU, 64MB RAM)..."
docker run --rm \
    --cpus=0.25 \
    --memory=64m \
    crypto-benchmark \
    > resultados_docker/iot_gama_baja.txt 2>&1
echo "  ✓ Resultados guardados en: resultados_docker/iot_gama_baja.txt"

# 4. Ultra-restringido (Nodo sensor: 10% CPU, 32MB RAM)
echo "[4/4] Dispositivo ultra-restringido (Sensor: 10% CPU, 32MB RAM)..."
docker run --rm \
    --cpus=0.1 \
    --memory=32m \
    crypto-benchmark \
    > resultados_docker/ultra_restringido.txt 2>&1
echo "  ✓ Resultados guardados en: resultados_docker/ultra_restringido.txt"

echo ""
echo "================================================================================"
echo "¡Todos los benchmarks Docker completados!"
echo "Los resultados están en el directorio resultados_docker/"
echo "================================================================================"
echo ""
echo "Para ver resultados:"
echo "  cat resultados_docker/iot_gama_media.txt"
echo "  cat resultados_docker/iot_gama_baja.txt"
echo ""
echo "Para ejecutar pruebas individuales:"
echo "  docker run --rm --cpus=0.5 --memory=256m crypto-benchmark"
echo "  docker run --rm --cpus=0.25 --memory=64m crypto-benchmark"
echo ""
