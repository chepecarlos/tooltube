#!/home/chepecarlos/5.Programas/2.Heramientas/5.tooltube/venv/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
import argparse
import os
import pickle
import httplib2
import random
import time

try:
    import httplib
except ImportError:
    import http.client as httplib

from pathlib import Path

from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from funcioneslogging import ConfigurarLogging

TagsDefaul = "ALSW"
logger = logging.getLogger(__name__)
ConfigurarLogging(logger)

httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                        httplib.IncompleteRead, httplib.ImproperConnectionState,
                        httplib.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


parser = argparse.ArgumentParser(description='Heramienta de Automatizacion de Youtube')
parser.add_argument('--thumbnails', '-t', help="Actualizar de Thumbnails video en Youtube", action="store_true")
parser.add_argument("--descripcion", '-d', help="Actualizar de descripcion video en Youtube", action="store_true")
parser.add_argument("--uploader", '-u', help="Suvir video a youtube", action="store_true")

parser.add_argument('--video_id', '-id', help="ID del video a actualizar Youtube")
parser.add_argument('--file', '-f', help="Archivo a usar para actualizar Youtube")
parser.add_argument("--max", '-m', help="Cantidad a actualizar", type=int)
parser.add_argument("--recursivo", '-r', help="Actualiza con todos los archivos disponibles", action="store_true")


ArchivoLocal = os.path.join(Path.home(), '.config/tooltube')

if sys.version_info[0] < 3:
    logger.error("Tienes que usar Python 3 para este programa")
    sys.exit(1)


def CargarCredenciales():
    """Optienes credenciales para API de youtube."""
    credentials = None
    ArchivoPickle = ArchivoLocal + "/data/token.pickle"
    if os.path.exists(ArchivoPickle):
        logger.info('Cargando credenciales API Youtube, del Archivo pickle...')
        with open(ArchivoPickle, 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info('Recargando credenciales...')
            credentials.refresh(Request())
        else:
            logger.info('Opteniendo nuevas credenciales...')
            client_secrets = ArchivoLocal + "/data/client_secrets.json"
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets,
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly',
                    'https://www.googleapis.com/auth/youtube',
                    'https://www.googleapis.com/auth/youtubepartner'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            with open(ArchivoPickle, 'wb') as f:
                logger.info('Salvando credenciales para el futuro en archivo pickle...')
                pickle.dump(credentials, f)

    return credentials


def ActualizarDescripcionVideo(credenciales, video_id, archivo=""):
    """Actualizar Descripcion de Video Youtube si es necesario."""
    DescripcionVideo = ""
    if not archivo:
        archivo = video_id + ".txt"
        logger.info(f"Usando el archivo {archivo} por defecto")

    if os.path.exists(archivo):
        with open(archivo, 'r') as linea:
            DescripcionVideo = linea.read()
    else:
        logger.warning(f"Erro fatal el archivo {archivo} no existe")
        return -1
    youtube = build("youtube", "v3", credentials=credenciales)

    SolisitudVideo = youtube.videos().list(
        id=video_id,
        part='snippet'
    )

    DataVideo = SolisitudVideo.execute()
    if len(DataVideo["items"]) > 0:
        SnippetVideo = DataVideo["items"][0]["snippet"]

        if DescripcionVideo == SnippetVideo["description"]:
            logger.info("Ya Actualizado")
            return 0

        SnippetVideo["description"] = DescripcionVideo

        SolisituActualizar = youtube.videos().update(
            part='snippet',
            body=dict(
                snippet=SnippetVideo,
                id=video_id
            ))

        RespuestaYoutube = SolisituActualizar.execute()
        if len(RespuestaYoutube['snippet']) > 0:
            logger.info("Actualizacion Completa")
            return 1
        else:
            logger.warning("Hubo un problema?")
            return -1
    else:
        logger.warning(f"No existe el video con ID {video_id}")
        return -1


def ActualizarDescripcionFolder(credenciales, Max=None):
    """Actualiza Descripciones de Video desde los archivos de un Folder."""
    contador = 0
    total = len(os.listdir("."))
    Actualizados = 0
    Error = 0
    for archivo in os.listdir("."):
        if archivo.endswith(".txt"):
            contador += 1
            video_id = archivo.replace(".txt", "")
            logger.info(f"Verificando ({contador}/{total}) - Video_ID:{video_id}")
            Resultado = ActualizarDescripcionVideo(credenciales, video_id, archivo)
            if Resultado == 1:
                Actualizados += 1
                logger.info(f"Link: https://youtu.be/{video_id}")
                if Max is not None:
                    if Actualizados >= Max:
                        logger.info(f"Se detubo al alcanzar {Actualizados} videos")
                        return
            elif Resultado == -1:
                Error += 1
    logger.info(f"Se actualizo {Actualizados}/{total} descripciones de video")
    if Error > 0:
        logger.info(f"Hubo error {Error}/{total}")


def ActualizarThumbnails(credenciales, video_id, archivo=""):
    """Actualiza la Miniatura de un video de Youtube."""
    if archivo == "":
        archivo = video_id + ".png"
    if os.path.exists(archivo):
        youtube = build("youtube", "v3", credentials=credenciales)
        Respuesta = youtube.thumbnails().set(
            videoId=video_id,
            media_body=archivo
        ).execute()
        if Respuesta['items'][0]:
            logger.info(f"Imagen Actualizada para {video_id} - {Respuesta['items'][0]['maxres']['url']}")
        else:
            logger.warning("Hubo un problema :(")
    else:
        logger.warning(f"No existe el archivo {archivo}")


def SubirVideo(credenciales, Archivo):
    """Sube Video a Youtube."""
    global TagsDefaul
    if not os.path.exists(Archivo):
        logger.warning(f"No encontrado el archivo {Archivo}")
        exit()
    youtube = build("youtube", "v3", credentials=credenciales)

    tags = None
    if TagsDefaul:
        tags = TagsDefaul.split(",")

    body = dict(
        snippet=dict(
            title=f"Titulo {Archivo}",
            description="Descripcion",
            tags=tags,
            categoryId=27
        ),
        status=dict(
            privacyStatus="unlisted"
        )
    )

    Respuesta = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(Archivo, chunksize=-1, resumable=True)
    )

    RegargarSuvida(Respuesta)


