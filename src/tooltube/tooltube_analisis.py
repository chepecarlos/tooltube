import argparse

import MiLibrerias
from operaciones import analisis, usuario

from .funcionesExtras import SalvarID, buscarID

logger = MiLibrerias.ConfigurarLogging(__name__)


def ArgumentosCLI():

    parser = argparse.ArgumentParser(prog="tooltube_analisis", description="Herramienta de Analisis de Youtube")

    parser.add_argument("--video_id", "-id", help="ID del video a actualizar Youtube")

    parser.add_argument("--salvar_id", help="Salvar ID del video")

    parser.add_argument("--vista", "-v", help="Mostar Vistas en Gráfica")
    parser.add_argument("--tiempo", "-t", help="Mostar Tiempo de Reproducción(Horas) en Gráfica")
    parser.add_argument("--duracion", "-d", help="Mostar Duración promedio de vista en Gráfica")
    parser.add_argument("--porcenta_clip", "-ctr", help="Mostar Click Through Rate en Gráfica")

    parser.add_argument("--usuario", help="Cambiar usuario del análisis")
    parser.add_argument("--url_analitica", "-csv", help="Pagina para descarga analítica del video", action="store_true")

    return parser.parse_args()


def main():
    logger.info("Iniciando el programa ToolTube Analisis")
    args = ArgumentosCLI()

    if args.salvar_id:
        logger.info(f"Salvando ID[{args.salvar_id}] del Video")
        SalvarID(args.salvar_id)
        return

    Video_id = None
    if args.video_id:
        Video_id = args.video_id
    else:
        Video_id = buscarID()

    if Video_id is not None:
        logger.info(f"[URL-Youtube] https://youtu.be/{Video_id}")

    if args.url_analitica:
        if Video_id is not None:
            logger.info("Descarga el cvs de la siguiente pagina:")
            logger.info(f" ID {Video_id}")
            logger.info(
                f"https://studio.youtube.com/video/{Video_id}/analytics/tab-overview/period-default/explore?entity_type=VIDEO&entity_id={Video_id}&time_period=lifetime&explore_type=TABLE_AND_CHART&metric=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&granularity=DAY&t_metrics=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&t_metrics=VIEWS&t_metrics=WATCH_TIME&t_metrics=AVERAGE_WATCH_TIME&dimension=DAY&o_column=VIDEO_THUMBNAIL_IMPRESSIONS_VTR&o_direction=ANALYTICS_ORDER_DIRECTION_DESC"
            )
        else:
            logger.warning("No encontró ID Video")
    elif args.usuario:
        usuario.SalvarUsuario(args.usuario)
    else:
        logger.info("Comandos no encontrado, prueba con -h")


if __name__ == "__main__":
    main()
