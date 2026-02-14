import threading
import os
import logging
import pythoncom
from typing import TYPE_CHECKING, Tuple, List, Dict, Any, Optional

from optimizer import (
    extract_specific_blocks,
    NetworkGraph,
    get_acad_com,
    seleccionar_cable,
    dibujar_debug_offset,
    dibujar_circulo_error,
    calcular_ruta_completa,
    insertar_etiqueta_reserva,
    insertar_etiqueta_tramo,
    get_config,
    load_config,
    exportar_csv,
    herramienta_inventario_rapido,
    herramienta_visualizar_extremos,
    herramienta_asociar_hubs,
    herramienta_analizar_fat,
    herramienta_dibujar_grafo_vial,
    garantizar_capa_existente,
    ASI,
    SysLayers,
    logger,
)

if TYPE_CHECKING:
    from .view import FiberUI


class GUIHandler(logging.Handler):
    """Handler personalizado para redirigir logs a la Vista."""

    def __init__(self, view: "FiberUI"):
        super().__init__()
        self.view = view

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.view.log_message(msg, record.levelname)


class FiberController:
    """
    Controlador Principal (MVC).
    Orquesta la comunicación entre la Vista (Tkinter) y el Modelo (Optimizer).
    Gestiona los hilos de ejecución para no congelar la interfaz.
    """

    def __init__(self, view: "FiberUI"):
        self.view = view
        self.view.set_controller(self)  # Conectar bidireccionalmente

        # Configurar Logs
        self._setup_logging()

    def _setup_logging(self) -> None:
        handler = GUIHandler(self.view)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    #  ACCIONES

    def cargar_config(self) -> None:
        """Abre diálogo para cargar un YAML externo."""
        path = self.view.ask_file()
        if path:
            if load_config(path):
                filename = os.path.basename(path)
                self.view.update_config_label(f".../{filename}")
                self.view.show_info("Config", "Cargada correctamente.")

    def ejecutar_herramienta(self, tipo: str) -> None:
        """
        Ejecuta herramientas de diagnóstico en un hilo secundario.
        Args:
            tipo (str): Identificador de la herramienta ('inventario', 'extremos', etc.)
        """

        def _task():
            pythoncom.CoInitialize()
            try:
                self.view.update_status(f"Ejecutando {tipo}...")
                res = ""
                titulo = "Resultado"

                if tipo == "inventario":
                    res = herramienta_inventario_rapido()
                    titulo = "Inventario"
                elif tipo == "grafo":
                    res = herramienta_dibujar_grafo_vial()
                    titulo = "Grafo Vial"
                elif tipo == "extremos":
                    res = herramienta_visualizar_extremos()
                    titulo = "Extremos"
                elif tipo == "asociar_hubs":
                    res = herramienta_asociar_hubs()
                    titulo = "Asociar Hubs"
                elif tipo == "analizar_fat":
                    res = herramienta_analizar_fat()
                    titulo = "Analizar FAT"

                self.view.show_info(titulo, res)

            except Exception as e:
                logger.error(f"Error en herramienta {tipo}: {e}")
                self.view.show_error("Error", str(e))
            finally:
                self.view.update_status("Listo.")

        threading.Thread(target=_task, daemon=True).start()

    def iniciar_proceso_principal(self) -> None:
        """Lanza el hilo principal de optimización."""
        self.view.toggle_run_button(False)
        self.view.update_status("Inicializando...", 0)

        thread = threading.Thread(target=self._proceso_worker, daemon=True)
        thread.start()

    def _proceso_worker(self) -> None:
        """Lógica central de optimización."""
        pythoncom.CoInitialize()
        try:
            # Conexion
            acad, doc, msp = self._conectar_autocad()
            if not acad:
                return

            opts = self._obtener_opciones_vista()
            logger.info(" INICIANDO OPTIMIZACIÓN ")

            # Preparar capas
            self._preparar_capas(doc, opts)

            # Construir grafo y equipos
            grafo = self._construir_grafo(msp, opts)
            bloques = self._obtener_catalogo_bloques()

            # Procesar tramos
            datos_reporte, exitos = self._procesar_tramos_red(
                msp, doc, grafo, bloques, opts
            )

            # Exportar resultados
            self._exportar_resultados(datos_reporte, opts)

            # Finalizar
            self.view.update_status("Finalizado.", 100)
            self.view.show_info("Fin", f"Proceso completado.\n{exitos} tramos OK.")

        except Exception as e:
            logger.critical(f"Error Fatal: {e}")
            self.view.show_error("Error Fatal", str(e))
        finally:
            self.view.toggle_run_button(True)

    # Metodos Privados para organizar el proceso

    def _conectar_autocad(self):
        """Conecta con la instancia activa de AutoCAD."""
        self.view.update_status("Conectando AutoCAD...", 5)
        acad = get_acad_com()

        if not acad:
            logger.critical("No se detectó AutoCAD.")
            self.view.show_error("Error", "AutoCAD no está abierto.")
            return None, None, None

        return acad, acad.ActiveDocument, acad.ActiveDocument.ModelSpace

    def _obtener_opciones_vista(self) -> Dict[str, Any]:
        """Extrae la configuración de los checkboxes de la UI."""
        return {
            "audit": self.view.var_audit.get(),
            "ruta_debug": self.view.var_debug_ruta.get(),
            "etiquetas": self.view.var_labels.get(),
            "errores": self.view.var_errores.get(),
            "csv": self.view.var_csv.get(),
            "capas": self.view.var_capas.get(),
        }

    def _preparar_capas(self, doc: Any, opts: Dict[str, Any]) -> None:
        """Asegura que existan las capas necesarias."""
        self.view.update_status("Verificando capas...", 8)

        garantizar_capa_existente(doc, SysLayers.DEBUG_RUTAS, color_id=ASI.MAGENTA)
        garantizar_capa_existente(doc, SysLayers.ERRORES, color_id=ASI.ROJO)
        garantizar_capa_existente(doc, SysLayers.DEBUG_NODOS, color_id=ASI.CYAN)
        garantizar_capa_existente(doc, SysLayers.DEBUG_ARISTAS, color_id=ASI.GRIS)

        if opts["etiquetas"]:
            garantizar_capa_existente(doc, SysLayers.TEXTO_TRAMOS, color_id=ASI.AZUL)
            garantizar_capa_existente(doc, SysLayers.TEXTO_RESERVAS, color_id=ASI.CYAN)

    def _construir_grafo(self, msp: Any, opts: Dict[str, Any]) -> NetworkGraph:
        """Digitaliza la red vial y construye el grafo en memoria."""
        self.view.update_status("Analizando Red...", 10)

        CAPA_RED = get_config("rutas.capa_red_vial")
        TOLERANCIA = get_config("tolerancias.snap_grafo_vial", 0.1)
        grafo = NetworkGraph(tolerance=TOLERANCIA)

        count_lines = 0
        for i in range(msp.Count):
            try:
                obj = msp.Item(i)
                if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == CAPA_RED:
                    grafo.add_line(obj.StartPoint[:2], obj.EndPoint[:2])
                    count_lines += 1
            except Exception:
                pass

        logger.info(
            f"Grafo construido: {count_lines} linea(s), {len(grafo.nodes)} nodo(s)."
        )
        return grafo

    def _obtener_catalogo_bloques(self) -> List[Dict[str, Any]]:
        """Carga y busca los bloques de equipos configurados."""
        self.view.update_status("Buscando Equipos...", 30)
        dic_equipos = get_config("equipos", {})
        lista_todos = [item for sublist in dic_equipos.values() for item in sublist]
        bloques = extract_specific_blocks(lista_todos)
        logger.info(f"Equipos encontrados: {len(bloques)} bloque(s).")

        return bloques

    def _procesar_tramos_red(
        self, msp: Any, doc: Any, grafo: NetworkGraph, bloques: List[Dict], opts: Dict
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Itera sobre los tramos y calcula la lógica de negocio."""
        self.view.update_status("Calculando Rutas...", 40)

        CAPA_TRAMO = get_config("rutas.capa_tramos_logicos")
        tramos = [
            msp.Item(i)
            for i in range(msp.Count)
            if getattr(msp.Item(i), "ObjectName", "") == "AcDbPolyline"
            and getattr(msp.Item(i), "Layer", "").upper() == CAPA_TRAMO
        ]

        total = len(tramos)
        datos_reporte = []
        exitos = 0

        for idx, obj in enumerate(tramos):
            pct = 40 + int((idx / total) * 50)
            self.view.update_status(f"Tramo {idx + 1}/{total}", pct)

            resultado = self._procesar_un_tramo(msp, doc, obj, grafo, bloques, opts)
            if result_data := resultado:
                datos_reporte.append(result_data)
                if result_data.get("estado") == "OK":
                    exitos += 1

        return datos_reporte, exitos

    def _procesar_un_tramo(
        self,
        msp: Any,
        doc: Any,
        obj: Any,
        grafo: NetworkGraph,
        bloques: List[Dict],
        opts: Dict,
    ) -> Optional[Dict[str, Any]]:
        """Lógica unitaria para un solo tramo."""
        try:
            coords = obj.Coordinates
            if len(coords) < 4:
                return None

            p_start = (coords[0], coords[1])
            p_end = (coords[-2], coords[-1])

            dist, ruta, meta = calcular_ruta_completa(p_start, p_end, grafo, bloques)

            if not dist:
                msg = (
                    meta
                    if isinstance(meta, str)
                    else meta.get("error", "Error desconocido")
                )
                logger.warning(f"Tramo {obj.Handle}: {msg}")
                if opts["errores"]:
                    dibujar_circulo_error(msp, p_start)
                return {"handle": obj.Handle, "estado": f"ERROR: {msg}"}

            cable, res, tipo = seleccionar_cable(dist, meta["origen"], meta["destino"])

            if opts["ruta_debug"]:
                dibujar_debug_offset(msp, ruta)

            if opts["etiquetas"]:
                txt_tramo = f"{tipo} {int(cable)}m"
                insertar_etiqueta_tramo(
                    msp, ruta, txt_tramo, capa=SysLayers.TEXTO_TRAMOS
                )
                insertar_etiqueta_reserva(
                    msp, ruta[-1], res, capa=SysLayers.TEXTO_RESERVAS
                )

            if opts["capas"]:
                self._aplicar_cambio_capa(doc, obj, tipo, cable)

            return {
                "handle": obj.Handle,
                "origen": meta["origen"],
                "destino": meta["destino"],
                "longitud_real": dist,
                "cable_asignado": cable,
                "tipo_tecnico": tipo,
                "reserva": res,
                "estado": "OK",
            }

        except Exception as e:
            logger.error(f"Excepción en tramo {getattr(obj, 'Handle', '?')}: {e}")
            return None

    def _aplicar_cambio_capa(self, doc: Any, obj: Any, tipo: str, cable: float) -> None:
        """
        Intenta cambiar la capa del objeto según reglas de negocio."""
        try:
            prefijo = get_config("capas_resultados.prefijo_capa", "CABLE PRECONECT")
            # CABLE PRECONECT + 2H SM + (100M)
            nombre_capa = f"{prefijo} {tipo} ({int(cable)}M)"

            if garantizar_capa_existente(doc, nombre_capa):
                obj.Layer = nombre_capa
                obj.ConstantWidth = 0.5
                obj.LinetypeScale = 4

        except Exception as e:
            logger.warning(f"No se pudo cambiar capa en {obj.Handle}: {e}")

    def _exportar_resultados(self, datos: List[Dict], opts: Dict) -> None:
        """ "General el archivo CSV con los resultados."""
        if opts["csv"]:
            self.view.update_status("Exportando...", 95)
            exportar_csv(datos)
