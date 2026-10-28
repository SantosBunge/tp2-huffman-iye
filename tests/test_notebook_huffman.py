"""Regresiones de la compresión del cuaderno: python -m unittest discover -s tests."""

import ast
import json
from pathlib import Path
import unittest

import numpy as np

import funciones_auxiliares_tp2 as aux


def cargar_funciones():
    """Ejecuta las definiciones reales sin cargar imágenes ni dibujar gráficos."""
    path = Path(__file__).resolve().parents[1] / "resolucion.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"np": np, "aux": aux}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            tree = ast.parse("".join(cell["source"]))
            tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
            exec(compile(tree, str(path), "exec"), namespace)
    return namespace["comprimir_huffman"]


class HuffmanNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comprimir = staticmethod(cargar_funciones())

    def comprobar_reconstruccion(self, simbolos, alfabeto=None):
        result = self.comprimir(simbolos, alfabeto)
        bits = "".join(result["codigo"][int(s)] for s in simbolos.ravel())
        decoded = np.array(aux.huffman_decode(bits, result["codigo"]))
        np.testing.assert_array_equal(decoded.reshape(simbolos.shape), simbolos)
        self.assertEqual(result["bits_totales"], len(bits))
        self.assertAlmostEqual(result["bits_promedio"], result["L"])
        return result

    def test_imagen_constante_conserva_todos_los_pixeles(self):
        result = self.comprobar_reconstruccion(np.full((4, 4), 70, dtype=np.uint8))
        self.assertEqual(result["H"], 0)
        self.assertEqual(result["bits_totales"], 16)
        self.assertEqual(result["L"], 1)

    def test_residuos_constantes_incluidos_negativos(self):
        for simbolo in (-255, 0, 255):
            with self.subTest(simbolo=simbolo):
                self.comprobar_reconstruccion(np.full(15, simbolo), np.arange(-255, 256))

    def test_un_solo_pixel(self):
        self.comprobar_reconstruccion(np.array([[255]], dtype=np.uint8))

    def test_dos_simbolos_equiprobables_alcanzan_la_entropia(self):
        result = self.comprobar_reconstruccion(np.array([[0, 255], [255, 0]], dtype=np.uint8))
        self.assertEqual(result["H"], 1)
        self.assertEqual(result["L"], 1)
        self.assertEqual(result["bits_totales"], 4)


if __name__ == "__main__":
    unittest.main()
