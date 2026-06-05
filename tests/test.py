"""
test.py
-------
Pruebas unitarias del proyecto "¿Dónde pongo mi concierto?".

Cómo ejecutar:
    python tests/test.py          (desde la raíz del proyecto)
    python -m pytest tests/ -v    (si tienes pytest instalado)

Cobertura:
    - Parser   : formato correcto, nombres con espacios, líneas vacías,
                 entradas inválidas.
    - Validador: coordenadas, duplicados, ciudad única, N negativo.
    - Factibilidad: casos infactibles, zona de advertencia, integración.
    - Generador: estructura del código MiniZinc, secciones clave.
"""

import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.parser_entrada import parse_input, validate_input
from src.core.validador_entrada import validar_datos, verificar_factibilidad
from src.core.generador_minizinc import generar_codigo_minizinc


# ─────────────────────────────────────────────────────────────
# Tests del parser
# ─────────────────────────────────────────────────────────────

class TestParser(unittest.TestCase):
    """Pruebas para parse_input() en parser_entrada.py."""

    def test_entrada_valida_basica(self):
        """Entrada bien formada debe parsearse sin error."""
        texto = "10\n3\nCali 2 3\nPalmira 5 7\nBuga 8 1"
        n, ciudades, error = parse_input(texto)
        self.assertIsNone(error)
        self.assertEqual(n, 10)
        self.assertEqual(len(ciudades), 3)
        self.assertEqual(ciudades[0], ("Cali", 2, 3))
        self.assertEqual(ciudades[2], ("Buga", 8, 1))

    def test_nombre_con_espacios(self):
        """
        Un nombre compuesto como 'Santa Marta' debe parsearse correctamente.
        Los dos últimos tokens son X e Y; todo lo anterior es el nombre.
        """
        texto = "10\n2\nSanta Marta 3 5\nSan Andres 7 2"
        n, ciudades, error = parse_input(texto)
        self.assertIsNone(error, f"No debería haber error: {error}")
        self.assertEqual(ciudades[0], ("Santa Marta", 3, 5))
        self.assertEqual(ciudades[1], ("San Andres", 7, 2))

    def test_lineas_vacias_ignoradas(self):
        """Las líneas en blanco dentro de la entrada deben ignorarse."""
        texto = "10\n\n2\nCali 2 3\n\nPalmira 7 5"
        n, ciudades, error = parse_input(texto)
        self.assertIsNone(error, f"No debería haber error: {error}")
        self.assertEqual(n, 10)
        self.assertEqual(len(ciudades), 2)

    def test_lineas_vacias_al_inicio_y_final(self):
        """Líneas en blanco al inicio y al final también deben ignorarse."""
        texto = "\n\n10\n2\nCali 2 3\nPalmira 7 5\n\n"
        n, ciudades, error = parse_input(texto)
        self.assertIsNone(error, f"No debería haber error: {error}")
        self.assertEqual(n, 10)

    def test_entrada_incompleta(self):
        """Entrada con solo N (sin M ni ciudades) debe retornar error."""
        n, ciudades, error = parse_input("10")
        self.assertIsNotNone(error)

    def test_n_no_es_entero(self):
        """Si N no es entero, debe retornar error."""
        n, ciudades, error = parse_input("abc\n2\nCali 1 1\nPalmira 2 2")
        self.assertIsNotNone(error)

    def test_m_no_es_entero(self):
        """Si M no es entero, debe retornar error."""
        n, ciudades, error = parse_input("10\ndos\nCali 1 1")
        self.assertIsNotNone(error)

    def test_coordenada_no_entera(self):
        """Si X o Y no son enteros, debe retornar error."""
        n, ciudades, error = parse_input("10\n1\nCali dos tres")
        self.assertIsNotNone(error)

    def test_pocas_ciudades_respecto_a_m(self):
        """Si M dice 3 pero solo hay 1 ciudad, debe retornar error."""
        n, ciudades, error = parse_input("10\n3\nCali 2 3")
        self.assertIsNotNone(error)

    def test_linea_ciudad_incompleta(self):
        """Una línea de ciudad con menos de 3 tokens debe retornar error."""
        n, ciudades, error = parse_input("10\n1\nCali 5")
        self.assertIsNotNone(error)

    def test_entrada_vacia(self):
        """Texto completamente vacío debe retornar error."""
        n, ciudades, error = parse_input("")
        self.assertIsNotNone(error)

    def test_nombre_tres_palabras(self):
        """Un nombre de tres palabras debe funcionar correctamente."""
        texto = "20\n1\nLa Virginia Risaralda 10 15"
        n, ciudades, error = parse_input(texto)
        self.assertIsNone(error)
        self.assertEqual(ciudades[0][0], "La Virginia Risaralda")
        self.assertEqual(ciudades[0][1], 10)
        self.assertEqual(ciudades[0][2], 15)


