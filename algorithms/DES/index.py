from .constants import IP, IP_INV, E, P, S_BOXES, PC1, PC2, SHIFT_SCHEDULE
from algorithms.utils.index import (
    string_a_bits,
    xor_bits,
    rotacion_izquierda,
)


def permutar(bloque, tabla):
    return [bloque[i - 1] for i in tabla]


def generar_claves_ronda(clave):
    clave_56 = permutar(clave, PC1)
    C = clave_56[:28]
    D = clave_56[28:]

    claves_ronda = []

    for i in range(16):
        C = rotacion_izquierda(C, SHIFT_SCHEDULE[i])
        D = rotacion_izquierda(D, SHIFT_SCHEDULE[i])
        CD = C + D
        clave_ronda = permutar(CD, PC2)
        claves_ronda.append(clave_ronda)

    return claves_ronda


def sustitucion_sbox(bloque_48):
    resultado = []

    for i in range(8):
        fragmento = bloque_48[i * 6 : (i + 1) * 6]
        fila = (fragmento[0] << 1) | fragmento[5]
        columna = (
            (fragmento[1] << 3)
            | (fragmento[2] << 2)
            | (fragmento[3] << 1)
            | fragmento[4]
        )
        val = S_BOXES[i][fila][columna]
        for j in range(3, -1, -1):
            resultado.append((val >> j) & 1)

    return resultado


def funcion_feistel(derecha_32, clave_ronda):
    expandido = permutar(derecha_32, E)
    xoreado = xor_bits(expandido, clave_ronda)
    sustituido = sustitucion_sbox(xoreado)
    resultado = permutar(sustituido, P)
    return resultado


def des_cifrar_bloque(texto_plano_64, claves_ronda):
    permutado = permutar(texto_plano_64, IP)
    L = permutado[:32]
    R = permutado[32:]

    for i in range(16):
        R_antigua = R[:]
        R = xor_bits(L, funcion_feistel(R, claves_ronda[i]))
        L = R_antigua

    combinado = R + L
    texto_cifrado = permutar(combinado, IP_INV)
    return texto_cifrado


def DES_cifrar(texto_plano, clave):
    bits_texto_plano = string_a_bits(texto_plano)
    bits_clave = string_a_bits(clave)

    if len(bits_clave) < 64:
        bits_clave = bits_clave + [0] * (64 - len(bits_clave))

    relleno_necesario = (64 - (len(bits_texto_plano) % 64)) % 64
    bits_texto_plano = bits_texto_plano + [0] * relleno_necesario
    claves_ronda = generar_claves_ronda(bits_clave)
    bits_texto_cifrado = []

    for i in range(0, len(bits_texto_plano), 64):
        bloque = bits_texto_plano[i : i + 64]
        bloque_cifrado = des_cifrar_bloque(bloque, claves_ronda)
        bits_texto_cifrado.extend(bloque_cifrado)

    return bits_texto_cifrado


def DES_descifrar(bits_texto_cifrado, clave):
    bits_clave = string_a_bits(clave)

    if len(bits_clave) < 64:
        bits_clave = bits_clave + [0] * (64 - len(bits_clave))

    claves_ronda = generar_claves_ronda(bits_clave)
    claves_ronda = claves_ronda[::-1]
    bits_texto_plano = []
    for i in range(0, len(bits_texto_cifrado), 64):
        bloque = bits_texto_cifrado[i : i + 64]
        bloque_descifrado = des_cifrar_bloque(bloque, claves_ronda)
        bits_texto_plano.extend(bloque_descifrado)

    return bits_texto_plano
