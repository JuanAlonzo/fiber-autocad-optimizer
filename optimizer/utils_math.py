import math
from typing import Tuple

Point2D = Tuple[float, float]


def distancia_euclidiana(p1: Point2D, p2: Point2D) -> float:
    """Calcula la distancia euclidiana entre dos puntos en 2D."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def obtener_angulo(p1: Point2D, p2: Point2D) -> float:
    """Calcula el ángulo en grados entre dos puntos."""
    delta_y = p2[1] - p1[1]
    delta_x = p2[0] - p1[0]

    return math.atan2(delta_y, delta_x)


def obtener_angulo_legible(p1: Point2D, p2: Point2D) -> float:
    """
    Devuelve el ángulo ajustado para textos (evita que queden de cabeza).
    Usa obtener_angulo internamente.
    """
    angulo = obtener_angulo(p1, p2)
    # Si el angulo apunta hacia la izquierda (Cuadrantes II y III), rotar 180°
    if abs(angulo) > math.pi / 2:
        angulo += math.pi

    return angulo


def obtener_punto_medio(p1: Point2D, p2: Point2D) -> Point2D:
    """Calcula el punto medio entre dos puntos en 2D."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def obtener_vectores_offset(p1: Point2D, p2: Point2D, distancia: float) -> Point2D:
    """Calcula los vectores offset perpendiculares a la línea entre p1 y p2."""
    delta_x = p2[0] - p1[0]
    delta_y = p2[1] - p1[1]
    longitud = math.hypot(delta_x, delta_y)

    if longitud == 0:
        return (0, 0)

    # Dirección perpendicular (-y, x) normalizada
    # Ajustamos el signo según la dirección del texto para mantener coherencia
    angulo = math.atan2(delta_y, delta_x)
    inv = -1 if abs(angulo) > math.pi / 2 else 1

    off_x = (-delta_y / longitud) * distancia * inv
    off_y = (delta_x / longitud) * distancia * inv

    return (off_x, off_y)
