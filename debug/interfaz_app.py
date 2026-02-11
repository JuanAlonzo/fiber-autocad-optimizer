# debug/gui_prototype.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time


class FiberOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fiber AutoCAD Optimizer v1.0 - Debug Interface")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        # --- ESTILOS ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TLabel", font=("Segoe UI", 10), background="#f0f0f0")
        style.configure(
            "Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#333"
        )

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self._crear_seccion_perfil()
        self._crear_separador()
        self._crear_seccion_config()
        self._crear_separador()
        self._crear_seccion_opciones()
        self._crear_separador()
        self._crear_seccion_ejecucion()

    def _crear_seccion_perfil(self):
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=5)

        lbl_icon = ttk.Label(frame, text="👤", font=("Segoe UI", 24))
        lbl_icon.pack(side=tk.LEFT, padx=(0, 10))

        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT)

        ttk.Label(info_frame, text="Perfil de Usuario", style="Header.TLabel").pack(
            anchor="w"
        )
        ttk.Label(info_frame, text="PC: HFC-01").pack(anchor="w")
        ttk.Label(
            info_frame, text="Licencia: PRO - Expira 2026", foreground="green"
        ).pack(anchor="w")

    def _crear_seccion_config(self):
        frame = ttk.LabelFrame(self.main_frame, text=" Configuración ", padding=10)
        frame.pack(fill=tk.X, pady=10)

        self.lbl_path = ttk.Label(frame, text="config.yaml no seleccionado")
        self.lbl_path.pack(fill=tk.X, pady=(0, 5))

        btn_load = ttk.Button(
            frame, text="📂 Seleccionar Config", command=self.cargar_config
        )
        btn_load.pack(anchor="e")

    def _crear_seccion_opciones(self):
        frame = ttk.LabelFrame(self.main_frame, text=" Opciones de Debug ", padding=10)
        frame.pack(fill=tk.X, pady=10)

        self.var_grafo = tk.BooleanVar()
        self.var_layer = tk.BooleanVar(value=True)
        self.var_label = tk.BooleanVar()
        self.var_errores = tk.BooleanVar(value=True)
        self.var_csv = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            frame, text="Dibujar Grafo Completo (Lento)", variable=self.var_grafo
        ).pack(anchor="w")
        ttk.Checkbutton(
            frame, text="Cambiar capas (A polilinea TRAMO)", variable=self.var_layer
        ).pack(anchor="w")
        ttk.Checkbutton(
            frame, text="Mostrar solo etiquetas", variable=self.var_label
        ).pack(anchor="w")
        ttk.Checkbutton(
            frame,
            text="Marcar Errores Topológicos (Círculos Rojos)",
            variable=self.var_errores,
        ).pack(anchor="w")
        ttk.Checkbutton(
            frame, text="Generar Reporte CSV automático", variable=self.var_csv
        ).pack(anchor="w")

    def _crear_seccion_ejecucion(self):
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=20)

        self.btn_run = ttk.Button(
            frame, text="🚀 EJECUTAR OPTIMIZACIÓN", command=self.ejecutar_proceso
        )
        self.btn_run.pack(fill=tk.X, pady=(0, 10))

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(fill=tk.X)

        self.lbl_status = ttk.Label(
            frame, text="Listo para iniciar.", font=("Segoe UI", 9)
        )
        self.lbl_status.pack(pady=5)

    def _crear_separador(self):
        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=5)

    def cargar_config(self):
        path = filedialog.askopenfilename(filetypes=[("YAML Config", "*.yaml")])
        if path:
            self.lbl_path.config(text=f".../{path.split('/')[-1]}")

    def ejecutar_proceso(self):
        # Simulación de proceso en hilo aparte para no congelar la GUI
        self.btn_run.config(state="disabled")
        threading.Thread(target=self._proceso_simulado).start()

    def _proceso_simulado(self):
        pasos = [
            "Leyendo Red Vial...",
            "Indexando Equipos...",
            "Calculando Rutas...",
            "Generando Reporte...",
        ]
        self.progress["maximum"] = 100

        for i, paso in enumerate(pasos):
            self.root.after(0, lambda paso=paso: self.lbl_status.config(text=paso))
            time.sleep(1)  # Simular trabajo
            avance = (i + 1) * 25
            self.root.after(
                0, lambda avance=avance: self.progress.configure(value=avance)
            )

        self.root.after(
            0, lambda: self.lbl_status.config(text="✅ Proceso Finalizado Exitosamente")
        )
        self.root.after(0, lambda: self.btn_run.config(state="normal"))
        messagebox.showinfo(
            "Éxito", "Optimización completada.\nSe procesaron 134 tramos."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FiberOptimizerApp(root)
    root.mainloop()
