import argparse
import os

import colorama
import numpy as np
import pandas as pd
from colorama import Back, Fore, Style

import tooltube.funcionesExtras as FuncionesExtras
import tooltube.miLibrerias as miLibrerias
from tooltube.miLibrerias import FuncionesArchivos
from tooltube.obtenerDataYoutube import obtenerDataVideo
from tooltube.operaciones import analisis, usuario

from .funcionesExtras import SalvarID, buscarID

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

    parser.add_argument("--resumen", "-r", help="Cambios Globales", action="store_true")
    parser.add_argument("--usuario", help="Cambiar usuario del análisis")
    parser.add_argument("--url_analitica", "-csv", help="Pagina para descarga analítica del video", action="store_true")

    parser.add_argument("--file", "-f", help="Usando archivo")

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


def main():
    logger.info("Iniciando el programa ToolTube Analisis")
    colorama.init(autoreset=True)
    args = ArgumentosCLI()

    if args.file:
        logger.info(f"Usando el Archivo: {args.file}")
        analisis.crearGrafica("Vistas", args.file)
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

    if Video_id is not None:
        logger.info(f"[URL-Youtube] https://youtu.be/{Video_id}")

    if args.url_analitica:
        if Video_id is not None and Video_id != "ID_Youtube":
            logger.info("Descarga el cvs de la siguiente pagina:")
            logger.info(f" ID {Video_id}")
            logger.info(
                f"https://studio.youtube.com/video/{Video_id}/analytics/tab-overview/period-default/explore?entity_type=VIDEO&entity_id={Video_id}&time_period=lifetime&explore_type=TABLE_AND_CHART&metric=TOTAL_ESTIMATED_EARNINGS&granularity=DAY&t_metrics=TOTAL_ESTIMATED_EARNINGS&t_metrics=SUBSCRIBERS_NET_CHANGE&t_metrics=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&t_metrics=VIEWS&t_metrics=WATCH_TIME&t_metrics=AVERAGE_WATCH_TIME&dimension=DAY&o_column=DAY&o_direction=ANALYTICS_ORDER_DIRECTION_DESC"
            )
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
    elif args.data and Video_id:
        DataVideo(Video_id)
    else:
        logger.info("Comandos no encontrado, prueba con -h")


if __name__ == "__main__":
    main()
