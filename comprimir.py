#!/usr/bin/env python3
"""
Comprime una imagen (jpg, png, etc.) a un archivo binario .tp2 usando
codificación de Huffman sobre residuos entre píxeles vecinos.

Uso:
    python comprimir.py imagen.jpg              -> genera imagen.tp2
    python comprimir.py imagen.jpg -o salida.tp2
"""

import argparse
import os

from huffman_residuos import cargar_imagen_gris, escribir_tp2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("imagen", help="imagen de entrada en un formato estándar (jpg, png, ...)")
    parser.add_argument("-o", "--salida", help="nombre del archivo .tp2 (por defecto, el de la imagen)")
    args = parser.parse_args()

    salida = args.salida or os.path.splitext(args.imagen)[0] + ".tp2"
    if not salida.endswith(".tp2"):
        salida += ".tp2"

    img = cargar_imagen_gris(args.imagen)
    stats = escribir_tp2(salida, img)

    bytes_original = img.size
    bytes_tp2 = os.path.getsize(salida)
    print(f"Imagen:        {args.imagen}  ({img.shape[0]}x{img.shape[1]} px, escala de grises)")
    print(f"Salida:        {salida}")
    print(f"Símbolos:      {stats['simbolos']} residuos distintos")
    print(f"Bits/píxel:    {stats['bits_por_pixel']:.4f}  (datos, sin contar el encabezado)")
    print(f"Tamaño:        {bytes_original} B sin comprimir  ->  {bytes_tp2} B comprimido")
    print(f"Tasa:          {bytes_original / bytes_tp2:.3f}")


if __name__ == "__main__":
    main()
