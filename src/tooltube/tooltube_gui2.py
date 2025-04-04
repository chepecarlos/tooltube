"""
Aplicación Gráfica con NiceGUI para actualizar Proyecto de Notion.
"""

from nicegui import ui, app
from pathlib import Path

from tooltube.minotion.minotion import actualizarNotion
from tooltube.minotion.minotion import actualizarEstadoNotion
import tooltube.miLibrerias as miLibrerias
from datetime import datetime
from tooltube.tooltube_analisis import actualizarIconos


class ventanaEstado:
    "Ventana que cambia estado del Proyecto"

    tamañoVentana = (300, 450)
    "Tamaño por defecto de la Ventana"

    estados: list[str] = [
        'desconocido',
        'idea',
        'desarrollo',
        'guion',
        'grabado',
        'edicion',
        'tomab',
        'revision',
        'preparado',
        'publicado',
        'analizando'
    ]
    "Lista Estados del Proyectos"

    encargados: list[str] = [
        'desconocido',
        'paty',
        'chepecarlos',
        'ingjuan',
        'gerardo'
    ]
    "Lista Encargados del Proyecto "

    canal: list[str] = [
        'desconocido',
        'ChepeCarlos',
        'Curso_Venta',
        'CtrlZ',
        'Tiktok'
    ]
    "Lista de Cuentas"

    folder: str
    "Ruta del Proyecto"

    def __init__(self, ruta: str):
        self.folder: str = ruta

    def ejecutar(self):
        "Ejecutar Ventana"

        proyecto = self.folder.split("/")[-1]
        proyecto = proyecto.split("_")
        proyecto = " ".join(proyecto)

        self.rutaInfo = f"{self.folder}/1.Guion/1.Info.md"

        if not Path(self.rutaInfo).exists():
            print("Error folder no es proyecto")
            ui.label("Error no se encontró proyecto")
            ui.run(native=True, reload=False, dark=True, language="es", title=f"Sistema Estado - Error")
        else:

            actualizarNotion(self.rutaInfo)

            estado = miLibrerias.ObtenerValor(self.rutaInfo, "estado")
            encargado = miLibrerias.ObtenerValor(self.rutaInfo, "asignado")
            canal = miLibrerias.ObtenerValor(self.rutaInfo, "canal")

            with ui.column().classes('fixed-center'):
                with ui.column().classes('w-full items-center'):
                    with ui.row():
                        ui.label(f"Proyecto: {proyecto}")
                self.selecionEstado = ui.select(options=self.estados, with_input=True, label="Estado", value=estado)
                self.selecionEncargado = ui.select(options=self.encargados, with_input=True, label="Encargado", value=encargado)
                self.selecionCanal = ui.select(options=self.canal, with_input=True, label="Canal", value=canal)
                with ui.column().classes('w-full items-center'):
                    with ui.row():
                        ui.button('Actualizar', on_click=self.actualizarData)

            # app.native.window_args['resizable'] = False

            ui.run(native=True, reload=False, dark=True, language="es", window_size=self.tamañoVentana, title=f"Sistema Estado - {proyecto}")

    def agregarEncargado(self, encargado):
        noAgregarEncargado = ["desconocido", "chepecarlos"]

        listaColaboradores = miLibrerias.ObtenerValor(self.rutaInfo, "listaColaboradores")
        if listaColaboradores is None:
            listaColaboradores = []

        if encargado not in listaColaboradores and encargado not in noAgregarEncargado:
            listaColaboradores.append(encargado)

        miLibrerias.SalvarValor(self.rutaInfo, "listaColaboradores", listaColaboradores)

    def actualizarData(self):
        "Salva los Datos local y Notion"
        estado = self.selecionEstado.value
        encargado = self.selecionEncargado.value
        canal = self.selecionCanal.value
        fechaHoy = datetime.now()
        textoFechaHoy = fechaHoy.strftime("%Y-%m-%d")
        ui.notify(f"Actualizando Data! {estado}")
        print(f"Estado: {estado} - Encargado: {encargado} - Canal: {canal}")
        if estado == "publicado":
            print(f"Se publico el video {textoFechaHoy}")

        respuestaNotion = actualizarEstadoNotion(self.rutaInfo, estado, encargado, canal, textoFechaHoy)

        if respuestaNotion:
            self.agregarEncargado(encargado)

            miLibrerias.SalvarValor(self.rutaInfo, "asignado", encargado)
            miLibrerias.SalvarValor(self.rutaInfo, "canal", canal)
            miLibrerias.SalvarValor(self.rutaInfo, "estado", estado)
            if estado == "publicado":
                miLibrerias.SalvarValor(self.rutaInfo, "terminado", True)
                miLibrerias.SalvarValor(self.rutaInfo, "fecha", textoFechaHoy)
            else:
                miLibrerias.SalvarValor(self.rutaInfo, "terminado", False)
                miLibrerias.SalvarValor(self.rutaInfo, "fecha", "")
            actualizarIconos(self.folder)
            ui.notify("Se actualizar Estado", type='positive')
        else:
            ui.notify("No se actualizar Estado", type='negative')
