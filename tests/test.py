"""
test.py
-------
Pruebas básicas para verificar que los módulos principales funcionan.

Cómo ejecutar:
    python -m pytest tests/test.py -v
    
    O directamente:
    python tests/test.py

Estas pruebas cubren:
    - El parser (parse_input y validate_input).
    - El validador (validar_datos).
    - El generador de código MiniZinc (generar_codigo_minizinc).
"""

import sys
import os
import unittest

# Permitir importar módulos de src desde la carpeta tests/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.parser_entrada import parse_input, validate_input
from src.core.validador_entrada import validar_datos
from src.core.generador_minizinc import generar_codigo_minizinc


# ─────────────────────────────────────────────────────────────
# Tests del parser
# ─────────────────────────────────────────────────────────────

class TestParser(unittest.TestCase):
    """Pruebas para parse_input() en parser_entrada.py."""

    def test_entrada_valida(self):
        """Una entrada bien formada debe parsearse sin error."""
        texto = "10\n3\nCali 2 3\nPalmira 5 7\nBuga 8 1"
        n, ciudades, error = parse_input(texto)

        self.assertIsNone(error, f"No debería haber error: {error}")
        self.assertEqual(n, 10)
        self.assertEqual(len(ciudades), 3)
        self.assertEqual(ciudades[0], ("Cali", 2, 3))
        self.assertEqual(ciudades[1], ("Palmira", 5, 7))
        self.assertEqual(ciudades[2], ("Buga", 8, 1))

    def test_entrada_incompleta(self):
        """Una entrada con menos líneas de las necesarias debe retornar error."""
        texto = "10"   # Falta M y las ciudades
        n, ciudades, error = parse_input(texto)
        self.assertIsNotNone(error)

    def test_n_no_es_entero(self):
        """Si N no es un entero, debe retornar error."""
        texto = "abc\n2\nCali 1 1\nPalmira 2 2"
        n, ciudades, error = parse_input(texto)
        self.assertIsNotNone(error)

    def test_coordenada_no_entera(self):
        """Si una coordenada no es entera, debe retornar error."""
        texto = "10\n1\nCali dos tres"
        n, ciudades, error = parse_input(texto)
        self.assertIsNotNone(error)

    def test_pocas_ciudades(self):
        """Si M dice 3 ciudades pero solo hay 1, debe retornar error."""
        texto = "10\n3\nCali 2 3"
        n, ciudades, error = parse_input(texto)
        self.assertIsNotNone(error)


# ─────────────────────────────────────────────────────────────
# Tests del validador
# ─────────────────────────────────────────────────────────────

class TestValidador(unittest.TestCase):
    """Pruebas para validar_datos() en validador_entrada.py."""

    def test_datos_validos(self):
        """Datos correctos no deben generar errores."""
        n = 10
        ciudades = [("Cali", 2, 3), ("Palmira", 5, 7)]
        errores = validar_datos(n, ciudades)
        self.assertEqual(errores, [], f"No debería haber errores: {errores}")

    def test_coordenada_fuera_de_rango(self):
        """Una coordenada fuera del cuadrado debe generar error."""
        n = 5
        ciudades = [("Cali", 7, 3), ("Palmira", 2, 2)]   # X=7 > N=5
        errores = validar_datos(n, ciudades)
        self.assertGreater(len(errores), 0)

    def test_ciudad_unica_genera_advertencia(self):
        """Con una sola ciudad el sistema debe avisar (problema trivial)."""
        n = 10
        ciudades = [("Cali", 3, 3)]
        errores = validar_datos(n, ciudades)
        # Debe haber al menos un mensaje de advertencia
        self.assertGreater(len(errores), 0)

    def test_n_negativo(self):
        """N negativo debe generar error."""
        n = -5
        ciudades = [("Cali", 2, 3), ("Palmira", 1, 1)]
        errores = validar_datos(n, ciudades)
        self.assertGreater(len(errores), 0)


# ─────────────────────────────────────────────────────────────
# Tests del generador MiniZinc
# ─────────────────────────────────────────────────────────────

class TestGeneradorMiniZinc(unittest.TestCase):
    """Pruebas para generar_codigo_minizinc() en generador_minizinc.py."""

    def setUp(self):
        """Datos base que se usan en varios tests."""
        self.datos = {
            "n": 10,
            "ciudades": [("Cali", 2, 3), ("Palmira", 5, 7), ("Buga", 8, 1)]
        }

    def test_genera_string(self):
        """El generador siempre debe retornar un string."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIsInstance(codigo, str)

    def test_contiene_n_correcto(self):
        """El código generado debe incluir el valor de N."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("int: N = 10;", codigo)

    def test_contiene_m_correcto(self):
        """El código generado debe incluir el valor de M."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("int: M = 3;", codigo)

    def test_contiene_coordenadas(self):
        """El código generado debe incluir los arreglos de coordenadas."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("ciudad_x", codigo)
        self.assertIn("ciudad_y", codigo)
        self.assertIn("[2, 5, 8]", codigo)   # coordenadas X
        self.assertIn("[3, 7, 1]", codigo)   # coordenadas Y

    def test_contiene_solve_minimize(self):
        """El código generado debe incluir el objetivo de minimización."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("solve minimize dist_max;", codigo)

    def test_contiene_restriccion_no_ciudad(self):
        """El código debe incluir la restricción de no estar en una ciudad."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("not (px = ciudad_x[i]", codigo)

    def test_datos_invalidos_retorna_error(self):
        """Datos que no son diccionario deben retornar mensaje de error."""
        codigo = generar_codigo_minizinc(None)
        self.assertIn("ERROR", codigo)

    def test_sin_ciudades_retorna_error(self):
        """Un diccionario sin ciudades debe retornar error."""
        codigo = generar_codigo_minizinc({"n": 10, "ciudades": []})
        self.assertIn("ERROR", codigo)

    def test_nombres_aparecen_en_comentario(self):
        """Los nombres de las ciudades deben aparecer en el código como comentario."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("Cali", codigo)
        self.assertIn("Palmira", codigo)
        self.assertIn("Buga", codigo)


# ─────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Ejecutando pruebas del proyecto — Concierto en el Valle")
    print("=" * 60)
    unittest.main(verbosity=2)
