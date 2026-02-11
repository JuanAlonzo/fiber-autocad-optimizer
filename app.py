import tkinter as tk
from optimizer import verificar_entorno
from interface.view import FiberUI
from interface.controller import FiberController

if __name__ == "__main__":
    verificar_entorno()

    root = tk.Tk()

    view = FiberUI(root)
    controller = FiberController(view)

    root.mainloop()
