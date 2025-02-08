from nicegui import ui, app
from pathlib import Path

import tooltube.tooltube_analisis as analitica
from tooltube.minotion.minotion import actualizarNotion
import tooltube.miLibrerias as miLibrerias
from datetime import datetime

class ventanaEstado:
    
    tamanoVentana = (260, 400)

    def __init__(self, ruta: str):
        self.folder: str = ruta

        self.encargados = [
            'desconocido',
            'paty',
            'chepecarlos',
            'ingjuan',
            'luis'
        ]

        self.estados = [
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

        self.canal = [
            'desconocido',
            'ChepeCarlos',
            'Curso_Venta',
            'CtrlZ',
            'Tiktok'
        ]

    def ejecutar(self):

        proyecto = self.folder.split("/")[-1]
        proyecto = proyecto.split("_")  
        proyecto = " ".join(proyecto) 

        rutaInfo = f"{self.folder}/1.Guion/1.Info.md"

        if not Path(rutaInfo).exists():
            print("Error folder no es proyecto")
            ui.label("Error no se encontró proyecto")
            ui.run(native=True, reload=False, dark=True, language="es", title=f"Sistema Estado - Error")
        else:

            actualizarNotion(rutaInfo)
            
            estado = miLibrerias.ObtenerValor(rutaInfo, "estado")
            encargado = miLibrerias.ObtenerValor(rutaInfo, "asignado")
            canal = miLibrerias.ObtenerValor(rutaInfo, "canal")

            with ui.column().classes('fixed-center'):
                with ui.column().classes('w-full items-center'):
                    with ui.row():
                        ui.label(f"Proyecto: {proyecto}")
                self.selecionEstado = ui.select(options=self.estados, with_input=True, label="Estado", on_change=lambda e: ui.notify(e.value), value=estado)
                self.selecionEncargado = ui.select(options=self.encargados, with_input=True, label="Encargado", on_change=lambda e: ui.notify(e.value), value=encargado)
                self.selecionCanal = ui.select(options=self.canal, with_input=True, label="Canal", on_change=lambda e: ui.notify(e.value), value=canal)
                with ui.column().classes('w-full items-center'):
                    with ui.row():
                        ui.button('Actualizar', on_click=self.actualizarData)
            
            app.native.window_args['resizable'] = False

            ui.run(native=True, reload=False, dark=True, language="es", window_size=self.tamanoVentana, title=f"Sistema Estado - {proyecto}")

    def actualizarData(self):
        Estado = self.selecionEstado.value
        Encargado = self.selecionEncargado.value
        Canal = self.selecionCanal.value
        fechaHoy = datetime.now()
        textoFechaHoy = fechaHoy.strftime("%Y-%m-%d")
        ui.notify(f"Actualizando Data! {Estado}")
        print(f"Estado: {Estado} - Encargado: {Encargado} - Canal: {Canal}")
        if Estado == "publicado":
            print(f"Se publico el video {textoFechaHoy}")