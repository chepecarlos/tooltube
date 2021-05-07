#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import logging
import argparse
import os
import pickle
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from funcioneslogging import ConfigurarLogging

logger = logging.getLogger(__name__)
ConfigurarLogging(logger)

parser = argparse.ArgumentParser(description='Heramienta de Automatizacion de Youtube')
parser.add_argument('--thumbnails', '-t', help="Archivo de Thumbnails  en Youtube",  action="store_true")
parser.add_argument("--descripcion", '-d', help="ID del video a actualizar descripcipn en Youtube",  action="store_true")

parser.add_argument('--video_id', '-id', help="ID del video a actualizar Youtube")
parser.add_argument('--file', '-f', help="Archivo a usar para actualizar Youtube")
parser.add_argument("--recursivo", '-r', help="Actualiza con todos los archivos disponibles",  action="store_true")

ArchivoLocal = os.path.join(Path.home(), '.config/tooltube')

if sys.version_info[0] < 3:
    logger.error("Tienes que usar Python 3 para este programa")
    sys.exit(1)


def CargarCredenciales():
    '''Optienes credenciales para API de youtube'''
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


def ActualizarDescripcion(video_id, archivo=""):
    credenciales = CargarCredenciales()
    if archivo == "":
        ActualizarVideo(video_id, credenciales)
    else:
        ActualizarVideo(video_id, credenciales, archivo)


def ActualizarVideo(video_id, credenciales, archivo=""):
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


def ActualizarDescripcionFolder():
    credenciales = CargarCredenciales()
    contador = 0
    total = len(os.listdir("."))
    Actualizados = 0
    Error = 0
    for archivo in os.listdir("."):
        if archivo.endswith(".txt"):
            contador += 1
            video_id = archivo.replace(".txt", "")
            logger.info(f"Verificando ({contador}/{total}) - Video_ID:{video_id}")
            Resultado = ActualizarVideo(video_id, credenciales, archivo)
            if Resultado == 1:
                Actualizados += 1
                logger.info(f"Link: https://youtu.be/{video_id}")
            elif Resultado == -1:
                Error += 1
    logger.info(f"Se actualizo {Actualizados}/{total} descripciones de video")
    if Error > 0:
        logger.info(f"Hubo error {Error}/{total}")


def ActualizarThumbnails(video_id, archivo=""):
    credenciales = CargarCredenciales()
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


if __name__ == "__main__":
    logger.info("Iniciando el programa ToolTube")
    args = parser.parse_args()

    if args.descripcion:
        if args.video_id:
            logger.info(f"Actualizando descripcion del Video {args.video_id}")
            if args.file:
                ActualizarDescripcion(args.video_id, args.file)
            else:
                ActualizarDescripcion(args.video_id)
        elif args.recursivo:
            logger.info("Empezando recursivo")
            ActualizarDescripcionFolder()
        else:
            logger.info("Falta el ID del video")
