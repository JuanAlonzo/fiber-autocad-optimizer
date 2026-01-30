import unittest
import win32com.client
from optimizer.acad_tools import get_acad_com


class TestIntegracionCAD(unittest.TestCase):
    def setUp(self):
        self.acad = get_acad_com()
        if not self.acad:
            self.skipTest("AutoCAD no detectado")

    def test_conexion_com(self):
        """Verifica que tenemos control del ModelSpace."""
        doc = self.acad.ActiveDocument
        msp = doc.ModelSpace
        self.assertIsNotNone(msp.Count)
        print(f"\n[TEST] Conectado a: {doc.Name}")

    def test_dibujar_linea(self):
        """Intenta dibujar una línea temporal y borrarla."""
        msp = self.acad.ActiveDocument.ModelSpace
        import pythoncom

        # Dibujar línea (0,0) a (10,10)
        p1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (0, 0, 0))
        p2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (10, 10, 0))

        linea = msp.AddLine(p1, p2)
        handle = linea.Handle

        self.assertTrue(handle)  # Si tiene handle, existe
        linea.Delete()  # Limpieza


if __name__ == "__main__":
    unittest.main()
