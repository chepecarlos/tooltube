# -*- coding: utf-8 -*-
# https://github.com/youtube/api-samples

import argparse
import os
import pickle
import random
import sys
import time
import json


import colorama
import httplib2
import pyperclip
from googleapiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import tooltube.funcionesExtras as FuncionesExtras
import tooltube.miLibrerias as miLibrerias
import tooltube.obtenerDataYoutube as dataYoutube
from tooltube.operaciones import analisis, usuario

try:
    import httplib
except ImportError:
    import http.client as httplib

from pathlib import Path

from colorama import Back, Fore, Style

colorama.init(autoreset=True)

logger = miLibrerias.ConfigurarLogging(__name__)

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
        FolderData = os.path.join(FolderData, Canal)

    logger.info(f"Usando canal {Canal}")
    if not os.path.exists(FolderData):
        os.makedirs(FolderData)

    ArchivoPickle = FolderData + "/token.pickle"
    ArchivoInfo = FolderData + "/info.md"

    if os.path.exists(ArchivoInfo):
        logger.info("Permisos sin Membrecía")
        permisosYoutube = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtubepartner",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ]
    else:
        logger.info("Permisos con Membrecía")
        permisosYoutube = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtubepartner",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.channel-memberships.creator",
        ]

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
            # Todo: Hacer un error mas fatal
            if not os.path.exists(client_secrets):
                logger.warning("No existe client_secrets.json agrégalo a {FolderData}")
                return
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets,
                scopes=permisosYoutube,
            )

            flow.run_local_server(
                port=8080, prompt="consent", authorization_prompt_message=""
            )
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
            logger.info(f"Titulo del Video {video_id} ya actualizado")
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

    try:
        DataVideo = solicitudVideo.execute()
    except HttpError as e:
        return imprimirError(e, video_id)
    except httplib2.error.ServerNotFoundError as error:
        print(f"Error fatal con solicitud {error}")
        exit()
    except:
        print("Error fatal con solicitud")
        exit()

    if len(DataVideo["items"]) > 0:
        SnippetVideo = DataVideo["items"][0]["snippet"]

        if nuevaDescripcion == SnippetVideo["description"]:
            return 0

        SnippetVideo["description"] = nuevaDescripcion

        SolisituActualizar = youtube.videos().update(part="snippet", body=dict(snippet=SnippetVideo, id=video_id))

        try:
            RespuestaYoutube = SolisituActualizar.execute()
        except HttpError as e:
            return imprimirError(e, video_id)

        if len(RespuestaYoutube["snippet"]) > 0:
            logger.info(f"Actualización Completa - Link: https://youtu.be/{video_id}")
            return 1
        else:
            logger.warning("Hubo un problema?")
            return -1
    else:
        logger.warning(f"No existe el video con ID {video_id}")
        return -1


def imprimirError(error, video_id):
    rasonError = error.resp.reason
    if error.resp.status == 403:
        if rasonError in ['Forbidden']:
            logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + f"https://youtu.be/{video_id} - {rasonError} No tienes permisos, API-Youtube: {error.resp.status}")
            return -1
        else:
            logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT +
                           f"https://youtu.be/{video_id} - {rasonError} Sobrepaso de llamas a API esperar 24 horas, API-Youtube: {error.resp.status}")
        exit()
    logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + f"Erro https://youtu.be/{video_id} - {rasonError} con API-Youtube: {error.resp.status}")
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
            logger.warning("No necesario cambiar estado")
            return False

        data_estado["privacyStatus"] = estado
        print("--" * 40)
        print(data_estado)
        print(data_estado["privacyStatus"])

        solicitudActualizar = youtube.videos().update(
            part="status", body=dict(status=data_estado, id=video_id)
        )

        respuesta_youtube = solicitudActualizar.execute()

        print(respuesta_youtube)

        # print(data_video["status"]["status"])


