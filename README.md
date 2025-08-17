# tooltube

**ToolTube** es una herramienta de automatización para la gestión de videos en YouTube. Permite actualizar miniaturas, descripciones y subir videos de forma sencilla desde la línea de comandos. Está pensada para creadores de contenido que buscan agilizar tareas repetitivas y mantener sus canales organizados.

```bash
tooltube.py -h
__main__ - INFO - Iniciando el programa ToolTube
usage: tooltube.py [-h] [--thumbnails] [--descripcion] [--uploader] [--video_id VIDEO_ID] [--file FILE] [--recursivo]

Heramienta de Automatizacion de Youtube

optional arguments:
  -h, --help            show this help message and exit
  --thumbnails, -t      Actualizar de Thumbnails video en Youtube
  --descripcion, -d     Actualizar de descripcion video en Youtube
  --uploader, -u        Suvir video a youtube
  --video_id VIDEO_ID, -id VIDEO_ID
                        ID del video a actualizar Youtube
  --file FILE, -f FILE  Archivo a usar para actualizar Youtube
  --recursivo, -r       Actualiza con todos los archivos disponibles

```
