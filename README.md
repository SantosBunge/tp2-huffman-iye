# TP2 – Compresión sin pérdida mediante codificación de Huffman

Compresión de imágenes en escala de grises con código de Huffman, comparando la
codificación píxel a píxel con la codificación diferencial mediante residuos.

## Archivos

| Archivo | Contenido |
|---|---|
| `resolucion.ipynb` | Ejercicios 1, 2 y 3, respuestas conceptuales y un control adicional con píxeles barajados. Al ejecutarlo se guardan las figuras del informe. |
| `funciones_auxiliares_tp2.py` | Funciones provistas por la cátedra: `huffman_code` (construye el código a partir de las probabilidades) y `huffman_decode`. |
| `huffman_residuos.py` | Lógica compartida del ejercicio 4: recorrido en serpentina, cálculo y reconstrucción de residuos, codificación, empaquetado de bits y lectura/escritura del formato `.tp2`. |
| `comprimir.py` | Programa de línea de comando que comprime una imagen a `.tp2`. |
| `descomprimir.py` | Programa de línea de comando que descomprime un `.tp2` y muestra la imagen. |
| `informe/TP2_G01.tex` | Fuente LaTeX del informe. Las figuras en `informe/figures/` se generan ejecutando el cuaderno. |
| `informe/TP2_G01.pdf` | Informe compilado (`tectonic TP2_G01.tex` desde la carpeta `informe/`). |

Las imágenes `img_XX.jpg` no forman parte de la entrega.

## Requisitos

Python 3.10 o superior con `numpy`, `matplotlib`, `pillow` y Jupyter para abrir el cuaderno:

```bash
pip install numpy matplotlib pillow jupyter
```

## Cuaderno (ejercicios 1 a 3)

Abrir `resolucion.ipynb` con Jupyter y ejecutar todas las celdas en orden. Las imágenes
deben estar en la misma carpeta que el cuaderno. Las funciones de los primeros ejercicios
(`estimar_probabilidad`, `entropia`, `comprimir_huffman`, etc.) se reutilizan en los siguientes.
El apartado de barajado usa la semilla 42 y conserva exactamente el histograma de `img_01`.
Las figuras se actualizan en `informe/figures/`, en PDF y PNG. Para recompilar el informe,
ejecutar `pdflatex TP2_G01.tex` dos veces desde `informe/`, o usar `tectonic TP2_G01.tex`.

## Ejercicio 4: programas de línea de comando

### Comprimir

```bash
python comprimir.py img_01.jpg
```

Genera `img_01.tp2` e imprime bits por píxel, tamaño original y comprimido, y tasa de
compresión. Con `-o` se elige otro nombre de salida:

```bash
python comprimir.py img_01.jpg -o salida.tp2
```

La imagen se convierte a escala de grises de 8 bits antes de comprimir. La compresión es
sin pérdida respecto de esa imagen en escala de grises.

### Descomprimir

```bash
python descomprimir.py img_01.tp2
```

Reconstruye la imagen y la muestra en una ventana. Opciones:

```bash
python descomprimir.py img_01.tp2 -o reconstruida.png        # además la guarda
python descomprimir.py img_01.tp2 --verificar img_01.jpg     # compara con la original
python descomprimir.py img_01.tp2 --no-mostrar               # no abre la ventana
```

`--verificar` informa si la reconstrucción es idéntica, píxel a píxel, a la imagen original
convertida a escala de grises.
La salida opcional admite PNG, BMP o TIFF para conservar los píxeles. Se rechaza JPEG porque
volvería a introducir pérdidas al guardar.

### Cómo funciona

1. La imagen se recorre en serpentina (filas pares de izquierda a derecha, impares al revés),
   de modo que cada píxel es vecino espacial del anterior y alcanza con guardar un único píxel
   inicial.
2. Se calculan los residuos $y_k = x_k - x_{k-1}$, con valores en $[-255, 255]$.
3. Se estima $p(y)$ por frecuencia relativa y se construye el código de Huffman con
   `huffman_code`.
4. Los residuos codificados se empaquetan en bytes y se escriben junto con el encabezado.
5. Al descomprimir se lee la tabla de códigos, se decodifica con `huffman_decode`, se suman
   los residuos acumulativamente desde el píxel inicial y se deshace la serpentina.

### Formato del archivo `.tp2`

| Campo | Tamaño | Descripción |
|---|---|---|
| magic | 4 B | `TP2\x01` |
| alto, ancho | 4 B + 4 B | dimensiones (uint32) |
| píxel inicial | 1 B | primer píxel de la serpentina |
| n | 2 B | cantidad de símbolos en la tabla |
| tabla | 3n B | por símbolo: residuo (int16) y longitud de su código (uint8) |
| n_bits | 8 B | cantidad de bits útiles del bitstream |
| bitstream | resto | los n códigos concatenados, luego los residuos codificados |

Incluyendo las palabras de código, los metadatos ocupan aproximadamente entre 1.1 y 1.4 KB
en las imágenes provistas. El tamaño `.tp2` de la tabla siguiente incluye ese costo.

## Resultados sobre las imágenes provistas

| imagen | bits/píxel | tamaño original | tamaño `.tp2` | tasa |
|---|---|---|---|---|
| img_01 | 2.84 | 227 200 B | 81 763 B | 2.78 |
| img_02 | 7.18 | 249 696 B | 225 407 B | 1.11 |
| img_04 | 4.89 | 72 128 B | 45 543 B | 1.58 |

Las tres reconstrucciones son idénticas a las originales en escala de grises.

## Verificación

Desde la carpeta del cuaderno:

```bash
python -m unittest discover -s tests -v
```

Se comprueban fuentes de un solo símbolo, residuos constantes, imágenes de un píxel y
exportación sin pérdida. El cuaderno también verifica cada decodificación y la conservación
del histograma y de los bits directos en el experimento de barajado.
