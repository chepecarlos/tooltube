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

    if "title" in data:
        return data["title"]


def obtenerDescripcion(id):

    data = obtenerDataVideo(id)

    if data is None:
        return None

    if "description" in data:
        return data["description"]
