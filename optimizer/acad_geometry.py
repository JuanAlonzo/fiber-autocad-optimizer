"""
Módulo de Geometría y Grafos.
Gestiona la estructura de datos espacial (Grafo) de la red vial.
Realiza cálculos de ruta (Pathfinding) y snaps geométricos.
"""

from typing import Tuple, List, Dict, Optional, Any
from .utils_math import distancia_euclidiana
from .feedback_logger import logger
from .constants import Geometry

Point2D = Tuple[float, float]


def point_to_key(point: Point2D, tolerance: float) -> Tuple[float, float]:
    """
    Normaliza una coordenada aplicando un redondeo (snap) basado en tolerancia.
    Permite que puntos infinitesimalmente cercanos se consideren el mismo nodo.
    """
    if tolerance == 0:
        return point
    x = round(point[0] / tolerance) * tolerance
    y = round(point[1] / tolerance) * tolerance
    return (x, y)


class NetworkGraph:
    """
    Grafo no dirigido que representa la linea de red existente.
    Usa listas de adyacencia para almacenar conexiones y pesos (distancias).
    """

    def __init__(self, tolerance: float = 0.1):
        """
        Inicializa el grafo vacío.

        Args:
            tolerance (float): Distancia mínima para fusionar nodos (metros).
        """
        self.adj: Dict[
            Tuple[float, float], List[Tuple[Tuple[float, float], float]]
        ] = {}
        self.nodes: Dict[Tuple[float, float], Point2D] = {}
        self.tolerance = tolerance
        logger.debug(f"Inicializando Grafo con tolerancia: {tolerance}m")

    def add_line(self, p1: Point2D, p2: Point2D) -> None:
        """
        Inserta una línea física al grafo, creando nodos y aristas.
        """
        # Ignorar líneas de longitud 0
        dist = distancia_euclidiana(p1, p2)
        if dist < 1e-6:
            return

        # Obtener claves únicas (con Snap)
        k1 = point_to_key(p1, self.tolerance)
        k2 = point_to_key(p2, self.tolerance)

        # Guardar coordenadas reales (promedio o la primera que llegue)
        if k1 not in self.nodes:
            self.nodes[k1] = p1
        if k2 not in self.nodes:
            self.nodes[k2] = p2

        # Inicializar listas
        if k1 not in self.adj:
            self.adj[k1] = []
        if k2 not in self.adj:
            self.adj[k2] = []

        # Crear conexión bidireccional (calle doble sentido)
        self.adj[k1].append((k2, dist))
        self.adj[k2].append((k1, dist))

    def find_nearest_node(
        self, point: Point2D, max_radius: float = Geometry.RADIO_SNAP_DEFECTO
    ) -> Tuple[Optional[Tuple[float, float]], Optional[float]]:
        """
        Encuentra el nodo del grafo más cercano a un punto dado (ej. un Equipo).

        Returns:
            Tuple(NodeKey, Distancia): Retorna None, None si no encuentra nada en el radio.
        """
        best_node = None
        min_dist = float("inf")

        # Búsqueda lineal optimizada con caja delimitadora simple
        for key, coords in self.nodes.items():
            if abs(point[0] - coords[0]) > max_radius:
                continue
            if abs(point[1] - coords[1]) > max_radius:
                continue

            d = distancia_euclidiana(point, coords)
            if d < min_dist:
                min_dist = d
                best_node = key

        # Solo logueamos si NO encuentra nada, para depurar
        if best_node is None and min_dist > max_radius:
            logger.debug(f"No se encontró nodo cercano a {point} en radio {max_radius}")
            pass

        if min_dist <= max_radius:
            return best_node, min_dist
        return None, None

    def get_path_length(
        self, start_node: Any, end_node: Any
    ) -> Tuple[Optional[float], List[Point2D]]:
        """
        Ejecuta el algoritmo de Dijkstra para encontrar la ruta más corta.

        Returns:
            Tuple(DistanciaTotal, ListaDePuntos): (None, []) si no hay camino.
        """
        import heapq

        # Cola de prioridad: (distancia_acumulada, nodo_actual)
        queue = [(0, start_node)]
        visited = {}  # Diccionario: nodo -> (distancia, nodo_padre)

        visited[start_node] = (0, None)  # distancia, nodo_previo

        while queue:
            current_dist, current_node = heapq.heappop(queue)

            if current_node == end_node:
                # Reconstruir camino hacia atrás
                path = []
                curr = end_node
                while curr is not None:
                    path.append(self.nodes[curr])
                    _, parent = visited[curr]
                    curr = parent
                return current_dist, path[
                    ::-1
                ]  # Se invierte para tener orden Inicio->Fin

            # Si encontramos un camino más largo al que ya conocemos, ignorar
            if current_dist > visited[current_node][0]:
                continue

            if current_node in self.adj:
                for neighbor, weight in self.adj[current_node]:
                    new_dist = current_dist + weight

                    if neighbor not in visited or new_dist < visited[neighbor][0]:
                        visited[neighbor] = (new_dist, current_node)
                        heapq.heappush(queue, (new_dist, neighbor))

        return None  # No hay camino (islas separadas)
