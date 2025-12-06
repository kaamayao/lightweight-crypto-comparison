from .constants import SBOX, INV_SBOX, P_LAYER, INV_P_LAYER
from algorithms.utils.index import string_a_bits, bits_a_entero, entero_a_bits


def generar_claves_ronda(clave_80):
    registro_clave = bits_a_entero(clave_80)
    claves_ronda = []

    for i in range(1, 33):
        clave_ronda = (registro_clave >> 16) & 0xFFFFFFFFFFFFFFFF
        claves_ronda.append(clave_ronda)

        registro_clave = ((registro_clave << 61) | (registro_clave >> 19)) & (
            (1 << 80) - 1
        )

        nibble_superior = (registro_clave >> 76) & 0xF
        registro_clave = (registro_clave & 0x0FFFFFFFFFFFFFFFFFFFF) | (
            SBOX[nibble_superior] << 76
        )

        registro_clave ^= i << 15

    return claves_ronda


def aplicar_sbox(estado):
    resultado = 0
    for i in range(16):
        nibble = (estado >> (i * 4)) & 0xF
        resultado |= SBOX[nibble] << (i * 4)
    return resultado


def aplicar_sbox_inversa(estado):
    resultado = 0
    for i in range(16):
        nibble = (estado >> (i * 4)) & 0xF
        resultado |= INV_SBOX[nibble] << (i * 4)
    return resultado


def aplicar_permutacion(estado):
    resultado = 0
    for i in range(64):
        if (estado >> i) & 1:
            resultado |= 1 << P_LAYER[i]
    return resultado


def aplicar_permutacion_inversa(estado):
    resultado = 0
    for i in range(64):
        if (estado >> i) & 1:
            resultado |= 1 << INV_P_LAYER[i]
    return resultado


def present_cifrar_bloque(bloque_64, claves_ronda):
    estado = bits_a_entero(bloque_64)

    for i in range(31):
        estado ^= claves_ronda[i]
        estado = aplicar_sbox(estado)
        estado = aplicar_permutacion(estado)

    estado ^= claves_ronda[31]

    return entero_a_bits(estado, 64)


def present_descifrar_bloque(bloque_64, claves_ronda):
    estado = bits_a_entero(bloque_64)

    estado ^= claves_ronda[31]

    for i in range(30, -1, -1):
        estado = aplicar_permutacion_inversa(estado)
        estado = aplicar_sbox_inversa(estado)
        estado ^= claves_ronda[i]

    return entero_a_bits(estado, 64)


def PRESENT_cifrar(texto_plano, clave):
    bits_texto_plano = string_a_bits(texto_plano)

    bits_clave = string_a_bits(clave)
    if len(bits_clave) < 80:
        bits_clave = bits_clave + [0] * (80 - len(bits_clave))

    relleno_necesario = (64 - (len(bits_texto_plano) % 64)) % 64
    bits_texto_plano = bits_texto_plano + [0] * relleno_necesario

    claves_ronda = generar_claves_ronda(bits_clave)

    bits_texto_cifrado = []
    for i in range(0, len(bits_texto_plano), 64):
        bloque = bits_texto_plano[i: i + 64]
        bloque_cifrado = present_cifrar_bloque(bloque, claves_ronda)
        bits_texto_cifrado.extend(bloque_cifrado)

    return bits_texto_cifrado


def PRESENT_descifrar(bits_texto_cifrado, clave):
    bits_clave = string_a_bits(clave)
    if len(bits_clave) < 80:
        bits_clave = bits_clave + [0] * (80 - len(bits_clave))

    claves_ronda = generar_claves_ronda(bits_clave)

    bits_texto_plano = []
    for i in range(0, len(bits_texto_cifrado), 64):
        bloque = bits_texto_cifrado[i: i + 64]
        bloque_descifrado = present_descifrar_bloque(bloque, claves_ronda)
        bits_texto_plano.extend(bloque_descifrado)

    return bits_texto_plano
