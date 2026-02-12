import threading
import os
import logging
import pythoncom
from typing import TYPE_CHECKING

from optimizer import (
    extract_specific_blocks,
    NetworkGraph,
    get_acad_com,
    seleccionar_cable,
    dibujar_debug_offset,
    dibujar_circulo_error,
    dibujar_grafo_completo,
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

    def emit(self, record):
        msg = self.format(record)
        self.view.log_message(msg)


class FiberController:
    def __init__(self, view: "FiberUI"):
        self.view = view
        self.view.set_controller(self)  # Conectar bidireccionalmente

        # Configurar Logs
        self._setup_logging()

    def _setup_logging(self):
        handler = GUIHandler(self.view)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    #  ACCIONES

    def cargar_config(self):
        path = self.view.ask_file()
        if path:
            if load_config(path):
                filename = os.path.basename(path)
                self.view.update_config_label(f".../{filename}")
                self.view.show_info("Config", "Cargada correctamente.")

    def ejecutar_herramienta(self, tipo):
        """Ejecuta herramientas en un hilo aparte."""

        def _task():
            pythoncom.CoInitialize()
            try:
                self.view.update_status(f"Ejecutando {tipo}...")

                if tipo == "inventario":
                    res = herramienta_inventario_rapido()
                    self.view.show_info("Inventario", res)
                elif tipo == "extremos":
                    res = herramienta_visualizar_extremos()
                    self.view.show_info("Extremos", res)
                elif tipo == "asociar_hubs":
                    res = herramienta_asociar_hubs()
                    self.view.show_info("Asociar Hubs", res)
                elif tipo == "analizar_fat":
                    res = herramienta_analizar_fat()
                    self.view.show_info("Analizar FAT", res)

            except Exception as e:
                logger.error(f"Error en herramienta {tipo}: {e}")
                self.view.show_error("Error", str(e))
            finally:
                self.view.update_status("Listo.")

        threading.Thread(target=_task, daemon=True).start()

    def iniciar_proceso_principal(self):
        """Lanza el hilo principal de optimización."""
        self.view.toggle_run_button(False)
        self.view.update_status("Iniciando...", 0)

        thread = threading.Thread(target=self._proceso_worker, daemon=True)
        thread.start()

    def _proceso_worker(self):
        """Lógica pesada (Movida de app.py a aquí)."""
        pythoncom.CoInitialize()
        try:
            self.view.update_status("Conectando AutoCAD...", 5)
            logger.info(" INICIANDO OPTIMIZACIÓN ")

            acad = get_acad_com()
            if not acad:
                logger.critical("No se detectó AutoCAD.")
                self.view.show_error("Error", "AutoCAD no está abierto.")
                return

            doc = acad.ActiveDocument
            msp = doc.ModelSpace

            #  LEER PARÁMETROS DE LA VISTA
            # Accedemos a las variables de Tkinter a través de la vista
            opts = {
                "grafo": self.view.var_grafo.get(),
                "ruta_debug": self.view.var_debug_ruta.get(),
                "etiquetas": self.view.var_labels.get(),
                "errores": self.view.var_errores.get(),
                "csv": self.view.var_csv.get(),
                "capas": self.view.var_capas.get(),
            }

            # Preparacion de capas
            self.view.update_status("Verificando capas...", 8)
            garantizar_capa_existente(doc, SysLayers.DEBUG_RUTAS, color_id=ASI.MAGENTA)
            garantizar_capa_existente(doc, SysLayers.ERRORES, color_id=ASI.ROJO)
            garantizar_capa_existente(doc, SysLayers.TEXTO_TRAMOS, color_id=ASI.AZUL)
            garantizar_capa_existente(doc, SysLayers.TEXTO_RESERVAS, color_id=ASI.CYAN)

            # 1. GRAFO
            self.view.update_status("Analizando Red...", 10)
            CAPA_RED = get_config("rutas.capa_red_vial")
            grafo = NetworkGraph(
                tolerance=get_config("tolerancias.snap_grafo_vial", 0.1)
            )

            if opts["grafo"]:
                self.view.update_status("Dibujando Grafo...", 15)
                dibujar_grafo_completo(msp, grafo)

            # Llenar grafo
            for i in range(msp.Count):
                try:
                    obj = msp.Item(i)
                    if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == CAPA_RED:
                        grafo.add_line(obj.StartPoint[:2], obj.EndPoint[:2])
                except Exception:
                    pass

            logger.info(f"Nodos en grafo: {len(grafo.nodes)}")

            # 2. EQUIPOS
            self.view.update_status("Buscando Equipos...", 30)
            dic_equipos = get_config("equipos", {})
            lista_todos = [item for sublist in dic_equipos.values() for item in sublist]
            bloques = extract_specific_blocks(lista_todos)

            #  3. PROCESAMIENTO
            self.view.update_status("Calculando Rutas...", 40)
            CAPA_TRAMO = get_config("rutas.capa_tramos_logicos")

            # Filtrar primero (optimización)
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

                try:
                    coords = obj.Coordinates
                    if len(coords) < 4:
                        continue
                    p_start = (coords[0], coords[1])
                    p_end = (coords[-2], coords[-1])

                    dist, ruta, meta = calcular_ruta_completa(
                        p_start, p_end, grafo, bloques
                    )

                    if dist:
                        cable, res, tipo = seleccionar_cable(
                            dist, meta["origen"], meta["destino"]
                        )

                        if opts["ruta_debug"]:
                            dibujar_debug_offset(msp, ruta)
                        if opts["etiquetas"]:
                            # Etiqueta Central
                            txt_tramo = f"{tipo} {int(cable)}m"
                            insertar_etiqueta_tramo(msp, ruta, txt_tramo)
                            # Etiqueta de Reserva
                            punto_fin = ruta[-1]
                            insertar_etiqueta_reserva(msp, punto_fin, res)
                        if opts["capas"]:
                            try:
                                # Leer prefijo del config
                                prefijo = get_config(
                                    "capas_resultados.prefijo_capa", "CABLE PRECONECT"
                                )

                                # Construir el nombre dinámicamente
                                # CABLE PRECONECT + 2H SM + (100M)
                                nombre_capa_final = f"{prefijo} {tipo} ({int(cable)}M)"

                                # Asegurar que la capa exista en AutoCAD
                                if garantizar_capa_existente(doc, nombre_capa_final):
                                    # Asignar la capa a la polilínea
                                    obj.Layer = nombre_capa_final
                                    obj.ConstantWidth = 0.5
                                    obj.LinetypeScale = 4
                            except Exception as e:
                                logger.warning(
                                    f"No se pudo cambiar capa en {obj.Handle}: {e}"
                                )

                        datos_reporte.append(
                            {
                                "handle": obj.Handle,
                                "origen": meta["origen"],
                                "destino": meta["destino"],
                                "longitud_real": dist,
                                "cable_asignado": cable,
                                "tipo_tecnico": tipo,
                                "reserva": res,
                                "estado": "OK",
                            }
                        )
                        exitos += 1
                    else:
                        msg = (
                            meta
                            if isinstance(meta, str)
                            else meta.get("error", "Error")
                        )
                        logger.warning(f"Error {obj.Handle}: {msg}")
                        if opts["errores"]:
                            dibujar_circulo_error(msp, p_start)
                        datos_reporte.append(
                            {"handle": obj.Handle, "estado": f"ERROR: {msg}"}
                        )

                except Exception as e:
                    logger.error(f"Excepción en tramo: {e}")

            # 4. EXPORTAR
            if opts["csv"]:
                self.view.update_status("Exportando...", 95)
                exportar_csv(datos_reporte)

            self.view.update_status("Finalizado.", 100)
            self.view.show_info("Fin", f"Proceso completado.\n{exitos} tramos OK.")

        except Exception as e:
            logger.critical(f"Error Fatal: {e}")
            self.view.show_error("Error Fatal", str(e))
        finally:
            self.view.toggle_run_button(True)
