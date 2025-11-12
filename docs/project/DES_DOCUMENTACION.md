# Documentación del Algoritmo DES (Data Encryption Standard)

## Índice
1. [Descripción General](#descripción-general)
2. [Arquitectura del Algoritmo](#arquitectura-del-algoritmo)
3. [Funciones Documentadas](#funciones-documentadas)
4. [Flujo de Ejecución](#flujo-de-ejecución)
5. [Ejemplo de Uso](#ejemplo-de-uso)
6. [Referencias](#referencias)

---

## Descripción General

**DES (Data Encryption Standard)** es un algoritmo de cifrado simétrico de bloque que opera en bloques de 64 bits utilizando una clave de 64 bits (56 bits efectivos + 8 bits de paridad).

### Características Principales

- **Tamaño de Bloque:** 64 bits
- **Tamaño de Clave:** 64 bits (56 bits efectivos)
- **Número de Rondas:** 16
- **Tipo:** Cifrado simétrico de bloque (Feistel)
- **Estado Actual:** Considerado inseguro (vulnerable a fuerza bruta)

### Componentes Clave

1. **Permutación Inicial (IP)** - Reorganiza bits del bloque inicial
2. **Red de Feistel** - 16 rondas de transformación
3. **Función F** - Función no lineal en cada ronda
4. **S-Boxes** - 8 cajas de sustitución (confusión)
5. **Permutación P** - Difusión de bits
6. **Permutación Final (IP⁻¹)** - Inversa de IP

---

## Arquitectura del Algoritmo

```
Texto Plano (64 bits)
         ↓
   [Permutación Inicial IP]
         ↓
    L₀ (32 bits) | R₀ (32 bits)
         ↓
   [16 Rondas Feistel]
    Ronda i: Lᵢ = Rᵢ₋₁
             Rᵢ = Lᵢ₋₁ ⊕ F(Rᵢ₋₁, Kᵢ)
         ↓
   [Intercambio Final]
    R₁₆ | L₁₆
         ↓
   [Permutación Final IP⁻¹]
         ↓
  Texto Cifrado (64 bits)
```

### Función Feistel F

```
R (32 bits)
    ↓
[Expansión E: 32 → 48 bits]
    ↓
[⊕ con Clave de Ronda (48 bits)]
    ↓
[8 S-Boxes: 48 → 32 bits]
    ↓
[Permutación P]
    ↓
Salida (32 bits)
```

---

## Funciones Documentadas

### 1. `permute(block, table)`

**Propósito:** Aplicar una tabla de permutación a un bloque de bits.

**Parámetros:**
- `block` (list): Lista de bits a permutar
- `table` (list): Tabla de permutación (índices 1-indexados)

**Retorna:** Lista de bits permutados

**Descripción:**
Reorganiza los bits según la tabla proporcionada. Las tablas están 1-indexadas (primer bit es 1, no 0).

**Ejemplo:**
```python
# Si table = [2, 1, 3] y block = [a, b, c]
# Resultado: [b, a, c]
result = permute([0, 1, 0], [2, 1, 3])  # → [1, 0, 0]
```

**Uso en DES:**
- Permutación Inicial (IP)
- Permutación de Expansión (E)
- Permutación P
- Permutación Final (IP⁻¹)
- Generación de claves (PC1, PC2)

---

### 2. `generate_round_keys(key)`

**Propósito:** Generar 16 claves de ronda a partir de la clave principal.

**Parámetros:**
- `key` (list): Clave de 64 bits

**Retorna:** Lista de 16 claves de ronda (cada una de 48 bits)

**Proceso:**
1. **Conversión a 64 bits** - Padding si es necesario
2. **PC1 (Permuted Choice 1)** - Reduce 64 bits a 56 bits
3. **División** - Split en dos mitades C₀ y D₀ (28 bits cada una)
4. **16 Iteraciones:**
   - Rotación circular izquierda de C y D según `SHIFT_SCHEDULE`
   - Combinación: CD = C + D (56 bits)
   - **PC2 (Permuted Choice 2)** - Reduce 56 bits a 48 bits
   - Guardar clave de ronda

**Tabla de Rotaciones (SHIFT_SCHEDULE):**
```
Ronda:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
Shift:  1  1  2  2  2  2  2  2  1  2  2  2  2  2  2  1
```

**Ejemplo:**
```python
key = [0,1,0,1,...] * 64  # 64 bits
round_keys = generate_round_keys(key)
# round_keys[0] → Clave ronda 1 (48 bits)
# round_keys[15] → Clave ronda 16 (48 bits)
```

---

### 3. `s_box_substitution(block_48)`

**Propósito:** Aplicar sustitución S-box a un bloque de 48 bits.

**Parámetros:**
- `block_48` (list): Bloque de 48 bits

**Retorna:** Lista de 32 bits

**Proceso:**
1. Dividir 48 bits en 8 bloques de 6 bits
2. Para cada bloque:
   - **Fila** = bits exterior (bit 0 y bit 5)
   - **Columna** = bits interiores (bits 1-4)
   - Buscar en S-Box[i][fila][columna]
   - Convertir valor (0-15) a 4 bits
3. Concatenar resultados (8 × 4 = 32 bits)

**Ejemplo de S-Box:**
```
Entrada: 011011 (6 bits)
  - Fila = 01₂ = 1
  - Columna = 1101₂ = 13
  - S-Box[i][1][13] = 9
  - Salida: 1001 (4 bits)
```

**Importancia:**
Las S-Boxes son el único componente **no lineal** de DES, proporcionando confusión criptográfica.

---

### 4. `feistel_function(right_32, round_key)`

**Propósito:** Implementar la función F de Feistel.

**Parámetros:**
- `right_32` (list): Mitad derecha del bloque (32 bits)
- `round_key` (list): Clave de ronda (48 bits)

**Retorna:** Lista de 32 bits

**Proceso:**
```
1. Expansión: 32 bits → 48 bits (tabla E)
2. XOR con clave de ronda
3. Sustitución S-Box: 48 bits → 32 bits
4. Permutación P: 32 bits → 32 bits
```

**Diagrama:**
```
    R (32 bits)
        ↓
    [E-Box]  Expansión: duplica algunos bits
        ↓
    48 bits
        ↓
    [⊕ K]  XOR con clave de ronda
        ↓
   [S-Boxes]  Sustitución no lineal
        ↓
    32 bits
        ↓
    [P-Box]  Permutación
        ↓
   F(R, K)
```

---

### 5. `des_encrypt_block(plaintext_64, round_keys)`

**Propósito:** Cifrar un bloque de 64 bits usando DES.

**Parámetros:**
- `plaintext_64` (list): Bloque de 64 bits
- `round_keys` (list): 16 claves de ronda

**Retorna:** Bloque cifrado de 64 bits

**Proceso Detallado:**

```python
# Paso 1: Permutación Inicial
permuted = IP(plaintext_64)

# Paso 2: División
L₀ = permuted[0:32]   # Mitad izquierda
R₀ = permuted[32:64]  # Mitad derecha

# Paso 3: 16 Rondas Feistel
for i in 0 to 15:
    Lᵢ = Rᵢ₋₁
    Rᵢ = Lᵢ₋₁ ⊕ F(Rᵢ₋₁, Kᵢ)

# Paso 4: Intercambio e Inversión
combined = R₁₆ + L₁₆  # ¡Nota: R primero!

# Paso 5: Permutación Final
ciphertext = IP⁻¹(combined)
```

**Nota Importante:**
El intercambio final (R₁₆ antes que L₁₆) es crucial para que el descifrado funcione con el mismo algoritmo.

---

### 6. `DES_encrypt(plaintext, key)`

**Propósito:** API de alto nivel para cifrar texto usando DES.

**Parámetros:**
- `plaintext` (str o list): Texto a cifrar
- `key` (str o list): Clave de 64 bits (8 caracteres)

**Retorna:** Lista de bits representando el texto cifrado

**Características:**
- ✅ Acepta strings o listas de bits
- ✅ Padding automático a múltiplo de 64 bits
- ✅ Maneja múltiples bloques
- ✅ Conversión automática de formato

**Proceso:**
```python
1. Convertir plaintext a bits
2. Convertir key a bits
3. Padding de clave a 64 bits
4. Padding de plaintext a múltiplo de 64 bits
5. Generar 16 claves de ronda
6. Cifrar cada bloque de 64 bits
7. Concatenar resultados
```

**Ejemplo:**
```python
plaintext = "Hello!!!"  # 8 bytes = 64 bits
key = "secret12"        # 8 bytes = 64 bits

ciphertext_bits = DES_encrypt(plaintext, key)
# ciphertext_bits es una lista de bits: [0,1,1,0,...]
```

---

### 7. `DES_decrypt(ciphertext_bits, key)`

**Propósito:** Descifrar texto cifrado usando DES.

**Parámetros:**
- `ciphertext_bits` (list): Bits del texto cifrado
- `key` (str o list): Clave de 64 bits

**Retorna:** Lista de bits representando el texto plano

**Diferencia con Cifrado:**
La única diferencia es que las **claves de ronda se usan en orden inverso**:
```python
round_keys = generate_round_keys(key)
round_keys = round_keys[::-1]  # Invertir orden
```

**Proceso:**
```python
1. Convertir key a bits
2. Padding de clave a 64 bits
3. Generar 16 claves de ronda
4. ⭐ INVERTIR orden de claves ⭐
5. Descifrar cada bloque usando des_encrypt_block
6. Concatenar resultados
```

**Ejemplo:**
```python
ciphertext = [0,1,1,0,...]  # Bits cifrados
key = "secret12"

plaintext_bits = DES_decrypt(ciphertext, key)
plaintext = bits_to_string(plaintext_bits)
# plaintext = "Hello!!!"
```

---

## Flujo de Ejecución

### Cifrado Completo

```
Entrada: "Hello!!!" + key "secret12"
    ↓
1. string_to_bits("Hello!!!")
   → [01001000, 01100101, ...] (64 bits)
    ↓
2. generate_round_keys(key)
   → [K₁, K₂, ..., K₁₆]
    ↓
3. des_encrypt_block(block, round_keys)
   ├─ IP(block)
   ├─ Split → L₀, R₀
   ├─ Ronda 1: L₁=R₀, R₁=L₀⊕F(R₀,K₁)
   ├─ Ronda 2: L₂=R₁, R₂=L₁⊕F(R₁,K₂)
   ├─ ...
   ├─ Ronda 16: L₁₆=R₁₅, R₁₆=L₁₅⊕F(R₁₅,K₁₆)
   ├─ Combine: R₁₆ + L₁₆
   └─ IP⁻¹(combined)
    ↓
Salida: Bits cifrados
```

### Descifrado Completo

```
Entrada: bits cifrados + key "secret12"
    ↓
1. generate_round_keys(key)
   → [K₁, K₂, ..., K₁₆]
    ↓
2. Invertir claves
   → [K₁₆, K₁₅, ..., K₁]
    ↓
3. des_encrypt_block(cipher, reversed_keys)
   (¡Mismo algoritmo, claves invertidas!)
    ↓
Salida: Bits descifrados
```

---

## Ejemplo de Uso

### Ejemplo Básico

```python
from algorithms.DES.index import DES_encrypt, DES_decrypt
from utils.index import bits_to_hex, bits_to_string

# Cifrado
plaintext = "SecretMsg"
key = "mykey123"  # 8 caracteres

ciphertext_bits = DES_encrypt(plaintext, key)
print(f"Cifrado (hex): {bits_to_hex(ciphertext_bits)}")

# Descifrado
decrypted_bits = DES_decrypt(ciphertext_bits, key)
decrypted_text = bits_to_string(decrypted_bits)
print(f"Descifrado: {decrypted_text}")
```

### Ejemplo con Múltiples Bloques

```python
# Mensaje largo (más de 64 bits)
long_message = "Este mensaje es mucho más largo que 8 caracteres"
key = "password"

# DES automáticamente divide en bloques
ciphertext = DES_encrypt(long_message, key)

# Descifrado
plaintext = DES_decrypt(ciphertext, key)
original = bits_to_string(plaintext)
```

### Ejemplo con Bits Directamente

```python
# Trabajar con bits en lugar de strings
plaintext_bits = [0,1,0,1,0,1,0,1] * 8  # 64 bits
key_bits = [1,1,1,1,0,0,0,0] * 8        # 64 bits

ciphertext_bits = DES_encrypt(plaintext_bits, key_bits)
```

---

## Constantes Importantes

### Tablas de Permutación

- **IP (Initial Permutation):** 64 elementos
- **IP_INV (Inverse IP):** 64 elementos
- **E (Expansion):** 48 elementos (32 → 48 bits)
- **P (Permutation):** 32 elementos
- **PC1 (Permuted Choice 1):** 56 elementos (64 → 56 bits)
- **PC2 (Permuted Choice 2):** 48 elementos (56 → 48 bits)

### S-Boxes

8 S-Boxes, cada una:
- Entrada: 6 bits
- Salida: 4 bits
- Dimensión: 4 filas × 16 columnas
- Total: 8 × 4 × 16 = 512 valores

### SHIFT_SCHEDULE

Define rotaciones por ronda:
```python
[1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
```

---

## Consideraciones de Seguridad

### ⚠️ Vulnerabilidades Conocidas

1. **Tamaño de Clave Pequeño** (56 bits)
   - Vulnerable a ataques de fuerza bruta
   - Se puede romper en horas con hardware moderno

2. **S-Boxes Fijas**
   - Conocidas por todos
   - Posibles backdoors (controversia NSA)

3. **Ataques Conocidos**
   - Criptoanálisis diferencial
   - Criptoanálisis lineal
   - Ataques de fuerza bruta

### ✅ Uso Apropiado

- ❌ **NO** usar para datos sensibles nuevos
- ✅ Educación y aprendizaje
- ✅ Compatibilidad con sistemas legacy
- ✅ Usar Triple-DES (3DES) si se requiere DES

### Alternativas Modernas

- **AES-128/192/256** - Estándar actual
- **ChaCha20** - Para software
- **PRESENT** - Para hardware ultra-ligero

---

## Complejidad Computacional

### Tiempo de Ejecución

| Operación | Complejidad | Notas |
|-----------|-------------|-------|
| Permutación | O(n) | n = tamaño del bloque |
| S-Box | O(1) | Lookup table |
| Generación de claves | O(1) | 16 iteraciones fijas |
| Cifrado de bloque | O(1) | 16 rondas fijas |
| Cifrado completo | O(m) | m = número de bloques |

### Uso de Memoria

- **Claves de ronda:** 16 × 48 bits = 96 bytes
- **Bloque temporal:** 64 bits = 8 bytes
- **Constantes (S-Boxes, tablas):** ~2 KB
- **Total:** ~3 KB por instancia

---

## Preguntas Frecuentes

### ¿Por qué se intercambian L y R al final?

Para que el descifrado pueda usar el mismo algoritmo con claves invertidas. Sin el intercambio, necesitarías un algoritmo diferente para descifrar.

### ¿Por qué 56 bits efectivos si la clave es de 64 bits?

8 bits se usan para paridad (verificación de errores). Históricamente, esto permitió detección de errores en transmisión de claves.

### ¿Puedo usar DES para datos reales?

**NO.** DES es considerado inseguro desde los años 90. Usa AES o algoritmos modernos.

### ¿Cómo funciona el padding?

El padding añade ceros al final del mensaje para completar bloques de 64 bits. En producción, se usaría PKCS#7 u otros esquemas estándar.

---

## Referencias

1. **FIPS PUB 46-3** - Data Encryption Standard (DES)
2. **Applied Cryptography** - Bruce Schneier
3. **Introduction to Modern Cryptography** - Katz & Lindell
4. **NIST Special Publication 800-67** - Recommendation for Triple DES

---

## Resumen de Funciones

| Función | Entrada | Salida | Propósito |
|---------|---------|--------|-----------|
| `permute()` | bits, tabla | bits | Reorganizar bits |
| `generate_round_keys()` | clave (64b) | 16 claves (48b) | Generar subclaves |
| `s_box_substitution()` | 48 bits | 32 bits | Sustitución no lineal |
| `feistel_function()` | 32 bits, clave | 32 bits | Función F de ronda |
| `des_encrypt_block()` | 64 bits, claves | 64 bits | Cifrar bloque |
| `DES_encrypt()` | texto, clave | bits | API de cifrado |
| `DES_decrypt()` | bits, clave | bits | API de descifrado |

---

**Nota:** Este documento describe la implementación educativa de DES. No usar en producción para datos sensibles.
