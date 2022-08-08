"""Funciones de Usuario."""

import tooltube.miLibrerias as miLibrerias
from tooltube.miLibrerias import FuncionesArchivos

logger = miLibrerias.ConfigurarLogging(__name__)


def SalvarUsuario(Nombre):
    """
    Salvar nombre de usuario
    """
    logger.info(f"Salvando usuario {Nombre}")
    FuncionesArchivos.SalvarValor("data/usuario.json", "usuario", Nombre)


def ObtenerUsuario():
    return FuncionesArchivos.ObtenerValor("data/usuario.json", "usuario")
