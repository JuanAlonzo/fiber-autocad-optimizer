import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import threading
import sys
import os

from optimizer import logger


class TextHandler(logging.Handler):
    """
    Clase mágica que redirige los logs a un widget de texto de Tkinter.
    """

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.configure(state="disabled")
            self.text_widget.yview(tk.END)  # Auto-scroll

        self.text_widget.after(0, append)


class FiberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fiber AutoCAD Optimizer v0.1")
        self.root.geometry("600x500")

        # --- 1. Marco Principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Encabezado
        lbl_title = ttk.Label(
            main_frame,
            text="Optimización de Fibra Óptica",
            font=("Segoe UI", 14, "bold"),
        )
        lbl_title.pack(pady=(0, 10))

        # --- 2. Área de Logs (ScrolledText) ---
        log_frame = ttk.LabelFrame(main_frame, text=" Registro de Eventos ", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.txt_log = scrolledtext.ScrolledText(
            log_frame, state="disabled", height=10, font=("Consolas", 9)
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # --- 3. Botones ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_run = ttk.Button(
            btn_frame, text="EJECUTAR OPTIMIZACIÓN", command=self.iniciar_proceso
        )
        self.btn_run.pack(side=tk.RIGHT, padx=5)

        btn_clear = ttk.Button(btn_frame, text="Limpiar Log", command=self.limpiar_log)
        btn_clear.pack(side=tk.RIGHT)

        # --- 4. Configurar Redirección de Logs ---
        self.setup_gui_logging()

        logger.info("Interfaz iniciada correctamente.")
        logger.info("Esperando orden del usuario...")

    def setup_gui_logging(self):
        # Crear nuestro handler personalizado
        text_handler = TextHandler(self.txt_log)
        text_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
            )
        )

        # Añadirlo al logger del optimizer
        logger.addHandler(text_handler)

    def limpiar_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.configure(state="disabled")

    def iniciar_proceso(self):
        # AQUÍ HAREMOS LA MAGIA DEL HILO EN LA FASE 2
        logger.info(">>> Botón presionado. (Lógica pendiente de conexión)")


if __name__ == "__main__":
    root = tk.Tk()
    # Intentar poner icono si existe (opcional)
    # try: root.iconbitmap("icono.ico")
    # except: pass
    app = FiberApp(root)
    root.mainloop()
