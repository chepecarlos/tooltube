import argparse

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)
import funcionesExtras

from .funcionesExtras import SalvarID, buscarID


def ArgumentosCLI():

    parser = argparse.ArgumentParser(prog="tooltube_get", description="Obtiene Data de un video")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")

    parser.add_argument("--salvar_id", help="Salvar ID del video")

    return parser.parse_args()


def main():
    logger.info("Iniciando el programa ToolTube Analisis")
    args = ArgumentosCLI()

    Video_id = None
    if args.video_id:
        Video_id = args.video_id
    else:
        Video_id = funcionesExtras.buscarID()

    if args.id:
        pass