# ─────────────────────────────────────────────────────────────
# Tests del validador
# ─────────────────────────────────────────────────────────────

class TestValidador(unittest.TestCase):
    """Pruebas para validate_input() y validar_datos()."""

    def test_datos_validos_sin_errores(self):
        """Datos correctos no deben generar errores."""
        errores = validar_datos(10, [("Cali", 2, 3), ("Palmira", 5, 7)])
        self.assertEqual(errores, [])

    def test_coordenada_x_fuera_de_rango(self):
        """X mayor que N debe generar error."""
        errores = validar_datos(5, [("Cali", 7, 3), ("Palmira", 2, 2)])
        self.assertTrue(any("X=7" in e for e in errores))

    def test_coordenada_y_fuera_de_rango(self):
        """Y mayor que N debe generar error."""
        errores = validar_datos(5, [("Cali", 2, 9)])
        self.assertTrue(any("Y=9" in e for e in errores))

    def test_ciudad_unica_genera_advertencia(self):
        """Con una sola ciudad debe haber al menos una advertencia."""
        errores = validar_datos(10, [("Cali", 3, 3)])
        self.assertGreater(len(errores), 0)

    def test_n_negativo(self):
        """N negativo debe generar error."""
        errores = validar_datos(-5, [("Cali", 2, 3), ("Palmira", 1, 1)])
        self.assertGreater(len(errores), 0)

    def test_nombres_duplicados(self):
        """Dos ciudades con el mismo nombre deben generar error."""
        errores = validate_input(10, [("Cali", 2, 3), ("Cali", 5, 7)])
        self.assertTrue(any("duplicado" in e.lower() or "Cali" in e for e in errores))

    def test_posiciones_duplicadas(self):
        """Dos ciudades en la misma coordenada deben generar error."""
        errores = validate_input(10, [("Cali", 2, 3), ("Palmira", 2, 3)])
        self.assertTrue(any("duplicad" in e.lower() or "(2, 3)" in e for e in errores))


# ─────────────────────────────────────────────────────────────
# Tests de factibilidad
# ─────────────────────────────────────────────────────────────

class TestFactibilidad(unittest.TestCase):
    """Pruebas para verificar_factibilidad() en validador_entrada.py."""

    def test_n1_cuatro_ciudades_infactible(self):
        """N=1 tiene 4 posiciones. Con 4 ciudades → infactible."""
        r = verificar_factibilidad(1, [("A",0,0),("B",0,1),("C",1,0),("D",1,1)])
        self.assertTrue(r["infactible"])
        self.assertEqual(r["posiciones_libres"], 0)

    def test_n0_una_ciudad_infactible(self):
        """N=0 tiene 1 sola posición. Con 1 ciudad → infactible."""
        r = verificar_factibilidad(0, [("Cali", 0, 0)])
        self.assertTrue(r["infactible"])

    def test_n2_todas_posiciones_ocupadas(self):
        """N=2 tiene 9 posiciones. Con las 9 ocupadas → infactible."""
        ciudades = [
            ("A",0,0),("B",0,1),("C",0,2),
            ("D",1,0),("E",1,1),("F",1,2),
            ("G",2,0),("H",2,1),("I",2,2),
        ]
        r = verificar_factibilidad(2, ciudades)
        self.assertTrue(r["infactible"])
        self.assertEqual(r["total_posiciones"], 9)

    def test_mensaje_error_menciona_unsatisfiable(self):
        """El mensaje de error debe mencionar UNSATISFIABLE."""
        r = verificar_factibilidad(0, [("Cali", 0, 0)])
        self.assertIn("UNSATISFIABLE", r["mensaje_error"])

    def test_caso_factible_normal(self):
        """N=10 con 2 ciudades es completamente factible."""
        r = verificar_factibilidad(10, [("Cali", 2, 3), ("Palmira", 7, 8)])
        self.assertFalse(r["infactible"])
        self.assertFalse(r["advertencia"])
        self.assertEqual(r["posiciones_libres"], 119)

    def test_zona_advertencia_menos_de_5_libres(self):
        """N=2 con 5 ciudades deja 4 libres (<5) → advertencia."""
        ciudades = [("A",0,0),("B",0,1),("C",0,2),("D",1,0),("E",1,1)]
        r = verificar_factibilidad(2, ciudades)
        self.assertFalse(r["infactible"])
        self.assertTrue(r["advertencia"])
        self.assertEqual(r["posiciones_libres"], 4)

    def test_exactamente_5_libres_no_activa_advertencia(self):
        """Con exactamente 5 posiciones libres no se activa la advertencia."""
        ciudades = [("A",0,0),("B",0,1),("C",0,2),("D",1,0)]  # 4 ciudades → 5 libres
        r = verificar_factibilidad(2, ciudades)
        self.assertFalse(r["advertencia"])
        self.assertEqual(r["posiciones_libres"], 5)

    def test_validar_datos_bloquea_caso_infactible(self):
        """validar_datos() debe incluir error UNSATISFIABLE en caso infactible."""
        errores = validar_datos(1, [("A",0,0),("B",0,1),("C",1,0),("D",1,1)])
        self.assertTrue(any("UNSATISFIABLE" in e for e in errores))

    def test_validar_datos_permite_caso_valido(self):
        """Un caso válido y factible no debe producir ningún error."""
        errores = validar_datos(10, [("Cali",2,3),("Palmira",7,8),("Buga",5,1)])
        self.assertEqual(errores, [])


