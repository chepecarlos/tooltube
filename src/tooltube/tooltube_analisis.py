import argparse
import os
from datetime import datetime, timedelta

import colorama
import numpy as np
import pandas as pd
from pathlib import Path
from colorama import Back, Fore, Style

from tooltube import funcionesExtras
import tooltube.funcionesExtras as FuncionesExtras
import tooltube.miLibrerias as miLibrerias
from tooltube.miLibrerias import FuncionesArchivos
from tooltube.obtenerDataYoutube import obtenerDataVideo
from tooltube.operaciones import analisis, usuario
from tooltube.minotion.minotion import estadoNotion, asignadoNotion, actualizarNotion, crearNotion, canalNotion

from tooltube.funcionesExtras import SalvarID, buscarID


logger = miLibrerias.ConfigurarLogging(__name__)


def ArgumentosCLI():

    parser = argparse.ArgumentParser(prog="tooltube_analisis", description="Herramienta de Analisis de Youtube")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")

    parser.add_argument("--salvar_id", help="Salvar ID del video")

    parser.add_argument("--data", help="Mostar Data del video", action="store_true")

    parser.add_argument("--vista", "-v", help="Mostar Vistas en Gráfica", action="store_true")
    parser.add_argument("--tiempo", "-t", help="Mostar Tiempo de Reproducción(Horas) en Gráfica", action="store_true")
    parser.add_argument("--duracion", "-d", help="Mostar Duración promedio de vista en Gráfica", action="store_true")
    parser.add_argument("--porcenta_clip", "-ctr", help="Mostar Click Through Rate en Gráfica", action="store_true")
    parser.add_argument("--subscriptores", "-s", help="Subcriptores Rate en Gráfica", action="store_true")
    parser.add_argument("--ingresos", "-i", help="Ingresos estimados en Gráfica", action="store_true")

    parser.add_argument("--resumen", help="Cambios Globales", action="store_true")
    parser.add_argument("--usuario", help="Cambiar usuario del análisis")
    parser.add_argument("--url_analitica", "-csv", help="Pagina para descarga analítica del video", action="store_true")

    parser.add_argument("--file", "-f", help="Usando archivo")
    parser.add_argument("--folder", help="Folder a Realizar operacion")

    parser.add_argument("--revisar", "-r", help="Dias a revisar el video", type=int)
    parser.add_argument("--revisado", help="Video ya revisado", action="store_true")
    parser.add_argument("--buscar_revision", "-br", help="Buscar video a revisar", action="store_true")
    parser.add_argument("--update", "-u", help="actualizar obligado", action="store_true")

    parser.add_argument("--estado", "-e",
                        help="actualiza estado del proyecto de video",
                        choices=[
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
                        )
    parser.add_argument("--asignado", "-a",
                        help="actualiza a quien esta asignado del proyecto de video",
                        choices=[
                            'desconocido',
                            'paty',
                            'chepecarlos',
                            'ingjuan',
                            'luis'
                        ]
                        )
    parser.add_argument("--canal", "-c",
                        help="actualiza a canal proyecto de video",
                        choices=[
                            'desconocido',
                            'ChepeCarlos',
                            'Curso_Venta',
                            'CtrlZ',
                            'Tiktok'
                        ]
                        )

    parser.add_argument("--actualizar_estado", "-ae", help="busca estado del sistema", action="store_true")

    return parser.parse_args()


def cambiosGlobales():
    actual = os.getcwd()
    for base, dirs, files in os.walk(actual):
        for name in files:
            if name.endswith(("Info.md")):
                filepath = base + os.sep + name
                idArchivo = miLibrerias.ObtenerValor(filepath, "youtube_id")
                if idArchivo is not None and idArchivo != "ID_Youtube":
                    print(f"Video {idArchivo} - https://www.youtube.com/watch?v={idArchivo}")
                    folderProyecto = os.path.dirname(filepath).replace("/1.Guion", "")
                    print(f"Folder {folderProyecto}")
                    verCambios(folderProyecto)
                    print("-" * 50)
                    print()


def cambiarEstado(estadoNuevo: str, folderActual: str) -> None:

    if estadoNuevo is None:
        print("Error estado vació")
        return False


    nombreProyecto = Path(folderActual).name
    rutaInfo = f"{folderActual}/1.Guion/1.Info.md"

    if not Path(rutaInfo).exists():
        print("No es un proyecto")
        return False

    estadoActual = miLibrerias.ObtenerValor(rutaInfo, "estado")
    if estadoActual is None:
        estadoActual = "desconocido"
    funcionoNotion = estadoNotion(estadoNuevo, rutaInfo)
    if funcionoNotion:
        miLibrerias.SalvarValor(rutaInfo, "estado", estadoNuevo)
        print(f"Estado de {nombreProyecto}: {estadoActual} a {estadoNuevo}")
        print("Actualizar Icono")

    actualizarEstado(folderActual)


def cambiarCanal(canalNuevo: str, folderActual: str = None) -> None:
    if canalNuevo is None:
        print("Error canal Bacillo")

    if folderActual is None:
        folderActual = funcionesExtras.buscarRaiz()
        
    nombreProyecto = Path(folderActual).name
    rutaInfo = f"{folderActual}/1.Guion/1.Info.md"
    
    if not Path(rutaInfo).exists():
        print("No es un proyecto")
        return

    canalActual = miLibrerias.ObtenerValor(rutaInfo, "canal")
    if canalActual is None:
        canalActual = "desconocido"
    funcionoNotion = canalNotion(canalNuevo, rutaInfo)
    if funcionoNotion:
        miLibrerias.SalvarValor(rutaInfo, "canal", canalActual)
        print(f"Estado de {nombreProyecto}: {canalActual} a {canalNuevo}")


def cambiarAsignado(asignadoNuevo: str, folderActual: str = None) -> None:
    logger.info(f"Iniciando el cambio de usuario {asignadoNuevo} - {folderActual}")
    if asignadoNuevo is None:
        logger.error("Error asignado vacilo")
        return

    if folderActual is None:
        folderActual = funcionesExtras.buscarRaiz()

    nombreProyecto = Path(folderActual).name
    rutaInfo = f"{folderActual}/1.Guion/1.Info.md"

    estadoActual = miLibrerias.ObtenerValor(rutaInfo, "asignado")
    if estadoActual is None:
        estadoActual = "desconocido"
    funcionoNotion = asignadoNotion(asignadoNuevo, rutaInfo)
    if funcionoNotion:
        miLibrerias.SalvarValor(rutaInfo, "asignado", asignadoNuevo)
        logger.info(f"Asignado de {nombreProyecto}: {estadoActual} a {asignadoNuevo}")
    else:
        logger.error("Error con consulta")


def mostraRevisar():
    actual = os.getcwd()
    for base, dirs, files in os.walk(actual):
        for name in files:
            if name.endswith(("Info.md")):
                filepath = base + os.sep + name
                revisar = miLibrerias.ObtenerValor(filepath, "revisar")
                if revisar is None:
                    continue

                if revisar == "Listo":
                    continue
                fechaCreacion = miLibrerias.ObtenerValor(filepath, "fecha_revisar")
                dias = timedelta(days=revisar)
                fechaRevisar = fechaCreacion + dias
                direccionFolder = base.split("/")
                direccionFolder = direccionFolder[:-1]
                direccionFolder = "/".join(direccionFolder)
                if fechaRevisar < datetime.now():
                    diferencia = int((datetime.now() - fechaCreacion).total_seconds() / 60 / 60 / 24)
                    print("---" * 30)
                    print(f"Creado {fechaCreacion.strftime('%d/%m/%Y')} - {diferencia} Dias")
                    print(f"Control {revisar} días, desde {fechaRevisar.strftime('%d/%m/%Y')}")
                    print(f"Dirección: {direccionFolder}")
                    print()


def verCambios(rutaBase):
    dataTitulo = cargarCambios("titulos", rutaBase, "10.Analitica/1.Cambios/titulos.csv")
    dataMiniatura = cargarCambios("miniatura", rutaBase, "10.Analitica/1.Cambios/miniatura.csv")
    dataEstado = cargarCambios("estado", rutaBase, "10.Analitica/1.Cambios/estado.csv")

    if dataTitulo.size:
        mostarData(dataTitulo)

    if dataMiniatura.size:
        mostarData(dataMiniatura)
        # for index, row in dataMiniatura.iterrows():
        #     fecha = row["fecha"]

        #     print(f"{fecha.day}/{fecha.month}/{fecha.year} ", end="")
        #     print(row["cambio"], end="")
        #     if row["mensaje"] is np.nan:
        #         print(row["mensaje"])
        #     print()

    if dataEstado.size:
        mostarData(dataEstado)


def mostarData(data):
    for index, row in data.iterrows():
        fecha = row["fecha"]

        print(f"{fecha.day}/{fecha.month}/{fecha.year} ", end="")
        print(row["cambio"], end="")
        if row["mensaje"] is np.nan:
            print(row["mensaje"])
        print()


def cargarCambios(tipo, rutaBase, direccion):
    data = cargarData(rutaBase, direccion)
    if data is None:
        return
    etiquetaFechas = data.columns[0]
    data[etiquetaFechas] = pd.to_datetime(data[etiquetaFechas])
    return data
    print(data)


def cargarData(ruta, archivo, noTotales=False):
    archivoData = FuncionesArchivos.UnirPath(ruta, archivo)
    if not os.path.exists(archivoData):
        logger.warning(f"No se control {archivo}")
        return None
    data = pd.read_csv(archivoData)
    return data


def DataVideo(ID_Video):
    print(f"Buscando data  https://youtu.be/{ID_Video}")
    data = obtenerDataVideo(ID_Video)


def actualizarEstado(rutaActual: str = None, subir: bool = False):

    if rutaActual is None:
        rutaActual = os.getcwd()
    iconos = miLibrerias.ObtenerArchivo("data/iconos.md")
    emblemas = miLibrerias.ObtenerArchivo("data/emblemas.md")
    folder = iconos.get("folder")
    for base, dirs, files in os.walk(rutaActual):
        for name in files:
            if name.endswith(("Info.md")):
                archivoInfo = base + os.sep + name
                folderProyecto = Path(base + os.sep).parent
                seActualizoNotion = actualizarNotion(archivoInfo)
                if seActualizoNotion is None and subir:
                    crearNotion(folderProyecto)
                    actualizarNotion(archivoInfo)
                estado = miLibrerias.ObtenerValor(archivoInfo, "estado")
                if estado is None:
                    estado = "desconocido"
                nombreProyecto = folderProyecto.name
                iconoProyecto = iconos.get(estado, estado[0])
                iconoProyecto = miLibrerias.UnirPath(folder, iconoProyecto)
                FuncionesExtras.actualizarIconoDeterminado(iconoProyecto, folderProyecto)
                
                asignado = miLibrerias.ObtenerValor(archivoInfo, "asignado")
                if asignado is None:
                    asignado = "desconocido"
                iconoAsignado = emblemas.get(asignado)
                funcionesExtras.quitarEmblemas(folderProyecto)
                funcionesExtras.agregarEmblema(iconoAsignado, folderProyecto)
                FuncionesExtras.tocarFolder(folderProyecto)
                
                logger.info(f"Proyecto: {nombreProyecto}")
                logger.info(f"\tEstado: {estado}")
                logger.info(f"\tEncargado: {asignado}")
                
                print()


def main():
    logger.info("Iniciando el programa ToolTube Analisis")
    colorama.init(autoreset=True)
    args = ArgumentosCLI()

    if args.file:
        logger.info(f"Usando el Archivo: {args.file}")
        analisis.crearGraficaLocal(args.file)
        return

    if args.salvar_id:
        logger.info(f"Salvando ID[{args.salvar_id}] del Video")
        FuncionesExtras.SalvarDato("youtube_id", args.salvar_id)
        return

    Video_id = None
    if args.video_id:
        Video_id = args.video_id
    else:
        Video_id = buscarID()

    if Video_id is not None and Video_id != "ID_Youtube":
        logger.info(f"[URL-Youtube] https://youtu.be/{Video_id}")

    if args.url_analitica:
        if Video_id is not None and Video_id != "ID_Youtube":
            logger.info("Descarga el cvs de la siguiente pagina:")
            logger.info(f"Youtube-ID {Video_id}")
            print(f"\nTodo: https://studio.youtube.com/video/{Video_id}/analytics/tab-overview/period-default/explore?entity_type=VIDEO&entity_id={Video_id}&time_period=lifetime&explore_type=TABLE_AND_CHART&metric=VIEWS&granularity=DAY&t_metrics=TOTAL_ESTIMATED_EARNINGS&t_metrics=SUBSCRIBERS_NET_CHANGE&t_metrics=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&t_metrics=VIEWS&t_metrics=WATCH_TIME&t_metrics=AVERAGE_WATCH_TIME&dimension=DAY&o_column=VIEWS&o_direction=ANALYTICS_ORDER_DIRECTION_DESC")
            print(f"\n1 Año: https://studio.youtube.com/video/{Video_id}/analytics/tab-overview/period-default/explore?entity_type=VIDEO&entity_id={Video_id}&time_period=year&explore_type=TABLE_AND_CHART&metric=VIEWS&granularity=DAY&t_metrics=TOTAL_ESTIMATED_EARNINGS&t_metrics=SUBSCRIBERS_NET_CHANGE&t_metrics=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&t_metrics=VIEWS&t_metrics=WATCH_TIME&t_metrics=AVERAGE_WATCH_TIME&dimension=DAY&o_column=VIEWS&o_direction=ANALYTICS_ORDER_DIRECTION_DESC")
        else:
            logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + "Error Falta ID")
    elif args.usuario:
        usuario.SalvarUsuario(args.usuario)
    elif args.vista:
        analisis.crearGrafica("Vistas")
    elif args.tiempo:
        analisis.crearGrafica("Tiempo de reproducción (horas)")
    elif args.duracion:
        analisis.crearGrafica("Duración promedio de vistas")
    elif args.ingresos:
        analisis.crearGrafica("Tus ingresos estimados (USD)")
    elif args.porcenta_clip:
        analisis.crearGrafica("Tasa de clics de las impresiones (%)")
    elif args.subscriptores:
        analisis.crearGrafica("Suscriptores")
    elif args.resumen:
        cambiosGlobales()
    elif args.revisar:
        logger.info(f"Revisar video en {args.revisar} días")
        FuncionesExtras.SalvarDato("revisar", args.revisar)
        FuncionesExtras.SalvarDato("fecha_revisar", datetime.now())
    elif args.revisado:
        logger.info(f"Video revisado")
        FuncionesExtras.SalvarDato("revisar", "Listo")
        FuncionesExtras.SalvarDato("fecha_revisar", datetime.now())
    elif args.buscar_revision:
        logger.info(f"Video a revisar")
        mostraRevisar()
    elif args.data and Video_id:
        DataVideo(Video_id)
    elif args.actualizar_estado:
        logger.info("Empezando a buscar Proyecto contenido")
        if args.folder:
            actualizarEstado(rutaActual=args.folder)
        elif args.update:
            actualizarEstado(subir=True)
        else:
            actualizarEstado()
    elif args.estado:
        cambiarEstado(args.estado, args.folder)
    elif args.canal:
        cambiarCanal(args.canal)
    elif args.asignado:
        cambiarAsignado(args.asignado)
    else:
        logger.info("comandos no encontrado, prueba con -h")


if __name__ == "__main__":
    main()
