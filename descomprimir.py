#!/usr/bin/env python3
"""
Descomprime un archivo .tp2 y muestra la imagen reconstruida.

Uso:
    python descomprimir.py imagen.tp2                 -> muestra la imagen
    python descomprimir.py imagen.tp2 -o imagen.png   -> además la guarda
    python descomprimir.py imagen.tp2 --verificar original.jpg
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from huffman_residuos import cargar_imagen_gris, leer_tp2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("archivo", help="archivo .tp2 a descomprimir")
    parser.add_argument("-o", "--salida", help="guardar la imagen reconstruida (png, jpg, ...)")
    parser.add_argument("--verificar", metavar="ORIGINAL",
                        help="comparar la reconstrucción con la imagen original (en escala de grises)")
    parser.add_argument("--no-mostrar", action="store_true", help="no abrir la ventana con la imagen")
    args = parser.parse_args()

    img = leer_tp2(args.archivo)
    print(f"Archivo:       {args.archivo}")
    print(f"Reconstruida:  {img.shape[0]}x{img.shape[1]} px")

    if args.verificar:
        original = cargar_imagen_gris(args.verificar)
        iguales = original.shape == img.shape and np.array_equal(original, img)
        print(f"Verificación:  {'idéntica a' if iguales else 'DIFIERE de'} {args.verificar}")

    if args.salida:
        Image.fromarray(img).save(args.salida)
        print(f"Guardada en:   {args.salida}")

    if not args.no_mostrar:
        plt.imshow(img, cmap="gray", vmin=0, vmax=255)
        plt.title(args.archivo)
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    main()
