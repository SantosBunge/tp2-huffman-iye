"""Reconstrucción de casos mínimos y exportación sin pérdida por terminal."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

from huffman_residuos import escribir_tp2, leer_tp2


class ArchivoTP2Tests(unittest.TestCase):
    def test_archivo_de_un_pixel_conserva_su_valor(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "un_pixel.tp2"
            original = np.array([[173]], dtype=np.uint8)
            escribir_tp2(path, original)
            np.testing.assert_array_equal(leer_tp2(path), original)

    def exportar(self, extension):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        folder = Path(self.temp.name)
        original = np.array([[0, 30, 100], [255, 120, 5]], dtype=np.uint8)
        entrada, salida = folder / "imagen.tp2", folder / f"salida.{extension}"
        escribir_tp2(entrada, original)
        script = Path(__file__).resolve().parents[1] / "descomprimir.py"
        env = dict(os.environ, MPLBACKEND="Agg", MPLCONFIGDIR=str(folder / "mpl"))
        result = subprocess.run(
            [sys.executable, str(script), str(entrada), "-o", str(salida), "--no-mostrar"],
            capture_output=True, text=True, env=env, check=False,
        )
        return result, salida, original

    def test_salida_jpeg_se_rechaza_para_evitar_perdidas(self):
        result, salida, _ = self.exportar("jpg")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(salida.exists())

    def test_salida_png_conserva_los_pixeles(self):
        result, salida, original = self.exportar("png")
        self.assertEqual(result.returncode, 0, result.stderr)
        with Image.open(salida) as img:
            np.testing.assert_array_equal(np.array(img), original)


if __name__ == "__main__":
    unittest.main()
