"""_summary_
"""

import requests
from pathlib import Path
import json

from tooltube import funcionesExtras
import tooltube.miLibrerias as miLibrerias

logger = miLibrerias.ConfigurarLogging(__name__)


def urlBase(raiz: str = None) -> str:
    data = miLibrerias.ObtenerArchivo("data/notion.md")
    if data is None:
        logger.warning("No data de Notion")
    if raiz is None:
        raiz = funcionesExtras.buscarRaiz()
    raiz = raiz.split(data["base"])[1]
    return raiz


def consultaPost(ruta: str):
    dataNotion = miLibrerias.ObtenerArchivo("data/notion.md")
    if dataNotion is None:
        logger.warning("No data de Notion")
        return None
    urlConsulta = f"https://api.notion.com/v1/databases/{dataNotion.get('base_datos')}/query"
    cabezaConsulta = {
        "Authorization": f"Bearer {dataNotion.get('token')}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }

    busqueda = {
        "filter": {
            "property": "Ruta Archivo",
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


def urlNotion(rutaInfo: str = None, buscar: bool = False, ):
    if rutaInfo is None:
        raiz = funcionesExtras.buscarRaiz()
        rutaInfo = f"{raiz}/1.Guion/1.Info.md"
    dataInfo = miLibrerias.ObtenerArchivo(rutaInfo)
    if dataInfo is None:
        logger.warning("Error obtener Notion")
        return
    if "id_notion" in dataInfo and not buscar:
        urlNotion = dataInfo.get("url_notion")
        print(f"URL Proyecto {urlNotion}")
        return dataInfo.get("id_notion")
    rutaRelativa = urlBase(rutaInfo).replace("/1.Guion/1.Info.md", "")
    logger.info(f"Buscando {rutaRelativa} en Notion")
    dataNotion = consultaPost(rutaRelativa)
    if dataNotion is None:
        return
    tituloNotion = dataNotion.get("title")
    urlNotion = dataNotion.get("url")
    idNotion = dataNotion.get("id")
    miLibrerias.SalvarValor(rutaInfo, "url_notion", urlNotion)
    miLibrerias.SalvarValor(rutaInfo, "id_notion", idNotion)
    print(f"URL {tituloNotion}: {urlNotion}")
    return idNotion


def abriNotion(folderActual: str):

    if folderActual is None:
        folderActual = funcionesExtras.buscarRaiz()

    nombreProyecto = Path(folderActual).name
    rutaInfo = f"{folderActual}/1.Guion/1.Info.md"

    if not Path(rutaInfo).exists():
        print("No es un proyecto")
        return

    urlNotion = miLibrerias.ObtenerValor(rutaInfo, "url_notion")
    if urlNotion is not None:
        funcionesExtras.ruta(urlNotion)


def abriYouTube(folderActual: str):

    if folderActual is None:
        folderActual = funcionesExtras.buscarRaiz()

    nombreProyecto = Path(folderActual).name
    rutaInfo = f"{folderActual}/1.Guion/1.Info.md"

    if not Path(rutaInfo).exists():
        print("No es un proyecto")
        return

    idYoutube = miLibrerias.ObtenerValor(rutaInfo, "youtube_id")
    if idYoutube is not None and idYoutube != "ID_Youtube":
        rutaYoutube = f"https://www.youtube.com/watch?v={idYoutube}"
        print(rutaYoutube)
        print(f"Abriendo {nombreProyecto} Youtube: {rutaYoutube}")
        funcionesExtras.ruta(rutaYoutube)
    else:
        print("No se encontró ID de Youtube")


def estadoNotion(estado: str, rutaInfo: str = None) -> bool:
    idPagina = urlNotion(rutaInfo)

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


def actualizarEstadoNotion(rutaInfo: str, estado: str, encargado: str, canal: str, fecha: str) -> bool:
    idPagina = urlNotion(rutaInfo)

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

    dataJson = {
        "properties": {
            "Canal": {
                "select": {
                    "name": canal
                }
            },
            "Asignado": {
                "select": {
                    "name": encargado
                }
            },
            "Estado": {
                "select": {
                    "name": estado
                }
            }
        }
    }

    if estado == "publicado" or estado == "analizando":
        dataJson["properties"]["Terminado"] = {
            "checkbox": True
        }
        dataJson["properties"]["Hacer para"] = {
            "date": {
                "start": f"{fecha}"
            }
        }

    respuesta = requests.patch(urlConsulta, json=dataJson, headers=cabezaConsulta)

    if respuesta.status_code == 200:
        logger.info("Se actualizar pagina de Notion")
        return True
    else:
        logger.warning(f"No se puede actualizar Notion - {respuesta.status_code}")
        logger.warning(respuesta.json())
        return False


def canalNotion(canal: str, rutaInfo: str = None) -> bool:
    idPagina = urlNotion(rutaInfo)

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

    jsonEstado = {
        "properties": {
            "Canal": {
                "select": {
                    "name": canal
                }
            }
        }
    }

    respuesta = requests.patch(urlConsulta, json=jsonEstado, headers=cabezaConsulta)

    if respuesta.status_code == 200:
        logger.info("Se actualizar pagina de Notion")
        return True
    else:
        logger.warning("No se puede actualizar Notion")
        return False


def asignadoNotion(asignado: str, folderInfo: str = None) -> bool:
    idPagina = urlNotion(folderInfo)

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

    ruta = str(ruta)
    nombreTitulo = ruta.split("/")[-1]
    nombreTitulo = nombreTitulo.split("_")[1:]
    nombreTitulo = " ".join(nombreTitulo)
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
            "Canal": {
                "select": {
                    "name": "desconocido"
                }
            },
            "Ruta Archivo": {
                "rich_text": [
                    {
                        "text": {
                            "content": rutaRelativa
                        }
                    }
                ]
            },
            "Área": {
                "relation": [
                    {
                        "id": dataNotion.get("id_creacion_contenido")
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
        print(respuesta.json())


def actualizarNotion(rutaInfo: str, actualizar: bool = False) -> None:
    rutaRelativa = urlBase(rutaInfo).replace("/1.Guion/1.Info.md", "")
    dataNotion = consultaPost(rutaRelativa)

    if dataNotion is None:
        miLibrerias.SalvarValor(rutaInfo, "error", "no-notion")
        return None
    else:
        miLibrerias.SalvarValor(rutaInfo, "error", "no-error")

    urlNotion = dataNotion.get("url")

    terminadoNotion = dataNotion.get("properties").get("Terminado").get("checkbox")
    estadoNotion = "desconocido"
    if terminadoNotion == True:
        estadoNotion = "publicado"
    else:
        estadoNotion = dataNotion.get("properties").get("Estado").get("select")
        if estadoNotion is not None:
            estadoNotion = estadoNotion.get("name")
        if estadoNotion == "publicado":
            terminadoNotion = True

    asignadoNotion = dataNotion.get("properties").get("Asignado").get("select", "desconocido")
    if asignadoNotion is None:
        asignadoNotion = "desconocido"
    else:
        asignadoNotion = asignadoNotion.get("name")

    canalNotion = dataNotion.get("properties").get("Canal").get("select")
    if canalNotion is None:
        canalNotion = "desconocido"
    else:
        canalNotion = canalNotion.get("name")

    estadoAnterior = miLibrerias.ObtenerValor(rutaInfo, "estado")
    asignadoAnterior = miLibrerias.ObtenerValor(rutaInfo, "asignado")
    canalAnterior = miLibrerias.ObtenerValor(rutaInfo, "canal")

    miLibrerias.SalvarValor(rutaInfo, "estado", estadoNotion)
    miLibrerias.SalvarValor(rutaInfo, "asignado", asignadoNotion)
    miLibrerias.SalvarValor(rutaInfo, "canal", canalNotion)
    miLibrerias.SalvarValor(rutaInfo, "terminado", terminadoNotion)

    if estadoAnterior != estadoNotion:
        print(f"Actualizar estado {estadoAnterior} a {estadoNotion}")

    if asignadoAnterior != asignadoNotion:
        print(f"Actualizar asignado {asignadoAnterior} a {asignadoNotion}")

    if canalAnterior != canalNotion:
        print(f"Actualizar canal {canalAnterior} a {canalNotion}")

    print(f"Ruta: {urlNotion}")
    return True
