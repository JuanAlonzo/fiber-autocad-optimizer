import sys
import tkinter as tk
from tkinter import messagebox
from optimizer import verificar_entorno
from optimizer.config_loader import validar_configuracion
from interface.view import FiberUI
from interface.controller import FiberController

if __name__ == "__main__":
    verificar_entorno()
    errores = validar_configuracion()

    if errores:
        root_temp = tk.Tk()
        root_temp.withdraw()
        msg = "Errores en config.yaml:\n\n" + "\n".join(errores)
        messagebox.showerror("Configuración Inválida", msg)
        root_temp.destroy()
        sys.exit(1)  # Cierra el programa

    root = tk.Tk()

    view = FiberUI(root)
    controller = FiberController(view)

    root.mainloop()
