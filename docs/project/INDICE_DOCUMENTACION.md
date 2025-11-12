# Índice de Documentación Técnica

## Documentación de Algoritmos

Esta carpeta contiene documentación detallada de cada algoritmo de criptografía ligera implementado en el proyecto.

---

## 📚 Documentos Disponibles

### 1. [DES_DOCUMENTACION.md](./DES_DOCUMENTACION.md) (14 KB)

**Data Encryption Standard - Algoritmo Legado**

Documenta la implementación completa de DES, incluyendo:
- ✅ Arquitectura de red de Feistel (16 rondas)
- ✅ Generación de claves de ronda (PC1, PC2, rotaciones)
- ✅ Función F de Feistel (expansión E, S-Boxes, permutación P)
- ✅ Permutaciones inicial y final (IP, IP⁻¹)
- ✅ 7 funciones principales documentadas
- ✅ Ejemplos de uso y flujo de ejecución
- ✅ Consideraciones de seguridad

**Estructura:**
- Tamaño de bloque: 64 bits
- Tamaño de clave: 64 bits (56 bits efectivos)
- Rondas: 16
- Estado: ⚠️ Inseguro para uso moderno

**Funciones documentadas:**
1. `permute()` - Permutación genérica
2. `generate_round_keys()` - 16 claves de ronda
3. `s_box_substitution()` - 8 S-Boxes (6→4 bits)
4. `feistel_function()` - Función F
5. `des_encrypt_block()` - Cifrado de bloque
6. `DES_encrypt()` - API de cifrado
7. `DES_decrypt()` - API de descifrado

---

### 2. [AES_DOCUMENTACION.md](./AES_DOCUMENTACION.md) (19 KB)

**Advanced Encryption Standard - Estándar Actual**

Documentación completa de AES-128, incluyendo:
- ✅ Arquitectura SPN (Substitution-Permutation Network)
- ✅ Matemática de Campo de Galois GF(2⁸)
- ✅ Transformaciones de ronda (SubBytes, ShiftRows, MixColumns, AddRoundKey)
- ✅ Expansión de clave (KeyExpansion)
- ✅ 13 funciones principales documentadas
- ✅ Diagramas de flujo y ejemplos visuales
- ✅ Análisis de seguridad y rendimiento

**Estructura:**
- Tamaño de bloque: 128 bits (matriz 4×4)
- Tamaño de clave: 128 bits
- Rondas: 10
- Estado: ✅ Seguro, estándar actual

**Funciones documentadas:**
1. `gmul()` - Multiplicación en GF(2⁸)
2. `sub_bytes()` - S-Box (8→8 bits)
3. `inv_sub_bytes()` - S-Box inversa
4. `shift_rows()` - Rotación de filas
5. `inv_shift_rows()` - Rotación inversa
6. `mix_columns()` - Mezcla con matriz MDS
7. `inv_mix_columns()` - Mezcla inversa
8. `add_round_key()` - XOR con clave de ronda
9. `key_expansion()` - Genera 11 claves de ronda
10. `bytes_to_state()` - Conversión a matriz
11. `state_to_bytes()` - Conversión a bytes
12. `aes_encrypt_block()` - Cifrado de bloque
13. `AES_encrypt()` / `AES_decrypt()` - APIs

**Sección especial:** Matemáticas de Campo de Galois explicadas en detalle

---

### 3. [PRESENT_DOCUMENTACION.md](./PRESENT_DOCUMENTACION.md) (19 KB)

**PRESENT - Cifrado Ultra-Ligero para Hardware**

Documentación exhaustiva de PRESENT-80, incluyendo:
- ✅ Diseño optimizado para hardware (~1570 GE)
- ✅ Arquitectura SPN simplificada (31 rondas)
- ✅ S-Box de 4 bits (vs 8 bits en AES)
- ✅ Permutación de bits de costo cero
- ✅ 9 funciones principales documentadas
- ✅ Análisis comparativo con DES y AES
- ✅ Casos de uso en IoT/RFID

**Estructura:**
- Tamaño de bloque: 64 bits
- Tamaño de clave: 80 bits
- Rondas: 31
- Estado: ✅ Seguro para IoT/RFID

