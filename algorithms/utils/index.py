# Ejemplo: string_a_bits("AB") -> [0,1,0,0,0,0,0,1, 0,1,0,0,0,0,1,0]
def string_a_bits(texto):
    bits = []
    for caracter in texto:
        byte = ord(caracter)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


# Ejemplo: string_a_bytes("AB") -> [65, 66]
def string_a_bytes(texto):
    return [ord(c) for c in texto]


# Ejemplo: bits_a_hex([1,0,1,0, 1,1,1,1]) -> "af"
def bits_a_hex(bits):
    cadena_hex = ""
    for i in range(0, len(bits), 4):
        fragmento = bits[i: i + 4]
        val = 0
        for bit in fragmento:
            val = (val << 1) | bit
        cadena_hex += format(val, "x")
    return cadena_hex


# Ejemplo: bytes_a_hex([255, 16]) -> "ff10"
def bytes_a_hex(lista_bytes):
    return "".join(f"{b:02x}" for b in lista_bytes)


# Ejemplo: xor_bits([1,0,1,1], [0,1,1,0]) -> [1,1,0,1]
def xor_bits(bits1, bits2):
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]


# Ejemplo: rotacion_izquierda([1,2,3,4,5], 2) -> [3,4,5,1,2]
def rotacion_izquierda(bits, n):
    return bits[n:] + bits[:n]


# Ejemplo: bits_a_entero([1,0,1,1]) -> 11
def bits_a_entero(bits):
    """Convert list of bits to integer (MSB first)"""
    resultado = 0
    for bit in bits:
        resultado = (resultado << 1) | bit
    return resultado


# Ejemplo: entero_a_bits(11, 4) -> [1,0,1,1]
def entero_a_bits(valor, longitud):
    """Convert integer to list of bits (MSB first)"""
    return [(valor >> i) & 1 for i in range(longitud - 1, -1, -1)]
