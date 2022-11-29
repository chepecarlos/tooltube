import argparse
import os

import colorama

import tooltube.miLibrerias as miLibrerias
from tooltube.miLibrerias import FuncionesArchivos, ObtenerArchivo

logger = miLibrerias.ConfigurarLogging(__name__)
import tooltube.funcionesExtras as funcionesExtras
from tooltube.funcionesExtras import SalvarID, buscarID


def ArgumentosCLI():

    parser = argparse.ArgumentParser(prog="tooltube_get", description="Obtiene Data de un video")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")
    parser.add_argument("--salvar_id", "-s", help="Salvar ID del video")
    parser.add_argument("--buscar", "-b", help="Buscar un proyecto")

    parser.add_argument("-url", help="URL importante del video", action="store_true")

    return parser.parse_args()


def buscarProyecto(ID):
    actual = os.getcwd()
    for base, dirs, files in os.walk(actual):
        for name in files:
            if name.endswith(("Info.md")):
                filepath = base + os.sep + name
                idArchivo = miLibrerias.ObtenerValor(filepath, "youtube_id")
                if idArchivo == ID:
                    filepath = os.path.dirname(filepath)
                    filepath = os.path.dirname(filepath)
                    print(f"Encontrado el proyecto {idArchivo} en {filepath}")
                    print("Abriendo nemo")
                    os.system(f"nemo {filepath}")
                    return
    print(f"No encontrado {ID} :(")


def main():
    logger.info("Iniciando el programa ToolTube Análisis")
    colorama.init(autoreset=True)
    args = ArgumentosCLI()

    Video_id = None
    if args.video_id:
        Video_id = args.video_id
    else:
        Video_id = funcionesExtras.buscarID()

    if args.salvar_id:
        funcionesExtras.SalvarID(args.salvar_id)
    elif args.url:
        if Video_id is None or Video_id == "ID_Youtube":
            print("No se encontró ID en 1.Info.md")
        else:
            print(f"URL del Video {Video_id}")
            print(f"Video: https://www.youtube.com/watch?v={Video_id}")
            print(f"Editar: https://studio.youtube.com/video/{Video_id}/edit")
            print(f"Analítica: https://studio.youtube.com/video/{Video_id}/analytics/tab-overview/period-default")
    elif args.buscar:
        print(f"Buscando {args.buscar}")
        buscarProyecto(args.buscar)
    else:
        print("No se encontró opción prueba con -h")