**Funciones documentadas:**
1. `generate_round_keys()` - 32 claves de ronda
2. `sbox_layer()` - 16 S-Boxes de 4 bits
3. `inv_sbox_layer()` - S-Box inversa
4. `pbox_layer()` - Permutación de bits
5. `inv_pbox_layer()` - Permutación inversa
6. `add_round_key()` - XOR con clave
7. `present_encrypt_block()` - Cifrado de bloque
8. `present_decrypt_block()` - Descifrado
9. `PRESENT_encrypt()` / `PRESENT_decrypt()` - APIs

**Sección especial:** Diseño para hardware ligero con desglose de compuertas

---

## 📊 Comparación Rápida

| Algoritmo | Tamaño Doc | Bloque | Clave | Rondas | Mejor para |
|-----------|-----------|--------|-------|--------|------------|
| **DES** | 14 KB | 64 bits | 56 bits | 16 | Educación/Legacy |
| **AES-128** | 19 KB | 128 bits | 128 bits | 10 | Software general |
| **PRESENT-80** | 19 KB | 64 bits | 80 bits | 31 | Hardware IoT |

---

## 🎯 Cómo Usar Esta Documentación

### Para Estudiantes

1. **Comenzar con DES** - Más simple, concepto de Feistel claro
2. **Continuar con AES** - Entender SPN y matemática moderna
3. **Finalizar con PRESENT** - Ver optimizaciones para hardware

### Para Desarrolladores

1. **Buscar la función específica** en el índice de cada documento
2. **Revisar ejemplos de uso** al final de cada documento
3. **Consultar consideraciones de seguridad** antes de implementar

### Para Investigadores

1. **Comparar arquitecturas** entre los tres algoritmos
2. **Analizar complejidad** en secciones dedicadas
3. **Revisar referencias** académicas citadas

---

## 🔍 Estructura de Cada Documento

Todos los documentos siguen esta estructura:

1. **Descripción General**
   - Características principales
   - Componentes clave
   - Comparación con otros algoritmos

2. **Arquitectura del Algoritmo**
   - Diagramas de flujo
   - Estructura de rondas
   - Diseño general

3. **Funciones Documentadas**
   - Cada función con:
     - Propósito
     - Parámetros
     - Retorno
     - Proceso detallado
     - Ejemplos
     - Uso en el algoritmo

4. **Flujo de Ejecución**
   - Cifrado completo paso a paso
   - Descifrado completo
   - Diagramas visuales

5. **Ejemplo de Uso**
   - Código funcional
   - Casos de uso típicos
   - Manejo de errores

6. **Consideraciones**
   - Seguridad
   - Rendimiento
   - Casos de uso apropiados

7. **Referencias**
   - Papers académicos
   - Estándares (FIPS, ISO)
   - Recursos adicionales

---

## 📖 Convenciones de Documentación

### Símbolos Usados

- ✅ - Característica o ventaja
- ❌ - Desventaja o no recomendado
- ⚠️ - Advertencia o consideración importante
- 🔧 - Implementación o detalle técnico
- 📊 - Comparación o tabla
- 🔍 - Ejemplo o caso de estudio

### Notación Matemática

- `⊕` - XOR (OR exclusivo)
- `∧` - AND
- `∨` - OR
- `¬` - NOT
- `x^i` - x elevado a la potencia i
- `[a, b, c]` - Lista o array
- `{a, b, c}` - Conjunto

### Formato de Código

```python
# Comentarios explican el propósito
def funcion_ejemplo(entrada):
    """Docstring describe la función"""
    resultado = procesar(entrada)
    return resultado  # Comentario inline
```

---

## 🔗 Enlaces Útiles

### Dentro del Proyecto

- [LEEME.md](../LEEME.md) - README principal
- [GUIA_RAPIDA_DOCKER.md](../GUIA_RAPIDA_DOCKER.md) - Guía Docker
- [GUIA_SIMULACION_DISPOSITIVOS_LIMITADOS.md](../GUIA_SIMULACION_DISPOSITIVOS_LIMITADOS.md) - Simulación
- [refList.md](./refList.md) - Referencias académicas

### Código Fuente

- [algorithms/DES/index.py](../algorithms/DES/index.py) - Implementación DES
- [algorithms/AES/index.py](../algorithms/AES/index.py) - Implementación AES
- [algorithms/PRESENT/index.py](../algorithms/PRESENT/index.py) - Implementación PRESENT

---

## 📝 Notas de Versión

**Versión 1.0** (2025-11-11)
- Documentación inicial completa de DES
- Documentación inicial completa de AES-128
- Documentación inicial completa de PRESENT-80
- Incluye diagramas, ejemplos y análisis comparativo

