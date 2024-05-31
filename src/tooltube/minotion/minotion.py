"""_summary_
"""

import requests
import json

from tooltube import funcionesExtras
import tooltube.miLibrerias as miLibrerias

logger = miLibrerias.ConfigurarLogging(__name__)


def urlBase() -> str:
    data = miLibrerias.ObtenerArchivo("data/notion.md")
    if data is None:
        logger.warning("No data de Notion")
    raiz = funcionesExtras.buscarRaiz()
    raiz = raiz.split(data["base"])[1]
    return raiz


def consultaPost(dataNotion, ruta):
    urlConsulta = f"https://api.notion.com/v1/databases/{dataNotion.get('base_datos')}/query"
    cabezaConsulta = {
        "Authorization": f"Bearer {dataNotion.get('token')}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }

    busqueda = {
        "filter": {
            "property": "URL NocheProgramacion",
            "text": {
                "contains": ruta
            }
        }
    }

    respuesta = requests.post(urlConsulta, headers=cabezaConsulta, data=json.dumps(busqueda))
    if respuesta.status_code == 200:
        dataRespuesta = respuesta.json()
        dataRespuesta = dataRespuesta.get("results")
        if len(dataRespuesta) == 0:
            logger.info("No se encontró en Notion")
            return None
        dataRespuesta = dataRespuesta[0]
        return dataRespuesta


def urlNotion():
    logger.info("buscando url notion")
    dataNotion = miLibrerias.ObtenerArchivo("data/notion.md")
    if dataNotion is None:
        logger.warning("No data de Notion")
        return
    raiz = funcionesExtras.buscarRaiz()
    rutaInfo = f"{raiz}/1.Guion/1.Info.md"
    dataInfo = miLibrerias.ObtenerArchivo(rutaInfo)
    if "id_notion" in dataInfo:
        urlNotion = dataInfo.get("url_notion")
        print(f"URL Proyecto {urlNotion}")
        return dataInfo.get("id_notion")
    base = urlBase()
    dataNotion = consultaPost(dataNotion, base)
    if dataNotion is None:
        return
    urlNotion = dataNotion.get("url")
    idNotion = dataNotion.get("id")
    miLibrerias.SalvarValor(rutaInfo, "url_notion", urlNotion)
    miLibrerias.SalvarValor(rutaInfo, "id_notion", idNotion)
    print(f"URL Proyecto {urlNotion}")
    return idNotion


def estadoNotion(estado: str):
    idPagina = urlNotion()

    if idPagina is None:
        logger.warning("Error no se encontró ID")
        return

    dataNotion = miLibrerias.ObtenerArchivo("data/notion.md")
    if dataNotion is None:
        logger.warning("No data de Notion")
        return

    urlConsulta = f"https://api.notion.com/v1/pages/{idPagina}"

    cabezaConsulta = {
        "Authorization": f"Bearer {dataNotion.get('token')}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }

    estado = {
        "properties": {
            "Estado": {
                "select": {
                    "name": estado
                }
            }
        }
    }

    respuesta = requests.patch(urlConsulta, json=estado, headers=cabezaConsulta)

    if respuesta.status_code == 200:
        logger.info("Se actualizar pagina de Notion")
    else:
        logger.warning("No se puede actualizar Notion")
