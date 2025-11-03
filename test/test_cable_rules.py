"""
Tests para cable_rules.py
Valida la lógica de selección automática de cables
"""
import sys

from optimizer import seleccionar_cable, RESERVA_MINIMA


def test_seleccionar_cable_xbox_hub():
    """Test para cables XBOX → HUB BOX (MPO 12H 300m)"""
    print("\n=== TEST: XBOX → HUB BOX ===")

    # Caso 1: Tramo corto (250m) → debe usar 300m con reserva suficiente
    cable, reserva = seleccionar_cable(250, "xbox_hub")
    print(f"✓ Tramo 250m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 300, f"Expected cable 300m, got {cable}m"
    assert reserva == 50, f"Expected reserva 50m, got {reserva}m"
    assert reserva >= RESERVA_MINIMA, "Reserva debe ser >= 10m"

    # Caso 2: Tramo muy largo (295m) → debe usar 300m con poca reserva
    cable, reserva = seleccionar_cable(295, "xbox_hub")
    print(f"✓ Tramo 295m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 300, f"Expected cable 300m, got {cable}m"
    assert reserva == 5, f"Expected reserva 5m, got {reserva}m"

    # Caso 3: Tramo que excede disponible (310m) → usa el más largo disponible
    cable, reserva = seleccionar_cable(310, "xbox_hub")
    print(f"⚠ Tramo 310m → Cable {cable}m, Reserva {reserva}m (NEGATIVA)")
    assert cable == 300, f"Expected cable 300m, got {cable}m"
    assert reserva == -10, f"Expected reserva -10m, got {reserva}m"

    print("Todos los tests de xbox_hub pasaron")


def test_seleccionar_cable_hub_fat():
    """Test para cables HUB BOX → FATs (2H con 200/150/100m)"""
    print("\nTEST: HUB BOX → FATs")

    # Caso 1: Tramo 85m → debe usar 100m (reserva 15m)
    cable, reserva = seleccionar_cable(85, "hub_fat")
    print(f"✓ Tramo 85m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 100, f"Expected cable 100m, got {cable}m"
    assert reserva == 15, f"Expected reserva 15m, got {reserva}m"
    assert reserva >= RESERVA_MINIMA, "Reserva debe ser >= 10m"

    # Caso 2: Tramo 95m → NO cumple con 100m (solo 5m), debe usar 150m
    cable, reserva = seleccionar_cable(95, "hub_fat")
    print(f"✓ Tramo 95m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 150, f"Expected cable 150m, got {cable}m"
    assert reserva == 55, f"Expected reserva 55m, got {reserva}m"
    assert reserva >= RESERVA_MINIMA, "Reserva debe ser >= 10m"

    # Caso 3: Tramo 135m → debe usar 150m (reserva 15m)
    cable, reserva = seleccionar_cable(135, "hub_fat")
    print(f"✓ Tramo 135m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 150, f"Expected cable 150m, got {cable}m"
    assert reserva == 15, f"Expected reserva 15m, got {reserva}m"

    # Caso 4: Tramo 145m → NO cumple con 150m (solo 5m), debe usar 200m
    cable, reserva = seleccionar_cable(145, "hub_fat")
    print(f"✓ Tramo 145m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 200, f"Expected cable 200m, got {cable}m"
    assert reserva == 55, f"Expected reserva 55m, got {reserva}m"

    # Caso 5: Tramo 185m → debe usar 200m (reserva 15m)
    cable, reserva = seleccionar_cable(185, "hub_fat")
    print(f"✓ Tramo 185m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 200, f"Expected cable 200m, got {cable}m"
    assert reserva == 15, f"Expected reserva 15m, got {reserva}m"

    # Caso 6: Tramo que excede todo (210m) → usa el más largo
    cable, reserva = seleccionar_cable(210, "hub_fat")
    print(f"⚠ Tramo 210m → Cable {cable}m, Reserva {reserva}m (NEGATIVA)")
    assert cable == 200, f"Expected cable 200m, got {cable}m"
    assert reserva == -10, f"Expected reserva -10m, got {reserva}m"

    print("Todos los tests de hub_fat pasaron")


def test_seleccionar_cable_expansion():
    """Test para cables de expansión FATs (1H con 100/50m)"""
    print("\nTEST: FATs Expansión")

    # Caso 1: Tramo 35m → debe usar 50m (reserva 15m)
    cable, reserva = seleccionar_cable(35, "expansion")
    print(f"✓ Tramo 35m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 50, f"Expected cable 50m, got {cable}m"
    assert reserva == 15, f"Expected reserva 15m, got {reserva}m"

    # Caso 2: Tramo 45m → NO cumple con 50m (solo 5m), debe usar 100m
    cable, reserva = seleccionar_cable(45, "expansion")
    print(f"✓ Tramo 45m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 100, f"Expected cable 100m, got {cable}m"
    assert reserva == 55, f"Expected reserva 55m, got {reserva}m"

    # Caso 3: Tramo 85m → debe usar 100m (reserva 15m)
    cable, reserva = seleccionar_cable(85, "expansion")
    print(f"✓ Tramo 85m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 100, f"Expected cable 100m, got {cable}m"
    assert reserva == 15, f"Expected reserva 15m, got {reserva}m"

    # Caso 4: Tramo que excede (110m) → usa el más largo
    cable, reserva = seleccionar_cable(110, "expansion")
    print(f"⚠ Tramo 110m → Cable {cable}m, Reserva {reserva}m (NEGATIVA)")
    assert cable == 100, f"Expected cable 100m, got {cable}m"
    assert reserva == -10, f"Expected reserva -10m, got {reserva}m"

    print("Todos los tests de expansion pasaron")


def test_casos_limite():
    """Test de casos límite y edge cases"""
    print("\nTEST: Casos Límite")

    # Exactamente en el límite de reserva mínima
    cable, reserva = seleccionar_cable(290, "xbox_hub")
    print(
        f"✓ Tramo 290m → Cable {cable}m, Reserva {reserva}m (justo en límite)")
    assert reserva == 10, f"Expected reserva exacta de 10m, got {reserva}m"

    # Un metro menos que el límite (debe saltar al siguiente)
    cable, reserva = seleccionar_cable(91, "hub_fat")
    print(
        f"✓ Tramo 91m → Cable {cable}m, Reserva {reserva}m (salta al siguiente)")
    assert cable == 150, "Debe saltar a 150m porque 100m deja solo 9m"

    # Tramo muy corto
    cable, reserva = seleccionar_cable(5, "expansion")
    print(f"✓ Tramo 5m → Cable {cable}m, Reserva {reserva}m")
    assert cable == 50, f"Expected cable 50m, got {cable}m"
    assert reserva == 45, f"Expected reserva 45m, got {reserva}m"

    print("Todos los casos límite pasaron")


if __name__ == "__main__":
    try:
        test_seleccionar_cable_xbox_hub()
        test_seleccionar_cable_hub_fat()
        test_seleccionar_cable_expansion()
        test_casos_limite()
        print("\n" + "="*50)
        print("TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*50)
    except AssertionError as e:
        print(f"\nTEST FALLÓ: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
        sys.exit(1)
