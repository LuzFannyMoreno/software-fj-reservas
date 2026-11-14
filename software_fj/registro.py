"""Configuración del registro de errores y eventos con tolerancia a fallos."""
import logging
import sys
from pathlib import Path
from uuid import uuid4


def configurar_registro(carpeta: str | Path = "logs") -> logging.Logger:
    """Crea archivo de eventos; si falla el acceso, utiliza stderr.

    No se graban clientes ni reservas en archivos: únicamente eventos.
    """
    logger = logging.getLogger(f"software_fj.{uuid4().hex}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    try:
        ruta = Path(carpeta)
        ruta.mkdir(parents=True, exist_ok=True)
        manejador = logging.FileHandler(ruta / "eventos.log", encoding="utf-8")
    except OSError as exc:
        manejador = logging.StreamHandler(sys.stderr)
        manejador.setFormatter(formato)
        logger.addHandler(manejador)
        logger.error("No se pudo abrir el archivo de eventos: %s", exc)
        return logger
    manejador.setFormatter(formato)
    logger.addHandler(manejador)
    return logger
