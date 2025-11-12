# Documentación del Algoritmo AES-128 (Advanced Encryption Standard)

## Índice
1. [Descripción General](#descripción-general)
2. [Arquitectura del Algoritmo](#arquitectura-del-algoritmo)
3. [Funciones Documentadas](#funciones-documentadas)
4. [Matemáticas: Campo de Galois GF(2⁸)](#matemáticas-campo-de-galois-gf28)
5. [Flujo de Ejecución](#flujo-de-ejecución)
6. [Ejemplo de Uso](#ejemplo-de-uso)
7. [Referencias](#referencias)

---

## Descripción General

**AES (Advanced Encryption Standard)** es el estándar de cifrado simétrico moderno adoptado por NIST en 2001. Opera en bloques de 128 bits y usa una **red de sustitución-permutación** (SPN) en lugar de la red de Feistel de DES.

### Características Principales

- **Tamaño de Bloque:** 128 bits (16 bytes)
- **Tamaño de Clave:** 128, 192 o 256 bits (esta implementación: 128 bits)
- **Número de Rondas:** 10 (para AES-128)
- **Tipo:** Red de Sustitución-Permutación (SPN)
- **Estado Actual:** Estándar actual, considerado seguro

### Componentes Clave

1. **SubBytes** - Sustitución no lineal (S-Box)
2. **ShiftRows** - Permutación de filas
3. **MixColumns** - Difusión usando aritmética de campo de Galois
4. **AddRoundKey** - XOR con clave de ronda
5. **KeyExpansion** - Generación de 11 claves de ronda

### Ventajas sobre DES

✅ **Mayor seguridad** - 128 bits vs 56 bits
✅ **Más rápido** - Diseño moderno optimizable
✅ **Estructura elegante** - Matemática de campo de Galois
✅ **Aceleración hardware** - Instrucciones AES-NI en CPUs modernas
✅ **Sin backdoors conocidos** - Diseño transparente

---

## Arquitectura del Algoritmo

### Estructura de Estado (State Matrix)

AES opera en una matriz de estado 4×4 bytes:

```
    Columna
    0  1  2  3
F  [a0 a4 a8 ac]
i  [a1 a5 a9 ad]
l  [a2 a6 aa ae]
a  [a3 a7 ab af]
```

**Nota Importante:** Los bytes se organizan en **orden de columnas**, no filas.

### Flujo de Cifrado (10 Rondas)

```
Texto Plano (16 bytes)
         ↓
   [bytes_to_state]  Convertir a matriz 4×4
         ↓
   [AddRoundKey(K₀)]  Ronda inicial
         ↓
┌─────────────────────┐
│  Rondas 1-9:        │
│  1. SubBytes        │  ← Confusión (S-Box)
│  2. ShiftRows       │  ← Difusión (permutación)
│  3. MixColumns      │  ← Difusión (GF)
│  4. AddRoundKey(Kᵢ) │  ← Mezcla con clave
└─────────────────────┘
         ↓
  Ronda 10 (final):
  1. SubBytes
  2. ShiftRows
  3. AddRoundKey(K₁₀)  ← ¡Sin MixColumns!
         ↓
   [state_to_bytes]  Convertir a 16 bytes
         ↓
   Texto Cifrado
```

---

## Funciones Documentadas

### 1. `gmul(a, b)`

**Propósito:** Multiplicación en Campo de Galois GF(2⁸) para AES.

**Parámetros:**
- `a` (int): Primer operando (0-255)
- `b` (int): Segundo operando (0-255)

**Retorna:** Producto en GF(2⁸)

**Algoritmo (Peasant Multiplication):**
```python
p = 0
for cada bit en b:
    if bit es 1:
        p = p ⊕ a

    # Multiplicar a por x (shift left)
    if a >= 0x80:  # Si bit alto está set
        a = (a << 1) ⊕ 0x1B  # Reducir módulo polinomio
    else:
        a = a << 1

    b = b >> 1  # Siguiente bit

return p & 0xFF
```

**Polinomio Irreducible:** `m(x) = x⁸ + x⁴ + x³ + x + 1 = 0x11B`

**Ejemplos:**
```python
gmul(0x02, 0x87) → 0x15  # Multiplicar por 2
gmul(0x03, 0x6E) → 0xFB  # Multiplicar por 3
gmul(0x01, 0xFF) → 0xFF  # Identidad
gmul(0x00, 0xFF) → 0x00  # Anulador
```

**Uso en AES:**
- `MixColumns` usa `gmul(0x02, ...)` y `gmul(0x03, ...)`
- `InvMixColumns` usa `gmul(0x09, ...)`, `gmul(0x0B, ...)`, `gmul(0x0D, ...)`, `gmul(0x0E, ...)`

---

### 2. `sub_bytes(state)`

**Propósito:** Aplicar sustitución S-Box a cada byte del estado.

**Parámetros:**
- `state` (list[list]): Matriz 4×4 de bytes

**Retorna:** Nueva matriz 4×4 con bytes sustituidos

**Proceso:**
```python
for cada byte en state:
    nuevo_byte = SBOX[byte]
```

**La S-Box:**
- Tabla de lookup de 256 elementos (16×16)
- Proporciona **confusión** (no linealidad)
- Calculada usando inversión en GF(2⁸) + transformación afín
- Resistente a criptoanálisis diferencial y lineal

**Ejemplo:**
```python
state = [
    [0x19, 0xa0, 0x9a, 0xe9],
    [0x3d, 0xf4, 0xc6, 0xf8],
    ...
]

new_state = sub_bytes(state)
# 0x19 → SBOX[0x19] = 0xd4
# 0xa0 → SBOX[0xa0] = 0xe9
# etc.
```

**Propiedades de la S-Box:**
- Biyectiva (uno a uno)
- Sin puntos fijos: SBOX[x] ≠ x para todo x
- Alta no linealidad

---

### 3. `inv_sub_bytes(state)`

**Propósito:** Aplicar S-Box inversa (para descifrado).

**Parámetros:**
- `state` (list[list]): Matriz 4×4 de bytes

**Retorna:** Matriz 4×4 con sustitución inversa

**Relación:**
```python
inv_sub_bytes(sub_bytes(state)) == state
```

**Uso:** Solo en descifrado.

---

### 4. `shift_rows(state)`

**Propósito:** Rotación circular de filas para difusión.

**Proceso:**
```
Fila 0: No rotar     [a b c d] → [a b c d]
Fila 1: Rotar 1      [a b c d] → [b c d a]
Fila 2: Rotar 2      [a b c d] → [c d a b]
Fila 3: Rotar 3      [a b c d] → [d a b c]
```

**Ejemplo Visual:**
```
ANTES:              DESPUÉS:
[00 04 08 0c]       [00 04 08 0c]  Fila 0: sin cambio
[01 05 09 0d]       [05 09 0d 01]  Fila 1: shift 1
[02 06 0a 0e]   →   [0a 0e 02 06]  Fila 2: shift 2
[03 07 0b 0f]       [0f 03 07 0b]  Fila 3: shift 3
```

**Propósito:**
- Proporcionar **difusión** entre columnas
- Combinar con MixColumns para difusión completa en 2 rondas

**Código:**
```python
[
    state[0],              # Fila 0: sin cambio
    state[1][1:] + state[1][:1],   # Fila 1: rotar 1
    state[2][2:] + state[2][:2],   # Fila 2: rotar 2
    state[3][3:] + state[3][:3],   # Fila 3: rotar 3
]
```

---

### 5. `inv_shift_rows(state)`

**Propósito:** Rotación inversa (rotación a la derecha).

**Proceso:**
```
Fila 0: No rotar     [a b c d] → [a b c d]
Fila 1: Rotar -1     [a b c d] → [d a b c]
Fila 2: Rotar -2     [a b c d] → [c d a b]
Fila 3: Rotar -3     [a b c d] → [b c d a]
```

---

### 6. `mix_columns(state)`

**Propósito:** Mezclar columnas usando multiplicación en GF(2⁸).

**Proceso:**
Cada columna se multiplica por una matriz fija en GF(2⁸):

```
[02 03 01 01]   [s₀]   [s'₀]
[01 02 03 01] × [s₁] = [s'₁]
[01 01 02 03]   [s₂]   [s'₂]
[03 01 01 02]   [s₃]   [s'₃]
```

**Código (columna i):**
```python
result[0][i] = gmul(0x02, s[0][i]) ⊕ gmul(0x03, s[1][i]) ⊕ s[2][i] ⊕ s[3][i]
result[1][i] = s[0][i] ⊕ gmul(0x02, s[1][i]) ⊕ gmul(0x03, s[2][i]) ⊕ s[3][i]
result[2][i] = s[0][i] ⊕ s[1][i] ⊕ gmul(0x02, s[2][i]) ⊕ gmul(0x03, s[3][i])
result[3][i] = gmul(0x03, s[0][i]) ⊕ s[1][i] ⊕ s[2][i] ⊕ gmul(0x02, s[3][i])
```

**Propiedades:**
- **MDS (Maximum Distance Separable)**: Máxima difusión
- Cada byte de salida depende de todos los bytes de entrada de la columna
- Reversible (matriz invertible en GF(2⁸))

**Ejemplo:**
```python
columna = [0xdb, 0x13, 0x53, 0x45]

# Aplicar MixColumns
nueva_columna = [0x8e, 0x4d, 0xa1, 0xbc]
```

---

### 7. `inv_mix_columns(state)`

**Propósito:** MixColumns inversa (para descifrado).

**Matriz Inversa:**
```
[0e 0b 0d 09]
[09 0e 0b 0d]
[0d 09 0e 0b]
[0b 0d 09 0e]
```

**Relación:**
```python
inv_mix_columns(mix_columns(state)) == state
```

---

### 8. `add_round_key(state, round_key)`

**Propósito:** XOR del estado con la clave de ronda.

**Parámetros:**
- `state` (list[list]): Matriz 4×4 del estado
- `round_key` (list[list]): Matriz 4×4 de la clave de ronda

**Retorna:** Nuevo estado

**Proceso:**
```python
for i in 0..3:
    for j in 0..3:
        state[i][j] = state[i][j] ⊕ round_key[i][j]
```

**Propiedades:**
- Operación reversible (XOR es su propia inversa)
- Mismo código para cifrado y descifrado
- Introduce la clave en el proceso

**Ejemplo:**
```
State:      Key:        Resultado:
[19 a0]  ⊕  [a0 88]  =  [b9 28]
[3d f4]  ⊕  [23 2a]  =  [1e de]
```

---

### 9. `key_expansion(key)`

**Propósito:** Expandir clave de 128 bits a 11 claves de ronda.

**Parámetros:**
- `key` (list): 16 bytes de la clave maestra

**Retorna:** Lista de 11 matrices 4×4 (claves de ronda)

**Proceso:**

```python
# Paso 1: Dividir clave en 4 words (W[0] a W[3])
W[0] = [key[0], key[1], key[2], key[3]]
W[1] = [key[4], key[5], key[6], key[7]]
W[2] = [key[8], key[9], key[10], key[11]]
W[3] = [key[12], key[13], key[14], key[15]]

# Paso 2: Generar W[4] a W[43] (total: 44 words)
for i in 4..43:
    temp = W[i-1]

    if i % 4 == 0:
        # Aplicar transformación g()
        temp = RotWord(temp)      # Rotar [a,b,c,d] → [b,c,d,a]
        temp = SubWord(temp)      # Aplicar S-Box a cada byte
        temp[0] ^= RCON[i/4]      # XOR con constante de ronda

    W[i] = W[i-4] ⊕ temp

# Paso 3: Agrupar en 11 claves de ronda
RoundKey[i] = [W[4i], W[4i+1], W[4i+2], W[4i+3]]
```

**RCON (Round Constants):**
```python
RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
```

Calculados como: `RCON[i] = x^(i-1)` en GF(2⁸)

**Ejemplo Visual:**
```
Clave Maestra (16 bytes):
[2b 7e 15 16 28 ae d2 a6 ab f7 15 88 09 cf 4f 3c]

Word 0: [2b 7e 15 16]
Word 1: [28 ae d2 a6]
Word 2: [ab f7 15 88]
Word 3: [09 cf 4f 3c]

Word 4 = Word 0 ⊕ g(Word 3)
       = [2b 7e 15 16] ⊕ g([09 cf 4f 3c])
       = [2b 7e 15 16] ⊕ [8a 84 eb 01]
       = [a1 fa fe 17]

...continúa hasta Word 43
```

---

### 10. `bytes_to_state(block)` y `state_to_bytes(state)`

**Propósito:** Conversión entre representación lineal y matricial.

**bytes_to_state:**
```python
# Entrada: [b0, b1, b2, ..., b15]
# Salida: Matriz 4×4 en orden de COLUMNAS

    Col 0  Col 1  Col 2  Col 3
[  [ b0,    b4,    b8,    b12 ],  # Fila 0
   [ b1,    b5,    b9,    b13 ],  # Fila 1
   [ b2,    b6,    b10,   b14 ],  # Fila 2
   [ b3,    b7,    b11,   b15 ]   # Fila 3
]
```

**state_to_bytes:**
Proceso inverso, lee columna por columna.

**⚠️ Importante:** AES usa **orden de columnas**, no filas.

---

### 11. `aes_encrypt_block(block, round_keys)`

**Propósito:** Cifrar un bloque de 16 bytes.

**Parámetros:**
- `block` (list): 16 bytes de texto plano
- `round_keys` (list): 11 claves de ronda

**Retorna:** 16 bytes cifrados

**Algoritmo Completo:**

```python
state = bytes_to_state(block)

# Ronda Inicial
state = add_round_key(state, round_keys[0])

# Rondas 1-9
for round in 1..9:
    state = sub_bytes(state)
    state = shift_rows(state)
    state = mix_columns(state)      # ← Difusión completa
    state = add_round_key(state, round_keys[round])

# Ronda Final (10)
state = sub_bytes(state)
state = shift_rows(state)
# ¡Sin MixColumns en ronda final!
state = add_round_key(state, round_keys[10])

return state_to_bytes(state)
```

**¿Por qué sin MixColumns en la ronda final?**
- Para que cifrado y descifrado sean simétricos
- MixColumns no añade seguridad después de la última AddRoundKey

---

### 12. `aes_decrypt_block(block, round_keys)`

**Propósito:** Descifrar un bloque de 16 bytes.

**Proceso:**
Aplicar transformaciones inversas en orden inverso.

```python
state = bytes_to_state(block)

# Ronda Final Inversa
state = add_round_key(state, round_keys[10])
state = inv_shift_rows(state)
state = inv_sub_bytes(state)

# Rondas 9-1 (orden inverso)
for round in 9..1 (decreciente):
    state = add_round_key(state, round_keys[round])
    state = inv_mix_columns(state)
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)

# Ronda Inicial
state = add_round_key(state, round_keys[0])

return state_to_bytes(state)
```

**Orden de Operaciones:**
```
Cifrado:        Descifrado:
SubBytes        InvSubBytes
ShiftRows   →   InvShiftRows
MixColumns      InvMixColumns
AddRoundKey     AddRoundKey
```

---

### 13. `AES_encrypt(plaintext, key)` y `AES_decrypt(ciphertext, key)`

**Propósito:** APIs de alto nivel para cifrar/descifrar.

**Características:**
- ✅ Acepta strings o listas de bytes
- ✅ Validación de tamaño de clave (debe ser 16 bytes)
- ✅ Padding automático a múltiplo de 16 bytes
- ✅ Maneja múltiples bloques

**Ejemplo:**
```python
plaintext = "Hello AES World!"  # 16 bytes exactos
key = "my128bitkey12345"       # 16 bytes

ciphertext = AES_encrypt(plaintext, key)
plaintext = AES_decrypt(ciphertext, key)
```

---

## Matemáticas: Campo de Galois GF(2⁸)

### ¿Qué es GF(2⁸)?

Un **Campo de Galois** es un conjunto finito con operaciones de suma y multiplicación que cumplen propiedades de campo.

**GF(2⁸)** contiene 256 elementos: {0, 1, 2, ..., 255}

### Operaciones

**Suma:** XOR bit a bit
```
0x57 ⊕ 0x83 = 0xD4
01010111
⊕10000011
=========
11010100
```

**Multiplicación:** Producto con reducción módulo polinomio irreducible

**Polinomio Irreducible de AES:**
```
m(x) = x⁸ + x⁴ + x³ + x + 1
     = 0x11B
```

### Ejemplo de Multiplicación

```
gmul(0x57, 0x83):

Representación polinomial:
0x57 = x⁶ + x⁴ + x² + x + 1
0x83 = x⁷ + x + 1

Producto (antes de reducir):
x¹³ + x¹¹ + x⁹ + x⁸ + x⁷ + ... (grado > 7)

Reducir módulo m(x):
Resultado final en GF(2⁸)
```

### Propiedades Importantes

1. **Elemento neutro multiplicativo:** 1
2. **Todo elemento ≠ 0 tiene inverso**
3. **No hay divisores de cero**
4. **Orden del campo:** 256

### Uso en AES

- **MixColumns:** Multiplicación matricial en GF(2⁸)
- **S-Box:** Inversión en GF(2⁸) + transformación afín
- **Garantiza:** Difusión matemática rigurosa

---

## Flujo de Ejecución

### Cifrado Completo

```
"Hello AES World!" (16 bytes)
         ↓
   [string_to_bytes]
    [72,101,108,108,111,32,65,69,83,32,87,111,114,108,100,33]
         ↓
   [key_expansion]
    K₀, K₁, K₂, ..., K₁₀
         ↓
   [bytes_to_state]
    Matriz 4×4
         ↓
   [AddRoundKey(K₀)]
         ↓
   Ronda 1:
    [SubBytes → ShiftRows → MixColumns → AddRoundKey(K₁)]
         ↓
   Ronda 2:
    [SubBytes → ShiftRows → MixColumns → AddRoundKey(K₂)]
         ↓
    ... (Rondas 3-9)
         ↓
   Ronda 10:
    [SubBytes → ShiftRows → AddRoundKey(K₁₀)]
         ↓
   [state_to_bytes]
         ↓
   Texto Cifrado (16 bytes)
```

---

## Ejemplo de Uso

### Ejemplo Básico

```python
from algorithms.AES.index import AES_encrypt, AES_decrypt
from utils.index import bytes_to_string

# Cifrado
plaintext = "Top Secret Data!"
key = "MySecretKey12345"  # Exactamente 16 caracteres

ciphertext = AES_encrypt(plaintext, key)
print(f"Cifrado: {' '.join(f'{b:02x}' for b in ciphertext)}")

# Descifrado
decrypted = AES_decrypt(ciphertext, key)
print(f"Descifrado: {bytes_to_string(decrypted)}")
```

### Ejemplo con Mensajes Largos

```python
# Mensaje largo (más de 16 bytes)
long_message = "Este es un mensaje mucho más largo que requiere múltiples bloques de AES para cifrarse completamente."
key = "1234567890123456"

# AES divide automáticamente en bloques
ciphertext = AES_encrypt(long_message, key)
decrypted = bytes_to_string(AES_decrypt(ciphertext, key))
```

### Manejo de Errores

```python
try:
    # Clave incorrecta (no 16 bytes)
    AES_encrypt("data", "short")
except ValueError as e:
    print(f"Error: {e}")
    # Error: AES-128 requires a 16-byte (128-bit) key
```

---

## Consideraciones de Seguridad

### ✅ Fortalezas

1. **Clave de 128 bits** - 2¹²⁸ combinaciones (~10³⁸)
2. **Sin ataques prácticos conocidos** - Solo ataques teóricos
3. **Ampliamente analizado** - 20+ años de escrutinio
4. **Aceleración hardware** - AES-NI en procesadores modernos
5. **Diseño transparente** - Sin backdoors conocidos

### ⚠️ Consideraciones de Implementación

1. **Modo de Operación**
   - Esta implementación: ECB (no seguro para producción)
   - Usar: CBC, CTR, GCM en producción

2. **Padding**
   - Esta implementación: Zero padding
   - Producción: PKCS#7 o similar

3. **Protección contra Side-Channel**
   - Implementación constante en tiempo
   - Protección contra cache-timing attacks

### 🔒 Uso en Producción

```python
# ❌ NO hacer (esta implementación)
ciphertext = AES_encrypt(plaintext, key)

# ✅ SÍ hacer (biblioteca confiable)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
```

---

## Complejidad Computacional

### Tiempo de Ejecución

| Operación | Complejidad | Notas |
|-----------|-------------|-------|
| SubBytes | O(1) | Lookup table |
| ShiftRows | O(1) | Permutación simple |
| MixColumns | O(1) | 16 gmul fijas |
| AddRoundKey | O(1) | 16 XORs |
| KeyExpansion | O(1) | 44 words fijas |
| Cifrado de bloque | O(1) | 10 rondas fijas |
| Cifrado completo | O(n) | n = bloques |

### Uso de Memoria

- **Claves de ronda:** 11 × 16 bytes = 176 bytes
- **Estado:** 16 bytes
- **S-Box + Inv S-Box:** 2 × 256 bytes = 512 bytes
- **RCON:** 11 bytes
- **Total:** ~700 bytes

---

## Comparación AES vs DES

| Característica | DES | AES-128 |
|----------------|-----|---------|
| Tamaño de bloque | 64 bits | 128 bits |
| Tamaño de clave | 56 bits | 128 bits |
| Rondas | 16 | 10 |
| Estructura | Feistel | SPN |
| Seguridad | ❌ Roto | ✅ Seguro |
| Velocidad (SW) | Moderada | Rápida |
| Aceleración HW | Rara | Común (AES-NI) |
| Año | 1977 | 2001 |

---

## Preguntas Frecuentes

### ¿Por qué AES usa GF(2⁸)?

Proporciona propiedades matemáticas rigurosas para difusión óptima (código MDS).

### ¿Por qué la ronda final no tiene MixColumns?

Para simetría entre cifrado y descifrado. No reduce seguridad.

### ¿AES es resistente a computación cuántica?

AES-128: Vulnerable (reduce a ~64 bits con Grover).
**Solución:** Usar AES-256 (seguridad ~128 bits post-cuántica).

### ¿Puedo usar esta implementación en producción?

**NO.** Es educativa. Usa bibliotecas probadas como:
- `cryptography` (Python)
- OpenSSL
- Libsodium

---

## Referencias

1. **FIPS PUB 197** - Advanced Encryption Standard (AES)
2. **The Design of Rijndael** - Daemen & Rijmen
3. **A Stick Figure Guide to AES** - Explicación visual
4. **NIST SP 800-38A** - Modos de operación
5. **Intel AES-NI** - Documentación de instrucciones

---

## Resumen de Funciones

| Función | Entrada | Salida | Ronda | Propósito |
|---------|---------|--------|-------|-----------|
| `gmul()` | 2 bytes | 1 byte | Helper | Multiplicación GF(2⁸) |
| `sub_bytes()` | State 4×4 | State 4×4 | 1-10 | Confusión (S-Box) |
| `shift_rows()` | State 4×4 | State 4×4 | 1-10 | Difusión (permutación) |
| `mix_columns()` | State 4×4 | State 4×4 | 1-9 | Difusión (GF) |
| `add_round_key()` | State, Key | State | 0-10 | Mezcla con clave |
| `key_expansion()` | 16 bytes | 11 Keys | Setup | Generar subclaves |
| `aes_encrypt_block()` | 16 bytes | 16 bytes | - | Cifrar bloque |
| `AES_encrypt()` | texto, clave | bytes | - | API cifrado |
| `AES_decrypt()` | bytes, clave | bytes | - | API descifrado |

---

**Nota:** Esta es una implementación educativa de AES-128. Para aplicaciones de producción, usar bibliotecas criptográficas auditadas y probadas.
