import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime
import socket
from typing import TYPE_CHECKING, Optional
from optimizer import FECHA_EXPIRACION

if TYPE_CHECKING:
    from .controller import FiberController

# --- PALETA DE COLORES (Basada en la maqueta) ---
COLOR_BG_MAIN = "#F4F7F6"  # Fondo general gris claro
COLOR_BG_PANEL = "#FFFFFF"  # Fondo blanco de paneles
COLOR_HEADER_BG = "#2C3E50"  # Azul oscuro cabecera
COLOR_HEADER_TXT = "#ECF0F1"  # Texto claro cabecera
COLOR_ACCENT_GREEN = "#27AE60"  # Verde botón principal
COLOR_ACCENT_HOVER = "#2ECC71"  # Verde hover
COLOR_TXT_PRIMARY = "#2C3E50"  # Texto oscuro principal
COLOR_TXT_SECONDARY = "#7F8C8D"  # Texto gris secundario
COLOR_BORDER = "#BDC3C7"  # Bordes suaves


class FiberUI:
    """
    Interfaz Gráfica Moderna (Tkinter).
    Diseño basado en maqueta de dos columnas.
    """

    def __init__(self, root: tk.Tk, controller: Optional["FiberController"] = None):
        self.root = root
        self.controller = controller

        self.root.title("Fiber AutoCAD Optimizer v2.5 - Enterprise")
        self.root.geometry("900x750")
        self.root.minsize(850, 700)  # Corrección aplicada aquí también
        self.root.configure(bg=COLOR_BG_MAIN)

        # Variables
        self.var_debug_ruta = tk.BooleanVar(value=True)
        self.var_capas = tk.BooleanVar(value=True)
        self.var_labels = tk.BooleanVar(value=True)
        self.var_errores = tk.BooleanVar(value=True)
        self.var_csv = tk.BooleanVar(value=True)

        self._setup_styles()
        self._setup_header()

        # Layout Principal
        self.content_frame = ttk.Frame(root, style="Main.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.content_frame.columnconfigure(0, weight=4, uniform="cols")
        self.content_frame.columnconfigure(1, weight=6, uniform="cols")
        self.content_frame.rowconfigure(0, weight=1)

        self._setup_left_column(self.content_frame)
        self._setup_right_column(self.content_frame)
        self._setup_footer()

    def set_controller(self, controller: "FiberController"):
        self.controller = controller

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=COLOR_BG_MAIN)
        style.configure(
            "TLabel",
            background=COLOR_BG_MAIN,
            foreground=COLOR_TXT_PRIMARY,
            font=("Segoe UI", 10),
        )
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure(
            "TCheckbutton",
            background=COLOR_BG_PANEL,
            font=("Segoe UI", 10),
            focuscolor=COLOR_BG_PANEL,
        )
        style.configure("Panel.TFrame", background=COLOR_BG_PANEL, relief="flat")
        style.configure("Main.TFrame", background=COLOR_BG_MAIN)

        style.configure(
            "HeaderTitle.TLabel",
            background=COLOR_HEADER_BG,
            foreground=COLOR_HEADER_TXT,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "HeaderSub.TLabel",
            background=COLOR_HEADER_BG,
            foreground="#BDC3C7",
            font=("Segoe UI", 10),
        )
        style.configure(
            "PanelTitle.TLabel",
            background=COLOR_BG_PANEL,
            foreground=COLOR_TXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "PanelSub.TLabel",
            background=COLOR_BG_PANEL,
            foreground=COLOR_TXT_SECONDARY,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Status.TLabel",
            background=COLOR_BG_MAIN,
            foreground=COLOR_TXT_SECONDARY,
            font=("Segoe UI", 9),
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 12, "bold"),
            background=COLOR_ACCENT_GREEN,
            foreground="white",
            borderwidth=0,
            focuscolor=COLOR_ACCENT_GREEN,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLOR_ACCENT_HOVER), ("disabled", "#95A5A6")],
        )

        style.configure("Tool.TButton", font=("Segoe UI", 9), padding=10)

    def _setup_header(self):
        header_frame = tk.Frame(self.root, bg=COLOR_HEADER_BG, height=80, padx=20)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        lbl_icon = tk.Label(
            header_frame,
            text="⚡",
            font=("Segoe UI", 28),
            bg=COLOR_HEADER_BG,
            fg=COLOR_ACCENT_GREEN,
        )
        lbl_icon.pack(side=tk.LEFT)

        title_frame = tk.Frame(header_frame, bg=COLOR_HEADER_BG)
        title_frame.pack(side=tk.LEFT, padx=15, pady=15)
        ttk.Label(
            title_frame,
            text="Optimizador de Redes de Fibra",
            style="HeaderTitle.TLabel",
        ).pack(anchor="w")

        pc_name = socket.gethostname()
        try:
            dias = (FECHA_EXPIRACION - datetime.now()).days
        except Exception:
            dias = 0
        ttk.Label(
            title_frame,
            text=f"Estación: {pc_name} | Licencia PRO ({dias} días)",
            style="HeaderSub.TLabel",
        ).pack(anchor="w")

        status_frame = tk.Frame(header_frame, bg=COLOR_HEADER_BG)
        status_frame.pack(side=tk.RIGHT, pady=20)
        tk.Label(
            status_frame,
            text="●",
            fg=COLOR_ACCENT_GREEN,
            bg=COLOR_HEADER_BG,
            font=("Segoe UI", 14),
        ).pack(side=tk.LEFT)
        ttk.Label(
            status_frame, text=" Sistema Conectado", style="HeaderSub.TLabel"
        ).pack(side=tk.LEFT)

    def _setup_left_column(self, parent):
        left_frame = ttk.Frame(parent, style="Main.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        p_config = self._create_panel(left_frame, "CONFIGURACIÓN", "📂")
        self.lbl_config_path = ttk.Label(
            p_config,
            text="config.yaml (Por defecto)",
            style="PanelSub.TLabel",
            wraplength=250,
        )
        self.lbl_config_path.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(
            p_config,
            text="Seleccionar Archivo...",
            command=lambda: self.controller.cargar_config(),
        ).pack(fill=tk.X)

        p_options = self._create_panel(left_frame, "OPCIONES DE PROCESAMIENTO", "⚙️")
        opts_container = ttk.Frame(p_options, style="Panel.TFrame")
        opts_container.pack(fill=tk.BOTH, expand=True)

        self._add_checkbox(
            opts_container, "Dibujar ruta (Magenta)", self.var_debug_ruta, "〰️"
        )
        self._add_checkbox(
            opts_container, "Cambiar capas (Normalizar)", self.var_capas, "📚"
        )
        self._add_checkbox(
            opts_container, "Insertar etiquetas inteligentes", self.var_labels, "🏷️"
        )
        self._add_checkbox(
            opts_container, "Marcar errores topológicos", self.var_errores, "⭕"
        )
        self._add_checkbox(opts_container, "Generar reporte CSV", self.var_csv, "📊")

    def _setup_right_column(self, parent):
        right_frame = ttk.Frame(parent, style="Main.TFrame")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        p_tools = self._create_panel(right_frame, "HERRAMIENTAS DE DIAGNÓSTICO", "🛠️")

        tools_grid = ttk.Frame(p_tools, style="Panel.TFrame")
        tools_grid.pack(fill=tk.BOTH, expand=True)
        tools_grid.columnconfigure((0, 1), weight=1)

        # --- CORRECCIÓN AQUÍ: Separamos estilo de grid ---
        # Opciones para el .grid() (posicionamiento)
        grid_opts = {"sticky": "ew", "padx": 5, "pady": 5}
        # Estilo para el constructor (visual)
        btn_style = "Tool.TButton"

        # Fila 0
        self.btn_debug_graph = ttk.Button(
            tools_grid,
            text="🕸️ Visualizar Grafo Vial",
            style=btn_style,
            command=lambda: self.controller.ejecutar_herramienta("grafo"),
        )
        self.btn_debug_graph.grid(row=0, column=0, **grid_opts)

        self.btn_vis_extr = ttk.Button(
            tools_grid,
            text="↔️ Visualizar Extremos",
            style=btn_style,
            command=lambda: self.controller.ejecutar_herramienta("extremos"),
        )
        self.btn_vis_extr.grid(row=0, column=1, **grid_opts)

        # Fila 1
        self.btn_list_blocks = ttk.Button(
            tools_grid,
            text="📋 Inventario Bloques",
            style=btn_style,
            command=lambda: self.controller.ejecutar_herramienta("inventario"),
        )
        self.btn_list_blocks.grid(row=1, column=0, **grid_opts)

        self.btn_analizar_fat = ttk.Button(
            tools_grid,
            text="🔎 Analizar FATs",
            style=btn_style,
            command=lambda: self.controller.ejecutar_herramienta("analizar_fat"),
        )
        self.btn_analizar_fat.grid(row=1, column=1, **grid_opts)

        # Fila 2
        self.btn_asociar_hubs = ttk.Button(
            tools_grid,
            text="🔗 Asociar Hubs <-> Texto",
            style=btn_style,
            command=lambda: self.controller.ejecutar_herramienta("asociar_hubs"),
        )
        self.btn_asociar_hubs.grid(row=2, column=0, columnspan=2, **grid_opts)

        # --- LOGS ---
        p_logs_container = ttk.Frame(right_frame, style="Panel.TFrame", padding=1)
        p_logs_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        p_logs = ttk.Frame(p_logs_container, style="Panel.TFrame", padding=15)
        p_logs.pack(fill=tk.BOTH, expand=True)

        log_header = ttk.Frame(p_logs, style="Panel.TFrame")
        log_header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(
            log_header, text="📜 REGISTRO DE EJECUCIÓN", style="PanelTitle.TLabel"
        ).pack(side=tk.LEFT)

        btn_clear = ttk.Button(
            log_header, text="🗑️ Limpiar", style="Tool.TButton", command=self._clear_logs
        )
        btn_clear.pack(side=tk.RIGHT)

        self.txt_log = scrolledtext.ScrolledText(
            p_logs,
            state="disabled",
            height=10,
            font=("Consolas", 9),
            bg=COLOR_BG_MAIN,
            relief="flat",
            padx=5,
            pady=5,
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        self._setup_log_tags()

    def _setup_footer(self):
        footer_frame = tk.Frame(
            self.root, bg=COLOR_BG_MAIN, height=100, padx=20, pady=10
        )
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        self.btn_run = ttk.Button(
            footer_frame,
            text="🚀 EJECUTAR OPTIMIZACIÓN",
            style="Accent.TButton",
            command=lambda: self.controller.iniciar_proceso_principal(),
        )
        self.btn_run.pack(fill=tk.X, ipady=10, pady=(0, 10))

        self.progress = ttk.Progressbar(footer_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.lbl_status = ttk.Label(
            footer_frame,
            text="Sistema listo. Esperando órdenes.",
            style="Status.TLabel",
            anchor="center",
        )
        self.lbl_status.pack(fill=tk.X)

    # --- UTILIDADES VISUALES ---
    def _create_panel(self, parent, title, icon=""):
        outer = ttk.Frame(parent, style="Panel.TFrame", padding=1)
        outer.pack(fill=tk.BOTH, expand=False, pady=(0, 20))
        inner = ttk.Frame(outer, style="Panel.TFrame", padding=15)
        inner.pack(fill=tk.BOTH, expand=True)
        title_txt = f"{icon} {title}" if icon else title
        ttk.Label(inner, text=title_txt, style="PanelTitle.TLabel").pack(
            anchor="w", pady=(0, 15)
        )
        return inner

    def _add_checkbox(self, parent, text, variable, icon=""):
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.pack(fill=tk.X, pady=5)
        if icon:
            ttk.Label(frame, text=icon, style="PanelSub.TLabel").pack(
                side=tk.LEFT, padx=(0, 5)
            )
        ttk.Checkbutton(frame, text=text, variable=variable, style="TCheckbutton").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    def _setup_log_tags(self):
        self.txt_log.tag_config("INFO", foreground=COLOR_TXT_PRIMARY)
        self.txt_log.tag_config("WARNING", foreground="#D35400")
        self.txt_log.tag_config(
            "ERROR", foreground="#C0392B", font=("Consolas", 9, "bold")
        )
        self.txt_log.tag_config(
            "CRITICAL",
            foreground="white",
            background="#C0392B",
            font=("Consolas", 9, "bold"),
        )

    def update_status(self, text, progress=None):
        def _update():
            self.lbl_status.config(text=text)
            if progress is not None:
                self.progress["value"] = progress

        self.root.after(0, _update)

    def log_message(self, msg, level_name="INFO"):
        def _append():
            self.txt_log.configure(state="normal")
            self.txt_log.insert(tk.END, msg + "\n", level_name)
            self.txt_log.configure(state="disabled")
            self.txt_log.yview(tk.END)

        self.root.after(0, _append)

    def toggle_run_button(self, state):
        st = "normal" if state else "disabled"
        style = "Accent.TButton" if state else "TButton"
        self.root.after(0, lambda: self.btn_run.config(state=st, style=style))

    def update_config_label(self, text):
        self.lbl_config_path.config(text=text, foreground=COLOR_TXT_PRIMARY)

    def show_info(self, title, msg):
        messagebox.showinfo(title, msg)

    def show_error(self, title, msg):
        messagebox.showerror(title, msg)

    def ask_file(self):
        return filedialog.askopenfilename(filetypes=[("YAML Config", "*.yaml")])

    def _clear_logs(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")
        self.log_message("--- Logs Limpiados ---", "INFO")
