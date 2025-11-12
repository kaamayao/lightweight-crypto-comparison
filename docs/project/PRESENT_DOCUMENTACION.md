# Documentación del Algoritmo PRESENT-80

## Índice
1. [Descripción General](#descripción-general)
2. [Arquitectura del Algoritmo](#arquitectura-del-algoritmo)
3. [Funciones Documentadas](#funciones-documentadas)
4. [Diseño para Hardware Ligero](#diseño-para-hardware-ligero)
5. [Flujo de Ejecución](#flujo-de-ejecución)
6. [Ejemplo de Uso](#ejemplo-de-uso)
7. [Referencias](#referencias)

---

## Descripción General

**PRESENT** es un algoritmo de cifrado de bloque ultra-ligero diseñado específicamente para **implementación en hardware** con recursos extremadamente limitados. Fue propuesto en CHES 2007 por Bogdanov et al.

### Características Principales

- **Tamaño de Bloque:** 64 bits
- **Tamaño de Clave:** 80 bits o 128 bits (esta implementación: 80 bits)
- **Número de Rondas:** 31
- **Tipo:** Red de Sustitución-Permutación (SPN)
- **Optimizado para:** Hardware ultra-ligero (RFID, sensores)
- **Tamaño de Compuertas:** ~1570 GE (Gate Equivalents)

### Filosofía de Diseño

**PRESENT fue diseñado con una filosofía de "hardware primero":**

✅ **Mínima complejidad de hardware**
✅ **S-Box de 4 bits** (vs 8 bits en AES)
✅ **Permutación de bits simple**
✅ **Programación de clave eficiente**
✅ **Sin operaciones complejas**

### Comparación de Tamaño (Hardware)

| Algoritmo | Compuertas (GE) | Aplicación |
|-----------|-----------------|------------|
| **PRESENT-80** | ~1570 | RFID, sensores ultra-ligeros |
| **AES-128** | ~3400 | Dispositivos de gama media |
| **DES** | ~2300 | Legacy |

---

## Arquitectura del Algoritmo

### Estructura General (SPN - Substitution-Permutation Network)

```
Texto Plano (64 bits)
         ↓
┌─────────────────────┐
│  Rondas 1-31:       │
│  1. addRoundKey     │  ← XOR con clave de ronda
│  2. sBoxLayer       │  ← Sustitución (16 S-Boxes 4-bit)
│  3. pLayer          │  ← Permutación de bits
└─────────────────────┘
         ↓
   [addRoundKey]  ← Ronda final (solo XOR)
         ↓
   Texto Cifrado (64 bits)
```

### Capas de Transformación

**1. addRoundKey:** XOR de 64 bits con clave de ronda
**2. sBoxLayer:** 16 S-Boxes de 4→4 bits en paralelo
**3. pLayer:** Permutación de bits específica

---

## Funciones Documentadas

### 1. `generate_round_keys(key)`

**Propósito:** Generar 32 claves de ronda (una para cada ronda + inicial).

**Parámetros:**
- `key` (list): 80 bits de la clave maestra

**Retorna:** Lista de 32 claves de ronda (cada una de 64 bits)

**Algoritmo:**

```python
key_register = key  # 80 bits

for round_num in 1..32:
    # Paso 1: Extraer clave de ronda (primeros 64 bits)
    round_key[round_num] = key_register[0:63]

    # Paso 2: Rotar registro 61 posiciones a la izquierda
    key_register = rotate_left(key_register, 61)

    # Paso 3: Aplicar S-Box al nibble más alto (4 bits)
    key_register[0:3] = SBOX(key_register[0:3])

    # Paso 4: XOR con contador de ronda
    key_register[15:19] ^= round_num  # 5 bits
```

**Ejemplo Visual:**

```
Iteración 1:
  Key Register: [k79 k78 ... k1 k0]  (80 bits)
                 ↓
  Round Key 1:  [k79 k78 ... k16]    (64 bits)
                 ↓
  Rotar 61:     [k18 k17 ... k19]
                 ↓
  S-Box[k18..k15]: Nuevo nibble alto
                 ↓
  XOR contador:  bits[15:19] ^= 00001

Iteración 2:
  ...continúa con key_register modificado
```

**Características de la Programación de Clave:**

- **Rotación de 61 bits:** Proporciona difusión rápida
- **S-Box solo en 4 bits:** Mínima complejidad
- **Contador de ronda:** Previene claves de ronda idénticas
- **Mismas claves para cifrado/descifrado:** Simplifica hardware

---

### 2. `sbox_layer(state)`

**Propósito:** Aplicar S-Box de 4 bits a todos los 16 nibbles del estado.

**Parámetros:**
- `state` (list): 64 bits

**Retorna:** 64 bits transformados

**Proceso:**

```python
# Dividir 64 bits en 16 nibbles de 4 bits
for i in 0..15:
    nibble = state[i*4 : i*4+4]  # 4 bits
    nuevo_nibble = SBOX[nibble]  # Sustitución
    resultado += nuevo_nibble
```

**La S-Box de PRESENT:**

```
Input:  0 1 2 3 4 5 6 7 8 9 A B C D E F
Output: C 5 6 B 9 0 A D 3 E F 8 4 7 1 2
```

**Ejemplo:**
```
Nibble de entrada:  1011₂ = B₁₆ = 11₁₀
S-Box output:       1000₂ = 8₁₆ = 8₁₀
```

**Propiedades de la S-Box:**

- **Tamaño:** 4 bits → 4 bits (16 elementos)
- **Biyectiva:** Cada entrada tiene salida única
- **Criterio de no linealidad:** NL = 4
- **Criterio diferencial:** δ = 4
- **Optimizada para hardware:** Solo 28 compuertas

**Comparación:**

| Algoritmo | S-Box Size | Compuertas | No Linealidad |
|-----------|-----------|------------|---------------|
| PRESENT | 4×4 bits | 28 | 4 |
| AES | 8×8 bits | ~300 | 112 |

---

### 3. `inv_sbox_layer(state)`

**Propósito:** Aplicar S-Box inversa (para descifrado).

**S-Box Inversa:**

```
Input:  0 1 2 3 4 5 6 7 8 9 A B C D E F
Output: 5 E F 8 C 1 2 D 9 4 6 3 0 7 A B
```

**Relación:**
```python
inv_sbox_layer(sbox_layer(state)) == state
```

---

### 4. `pbox_layer(state)`

**Propósito:** Permutación de bits para difusión óptima.

**Parámetros:**
- `state` (list): 64 bits

**Retorna:** 64 bits permutados

**Algoritmo:**

```python
for i in 0..63:
    resultado[PBOX[i]] = state[i]
```

**Tabla de Permutación (PBOX):**

```
Bit  0 →  0   Bit 16 → 16   Bit 32 → 32   Bit 48 → 48
Bit  1 → 16   Bit 17 →  1   Bit 33 → 17   Bit 49 → 33
Bit  2 → 32   Bit 18 → 17   Bit 34 →  2   Bit 50 → 18
Bit  3 → 48   Bit 19 → 33   Bit 35 → 18   Bit 51 →  3
Bit  4 →  1   Bit 20 → 49   Bit 36 → 33   Bit 52 → 49
...
```

**Fórmula General:**
```
PBOX[i] = i * 16 mod 63  (para i < 63)
PBOX[63] = 63
```

**Propósito de la Permutación:**

1. **Difusión completa en 2 rondas:**
   - Cada bit de salida depende de todos los bits de entrada
   - Cambio de 1 bit afecta ~32 bits después de 2 rondas

2. **Simple en hardware:**
   - Solo re-ruteo de cables
   - Costo: 0 compuertas (solo interconexiones)

**Ejemplo Visual:**

```
Entrada (por nibbles):
[N0 N1 N2 N3 N4 N5 N6 N7 N8 N9 NA NB NC ND NE NF]
  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15

Después de pLayer:
Cada bit del nibble i se dispersa a diferentes nibbles
```

---

### 5. `inv_pbox_layer(state)`

**Propósito:** Permutación inversa (para descifrado).

**Proceso:**
```python
for i in 0..63:
    resultado[i] = state[PBOX[i]]
```

**Relación:**
```python
inv_pbox_layer(pbox_layer(state)) == state
```

---

### 6. `add_round_key(state, round_key)`

**Propósito:** XOR del estado con la clave de ronda.

**Parámetros:**
- `state` (list): 64 bits del estado
- `round_key` (list): 64 bits de la clave de ronda

**Retorna:** 64 bits resultantes

**Proceso:**
```python
for i in 0..63:
    resultado[i] = state[i] ⊕ round_key[i]
```

**Propiedades:**

- **Operación más simple posible:** Solo XOR
- **Auto-inversa:** `XOR(XOR(x, k), k) = x`
- **Costo en hardware:** 64 compuertas XOR
- **Tiempo constante:** O(1) en paralelo

---

### 7. `present_encrypt_block(block, round_keys)`

**Propósito:** Cifrar un bloque de 64 bits.

**Parámetros:**
- `block` (list): 64 bits de texto plano
- `round_keys` (list): 32 claves de ronda

**Retorna:** 64 bits cifrados

**Algoritmo Completo:**

```python
state = block

# Rondas 1-31
for round in 0..30:
    state = addRoundKey(state, round_keys[round])
    state = sBoxLayer(state)
    state = pLayer(state)

# Post-whitening (ronda final)
state = addRoundKey(state, round_keys[31])

return state
```

**Diagrama de Flujo:**

```
    Input (64 bits)
         ↓
    ┌─────────────┐
    │ Round 1     │
    │ AddRoundKey │ ← K₁
    │ sBoxLayer   │ ← 16 S-Boxes paralelas
    │ pLayer      │ ← Permutación de bits
    └─────────────┘
         ↓
    ┌─────────────┐
    │ Round 2     │
    │ AddRoundKey │ ← K₂
    │ sBoxLayer   │
    │ pLayer      │
    └─────────────┘
         ↓
       ...
         ↓
    ┌─────────────┐
    │ Round 31    │
    │ AddRoundKey │ ← K₃₁
    │ sBoxLayer   │
    │ pLayer      │
    └─────────────┘
         ↓
    AddRoundKey    ← K₃₂
         ↓
    Output (64 bits)
```

**Características:**

- **31 rondas completas** + whitening final
- **Estructura SPN pura** (no Feistel)
- **Cada ronda idéntica** (simplifica hardware)
- **Sin ronda final especial** (a diferencia de AES)

---

### 8. `present_decrypt_block(block, round_keys)`

**Propósito:** Descifrar un bloque de 64 bits.

**Proceso:**

Aplicar transformaciones inversas en orden inverso:

```python
state = block

# Post-whitening inverso
state = addRoundKey(state, round_keys[31])

# Rondas 31-1 (orden inverso)
for round in 30..0 (decreciente):
    state = inv_pLayer(state)
    state = inv_sBoxLayer(state)
    state = addRoundKey(state, round_keys[round])

return state
```

**Nota Importante:**

A diferencia de DES, PRESENT usa las **mismas claves de ronda** para cifrado y descifrado (no invertidas), solo se invierten las operaciones.

---

### 9. `PRESENT_encrypt(plaintext, key)` y `PRESENT_decrypt(ciphertext, key)`

**Propósito:** APIs de alto nivel.

**Características:**

- ✅ Acepta strings o listas de bits
- ✅ Validación de tamaño de clave (80 bits)
- ✅ Padding automático a múltiplo de 64 bits
- ✅ Maneja múltiples bloques

**Ejemplo:**

```python
plaintext = "Hello!!!"    # 8 bytes = 64 bits
key = "secret1234"       # 10 bytes = 80 bits

ciphertext = PRESENT_encrypt(plaintext, key)
plaintext = PRESENT_decrypt(ciphertext, key)
```

---

## Diseño para Hardware Ligero

### Filosofía de Diseño

PRESENT fue diseñado con restricciones específicas de hardware:

**Objetivo:** Minimizar área de silicio (Gate Equivalents)

**Decisiones de Diseño:**

1. **S-Box de 4 bits** vs 8 bits
   - Costo: 28 GE vs ~300 GE
   - 16 S-Boxes en paralelo: 448 GE total

2. **Permutación de bits**
   - Costo: 0 GE (solo cableado)
   - Implementación: Reorganizar conexiones

3. **Programación de clave simple**
   - Rotación: Cableado
   - 1 S-Box: 28 GE
   - XOR: 64 GE

4. **Sin multiplicación**
   - A diferencia de AES (MixColumns)
   - Solo XOR y permutaciones

### Desglose de Compuertas

| Componente | Compuertas (GE) | Porcentaje |
|------------|-----------------|------------|
| S-Boxes (16) | 448 | 28.5% |
| Registro de estado | 256 | 16.3% |
| Registro de clave | 320 | 20.4% |
| Control | 188 | 12.0% |
| Permutación | 0 | 0% |
| XOR | 64 | 4.1% |
| Otros | 294 | 18.7% |
| **Total** | **~1570 GE** | **100%** |

### Comparación con AES

**Implementación Hardware:**

| Métrica | PRESENT-80 | AES-128 | Ventaja |
|---------|-----------|---------|---------|
| Área (GE) | 1570 | 3400 | **2.2x menor** |
| Throughput @ 100kHz | 200 Kbps | 128 Kbps | Similar |
| Potencia | Ultra-baja | Baja | Mejor |
| Latencia | 32 ciclos | 11 ciclos | AES más rápido |

**Implementación Software:**

| Métrica | PRESENT-80 | AES-128 | Ventaja |
|---------|-----------|---------|---------|
| Velocidad | Lenta | Rápida | **AES 2-3x más rápido** |
| ROM | Pequeña | Media | PRESENT menor |
| RAM | Mínima | Media | PRESENT menor |

**Conclusión:** PRESENT es superior en **hardware**, AES en **software**.

---

## Flujo de Ejecución

### Cifrado Completo

```
"Hello!!!" (8 bytes = 64 bits)
         ↓
   [string_to_bits]
    [01001000, 01100101, ...]
         ↓
   [generate_round_keys]
    K₁, K₂, ..., K₃₂ (cada uno 64 bits)
         ↓
   [present_encrypt_block]
    ├─ AddRoundKey(K₁)
    ├─ sBoxLayer (16 nibbles)
    ├─ pLayer (permutación)
    ├─ AddRoundKey(K₂)
    ├─ sBoxLayer
    ├─ pLayer
    ├─ ... (hasta ronda 31)
    ├─ AddRoundKey(K₃₁)
    ├─ sBoxLayer
    ├─ pLayer
    └─ AddRoundKey(K₃₂)
         ↓
   Texto Cifrado (64 bits)
```

### Descifrado Completo

```
Texto Cifrado (64 bits)
         ↓
   [generate_round_keys]
    K₁, K₂, ..., K₃₂ (¡mismas claves!)
         ↓
   [present_decrypt_block]
    ├─ AddRoundKey(K₃₂)
    ├─ inv_pLayer
    ├─ inv_sBoxLayer
    ├─ AddRoundKey(K₃₁)
    ├─ inv_pLayer
    ├─ inv_sBoxLayer
    ├─ ... (hasta ronda 1)
    └─ AddRoundKey(K₁)
         ↓
   Texto Plano (64 bits)
```

---

## Ejemplo de Uso

### Ejemplo Básico

```python
from algorithms.PRESENT.index import PRESENT_encrypt, PRESENT_decrypt
from utils.index import bits_to_hex, bits_to_string

# Cifrado
plaintext = "Hello!!!"
key = "secret1234"  # 10 caracteres = 80 bits

ciphertext_bits = PRESENT_encrypt(plaintext, key)
print(f"Cifrado (hex): {bits_to_hex(ciphertext_bits)}")

# Descifrado
decrypted_bits = PRESENT_decrypt(ciphertext_bits, key)
decrypted_text = bits_to_string(decrypted_bits)
print(f"Descifrado: {decrypted_text}")
```

### Ejemplo con Múltiples Bloques

```python
# Mensaje largo
long_message = "Este mensaje tiene más de 64 bits y requiere múltiples bloques"
key = "clave12345"

# PRESENT divide automáticamente en bloques
ciphertext = PRESENT_encrypt(long_message, key)
plaintext = PRESENT_decrypt(ciphertext, key)

original = bits_to_string(plaintext)
```

### Trabajar con Bits Directamente

```python
# Bloque de 64 bits
plaintext_bits = [0,1,0,1,0,1,0,1] * 8  # 64 bits
key_bits = [1,1,0,0,1,1,0,0] * 10      # 80 bits

ciphertext_bits = PRESENT_encrypt(plaintext_bits, key_bits)
```

---

## Análisis de Seguridad

### Fortalezas

1. **Diseño Conservador**
   - Basado en principios probados de SPN
   - 31 rondas proporcionan gran margen de seguridad

2. **Resistencia a Ataques Conocidos**
   - **Diferencial:** Resistente hasta 16 rondas
   - **Lineal:** Resistente hasta 26 rondas
   - **Algebraico:** Alta complejidad

3. **Análisis Extensivo**
   - Estudiado por comunidad criptográfica desde 2007
   - Candidato a ISO/IEC 29192-2

### Debilidades Conocidas

1. **Tamaño de Bloque Pequeño** (64 bits)
   - Vulnerable a ataques de cumpleaños después de 2³² bloques
   - **Solución:** Re-cifrar después de ~32 GB de datos

2. **Rendimiento en Software**
   - 2-3x más lento que AES
   - Operaciones a nivel de bit no eficientes en CPU

3. **Ataques Publicados**
   - Ataques de texto plano relacionado en versión reducida
   - **No prácticos** para 31 rondas completas

### Casos de Uso Apropiados

✅ **SÍ usar PRESENT para:**
- RFID tags
- Nodos sensores inalámbricos
- Dispositivos IoT ultra-limitados
- Implementaciones hardware

❌ **NO usar PRESENT para:**
- Software en PCs/servidores → Usar AES
- Datos de gran volumen (>32 GB) → Re-keying
- Aplicaciones de alta velocidad → Usar AES

---

## Comparación Completa

### PRESENT vs DES

| Característica | PRESENT-80 | DES |
|----------------|-----------|-----|
| Diseño | Moderno (2007) | Legacy (1977) |
| Tamaño de bloque | 64 bits | 64 bits |
| Tamaño de clave | 80 bits | 56 bits |
| Rondas | 31 | 16 |
| Estructura | SPN | Feistel |
| Seguridad | ✅ Seguro | ❌ Roto |
| Hardware | Excelente | Bueno |
| Software | Lento | Moderado |

### PRESENT vs AES

| Característica | PRESENT-80 | AES-128 |
|----------------|-----------|---------|
| Tamaño de bloque | 64 bits | 128 bits |
| Tamaño de clave | 80 bits | 128 bits |
| Rondas | 31 | 10 |
| Área (GE) | **1570** | 3400 |
| Velocidad (SW) | Lenta | **Rápida** |
| Aceleración HW | ✅ | ✅✅ |
| Uso típico | RFID, sensores | General |

---

## Constantes Importantes

### S-Box (16 elementos)

```python
SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
        0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
```

### S-Box Inversa

```python
INV_SBOX = [0x5, 0xE, 0xF, 0x8, 0xC, 0x1, 0x2, 0xD,
            0xB, 0x4, 0x6, 0x3, 0x0, 0x7, 0xA, 0x9]
```

### P-Box (64 elementos)

Definida por la fórmula: `PBOX[i] = i * 16 mod 63` (i < 63), `PBOX[63] = 63`

---

## Complejidad Computacional

### Tiempo

| Operación | Complejidad | Notas |
|-----------|-------------|-------|
| sBoxLayer | O(1) | 16 S-Boxes paralelas |
| pLayer | O(n) | n = 64 (reorganización) |
| addRoundKey | O(n) | n = 64 XORs |
| generate_round_keys | O(1) | 32 iteraciones fijas |
| Cifrado de bloque | O(1) | 31 rondas fijas |
| Cifrado completo | O(m) | m = número de bloques |

### Espacio

- **Claves de ronda:** 32 × 64 bits = 256 bytes
- **Estado:** 64 bits = 8 bytes
- **S-Box:** 16 valores = 16 bytes
- **P-Box:** 64 valores = 64 bytes
- **Total:** ~344 bytes

---

## Preguntas Frecuentes

### ¿Por qué 31 rondas?

Para proporcionar margen de seguridad suficiente. Los mejores ataques conocidos alcanzan ~26 rondas, dejando margen de 5 rondas.

### ¿Por qué S-Box de 4 bits?

Minimiza área de hardware (~28 GE) vs S-Box de 8 bits (~300 GE). 16 S-Boxes de 4 bits = 448 GE total.

### ¿Es PRESENT más seguro que AES?

No necesariamente. **AES tiene mayor seguridad absoluta** (128 bits vs 80 bits). PRESENT es más eficiente en hardware ultra-ligero.

### ¿Puedo usar PRESENT en mi aplicación?

Depende:
- **RFID/IoT hardware:** ✅ Excelente elección
- **Software PC/móvil:** ❌ Usar AES (mucho más rápido)
- **Alto volumen de datos:** ⚠️ Re-keying necesario

### ¿PRESENT-80 o PRESENT-128?

- **PRESENT-80:** Menor área (1570 GE), seguridad adecuada para IoT
- **PRESENT-128:** Más seguro, ~10% más área

---

## Referencias

1. **PRESENT: An Ultra-Lightweight Block Cipher** - Bogdanov et al., CHES 2007
2. **ISO/IEC 29192-2:2012** - Lightweight cryptography — Part 2: Block ciphers
3. **Cryptanalysis of PRESENT** - Diversos papers académicos
4. **Lightweight Cryptography** - Survey papers

---

## Resumen de Funciones

| Función | Entrada | Salida | Propósito |
|---------|---------|--------|-----------|
| `generate_round_keys()` | 80 bits | 32×64 bits | Generar subclaves |
| `sbox_layer()` | 64 bits | 64 bits | Confusión (16 S-Boxes) |
| `pbox_layer()` | 64 bits | 64 bits | Difusión (permutación) |
| `add_round_key()` | 64b, 64b | 64 bits | Mezcla con clave (XOR) |
| `present_encrypt_block()` | 64 bits | 64 bits | Cifrar bloque |
| `PRESENT_encrypt()` | texto, clave | bits | API cifrado |
| `PRESENT_decrypt()` | bits, clave | bits | API descifrado |

---

**Nota:** PRESENT es óptimo para **hardware ultra-ligero**. Para software o dispositivos de recursos moderados, considerar **AES-128**.
