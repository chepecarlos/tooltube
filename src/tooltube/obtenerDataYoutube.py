
import re
import requests
from bs4 import BeautifulSoup

import tooltube.miLibrerias as miLibrerias
import youtube_dl

logger = miLibrerias.ConfigurarLogging(__name__)


def obtenerDataVideo(id):

    resultado = None

    try:
        ydl = youtube_dl.YoutubeDL({"outtmpl": "%(id)s.%(ext)s", "quiet": True})

        with ydl:
            resultado = ydl.extract_info(f"http://www.youtube.com/watch?v={id}", download=False)
    except youtube_dl.utils.ExtractorError:
        logger.info("Usar YouTube-API")
        return None
    except youtube_dl.utils.DownloadError:
        logger.info("Usar YouTube-API")
        return None

    if resultado is None:
        return None

    if "entries" in resultado:
        data = resultado["entries"][0]
    else:
        data = resultado

    return data


def obtenerTitulo(id):

    data = obtenerDataVideo(id)

    if data is None:
        return None

    return data.get("title", None)


def obtenerDescripcion(id: str) -> str:
    "Obtiene la descripción de un video de YouTube"

    url= f"https://www.youtube.com/watch?v={id}"
    contenido = requests.get(url)
    if contenido.status_code != 200:
        logger.warning(f"error consulta {contenido.status_code}")
        return None
    soup = BeautifulSoup(contenido.content, "html.parser")
    patron = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
    try:
        description = patron.findall(str(soup))[0].replace('\\n','\n')
    except IndexError:
        logger.warning(f"Error: No se encontró la descripción en el contenido de {url}")
        return None

    return description