def ActualizarDescripcionFolder(
    credenciales,
    Max=None,
    Directorio=None,
    total=None,
    contador=None,
    error=None,
    Actualizados=None,
):
    """Actualiza Descripciones de Video desde los archivos de un Folder."""
    if contador is None:
        contador = 0
    if error is None:
        error = 0
    if Directorio is None:
        Directorio = "."
    if total is None:
        total = totalTxt(Directorio)
        logger.info(f"Total Videos: {total}")
    if Actualizados is None:
        Actualizados = 0
    listaArchivos = sorted(os.listdir(Directorio), reverse=True)
    for archivo in listaArchivos:
        direcionArchivo = Directorio + "/" + archivo
        if os.path.isdir(direcionArchivo):
            [contador, Actualizados] = ActualizarDescripcionFolder(
                credenciales,
                contador=contador,
                Directorio=direcionArchivo,
                total=total,
                Actualizados=Actualizados,
            )
        if archivo.endswith(".txt"):
            contador += 1
            video_id = archivo.replace(".txt", "")
            # logger.info(f"V({contador}/{total}) A/{Actualizados} - Video_ID:{video_id} - folder:{Directorio}")
            print(f"V({contador}/{total}) A/{Actualizados} - Video_ID:{video_id} - folder:{Directorio}\r", end="")
            Resultado = ActualizarDescripcionVideo(credenciales, video_id, archivo, Directorio)
            if Resultado == 1:
                Actualizados += 1
                if Max is not None:
                    if Actualizados >= Max:
                        Porcentaje = (Actualizados / total) * 100
                        logger.info(f"Se actualizo {Actualizados}/{total} - {Porcentaje:.2f} % descripciones de video")
                        return
            elif Resultado == -1:
                error += 1
    if contador == total:
        # Todo: error de mostrar multiples veces esta linea por recursividad
        porcentaje = (Actualizados / total) * 100
        logger.info(f"Se actualizo {Actualizados}/{total} - {porcentaje:.2f} % descripciones de video")
        if error > 0:
            logger.info(f"Hubo error {error}/{total}")
    return [contador, Actualizados]


def totalTxt(Directorio):
    contador = 0
    for archivo in os.listdir(Directorio):
        direccionArchivo = Directorio + "/" + archivo
        if os.path.isdir(direccionArchivo):
            contador += totalTxt(direccionArchivo)

        if direccionArchivo.endswith(".txt"):
            contador += 1

    return contador


def ActualizarThumbnails(credenciales, video_id, archivo=None):
    """Actualiza la Miniatura de un video de Youtube."""
    if archivo is None:
        archivo = video_id + ".png"
    if os.path.exists(archivo):
        youtube = build("youtube", "v3", credentials=credenciales)
        Respuesta = (youtube.thumbnails().set(videoId=video_id, media_body=archivo).execute())
        if Respuesta["items"][0]:
            if "maxres" in Respuesta["items"][0]:
                logger.info(f"Imagen Actualizada para {video_id} - {Respuesta['items'][0]['maxres']['url']}")
            elif "default" in Respuesta["items"][0]:
                logger.info(f"Imagen Actualizada para {video_id} - {Respuesta['items'][0]['default']['url']}")
            else:
                print(Respuesta["items"][0])
            return True
        else:
            logger.warning("Hubo un problema :(")
    else:
        logger.warning(f"No existe el archivo {archivo}")

    return False


def ObtenerMiembros(credenciales):
    youtube = build("youtube", "v3", credentials=credenciales)
    solicitud = youtube.members().list(
        part="snippet",
        maxResults=5,  # Puedes ajustar la cantidad de resultados por página
        mode="all_current"  # Puedes cambiar el modo a "updates"
    )
    respuesta = solicitud.execute()
    print(respuesta)
    print(dir(respuesta))
    # TODO: Aun no funciona


