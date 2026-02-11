import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime
import socket

from optimizer import FECHA_EXPIRACION


class FiberUI:
    """
    Clase responsable EXCLUSIVAMENTE de la interfaz gráfica.
    No contiene lógica de negocio.
    """

    def __init__(self, root, controller=None):
        self.root = root
        self.controller = controller  # Referencia al controlador

        self.root.title("Fiber AutoCAD Optimizer v0.2.0")
        self.root.geometry("650x800")
        self.root.resizable(False, True)

        #  ESTILOS
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure(
            "Header.TLabel", font=("Segoe UI", 12, "bold"), background="#f0f0f0"
        )
        style.configure("Info.TLabel", font=("Segoe UI", 10), background="#f0f0f0")
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#555")

        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables de Control (Vinculadas a la UI)
        self.var_grafo = tk.BooleanVar(value=False)
        self.var_capas = tk.BooleanVar(value=True)
        self.var_debug_ruta = tk.BooleanVar(value=True)
        self.var_labels = tk.BooleanVar(value=True)
        self.var_errores = tk.BooleanVar(value=True)
        self.var_csv = tk.BooleanVar(value=True)

        # Construccion de la UI
        self._setup_header()
        self._add_separator()
        self._setup_config_ui()
        self._setup_tools_ui()
        self._setup_options_ui()
        self._setup_footer_ui()
        self._setup_logs_ui()

    def set_controller(self, controller):
        """Permite asignar el controlador después de inicializar."""
        self.controller = controller

    # --- CONSTRUCCION DE WIDGETS ---

    def _setup_header(self):
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=(0, 10))

        lbl_icon = ttk.Label(
            frame, text="👤", font=("Segoe UI", 32), background="#f0f0f0"
        )
        lbl_icon.pack(side=tk.LEFT, padx=(0, 15))

        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X)

        pc_name = socket.gethostname()
        dias_restantes = (FECHA_EXPIRACION - datetime.now()).days
        color_lic = "green" if dias_restantes > 30 else "red"

        ttk.Label(info_frame, text="Perfil de Usuario", style="Header.TLabel").pack(
            anchor="w"
        )
        ttk.Label(info_frame, text=f"PC: {pc_name}", style="Info.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            info_frame,
            text=f"Licencia: ACTIVADA | Expira en {dias_restantes} días",
            style="Info.TLabel",
            foreground=color_lic,
        ).pack(anchor="w")

    def _setup_config_ui(self):
        frame = ttk.LabelFrame(self.main_frame, text=" Configuración ", padding=10)
        frame.pack(fill=tk.X, pady=5)

        self.lbl_config_path = ttk.Label(
            frame, text="Automático (config.yaml)", foreground="gray"
        )
        self.lbl_config_path.pack(fill=tk.X, pady=(0, 5))

        # Llama al controlador
        btn = ttk.Button(
            frame,
            text="Seleccionar Config",
            command=lambda: self.controller.cargar_config(),
        )
        btn.pack(anchor="e")

    def _setup_options_ui(self):
        frame = ttk.LabelFrame(
            self.main_frame, text=" Opciones de Procesamiento ", padding=10
        )
        frame.pack(fill=tk.X, pady=5)

        # Checkboxes vinculados a self.var_...
        ttk.Checkbutton(
            frame,
            text="Dibujar Grafo Completo (Pasar a boton)",
            variable=self.var_grafo,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame,
            text="Dibujar Ruta Calculada (Línea Magenta)",
            variable=self.var_debug_ruta,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame,
            text="Cambiar capas [En desarrollo]",
            variable=self.var_capas,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame,
            text="Insertar etiquetas inteligentes (Por Defecto)",
            variable=self.var_labels,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame,
            text="Marcar Errores Topológicos (Círculos Rojos)",  # Checkbox o Boton?
            variable=self.var_errores,
        ).pack(anchor="w")

        ttk.Checkbutton(
            frame,
            text="Generar Reporte CSV automático (Por Defecto)",
            variable=self.var_csv,
        ).pack(anchor="w")

    def _setup_tools_ui(self):
        frame = ttk.LabelFrame(
            self.main_frame, text=" Herramientas de Diagnóstico ", padding=10
        )
        frame.pack(fill=tk.X, pady=5)

        opts = {"padx": 5, "pady": 5, "sticky": "ew"}
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        # Botones conectados al controlador
        ttk.Button(frame, text="Visualizar Grafo", state="disabled").grid(
            row=0, column=0, **opts
        )

        ttk.Button(
            frame,
            text="Asociar Hubs [En desarrollo]",  # (Seleccion por Defecto)
            state="disabled",
        ).grid(row=0, column=1, **opts)

        ttk.Button(
            frame,
            text="Modificar Atributos FAT",  # FAT[01,101,02] 202 <- Ejemplo
            state="disabled",
        ).grid(row=0, column=2, **opts)

        ttk.Button(
            frame,
            text="Listar Bloques Encontrados",
            command=lambda: self.controller.ejecutar_herramienta("inventario"),
        ).grid(row=1, column=0, **opts)

        ttk.Button(frame, text="Mutar Capas (Checkbox)", state="disabled").grid(
            row=1, column=1, **opts
        )

        ttk.Button(
            frame,
            text="Visualizar Extremos",  # (Marcar INI/FIN con círculos verde/rojo)
            command=lambda: self.controller.ejecutar_herramienta("extremos"),
        ).grid(row=1, column=2, **opts)

    def _setup_logs_ui(self):
        frame = ttk.LabelFrame(
            self.main_frame, text=" Registro de Ejecución ", padding=5
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.txt_log = scrolledtext.ScrolledText(
            frame, state="disabled", height=8, font=("Consolas", 8)
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def _setup_footer_ui(self):
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=5, side=tk.BOTTOM)

        self.btn_run = ttk.Button(
            frame,
            text=" EJECUTAR ",
            command=lambda: self.controller.iniciar_proceso_principal(),
        )
        self.btn_run.pack(fill=tk.X, pady=(0, 5), ipady=5)

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.lbl_status = ttk.Label(
            frame, text="Listo.", style="Status.TLabel", anchor="center"
        )
        self.lbl_status.pack(fill=tk.X)

    def _add_separator(self):
        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=5)

    #  METODOS PARA EL CONTROLADOR

    def update_status(self, text, progress=None):
        """Actualiza la barra de estado de forma segura."""

        def _update():
            self.lbl_status.config(text=text)
            if progress is not None:
                self.progress["value"] = progress

        self.root.after(0, _update)

    def log_message(self, msg):
        """Inserta texto en el log."""

        def _append():
            self.txt_log.configure(state="normal")
            self.txt_log.insert(tk.END, msg + "\n")
            self.txt_log.configure(state="disabled")
            self.txt_log.yview(tk.END)

        self.root.after(0, _append)

    def toggle_run_button(self, state):
        """Habilita/Deshabilita el botón principal."""
        st = "normal" if state else "disabled"
        self.root.after(0, lambda: self.btn_run.config(state=st))

    def update_config_label(self, text):
        self.lbl_config_path.config(text=text, foreground="black")

    def show_info(self, title, msg):
        messagebox.showinfo(title, msg)

    def show_error(self, title, msg):
        messagebox.showerror(title, msg)

    def ask_file(self):
        return filedialog.askopenfilename(filetypes=[("YAML Config", "*.yaml")])
