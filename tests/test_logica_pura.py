import unittest
from optimizer.cable_rules import seleccionar_cable
from optimizer.acad_geometry import NetworkGraph, distancia_euclidiana


class TestLogicaSinCad(unittest.TestCase):
    def test_matematica_distancia(self):
        """Verifica pitágoras básico."""
        p1 = (0, 0)
        p2 = (3, 4)
        self.assertEqual(distancia_euclidiana(p1, p2), 5.0)

    def test_grafo_pathfinding(self):
        """Prueba Dijkstra en memoria."""
        g = NetworkGraph(tolerance=0.1)
        g.add_line((0, 0), (10, 0))
        g.add_line((10, 0), (10, 10))

        # Debe encontrar camino de (0,0) a (10,10) -> distancia 20
        # Ojo: necesitamos encontrar los IDs de nodo primero o usar coordenadas exactas
        # Como NetworkGraph usa coordenadas redondeadas como keys:
        node_a = g.find_nearest_node((0, 0))[0]
        node_b = g.find_nearest_node((10, 10))[0]

        dist, path = g.get_path_length(node_a, node_b)
        self.assertAlmostEqual(dist, 20.0)

    def test_reglas_cable(self):
        """Verifica que el config de cables se lea y calcule bien."""
        # Caso: XBOX->HBOX (MPO 300). Distancia 250m. Debe sobrar 50m.
        cable, res, tipo = seleccionar_cable(250.0, "X_BOX_P", "HBOX_3.5P")
        self.assertEqual(cable, 300)
        self.assertEqual(res, 50.0)
        self.assertEqual(tipo, "MPO 12H")


if __name__ == "__main__":
    unittest.main()
