from .topology import distancia_euclidiana


def point_to_key(point, tolerance=0.01):
    """
    Convierte coordenadas flotantes a un string único (Key) para el grafo.
    Redondea según la tolerancia para unir puntos muy cercanos (Snap).
    """
    # Redondeamos para que (100.001, 200) sea igual a (100.002, 200)
    x = round(point[0] / tolerance) * tolerance
    y = round(point[1] / tolerance) * tolerance
    return (x, y)  # Retornamos tupla redondeada


class NetworkGraph:
    def __init__(self, tolerance=0.1):
        self.adj = {}  #  {nodo: [(vecino, peso), ...]}
        self.nodes = {}  # {key_nodo: (x, y) real}
        self.tolerance = tolerance

    def add_line(self, p1, p2):
        """Agrega una línea física al grafo virtual."""
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

    def find_nearest_node(self, point, max_radius=5.0):
        """Busca el nodo de la red más cercano a un equipo."""
        best_node = None
        min_dist = float("inf")

        for key, coords in self.nodes.items():
            # Optimización simple: caja rápida
            if abs(point[0] - coords[0]) > max_radius:
                continue
            if abs(point[1] - coords[1]) > max_radius:
                continue

            d = distancia_euclidiana(point, coords)
            if d < min_dist:
                min_dist = d
                best_node = key

        if min_dist <= max_radius:
            return best_node, min_dist
        return None, None

    def get_path_length(self, start_node, end_node):
        """
        Algoritmo Dijkstra simple para encontrar la distancia más corta.
        Retorna la distancia total o None si no hay camino.
        """
        import heapq

        # Cola de prioridad: (distancia_acumulada, nodo_actual)
        queue = [(0, start_node)]
        visited = set()

        while queue:
            current_dist, current_node = heapq.heappop(queue)

            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node == end_node:
                return current_dist

            if current_node in self.adj:
                for neighbor, weight in self.adj[current_node]:
                    if neighbor not in visited:
                        heapq.heappush(queue, (current_dist + weight, neighbor))

        return None  # No hay camino (islas separadas)
