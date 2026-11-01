"""
Lógica compartida por comprimir.py y descomprimir.py.

Esquema: la imagen en escala de grises se recorre en serpentina, se calculan
los residuos y = x_k - x_{k-1}, se codifican con Huffman y se escriben en un
archivo binario .tp2 junto con todo lo que el decodificador necesita:
dimensiones, píxel inicial y tabla de códigos.

Formato del archivo .tp2 (big endian):

    4 bytes   magic            b"TP2\\x01"
    4 bytes   alto             uint32
    4 bytes   ancho            uint32
    1 byte    píxel inicial    uint8
    2 bytes   n                uint16, cantidad de símbolos en la tabla
    3n bytes  tabla            n entradas (símbolo int16, longitud del código uint8)
    8 bytes   n_bits           uint64, cantidad de bits útiles del bitstream
    resto     bitstream        primero los n códigos concatenados (en el orden
                               de la tabla), luego los residuos codificados;
                               el último byte se completa con ceros
"""

import struct
import numpy as np
from PIL import Image

from funciones_auxiliares_tp2 import huffman_code, huffman_decode

MAGIC = b"TP2\x01"


# ---------------------------------------------------------------- imagen <-> residuos

def cargar_imagen_gris(path: str) -> np.ndarray:
    """Abre una imagen en cualquier formato estándar y la devuelve en escala de grises uint8."""
    return np.array(Image.open(path).convert("L"), dtype=np.uint8)


def serpentina(img: np.ndarray) -> np.ndarray:
    """Aplana la imagen recorriéndola en serpentina (filas impares de derecha a izquierda)."""
    s = img.copy()
    s[1::2] = s[1::2, ::-1]
    return s.ravel()


def deshacer_serpentina(seq: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Inversa de serpentina."""
    img = seq.reshape(shape).copy()
    img[1::2] = img[1::2, ::-1]
    return img


def calcular_residuos(img: np.ndarray) -> tuple[int, np.ndarray]:
    """Devuelve el píxel inicial y los residuos y_k = x_k - x_{k-1} sobre la serpentina."""
    seq = serpentina(img).astype(np.int64)
    return int(seq[0]), np.diff(seq)


def reconstruir(inicial: int, residuos: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Suma acumulada de los residuos a partir del píxel inicial y deshace la serpentina."""
    seq = np.concatenate([[inicial], residuos]).cumsum()
    return deshacer_serpentina(seq, shape).astype(np.uint8)


# ---------------------------------------------------------------- Huffman

def construir_codigo(residuos: np.ndarray) -> dict[int, str]:
    """Estima p(y) por frecuencia relativa y construye el código de Huffman."""
    if residuos.size == 0:  # imagen de un píxel: alcanza con el inicial
        return {}
    simbolos, conteos = np.unique(residuos, return_counts=True)
    prob = {int(s): float(c) / residuos.size for s, c in zip(simbolos, conteos)}
    if len(prob) == 1:  # caso degenerado: un único símbolo, huffman_code devolvería ''
        return {next(iter(prob)): "0"}
    return huffman_code(prob)


def codificar(simbolos: np.ndarray, codigo: dict[int, str]) -> str:
    """Concatena las palabras de código de cada símbolo."""
    return "".join(codigo[int(s)] for s in simbolos)


# ---------------------------------------------------------------- bits <-> bytes

def bits_a_bytes(bits: str) -> bytes:
    """Empaqueta una cadena de '0'/'1' en bytes, completando el último con ceros."""
    arr = np.frombuffer(bits.encode("ascii"), dtype=np.uint8) - ord("0")
    return np.packbits(arr).tobytes()


def bytes_a_bits(data: bytes, n_bits: int) -> str:
    """Desempaqueta bytes a una cadena de '0'/'1' de longitud n_bits."""
    arr = np.unpackbits(np.frombuffer(data, dtype=np.uint8))[:n_bits]
    return (arr + ord("0")).astype(np.uint8).tobytes().decode("ascii")


# ---------------------------------------------------------------- archivo .tp2

def escribir_tp2(path: str, img: np.ndarray) -> dict:
    """Comprime la imagen y escribe el archivo .tp2. Devuelve estadísticas."""
    alto, ancho = img.shape
    inicial, residuos = calcular_residuos(img)
    codigo = construir_codigo(residuos)

    tabla = sorted(codigo.items())
    bits_tabla = "".join(c for _, c in tabla)
    bits_datos = codificar(residuos, codigo)
    bitstream = bits_tabla + bits_datos

    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">IIBH", alto, ancho, inicial, len(tabla)))
        for simbolo, cod in tabla:
            f.write(struct.pack(">hB", simbolo, len(cod)))
        f.write(struct.pack(">Q", len(bitstream)))
        f.write(bits_a_bytes(bitstream))

    return {
        "pixeles": img.size,
        "simbolos": len(tabla),
        "bits_datos": len(bits_datos),
        "bits_tabla": len(bits_tabla) + 3 * 8 * len(tabla),
        "bits_por_pixel": len(bits_datos) / img.size,
    }


def leer_tp2(path: str) -> np.ndarray:
    """Lee un archivo .tp2 y reconstruye la imagen en escala de grises."""
    with open(path, "rb") as f:
        if f.read(4) != MAGIC:
            raise ValueError(f"{path} no es un archivo .tp2 válido")
        alto, ancho, inicial, n = struct.unpack(">IIBH", f.read(11))
        tabla = [struct.unpack(">hB", f.read(3)) for _ in range(n)]
        (n_bits,) = struct.unpack(">Q", f.read(8))
        bitstream = bytes_a_bits(f.read(), n_bits)

    # Reconstruir el diccionario de códigos a partir de las longitudes
    codigo, pos = {}, 0
    for simbolo, longitud in tabla:
        codigo[simbolo] = bitstream[pos:pos + longitud]
        pos += longitud

    residuos = np.array(huffman_decode(bitstream[pos:], codigo), dtype=np.int64)
    if residuos.size != alto * ancho - 1:
        raise ValueError("La cantidad de residuos no coincide con las dimensiones de la imagen")

    return reconstruir(inicial, residuos, (alto, ancho))
