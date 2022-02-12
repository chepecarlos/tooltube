# -*- coding: utf-8 -*-
# https://github.com/youtube/api-samples

import argparse
import os
import pickle
import random
import sys
import time

import httplib2

try:
    import httplib
except ImportError:
    import http.client as httplib

from pathlib import Path

import MiLibrerias
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from operaciones import analisis, usuario

import tooltube.obtenerDataYoutube as dataYoutube

from .funcionesExtras import SalvarID, buscarID

logger = MiLibrerias.ConfigurarLogging(__name__)

# Todo cambiar tas por default para agregar el chepecarlos
TagsDefault = "ALSW,ChepeCarlos,Jose Carlos Garcia Diaz"

httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    httplib.NotConnected,
    httplib.IncompleteRead,
    httplib.ImproperConnectionState,
    httplib.CannotSendRequest,
    httplib.CannotSendHeader,
    httplib.ResponseNotReady,
    httplib.BadStatusLine,
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


ArchivoLocal = os.path.join(Path.home(), ".config/tooltube")

if sys.version_info[0] < 3:
    logger.error("Tienes que usar Python 3 para este programa")
    sys.exit(1)


def CargarCredenciales(Canal=None):
    """Buscar credenciales para API de youtube."""
    credentials = None
    FolderData = os.path.join(ArchivoLocal, "data")

    if Canal is not None:
        logger.info(f"Usando canal {Canal}")
        FolderData = os.path.join(FolderData, Canal)

    if not os.path.exists(FolderData):
        os.makedirs(FolderData)

    ArchivoPickle = FolderData + "/token.pickle"

    if os.path.exists(ArchivoPickle):
        logger.info("Cargando credenciales API Youtube, del Archivo pickle...")
        with open(ArchivoPickle, "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info("Recargando credenciales...")
            credentials.refresh(Request())
        else:
            logger.info("Cargando nuevas credenciales...")
            client_secrets = FolderData + "/client_secrets.json"
            if not os.path.exists(client_secrets):
                logger.warning("No existe client_secrets.json agregalo a {FolderData}")
                return
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets,
                scopes=[
                    "https://www.googleapis.com/auth/youtube.readonly",
                    "https://www.googleapis.com/auth/youtube",
                    "https://www.googleapis.com/auth/youtubepartner",
                ],
            )

            flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")
            credentials = flow.credentials

            with open(ArchivoPickle, "wb") as f:
                logger.info("Salvando credenciales para el futuro en archivo pickle...")
                pickle.dump(credentials, f)

    return credentials


def ActualizarTituloVideo(credenciales, video_id, Titulo):
    """
    Actualiza el titulo del Video Youtube si es necesario
    """
    youtube = build("youtube", "v3", credentials=credenciales)

    solicitudVideo = youtube.videos().list(id=video_id, part="snippet")

    DataVideo = solicitudVideo.execute()
    if len(DataVideo["items"]) > 0:
        SnippetVideo = DataVideo["items"][0]["snippet"]

        if Titulo == SnippetVideo["title"]:
            logger.info(f"Video {video_id} ya actualizado")
            return 0

        SnippetVideo["title"] = Titulo

        SolisituActualizar = youtube.videos().update(part="snippet", body=dict(snippet=SnippetVideo, id=video_id))

        RespuestaYoutube = SolisituActualizar.execute()
        if len(RespuestaYoutube["snippet"]) > 0:
            logger.info(f"Titulo[{Titulo}] - Link: https://youtu.be/{video_id}")
            return True
        else:
            logger.warning("Hubo un problema?")
            return False


def ActualizarDescripcionVideo(credenciales, video_id, archivo=None, Directorio=None):
    """
    Actualizar Descripcion de Video Youtube si es necesario.
    """
    nuevaDescripcion = ""
    if archivo is None:
        archivo = video_id + ".txt"
        logger.info(f"Usando el archivo {archivo} por defecto")

    if Directorio is not None:
        archivo = os.path.join(Directorio, archivo)

    if os.path.exists(archivo):
        with open(archivo, "r") as linea:
            nuevaDescripcion = linea.read()
    else:
        logger.warning(f"Erro fatal el archivo {archivo} no existe")
        return -1

    viejaDescripcion = dataYoutube.obtenerDescripcion(video_id)

    if viejaDescripcion is not None and viejaDescripcion == nuevaDescripcion:
        return 0

    youtube = build("youtube", "v3", credentials=credenciales)

    solicitudVideo = youtube.videos().list(id=video_id, part="snippet")

    DataVideo = solicitudVideo.execute()
    if len(DataVideo["items"]) > 0:
        SnippetVideo = DataVideo["items"][0]["snippet"]

        if nuevaDescripcion == SnippetVideo["description"]:
            return 0

        SnippetVideo["description"] = nuevaDescripcion

        SolisituActualizar = youtube.videos().update(part="snippet", body=dict(snippet=SnippetVideo, id=video_id))

        RespuestaYoutube = SolisituActualizar.execute()
        if len(RespuestaYoutube["snippet"]) > 0:
            logger.info(f"Actualización Completa - Link: https://youtu.be/{video_id}")
            return 1
        else:
            logger.warning("Hubo un problema?")
            return -1
    else:
        logger.warning(f"No existe el video con ID {video_id}")
        return -1


