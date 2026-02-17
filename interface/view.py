import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import socket
from datetime import datetime
from typing import Optional, TYPE_CHECKING

try:
    from optimizer import FECHA_EXPIRACION
except ImportError:
    FECHA_EXPIRACION = datetime(2026, 12, 31)

if TYPE_CHECKING:
    from .controller import FiberController

# Configuración global de estilo
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class FiberUI(ctk.CTk):
    """
    Interfaz Gráfica con CustomTkinter.
    """

    def __init__(self, controller: Optional["FiberController"] = None):
        super().__init__()

        self.controller = controller

        self.title("Fiber AutoCAD Optimizer v2.5 - Enterprise")
        self.geometry("600x850")
        self.minsize(550, 650)

        # Colores personalizados
        self.color_bg_main = "#F0F0F0"
        self.color_frame_bg = "#D9D9D9"
        self.color_btn_primary = "#73899E"
        self.color_btn_hover = "#5A6E80"
        self.color_text_header = "#2B2B2B"

        self.configure(fg_color=self.color_bg_main)

        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Variables de Control
        self.var_debug_ruta = tk.BooleanVar(value=True)
        self.var_capas = tk.BooleanVar(value=True)
        self.var_labels = tk.BooleanVar(value=True)
        self.var_errores = tk.BooleanVar(value=True)
        self.var_csv = tk.BooleanVar(value=True)
        self.var_config_path = tk.StringVar(value="Automatico (config.yaml)")

        # Variables internas de UI
        self.var_status = tk.StringVar(value="Sistema listo...")

        # Layout Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Configuración
        self.grid_rowconfigure(1, weight=1)  # Cuerpo Principal
        self.grid_rowconfigure(2, weight=0)  # Footer

        # Construcción de la Interfaz
        self._setup_config_section()
        self._setup_main_body()
        self._setup_footer()

    def set_controller(self, controller: "FiberController"):
        self.controller = controller

    # CONSTRUCCIÓN DE LA UI
    # ----------------------

    def _setup_config_section(self):
        """Panel superior para cargar configuración."""
        frame = ctk.CTkFrame(self, fg_color=self.color_frame_bg, corner_radius=15)
        frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        frame.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            frame,
            text="Configuracion",
            font=("Roboto", 12, "bold"),
            text_color=self.color_text_header,
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))

        # Entry (Solo lectura visual)
        entry = ctk.CTkEntry(
            frame,
            textvariable=self.var_config_path,
            height=35,
            corner_radius=8,
            border_width=0,
            fg_color="white",
            state="disabled",
        )
        entry.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Botón Cargar
        btn = ctk.CTkButton(
            frame,
            text="Cargar config",
            width=120,
            height=35,
            fg_color=self.color_btn_primary,
            hover_color=self.color_btn_hover,
            corner_radius=8,
            font=("Roboto", 13, "bold"),
            command=self._on_click_cargar_config,
        )
        btn.grid(row=1, column=1, padx=(0, 15), pady=(5, 15))

    def _setup_main_body(self):
        """Contenedor central: Opciones/Log a la izquierda, Herramientas a la derecha."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)

        main_frame.grid_columnconfigure(0, weight=1)  # Columna Izquierda (Expandible)
        main_frame.grid_columnconfigure(1, weight=0)  # Columna Derecha (Fija)
        main_frame.grid_rowconfigure(0, weight=1)  # Expansión vertical

        #  COLUMNA IZQUIERDA
        left_col = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)  # El log se lleva el espacio extra

        # Opciones
        f_opts = ctk.CTkFrame(left_col, fg_color=self.color_frame_bg, corner_radius=15)
        f_opts.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(
            f_opts,
            text="Opciones de Procesamiento",
            font=("Roboto", 12, "bold"),
            text_color=self.color_text_header,
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self._add_checkbox(f_opts, "Dibujar ruta (Magenta)", self.var_debug_ruta)
        self._add_checkbox(f_opts, "Cambiar Capa (Default)", self.var_capas)
        self._add_checkbox(f_opts, "Etiquetas inteligentes", self.var_labels)
        self._add_checkbox(f_opts, "Errores topologicos", self.var_errores)
        self._add_checkbox(f_opts, "Reporte CSV", self.var_csv)
        ctk.CTkLabel(f_opts, text="", height=5).pack()

        # Logs de Ejecución
        f_log = ctk.CTkFrame(left_col, fg_color=self.color_frame_bg, corner_radius=15)
        f_log.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        h_log = ctk.CTkFrame(f_log, fg_color="transparent")
        h_log.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(
            h_log,
            text="Registro de ejecucion",
            font=("Roboto", 13, "bold"),
            text_color=self.color_text_header,
        ).pack(side="left")
        ctk.CTkButton(
            h_log,
            text="Limpiar",
            width=60,
            height=20,
            fg_color=self.color_btn_primary,
            font=("Roboto", 10),
            command=self._clear_logs,
        ).pack(side="right")

        self.txt_log = ctk.CTkTextbox(
            f_log,
            corner_radius=8,
            fg_color="#F9F9F9",
            text_color="black",
            font=("Consolas", 11),
        )
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.txt_log.insert("0.0", "Esperando inicio del proceso...\n")

        # Zona de Acción
        f_action = ctk.CTkFrame(left_col, fg_color="transparent")
        f_action.grid(row=2, column=0, sticky="ew")
        f_action.grid_columnconfigure(0, weight=1)

        self.btn_run = ctk.CTkButton(
            f_action,
            text="Iniciar Proceso",
            height=45,
            fg_color=self.color_btn_primary,
            hover_color=self.color_btn_hover,
            corner_radius=10,
            font=("Roboto", 16, "bold"),
            command=self._on_click_iniciar,
        )
        self.btn_run.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # BARRA DE PROGRESO
        self.progress = ctk.CTkProgressBar(f_action, height=12, corner_radius=5)
        self.progress.set(0)
        self.progress.configure(progress_color="#2E5C85")
        self.progress.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        lbl_st = ctk.CTkLabel(
            f_action,
            textvariable=self.var_status,
            font=("Roboto", 11, "italic"),
            text_color="#555",
        )
        lbl_st.grid(row=2, column=0, pady=(0, 0))

        #  COLUMNA DERECHA (HERRAMIENTAS)
        right_col = ctk.CTkFrame(
            main_frame, fg_color=self.color_frame_bg, corner_radius=15, width=200
        )
        right_col.grid(row=0, column=1, rowspan=3, sticky="ns")
        right_col.grid_propagate(False)

        ctk.CTkLabel(
            right_col,
            text="Diagnostico",
            font=("Roboto", 12, "bold"),
            text_color=self.color_text_header,
        ).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(
            right_col,
            text="Herramientas para\ndepurar en el dibujo.",
            font=("Roboto", 11),
            text_color="#555",
            justify="left",
        ).pack(anchor="w", padx=15, pady=(0, 15))

        self._add_tool_btn(right_col, "Visualizar Grafo", "grafo")
        self._add_tool_btn(right_col, "Asociar Hubs", "asociar_hubs")
        self._add_tool_btn(right_col, "Analizar FATs", "analizar_fat")
        self._add_tool_btn(right_col, "Inventario Bloques", "inventario")
        self._add_tool_btn(right_col, "Visualizar Extremos", "extremos")

        ctk.CTkButton(
            right_col,
            text="DISABLED",
            height=35,
            fg_color="#9AA5B1",
            state="disabled",
            corner_radius=8,
        ).pack(fill="x", padx=15, pady=8)

    def _setup_footer(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        pc_name = socket.gethostname()
        try:
            dias = (FECHA_EXPIRACION - datetime.now()).days
        except Exception:
            dias = 0

        lbl_lic = ctk.CTkLabel(
            frame,
            text=f"Licencia: ACTIVADA | Expira en {dias} dias",
            font=("Roboto", 11),
            text_color="green",
        )
        lbl_lic.pack(side="right", padx=(0, 10))

        lbl_pc = ctk.CTkLabel(
            frame,
            text=f"PC:{pc_name}",
            font=("Roboto", 12, "bold"),
            text_color="#2E5C85",
        )
        lbl_pc.pack(side="right", padx=(0, 5))

    # MÉTODOS AUXILIARES Y CONEXIONES
    # --------------------------------

    def _add_checkbox(self, parent, text, variable):
        cb = ctk.CTkCheckBox(
            parent,
            text=text,
            variable=variable,
            checkbox_height=20,
            checkbox_width=20,
            corner_radius=5,
            fg_color=self.color_btn_primary,
            hover_color=self.color_btn_hover,
            font=("Roboto", 12),
        )
        cb.pack(anchor="w", padx=15, pady=5)

    def _add_tool_btn(self, parent, text, tool_key):
        btn = ctk.CTkButton(
            parent,
            text=text,
            height=35,
            fg_color=self.color_btn_primary,
            hover_color=self.color_btn_hover,
            corner_radius=8,
            font=("Roboto", 12, "bold"),
            command=lambda: self._ejecutar_herramienta(tool_key),
        )
        btn.pack(fill="x", padx=15, pady=8)

    def _on_click_cargar_config(self):
        if self.controller:
            self.controller.cargar_config()
        else:
            self.log_message("Controlador desconectado.", "ERROR")

    def _on_click_iniciar(self):
        if self.controller:
            self.controller.iniciar_proceso_principal()
        else:
            self.log_message("Controlador desconectado.", "ERROR")

    def _ejecutar_herramienta(self, tool_name):
        if self.controller:
            self.controller.ejecutar_herramienta(tool_name)
        else:
            self.log_message(f"Controlador desconectado ({tool_name}).", "ERROR")

    def _clear_logs(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("0.0", "end")
        self.txt_log.configure(state="disabled")
        self.log_message("--- Logs Limpiados ---")

    #  API PÚBLICA PARA EL CONTROLADOR

    def ask_file(self):
        return filedialog.askopenfilename(filetypes=[("YAML Config", "*.yaml")])

    def update_config_label(self, text):
        self.var_config_path.set(text)

    def log_message(self, msg, level_name="INFO"):
        prefix = (
            "❌ "
            if level_name == "ERROR"
            else "⚠️ "
            if level_name == "WARNING"
            else "ℹ️ "
        )
        full_msg = f"{prefix}{msg}\n"

        def _append():
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", full_msg)
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")

        self.after(0, _append)

    def update_status(self, text, progress=None):
        """
        Actualiza el texto de estado y la barra de progreso.
        Acepta progress en rango 0-100 (int) o 0.0-1.0 (float).
        """

        def _update():
            self.var_status.set(text)
            if progress is not None:
                # CustomTkinter usa 0.0 a 1.0
                val = float(progress)
                if val > 1.0:
                    val = val / 100.0
                self.progress.set(val)

        self.after(0, _update)

    def toggle_run_button(self, state):
        st = "normal" if state else "disabled"
        color = self.color_btn_primary if state else "#9AA5B1"

        def _update():
            self.btn_run.configure(state=st, fg_color=color)

        self.after(0, _update)

    def show_info(self, title, msg):
        messagebox.showinfo(title, msg)

    def show_error(self, title, msg):
        messagebox.showerror(title, msg)

    def on_close(self):
        if self.controller:
            try:
                self.controller.guardar_preferencias()
            except Exception:
                pass
        self.destroy()


if __name__ == "__main__":
    app = FiberUI()
    app.log_message("Modo prueba UI iniciado.")
    # Prueba de la barra de progreso
    app.update_status("Probando barra...", 50)
    app.mainloop()
