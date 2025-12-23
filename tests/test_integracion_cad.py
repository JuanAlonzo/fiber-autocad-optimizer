"""
Tests de integración con AutoCAD (Requiere AutoCAD abierto)
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'src')))

from optimizer.autocad_utils import obtener_tramos, get_acad_instance   # noqa E402


class TestAutoCADIntegration(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test. Verifica conexión."""
        try:
            self.acad = get_acad_instance()
            # Verificamos si realmente hay conexión probando una propiedad simple
            _ = self.acad.doc.Name
        except Exception:
            self.skipTest(
                "AutoCAD no está disponible o abierto. Saltando tests de integración.")

    def test_conexion_activa(self):
        """Verifica que la instancia de AutoCAD responda"""
        self.assertIsNotNone(self.acad.doc)

    def test_obtener_tramos_estructura(self):
        """Verifica que obtener_tramos devuelva una lista de diccionarios con las llaves correctas"""
        tramos = obtener_tramos(self.acad)

        # Si no hay tramos dibujados, la lista está vacía, lo cual es válido
        if not tramos:
            print("\n[INFO] No se encontraron tramos para testear estructura.")
            return

        # Si hay tramos, verificamos el primero
        tramo = tramos[0]
        self.assertIn("handle", tramo)
        self.assertIn("layer", tramo)
        self.assertIn("longitud", tramo)
        self.assertIn("obj", tramo)
        self.assertIsInstance(tramo["longitud"], float)


if __name__ == '__main__':
    unittest.main()