def ActualizarEstadoVideo(credenciales, video_id, estado):

    lista_estado = {"publico": "public", "privado": "private", "nolistado": "unlisted"}

    if estado in lista_estado:
        estado = lista_estado[estado]
    else:
        logger.warning("Estado no reconocido")

    youtube = build("youtube", "v3", credentials=credenciales)
    solicitadVideo = youtube.videos().list(id=video_id, part="status")
    data_video = solicitadVideo.execute()
    if data_video:
        data_estado = data_video["items"][0]["status"]

        print(data_video["items"][0])

        if estado == data_estado["privacyStatus"]:
            logger.info("No necesario cambiar estado")
            return False

        data_estado["privacyStatus"] = estado
        print("--" * 40)
        print(data_estado)
        print(data_estado["privacyStatus"])

        solicitudActualizar = youtube.videos().update(part="status", body=dict(status=data_estado, id=video_id))

        respuesta_youtube = solicitudActualizar.execute()

        print(respuesta_youtube)

        # print(data_video["status"]["status"])


def ActualizarDescripcionFolder(credenciales, Max=None, Directorio=None):
    """Actualiza Descripciones de Video desde los archivos de un Folder."""
    contador = 0
    if Directorio is None:
        Directorio = "."
    total = len(os.listdir(Directorio))
    Actualizados = 0
    Error = 0
    for archivo in os.listdir(Directorio):
        if archivo.endswith(".txt"):
            contador += 1
            video_id = archivo.replace(".txt", "")
            logger.info(f"Verificando ({contador}/{total}) - Video_ID:{video_id}")
            Resultado = ActualizarDescripcionVideo(credenciales, video_id, archivo, Directorio)
            if Resultado == 1:
                Actualizados += 1
                if Max is not None:
                    if Actualizados >= Max:
                        Porcentaje = (Actualizados / total) * 100
                        logger.info(f"Se actualizo {Actualizados}/{total} - {Porcentaje:.2f} % descripciones de video")
                        logger.info(f"Se actualizo {Actualizados}/{total} descripciones de video")
                        return
            elif Resultado == -1:
                Error += 1
    Porcentaje = (Actualizados / total) * 100
    logger.info(f"Se actualizo {Actualizados}/{total} - {Porcentaje:.2f} % descripciones de video")
    if Error > 0:
        logger.info(f"Hubo error {Error}/{total}")


def ActualizarThumbnails(credenciales, video_id, archivo=None):
    """Actualiza la Miniatura de un video de Youtube."""
    if archivo is None:
        archivo = video_id + ".png"
    if os.path.exists(archivo):
        youtube = build("youtube", "v3", credentials=credenciales)
        Respuesta = youtube.thumbnails().set(videoId=video_id, media_body=archivo).execute()
        if Respuesta["items"][0]:
            logger.info(f"Imagen Actualizada para {video_id} - {Respuesta['items'][0]['maxres']['url']}")
            return True
        else:
            logger.warning("Hubo un problema :(")
    else:
        logger.warning(f"No existe el archivo {archivo}")

    return False


def ActualizarIdioma(credenciales, video_id, Lenguaje="es"):
    """
    Actualizá Lenguaje video y descripcion
    """

    youtube = build("youtube", "v3", credentials=credenciales)

    results = youtube.videos().list(part="snippet,localizations", id=video_id).execute()

    video = results["items"][0]
    SnippetVideo = video["snippet"]

    if Lenguaje and Lenguaje != "":

        SnippetVideo["defaultLanguage"] = Lenguaje
        SnippetVideo["defaultAudioLanguage"] = Lenguaje

        SolicitudActualizar = youtube.videos().update(part="snippet", body=dict(snippet=SnippetVideo, id=video_id))

        RespuestaYoutube = SolicitudActualizar.execute()
        if len(RespuestaYoutube["snippet"]) > 0:
            logger.info(f"Lenguaje Actualizado - Link: https://youtu.be/{video_id}")
            return 1
        else:
            logger.warning("No se puedo Actualizar Lenguaje")
            return -1


def SubirVideo(credenciales, Archivo, Comentario=""):
    """Sube Video a Youtube."""
    global TagsDefault
    if not os.path.exists(Archivo):
        logger.warning(f"No encontrado el archivo {Archivo}")
        exit()
    youtube = build("youtube", "v3", credentials=credenciales)

    tags = None
    if TagsDefault:
        tags = TagsDefault.split(",")

    body = dict(
        snippet=dict(
            title=f"Titulo {Archivo}",
            description="Descripcion",
            tags=tags,
            categoryId=27,
            defaultLanguage="es",
            defaultAudioLanguage="es",
        ),
        status=dict(privacyStatus="unlisted"),
    )

    Respuesta = youtube.videos().insert(
        part=",".join(body.keys()), body=body, media_body=MediaFileUpload(Archivo, chunksize=-1, resumable=True)
    )

    RecargarSubida(Respuesta, Comentario)