---

## 🤝 Contribuir a la Documentación

Si encuentras errores o quieres mejorar la documentación:

1. Revisa el código fuente correspondiente
2. Verifica las referencias académicas
3. Sigue el formato establecido
4. Incluye ejemplos claros
5. Añade diagramas si es posible

---

## ❓ Preguntas Frecuentes

### ¿Cuál documento leer primero?

Depende de tu objetivo:
- **Aprendizaje:** DES → AES → PRESENT
- **Uso práctico:** AES (para software) o PRESENT (para hardware)
- **Investigación:** Los tres para comparación

### ¿Necesito saber matemáticas avanzadas?

- **DES:** No, operaciones básicas de bits
- **AES:** Sí, Campo de Galois GF(2⁸) - explicado en detalle
- **PRESENT:** No, operaciones simples

### ¿Los ejemplos son funcionales?

Sí, todos los ejemplos de código son funcionales y pueden ejecutarse con las implementaciones del proyecto.

### ¿Puedo usar estas implementaciones en producción?

**NO.** Son implementaciones educativas. Para producción usar:
- Python: `cryptography`, `pycryptodome`
- C/C++: OpenSSL, libsodium
- Hardware: Cores verificados

---

## 📊 Estadísticas de Documentación

| Métrica | Valor |
|---------|-------|
| Total de páginas | ~52 páginas (impreso) |
| Total de palabras | ~24,000 palabras |
| Funciones documentadas | 29 funciones |
| Ejemplos de código | 45+ ejemplos |
| Diagramas/tablas | 60+ visualizaciones |
| Referencias | 15+ papers/estándares |

---

## 📧 Contacto

Para preguntas sobre la documentación técnica:
- Abrir issue en el repositorio
- Revisar código fuente en `algorithms/`
- Consultar referencias académicas en cada documento

---

**Última actualización:** 2025-11-11
**Idioma:** Español
**Formato:** Markdown
**Licencia:** [Especificar]

---

## Índice Alfabético de Funciones

### DES
- `DES_decrypt()` - DES_DOCUMENTACION.md
- `DES_encrypt()` - DES_DOCUMENTACION.md
- `des_encrypt_block()` - DES_DOCUMENTACION.md
- `feistel_function()` - DES_DOCUMENTACION.md
- `generate_round_keys()` - DES_DOCUMENTACION.md
- `permute()` - DES_DOCUMENTACION.md
- `s_box_substitution()` - DES_DOCUMENTACION.md

### AES
- `add_round_key()` - AES_DOCUMENTACION.md
- `AES_decrypt()` - AES_DOCUMENTACION.md
- `AES_encrypt()` - AES_DOCUMENTACION.md
- `aes_decrypt_block()` - AES_DOCUMENTACION.md
- `aes_encrypt_block()` - AES_DOCUMENTACION.md
- `bytes_to_state()` - AES_DOCUMENTACION.md
- `gmul()` - AES_DOCUMENTACION.md
- `inv_mix_columns()` - AES_DOCUMENTACION.md
- `inv_shift_rows()` - AES_DOCUMENTACION.md
- `inv_sub_bytes()` - AES_DOCUMENTACION.md
- `key_expansion()` - AES_DOCUMENTACION.md
- `mix_columns()` - AES_DOCUMENTACION.md
- `shift_rows()` - AES_DOCUMENTACION.md
- `state_to_bytes()` - AES_DOCUMENTACION.md
- `sub_bytes()` - AES_DOCUMENTACION.md

### PRESENT
- `add_round_key()` - PRESENT_DOCUMENTACION.md
- `generate_round_keys()` - PRESENT_DOCUMENTACION.md
- `inv_pbox_layer()` - PRESENT_DOCUMENTACION.md
- `inv_sbox_layer()` - PRESENT_DOCUMENTACION.md
- `pbox_layer()` - PRESENT_DOCUMENTACION.md
- `PRESENT_decrypt()` - PRESENT_DOCUMENTACION.md
- `PRESENT_encrypt()` - PRESENT_DOCUMENTACION.md
- `present_decrypt_block()` - PRESENT_DOCUMENTACION.md
- `present_encrypt_block()` - PRESENT_DOCUMENTACION.md
- `sbox_layer()` - PRESENT_DOCUMENTACION.md

---

**Total:** 29 funciones documentadas
