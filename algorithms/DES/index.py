from .constants import IP, IP_INV, E, P, S_BOXES, PC1, PC2, SHIFT_SCHEDULE
from algorithms.utils.index import (
    string_a_bits,
    xor_bits,
    rotacion_izquierda,
)


def permutar(bloque, tabla):
    """Aplicar tabla de permutación a un bloque de bits"""
    return [bloque[i - 1] for i in tabla]


def generar_claves_ronda(clave):
    """Generar 16 claves de ronda a partir de la clave principal"""
    # Convertir clave a 64 bits si es necesario
    if len(clave) >= 64:
        bits_clave = clave[:64]
    else:
        bits_clave = clave + [0] * (64 - len(clave))

    # Aplicar PC1 para obtener clave de 56 bits
    clave_56 = permutar(bits_clave, PC1)

    # Dividir en dos mitades de 28 bits
    C = clave_56[:28]
    D = clave_56[28:]

    claves_ronda = []
    for i in range(16):
        # Rotar ambas mitades
        C = rotacion_izquierda(C, SHIFT_SCHEDULE[i])
        D = rotacion_izquierda(D, SHIFT_SCHEDULE[i])

        # Combinar y aplicar PC2 para obtener clave de ronda de 48 bits
        CD = C + D
        clave_ronda = permutar(CD, PC2)
        claves_ronda.append(clave_ronda)

    return claves_ronda


def sustitucion_sbox(bloque_48):
    """Aplicar sustitución S-box a un bloque de 48 bits"""
    resultado = []

    for i in range(8):
        # Obtener fragmento de 6 bits
        fragmento = bloque_48[i * 6: (i + 1) * 6]

        # La fila está determinada por el primer y último bit
        fila = (fragmento[0] << 1) | fragmento[5]

        # La columna está determinada por los 4 bits centrales
        columna = (
            (fragmento[1] << 3)
            | (fragmento[2] << 2)
            | (fragmento[3] << 1)
            | fragmento[4]
        )

        # Obtener valor de S-box
        val = S_BOXES[i][fila][columna]

        # Convertir a 4 bits
        for j in range(3, -1, -1):
            resultado.append((val >> j) & 1)

    return resultado


def funcion_feistel(derecha_32, clave_ronda):
    """La función Feistel F"""
    # Expandir R de 32 a 48 bits
    expandido = permutar(derecha_32, E)

    # XOR con la clave de ronda
    xoreado = xor_bits(expandido, clave_ronda)

    # Aplicar S-boxes (48 bits -> 32 bits)
    sustituido = sustitucion_sbox(xoreado)

    # Aplicar permutación P
    resultado = permutar(sustituido, P)

    return resultado


def des_cifrar_bloque(texto_plano_64, claves_ronda):
    """Cifrar un bloque de 64 bits usando DES"""
    # Aplicar permutación inicial
    permutado = permutar(texto_plano_64, IP)

    # Dividir en mitades izquierda y derecha
    L = permutado[:32]
    R = permutado[32:]

    # 16 rondas de Feistel
    for i in range(16):
        # Guardar R antigua
        R_antigua = R[:]

        # R_i = L_{i-1} XOR F(R_{i-1}, K_i)
        R = xor_bits(L, funcion_feistel(R, claves_ronda[i]))

        # L_i = R_{i-1}
        L = R_antigua

    # Combinar R16 y L16 (nota: R va primero en la combinación final)
    combinado = R + L

    # Aplicar permutación final (IP^-1)
    texto_cifrado = permutar(combinado, IP_INV)

    return texto_cifrado


def DES_cifrar(texto_plano, clave):
    """
    Cifrar texto plano usando el algoritmo DES

    Args:
        texto_plano: String a cifrar (se rellenará a múltiplo de 8 bytes)
        clave: Clave de 64 bits como string (8 caracteres) o lista de bits

    Returns:
        Lista de bits representando el texto cifrado
    """
    if isinstance(texto_plano, str):
        bits_texto_plano = string_a_bits(texto_plano)
    else:
        bits_texto_plano = texto_plano

    if isinstance(clave, str):
        bits_clave = string_a_bits(clave)
    else:
        bits_clave = clave

    # Asegurar que la clave sea de 64 bits
    if len(bits_clave) < 64:
        bits_clave = bits_clave + [0] * (64 - len(bits_clave))

    # Rellenar texto plano a múltiplo de 64 bits
    relleno_necesario = (64 - (len(bits_texto_plano) % 64)) % 64
    bits_texto_plano = bits_texto_plano + [0] * relleno_necesario

    # Generar claves de ronda
    claves_ronda = generar_claves_ronda(bits_clave)

    # Cifrar cada bloque de 64 bits
    bits_texto_cifrado = []
    for i in range(0, len(bits_texto_plano), 64):
        bloque = bits_texto_plano[i: i + 64]
        bloque_cifrado = des_cifrar_bloque(bloque, claves_ronda)
        bits_texto_cifrado.extend(bloque_cifrado)

    return bits_texto_cifrado


def DES_descifrar(bits_texto_cifrado, clave):
    """
    Descifrar texto cifrado usando el algoritmo DES

    Args:
        bits_texto_cifrado: Lista de bits representando el texto cifrado
        clave: Clave de 64 bits como string (8 caracteres) o lista de bits

    Returns:
        Lista de bits representando el texto plano
    """
    if isinstance(clave, str):
        bits_clave = string_a_bits(clave)
    else:
        bits_clave = clave

    # Asegurar que la clave sea de 64 bits
    if len(bits_clave) < 64:
        bits_clave = bits_clave + [0] * (64 - len(bits_clave))

    # Generar claves de ronda
    claves_ronda = generar_claves_ronda(bits_clave)

    # Para descifrado, usar claves de ronda en orden inverso
    claves_ronda = claves_ronda[::-1]

    # Descifrar cada bloque de 64 bits
    bits_texto_plano = []
    for i in range(0, len(bits_texto_cifrado), 64):
        bloque = bits_texto_cifrado[i: i + 64]
        bloque_descifrado = des_cifrar_bloque(bloque, claves_ronda)
        bits_texto_plano.extend(bloque_descifrado)

    return bits_texto_plano
