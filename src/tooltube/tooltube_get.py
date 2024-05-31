from tooltube.tooltube import CargarCredenciales
from tooltube.funcionesExtras import SalvarID, buscarID
import tooltube.funcionesExtras as funcionesExtras
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import argparse
import os

import colorama

import tooltube.miLibrerias as miLibrerias
from tooltube.miLibrerias import FuncionesArchivos, ObtenerArchivo
from tooltube.minotion.minotion import urlNotion

logger = miLibrerias.ConfigurarLogging(__name__)


def ArgumentosCLI():

    parser = argparse.ArgumentParser(prog="tooltube_get", description="Obtiene Data de un video")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")
    parser.add_argument("--salvar_id", "-s", help="Salvar ID del video")
    parser.add_argument("--buscar", "-b", help="Buscar un proyecto")
    parser.add_argument("--miembros", "-m", help="Descarga miembros actuales", action="store_true")
    parser.add_argument("--notion", "-n", help="URL proyecto en Notion", action="store_true")

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


def descargarMiembros():
    pass
    # credenciales = CargarCredenciales()

    # youtube = build('youtube', 'v3', credentials=credenciales)
    # MEMBERS_SECTION_ID = '181'
    # MEMBERS_SECTION_LEVEL = 2
    # try:
    #     # Realizar la solicitud para obtener la lista de miembros del canal.
    #     next_page_token = None

    #     request = youtube.members().list(
    #         part='snippet',
    #         filterByMemberChannelId="UCS5yb75qx5GFOG-uV5JLYlQ",
    #         maxResults=50,
    #         pageToken=next_page_token
    #     )

    #     response = request.execute()

    #     print(response)

    # Abrir el archivo CSV para escribir la lista de miembros.
    # with open('miembros.csv', mode='w', newline='') as file:
    #     writer = csv.writer(file)

    #     # Escribir los encabezados de las columnas.
    #     writer.writerow(['ID de canal', 'Nombre de usuario'])

    #     # Escribir los datos de cada miembro.
    #     for item in response['items']:
    #         writer.writerow([item['snippet']['memberDetails']['channelId'], item['snippet']['memberDetails']['displayName']])

    # print("Se ha descargado la lista de miembros en el archivo 'miembros.csv'.")

    # except HttpError as error:
    #     print(f"Se produjo un error al intentar obtener la lista de miembros: {error}")


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
    elif args.miembros:
        descargarMiembros()
    elif args.notion:
        urlNotion()
    else:
        print("No se encontró opción prueba con -h")
