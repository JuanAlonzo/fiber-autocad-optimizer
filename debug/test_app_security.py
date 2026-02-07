import socket
import os

pc_name = socket.gethostname().upper()
PERMITIDOS = ["HFC ALEJANDRO", "HFC ALEJANDRO-PC", "HFC-01"]


def verificar_seguridad():
    if pc_name not in PERMITIDOS:
        print(f"Acceso denegado: PC '{pc_name}' no autorizada.")
        return False
    else:
        print(f"Acceso autorizado para PC '{pc_name}'.")
        return True


def verificar_candado():
    # O el dominio de usuario
    dominio_actual = os.environ.get("USERDOMAIN", "").upper()

    if pc_name not in PERMITIDOS and dominio_actual != "MI_EMPRESA_SAC":
        print("⛔ LICENCIA NO AUTORIZADA PARA ESTE EQUIPO.")
        print(
            f"ID de Equipo: {pc_name}"
        )  # Para que te lo dicten si quieres autorizarlos
        input("Presione Enter para cerrar...")
        exit()
    else:
        print("✅ Licencia verificada. Ejecución permitida.")
        print(f"ID de Equipo: {pc_name} | Dominio: {dominio_actual}")


if __name__ == "__main__":
    verificar_candado()