# ─────────────────────────────────────────────────────────────
# Tests del generador MiniZinc
# ─────────────────────────────────────────────────────────────

class TestGeneradorMiniZinc(unittest.TestCase):
    """Pruebas para generar_codigo_minizinc() en generador_minizinc.py."""

    def setUp(self):
        self.datos = {
            "n": 10,
            "ciudades": [("Cali", 2, 3), ("Palmira", 5, 7), ("Buga", 8, 1)]
        }

    def test_genera_string(self):
        """El resultado siempre debe ser un string."""
        self.assertIsInstance(generar_codigo_minizinc(self.datos), str)

    def test_contiene_n_correcto(self):
        """El código debe declarar N con el valor correcto."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("int: N = 10;", codigo)

    def test_contiene_m_correcto(self):
        """El código debe declarar M con el valor correcto."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("int: M = 3;", codigo)

    def test_contiene_coordenadas_x(self):
        """El código debe incluir el arreglo de coordenadas X."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("[2, 5, 8]", codigo)

    def test_contiene_coordenadas_y(self):
        """El código debe incluir el arreglo de coordenadas Y."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("[3, 7, 1]", codigo)

    def test_contiene_solve_minimize(self):
        """El código debe incluir el objetivo minimax."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("solve minimize dist_max;", codigo)

    def test_contiene_restriccion_no_ciudad(self):
        """El código debe incluir la restricción de no estar en ciudad."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("not (px = ciudad_x[i]", codigo)

    def test_contiene_distancia_manhattan(self):
        """El código debe usar distancia Manhattan (abs + abs)."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("abs(px - ciudad_x[i]) + abs(py - ciudad_y[i])", codigo)

    def test_nombres_en_comentario(self):
        """Los nombres de las ciudades deben aparecer como comentario."""
        codigo = generar_codigo_minizinc(self.datos)
        self.assertIn("Cali", codigo)
        self.assertIn("Palmira", codigo)

    def test_datos_invalidos_retorna_error(self):
        """Datos que no son diccionario deben retornar mensaje de error."""
        self.assertIn("ERROR", generar_codigo_minizinc(None))

    def test_sin_ciudades_retorna_error(self):
        """Diccionario sin ciudades debe retornar error."""
        self.assertIn("ERROR", generar_codigo_minizinc({"n": 10, "ciudades": []}))

    def test_ciudad_nombre_con_espacios(self):
        """Ciudades con nombre compuesto deben aparecer en el código."""
        datos = {"n": 15, "ciudades": [("Santa Marta", 3, 5), ("San Andres", 10, 8)]}
        codigo = generar_codigo_minizinc(datos)
        self.assertIn("Santa Marta", codigo)
        self.assertIn("San Andres", codigo)
        self.assertIn("[3, 10]", codigo)   # coordenadas X
        self.assertIn("[5, 8]", codigo)    # coordenadas Y


# ─────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Ejecutando pruebas del proyecto — Concierto en el Valle")
    print("=" * 60)
    unittest.main(verbosity=2)
