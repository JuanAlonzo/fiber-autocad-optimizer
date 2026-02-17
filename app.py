import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from optimizer import verificar_entorno, validar_configuracion
from interface.controller import FiberController
from interface.view import FiberUI

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

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

    app_view = FiberUI()

    controller = FiberController(app_view)

    app_view.set_controller(controller)

    app_view.mainloop()