def RegargarSuvida(Respuesta):
    """Mantiene la subida del video."""
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.info("Subiendo Archivo...")
            status, response = Respuesta.next_chunk()
            if response is not None:
                if 'id' in response:
                    logger.info(f"Se subio con exito {response['id']} | https://youtu.be/{response['id']} ")
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
                logger.warning("No mas intento de reconeccion")
                exit()

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            logger.warning(f"durmiendo por {sleep_seconds} y despues reintentando")
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    logger.info("Iniciando el programa ToolTube")
    args = parser.parse_args()

    Credenciales = CargarCredenciales()

    if args.descripcion:
        if args.video_id:
            logger.info(f"Actualizando descripcion del Video {args.video_id}")
            if args.file:
                ActualizarDescripcionVideo(Credenciales, args.video_id, args.file)
            else:
                ActualizarDescripcionVideo(Credenciales, args.video_id)
        elif args.recursivo:
            logger.info("Actualizando descripciones de los video")
            if args.max:
                logger.info(f"Con limite {args.max} Videos")
                ActualizarDescripcionFolder(Credenciales, args.max)
            else:
                ActualizarDescripcionFolder(Credenciales)
        else:
            logger.info("Falta el ID del video")
    elif args.thumbnails:
        if args.video_id:
            logger.info(f"Actualizando Miniatura del Video {args.video_id}")
            if args.file:
                ActualizarThumbnails(Credenciales, args.video_id, args.file)
            else:
                ActualizarThumbnails(Credenciales, args.video_id)
    elif args.uploader:
        if args.file:
            logger.info(f"Subiendo video {args.file} a Youtube")
            try:
                SubirVideo(Credenciales, args.file)
            except HttpError as e:
                print("un error HTTP %d occurred:\n%s" % (e.resp.status, e.content))
        else:
            logger.info("Falta Archivo para subir")
    else:
        logger.info("Comandos no encontrado")
