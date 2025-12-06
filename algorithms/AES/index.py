from .constants import SBOX, INV_SBOX, RCON
from algorithms.utils.index import string_a_bytes


def agregar_clave_ronda(estado, clave_ronda):
    return [[estado[i][j] ^ clave_ronda[i][j] for j in range(4)] for i in range(4)]


def expansion_clave(clave):
    palabras_clave = []
    for i in range(0, 16, 4):
        palabras_clave.append(
            [clave[i], clave[i + 1], clave[i + 2], clave[i + 3]])

    for i in range(4, 44):
        temp = palabras_clave[i - 1][:]
        if i % 4 == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            temp[0] ^= RCON[i // 4]
        palabras_clave.append(
            [palabras_clave[i - 4][j] ^ temp[j] for j in range(4)])

    claves_ronda = []
    for i in range(0, 44, 4):
        claves_ronda.append(
            [
                [
                    palabras_clave[i][j],
                    palabras_clave[i + 1][j],
                    palabras_clave[i + 2][j],
                    palabras_clave[i + 3][j],
                ]
                for j in range(4)
            ]
        )
    return claves_ronda


def bytes_a_estado(bloque):
    return [[bloque[i + 4 * j] for j in range(4)] for i in range(4)]


def estado_a_bytes(estado):
    return [estado[i][j] for j in range(4) for i in range(4)]


def multiplicar_galois(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        bit_alto_set = a & 0x80
        a <<= 1
        if bit_alto_set:
            a ^= 0x1B
        b >>= 1
    return p & 0xFF


# Funciones de desencriptación


def aes_descifrar_bloque(bloque, claves_ronda):
    estado = bytes_a_estado(bloque)
    estado = agregar_clave_ronda(estado, claves_ronda[10])

    for num_ronda in range(9, 0, -1):
        estado = desplazar_filas_inverso(estado)
        estado = sub_bytes_inverso(estado)
        estado = agregar_clave_ronda(estado, claves_ronda[num_ronda])
        estado = mezclar_columnas_inverso(estado)

    estado = desplazar_filas_inverso(estado)
    estado = sub_bytes_inverso(estado)
    estado = agregar_clave_ronda(estado, claves_ronda[0])

    return estado_a_bytes(estado)


def sub_bytes_inverso(estado):
    return [[INV_SBOX[byte] for byte in fila] for fila in estado]


def mezclar_columnas_inverso(estado):
    resultado = [[0] * 4 for _ in range(4)]
    for i in range(4):
        resultado[0][i] = (
            multiplicar_galois(0x0E, estado[0][i])
            ^ multiplicar_galois(0x0B, estado[1][i])
            ^ multiplicar_galois(0x0D, estado[2][i])
            ^ multiplicar_galois(0x09, estado[3][i])
        )
        resultado[1][i] = (
            multiplicar_galois(0x09, estado[0][i])
            ^ multiplicar_galois(0x0E, estado[1][i])
            ^ multiplicar_galois(0x0B, estado[2][i])
            ^ multiplicar_galois(0x0D, estado[3][i])
        )
        resultado[2][i] = (
            multiplicar_galois(0x0D, estado[0][i])
            ^ multiplicar_galois(0x09, estado[1][i])
            ^ multiplicar_galois(0x0E, estado[2][i])
            ^ multiplicar_galois(0x0B, estado[3][i])
        )
        resultado[3][i] = (
            multiplicar_galois(0x0B, estado[0][i])
            ^ multiplicar_galois(0x0D, estado[1][i])
            ^ multiplicar_galois(0x09, estado[2][i])
            ^ multiplicar_galois(0x0E, estado[3][i])
        )
    return resultado


def desplazar_filas_inverso(estado):
    return [
        estado[0],
        estado[1][-1:] + estado[1][:-1],
        estado[2][-2:] + estado[2][:-2],
        estado[3][-3:] + estado[3][:-3],
    ]


# Funciones de encriptación


def aes_cifrar_bloque(bloque, claves_ronda):
    estado = bytes_a_estado(bloque)
    estado = agregar_clave_ronda(estado, claves_ronda[0])

    for num_ronda in range(1, 10):
        estado = sub_bytes(estado)
        estado = desplazar_filas(estado)
        estado = mezclar_columnas(estado)
        estado = agregar_clave_ronda(estado, claves_ronda[num_ronda])

    estado = sub_bytes(estado)
    estado = desplazar_filas(estado)
    estado = agregar_clave_ronda(estado, claves_ronda[10])

    return estado_a_bytes(estado)


def sub_bytes(estado):
    return [[SBOX[byte] for byte in fila] for fila in estado]


def desplazar_filas(estado):
    return [
        estado[0],
        estado[1][1:] + estado[1][:1],
        estado[2][2:] + estado[2][:2],
        estado[3][3:] + estado[3][:3],
    ]


def mezclar_columnas(estado):
    resultado = [[0] * 4 for _ in range(4)]
    for i in range(4):
        resultado[0][i] = (
            multiplicar_galois(0x02, estado[0][i])
            ^ multiplicar_galois(0x03, estado[1][i])
            ^ estado[2][i]
            ^ estado[3][i]
        )
        resultado[1][i] = (
            estado[0][i]
            ^ multiplicar_galois(0x02, estado[1][i])
            ^ multiplicar_galois(0x03, estado[2][i])
            ^ estado[3][i]
        )
        resultado[2][i] = (
            estado[0][i]
            ^ estado[1][i]
            ^ multiplicar_galois(0x02, estado[2][i])
            ^ multiplicar_galois(0x03, estado[3][i])
        )
        resultado[3][i] = (
            multiplicar_galois(0x03, estado[0][i])
            ^ estado[1][i]
            ^ estado[2][i]
            ^ multiplicar_galois(0x02, estado[3][i])
        )
    return resultado


# Funciones main


def AES_cifrar(texto_plano, clave):
    bytes_texto_plano = string_a_bytes(texto_plano)
    bytes_clave = string_a_bytes(clave)
    relleno_necesario = (16 - (len(bytes_texto_plano) % 16)) % 16
    bytes_texto_plano = bytes_texto_plano + [0] * relleno_necesario

    claves_ronda = expansion_clave(bytes_clave)

    bytes_texto_cifrado = []
    for i in range(0, len(bytes_texto_plano), 16):
        bloque = bytes_texto_plano[i: i + 16]
        bloque_cifrado = aes_cifrar_bloque(bloque, claves_ronda)
        bytes_texto_cifrado.extend(bloque_cifrado)

    return bytes_texto_cifrado


def AES_descifrar(bytes_texto_cifrado, clave):
    bytes_clave = string_a_bytes(clave)

    if len(bytes_clave) != 16:
        raise ValueError("AES-128 requiere una clave de 16 bytes (128 bits)")

    claves_ronda = expansion_clave(bytes_clave)

    bytes_texto_plano = []
    for i in range(0, len(bytes_texto_cifrado), 16):
        bloque = bytes_texto_cifrado[i: i + 16]
        bloque_descifrado = aes_descifrar_bloque(bloque, claves_ronda)
        bytes_texto_plano.extend(bloque_descifrado)

    return bytes_texto_plano