def RecargarSubida(Respuesta, Comentario):
    """Mantiene la subida del video."""
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.info("Subiendo Archivo...")
            status, response = Respuesta.next_chunk()
            if response is not None:
                if "id" in response:
                    SalvarID(response["id"])
                    logger.info(f"Se subio con exito {response['id']} | https://youtu.be/{response['id']} ")
                    analisis.salvar_data_analitica("1.Cambios/estado.csv", "suvido", Comentario)
                else:
                    logger.warning(f"The upload failed with an unexpected response: {response}")
                    exit()
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                logger.warning("No mas intento de conexión")
                exit()

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            logger.warning(f"durmiendo por {sleep_seconds} y despues reintentando")
            time.sleep(sleep_seconds)


def ArgumentosCLI():

    parser = argparse.ArgumentParser(prog="tooltube", description="Herramienta de Automatización de Youtube")
    parser.add_argument("--estado", "-e", help="Actualiza Estado de un video")
    parser.add_argument("--miniatura", "-m", help="Actualizar de Miniatura de video en Youtube")
    parser.add_argument("--titulo", "-t", help="Actualizar de titulo video en Youtube")
    parser.add_argument("--descripcion", "-d", help="Actualizar de descripcion video en Youtube", action="store_true")
    parser.add_argument("--uploader", "-u", help="Subir video a youtube", action="store_true")
    parser.add_argument("--idioma", "-i", help="Actualizar de Idioma video a youtube", action="store_true")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")
    parser.add_argument("--file", "-f", help="Archivo a usar para actualizar Youtube")
    parser.add_argument("--folder", help="Directorio a usar")
    parser.add_argument("--max", help="Cantidad a actualizar", type=int)
    parser.add_argument("--recursivo", "-r", help="Actualiza con todos los archivos disponibles", action="store_true")

    parser.add_argument("--canal", "-c", help="Canal Youtube a usar")
    parser.add_argument("--nota", "-n", help="Mensaje confirmacion de cambio")

    return parser.parse_args()


def main():
    logger.info("Iniciando el programa ToolTube")
    args = ArgumentosCLI()

    Video_id = None
    if args.video_id:
        Video_id = args.video_id
    else:
        Video_id = buscarID()

    if Video_id is not None:
        logger.info(f"[URL-Youtube] https://youtu.be/{Video_id}")

    Credenciales = CargarCredenciales(args.canal)

    if args.uploader:
        if args.file:
            logger.info(f"Subiendo video {args.file} a Youtube")
            try:
                SubirVideo(Credenciales, args.file, args.nota)
            except HttpError as e:
                print("un error HTTP %d occurred:\n%s" % (e.resp.status, e.content))
        else:
            logger.info("Falta Archivo para subir -f")
    elif args.estado:
        logger.info(f"Actualizando estado del video {Video_id}")
        ActualizarEstadoVideo(Credenciales, Video_id, args.estado)
    elif args.descripcion:
        if args.folder:
            logger.info(f"Usando Folder {args.folder}")
        if Video_id:
            logger.info(f"Actualizando descripcion del Video {Video_id}")
            ActualizarDescripcionVideo(Credenciales, Video_id, args.file, Directorio=args.folder)
        elif args.recursivo:
            logger.info("Actualizando descripciones de los video dentro de folder")
            if args.max:
                logger.info(f"Con limite {args.max} Videos")
            ActualizarDescripcionFolder(Credenciales, Max=args.max, Directorio=args.folder)
        else:
            logger.info("Falta el ID del video")
    elif args.titulo:
        if Video_id is not None:
            respuesta = ActualizarTituloVideo(Credenciales, Video_id, args.titulo)
            if respuesta:
                analisis.salvar_data_analitica("1.Cambios/titulos.csv", args.titulo, args.nota)
        else:
            logger.info(f"Necesario indicar ID del video")
    elif args.miniatura:
        if Video_id is not None:
            logger.info(f"Actualizando Miniatura del Video {Video_id}")
            respuesta = ActualizarThumbnails(Credenciales, Video_id, args.miniatura)

            if respuesta is not None:
                if respuesta:
                    analisis.salvar_data_analitica("1.Cambios/miniatura.csv", args.file, args.nota)
        else:
            logger.info(f"Necesario indicar ID del video")
    elif args.idioma:
        if Video_id:
            logger.info(f"Actualizando Idioma del Video {Video_id}")
            ActualizarIdioma(Credenciales, Video_id)
    else:
        logger.info("Comandos no encontrado, prueba con -h")


if __name__ == "__main__":
    main()
