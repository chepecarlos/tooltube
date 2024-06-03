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


def estadoNotion(estado: str) -> bool:
    idPagina = urlNotion()

    if idPagina is None:
        logger.warning("Error no se encontró ID")
        return False

    dataNotion = miLibrerias.ObtenerArchivo("data/notion.md")
    if dataNotion is None:
        logger.warning("No data de Notion")
        return False

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
        return True
    else:
        logger.warning("No se puede actualizar Notion")
        return False


def asignadoNotion(asignado: str) -> bool:
    idPagina = urlNotion()

    if idPagina is None:
        logger.warning("Error no se encontró ID")
        return False

    dataNotion = miLibrerias.ObtenerArchivo("data/notion.md")
    if dataNotion is None:
        logger.warning("No data de Notion")
        return False

    urlConsulta = f"https://api.notion.com/v1/pages/{idPagina}"

    cabezaConsulta = {
        "Authorization": f"Bearer {dataNotion.get('token')}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }

    asignado = {
        "properties": {
            "Asignado": {
                "select": {
                    "name": asignado
                }
            }
        }
    }

    respuesta = requests.patch(urlConsulta, json=asignado, headers=cabezaConsulta)

    if respuesta.status_code == 200:
        logger.info("Se actualizar pagina de Notion")
        return True
    else:
        logger.warning("No se puede actualizar Notion")
        return False


def crearNotion(ruta: str) -> bool:

    dataNotion = miLibrerias.ObtenerArchivo("data/notion.md")
    if dataNotion is None:
        logger.warning("No data de Notion")
        return False

    nombreTitulo = ruta.split("/")[-1]
    nombreTitulo = nombreTitulo.split("_")[1:]
    nombreTitulo = "".join(nombreTitulo)
    rutaRelativa = ruta.split(dataNotion.get("base"))[1]
    print()
    print(f"Creando en Notion {nombreTitulo}- {ruta}")

    urlConsulta = "https://api.notion.com/v1/pages"

    cabezaConsulta = {
        "Authorization": f"Bearer {dataNotion.get('token')}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }

    dataPagina = {
        "parent": {
            "database_id": dataNotion.get('base_datos')
        },
        "properties": {
            "Nombre": {
                "title": [
                    {
                        "text": {
                            "content": nombreTitulo
                        }
                    }
                ]
            },
            "Asignado": {
                "select": {
                    "name": "desconocido"
                }
            },
            "Estado": {
                "select": {
                    "name": "desconocido"
                }
            },
            "URL NocheProgramacion": {
                "rich_text": [
                    {
                        "text": {
                            "content": rutaRelativa
                        }
                    }
                ]
            }
        }
    }
    
    respuesta = requests.post(urlConsulta, headers=cabezaConsulta, data=json.dumps(dataPagina))
    
    if respuesta.status_code == 200:
        
        dataNotion = respuesta.json()

        rutaInfo = f"{ruta}/1.Guion/1.Info.md"
        urlNotion = dataNotion.get("url")
        idNotion = dataNotion.get("id")
        
        miLibrerias.SalvarValor(rutaInfo, "url_notion", urlNotion)
        miLibrerias.SalvarValor(rutaInfo, "id_notion", idNotion)
        
        print(f"Información Salvada Notion en URL: {urlNotion}")
    else:
        print("Error notion subiendo el video")
