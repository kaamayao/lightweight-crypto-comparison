def string_a_bits(texto):
    """Convertir string a lista de bits"""
    bits = []
    for caracter in texto:
        byte = ord(caracter)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_a_string(bits):
    """Convertir lista de bits a string"""
    caracteres = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bits):
                byte = (byte << 1) | bits[i + j]
        caracteres.append(chr(byte))
    return "".join(caracteres)


def string_a_bytes(texto):
    """Convertir string a lista de bytes"""
    return [ord(c) for c in texto]


def bytes_a_string(lista_bytes):
    """Convertir lista de bytes a string"""
    return "".join(chr(b) for b in lista_bytes)


def entero_a_bits(valor, longitud):
    """Convertir entero a lista de bits de longitud especificada"""
    return [(valor >> i) & 1 for i in range(longitud - 1, -1, -1)]


def bits_a_entero(bits):
    """Convertir lista de bits a entero"""
    resultado = 0
    for bit in bits:
        resultado = (resultado << 1) | bit
    return resultado


def bits_a_hex(bits):
    """Convertir bits a string hexadecimal"""
    cadena_hex = ""
    for i in range(0, len(bits), 4):
        fragmento = bits[i : i + 4]
        val = 0
        for bit in fragmento:
            val = (val << 1) | bit
        cadena_hex += format(val, "x")
    return cadena_hex


def bytes_a_hex(lista_bytes):
    """Convertir lista de bytes a string hexadecimal"""
    return "".join(f"{b:02x}" for b in lista_bytes)


def xor_bits(bits1, bits2):
    """XOR de dos arreglos de bits"""
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]


def xor_bytes(a, b):
    """XOR de dos arreglos de bytes"""
    return [x ^ y for x, y in zip(a, b)]


def rotar_izquierda(bits, n):
    """Rotar lista de bits a la izquierda n posiciones"""
    return bits[n:] + bits[:n]


def rotacion_izquierda(bits, n):
    """Alias para rotar_izquierda"""
    return bits[n:] + bits[:n]
