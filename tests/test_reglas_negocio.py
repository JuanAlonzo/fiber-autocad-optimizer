import unittest
from optimizer import seleccionar_cable, obtener_reserva_requerida


class TestReglasCables(unittest.TestCase):
    def test_reserva_requerida_valores_config(self):
        """Verifica que XBOX pida 15m y el resto 10m"""
        self.assertEqual(obtener_reserva_requerida("xbox_hub"), 15)
        self.assertEqual(obtener_reserva_requerida("hub_fat"), 10)
        self.assertEqual(obtener_reserva_requerida("expansion"), 10)

    def test_seleccion_cable_xbox_caso_ideal(self):
        """Tramo 285m (req 15m reserva) -> Cable 300m -> Reserva exacta 15m"""
        cable, reserva = seleccionar_cable(285, "xbox_hub")
        self.assertEqual(cable, 300)
        self.assertEqual(reserva, 15)

    def test_seleccion_cable_xbox_caso_insuficiente(self):
        """Tramo 290m -> Cable 300m -> Reserva 10m (Matemáticamente correcto, aunque sea bajo)"""
        # El test valida que la matemática funcione, la alerta es otro tema
        cable, reserva = seleccionar_cable(290, "xbox_hub")
        self.assertEqual(cable, 300)
        self.assertEqual(reserva, 10)

    def test_seleccion_cable_salto_automatico(self):
        """Tramo 95m (Hub->Fat). Cable 100m da 5m reserva (<10). Debe saltar a 150m."""
        cable, reserva = seleccionar_cable(95, "hub_fat")
        self.assertEqual(cable, 150)
        self.assertEqual(reserva, 55)  # 150 - 95 = 55

    def test_error_tipo_desconocido(self):
        """Debe fallar si pido un tipo de cable que no existe"""
        with self.assertRaises(ValueError):
            seleccionar_cable(100, "TIPO_INVENTADO_XYZ")


if __name__ == "__main__":
    unittest.main()