def ActualizarIdioma(credenciales, video_id, Lenguaje="es"):
    """
    Actualiza Lenguaje video y descripción
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


def SubirVideo(credenciales, archivo, Comentario=""):
    """Sube Video a Youtube."""
    global TagsDefault
    if not os.path.exists(archivo):
        logger.warning(f"No encontrado el archivo {archivo}")
        exit()
    youtube = build("youtube", "v3", credentials=credenciales)

    tags = None
    if TagsDefault:
        tags = TagsDefault.split(",")

    tituloVideo = archivo.split("/")[-1]

    body = dict(
        snippet=dict(
            title=f"Titulo {tituloVideo}",
            description="Descripcion",
            tags=tags,
            categoryId=27,
            defaultLanguage="es",
            defaultAudioLanguage="es",
        ),
        status=dict(privacyStatus="unlisted"),
    )

    Respuesta = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(archivo, chunksize=-1, resumable=True),
    )

    return RecargarSubida(Respuesta, Comentario, archivo)


def RecargarSubida(respuesta, comentario, archivo: str = None):
    """Mantiene la subida del video."""
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.info("Subiendo Archivo...")
            status, response = respuesta.next_chunk()
            if response is not None:
                if "id" in response:
                    folderArchivo = None
                    if archivo is not None:
                        folderArchivo = Path(archivo).parents[0]
                        folderArchivo = miLibrerias.rutaAbsoluta(folderArchivo)
                    FuncionesExtras.SalvarDato("youtube_id", response["id"], folderArchivo)
                    logger.info(f"Se subio con exito {response['id']} | https://youtu.be/{response['id']} ")
                    analisis.salvar_data_analitica("1.Cambios/estado.csv", "suvido", comentario, folderArchivo)
                else:
                    logger.warning(f"The upload failed with an unexpected response: {response}")
                    exit()
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content,)
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
            logger.warning(f"durmiendo por {sleep_seconds} y después reintentando")
            time.sleep(sleep_seconds)


def ActualizarMiniatura(Credenciales, miniatura, id, nota):
    logger.info(f"Actualizando Miniatura del Video {id}")
    respuesta = ActualizarThumbnails(Credenciales, id, miniatura)

    if respuesta is not None:
        if respuesta:
            analisis.salvar_data_analitica("1.Cambios/miniatura.csv", miniatura, nota)


def ActualizarTitulo(Credenciales, titulo, id, nota) -> None:
    respuesta = ActualizarTituloVideo(Credenciales, id, titulo)
    if respuesta:
        analisis.salvar_data_analitica("1.Cambios/titulos.csv", titulo, nota)
        FuncionesExtras.SalvarDato("titulo", titulo)


def ActualizarMetadata(credenciales, ID, folderActual: str = None) -> None:
    Titulo = FuncionesExtras.buscarDato("titulo", folderActual)
    Miniatura = FuncionesExtras.buscarDato("miniatura", folderActual)
    if Titulo and Titulo != "Titulo Video":
        print(f"Titulo: {Titulo} ")
        ActualizarTitulo(credenciales, Titulo, ID, "Actualizado por herramienta")
    if Miniatura:
        print(f"Miniatura: {Miniatura} ")
        archivo = FuncionesExtras.rutaBase(folderActual) + "/7.Miniatura/2.Render/" + Miniatura
        ActualizarMiniatura(credenciales, archivo, ID, "Actualizado por herramienta")


def FuncionSinID(args):
    if args.titulo:
        FuncionesExtras.SalvarDato("titulo", args.titulo)
    elif args.miniatura:
        FuncionesExtras.SalvarDato("miniatura", args.miniatura)
    else:
        logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + "Error Falta ID")


def obtenerColaboradores():
    texto = ""
    lista = FuncionesExtras.buscarDato("listaColaboradores")
    if lista is None:
        logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + "No hay Colaboradores")
        return
    
    for colaborador in lista:
        texto += f"  - colaborador: {colaborador}\n"
    pyperclip.copy(texto)
    logger.info(Fore.BLACK + Back.GREEN + Style.BRIGHT + "Lista Colaboradores Copiada al portapapeles")


def ArgumentosCLI() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="tooltube", description="Herramienta de Automatización de Youtube")
    parser.add_argument("--estado", "-e", help="Actualiza Estado de un video")
    parser.add_argument("--miniatura", "-m", help="Actualizar de Miniatura de video en Youtube")
    parser.add_argument("--titulo", "-t", help="Actualizar de titulo video en Youtube")
    parser.add_argument("--descripcion", "-d", help="Actualizar de descripción video en Youtube", action="store_true")
    parser.add_argument("--uploader", "-u", help="Subir video a youtube")
    parser.add_argument("--actualizar", "-a", help="Actualizar la metadata", action="store_true")
    parser.add_argument("--idioma", "-i", help="Actualizar de Idioma video a youtube", action="store_true")
    parser.add_argument("--miembros", help="Descarga los miembros del canal", action="store_true")
    parser.add_argument("--colaboradores", help="Descarga los miembros del canal", action="store_true")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")
    parser.add_argument("--file", "-f", help="Archivo a usar para actualizar Youtube")
    parser.add_argument("--folder", help="Directorio a usar")
    parser.add_argument("--max", help="Cantidad a actualizar", type=int)
    parser.add_argument("--recursivo", "-r", help="Actualiza con todos los archivos disponibles", action="store_true")

    parser.add_argument("--canal", "-c", help="Canal Youtube a usar")
    parser.add_argument("--nota", "-n", help="Mensaje confirmación de cambio")

    return parser.parse_args()


def main():
    logger.info("Iniciando el programa ToolTube")
    args = ArgumentosCLI()

    Video_id = None
    if args.video_id:
        Video_id = args.video_id
    else:
        Video_id = FuncionesExtras.buscarDato("youtube_id")

    if Video_id is not None:
        if not args.colaboradores and not args.uploader:
            if Video_id == "ID_Youtube":
                FuncionSinID(args)
                return
        logger.info(f"[URL-Youtube] https://youtu.be/{Video_id}")

    Credenciales = CargarCredenciales(args.canal)

    if args.uploader:
        # if args.file:
        logger.info(f"Subiendo video {args.uploader} a Youtube")
        try:
            SubirVideo(Credenciales, args.uploader, args.nota)
            ActualizarMetadata(Credenciales, FuncionesExtras.buscarDato("youtube_id"))
        except HttpError as e:
            dataProblema = json.loads(e.content)
            problema = dataProblema.get("error").get("errors")[0].get("reason")
            if problema == "quotaExceeded":
                logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + f"Cuota sobre pasada esperar al siguiente dia")
            else:
                print("un error HTTP %d occurred:\n%s" % (e.resp.status, e.content))
        # else:
        #     logger.info("Falta Archivo para subir -f")
    elif args.estado:
        logger.info(f"Actualizando estado del video {Video_id}")
        ActualizarEstadoVideo(Credenciales, Video_id, args.estado)
    elif args.descripcion:
        if args.folder:
            logger.info(f"Usando Folder {args.folder}")
        if Video_id:
            logger.info(f"Actualizando descripción del Video {Video_id}")
            ActualizarDescripcionVideo(Credenciales, Video_id, args.file, Directorio=args.folder)
        elif args.recursivo:
            logger.info("Actualizando descripciones de los video dentro de folder")
            if args.max:
                logger.info(f"Con limite {args.max} Videos")
            try:
                ActualizarDescripcionFolder(Credenciales, Max=args.max, Directorio=args.folder)
            except KeyboardInterrupt:
                logger.info("Cancelando Actualización de Folder")
        else:
            logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + "Falta el ID del video")
    elif args.titulo:
        if Video_id is not None:
            ActualizarTitulo(Credenciales, args.titulo, Video_id, args.nota)
        else:
            logger.warning(
                Fore.WHITE
                + Back.RED
                + Style.BRIGHT
                + f"Error no encontrado ID Video en 1.Info.md"
            )
    elif args.miniatura:
        if Video_id is not None:
            ActualizarMiniatura(Credenciales, args.miniatura, Video_id, args.nota)
        else:
            logger.warning(
                Fore.WHITE
                + Back.RED
                + Style.BRIGHT
                + f"Error no encontrado ID Video en 1.Info.md"
            )
    elif args.idioma:
        if Video_id:
            logger.info(f"Actualizando Idioma del Video {Video_id}")
            ActualizarIdioma(Credenciales, Video_id)
    elif args.actualizar:
        ActualizarMetadata(Credenciales, Video_id)
    elif args.miembros:
        ObtenerMiembros(Credenciales)
    elif args.colaboradores:
        obtenerColaboradores()
    else:
        logger.warning(
            Fore.WHITE
            + Back.RED
            + Style.BRIGHT
            + "comandos no encontrado, prueba con -h"
        )


if __name__ == "__main__":
    main()
