#!/usr/bin/env python3
"""Asegura que el proceso corre con el Python del entorno propio del proyecto.

Telethon y BeautifulSoup no pueden quedarse en manos del paquete de Debian: el
07/09/2026 la pasada diaria falló entera porque Telegram estrenó un constructor
(`0x1c32b11c`) que la Telethon del sistema —la 1.25.1, de hace años— no sabía
leer, y dos de los tres grupos dejaron de exportarse. Las dependencias viven
ahora en `.venv/`, que se actualiza cuando queremos y no cuando actualice el
sistema operativo.

Como los scripts se llaman de muchas maneras —cron, a mano con `python3
scripts/actualizar.py`, o desde el reparador automático—, no basta con apuntar
un lanzador al venv: cada punto de entrada llama a `usar_venv()` como primera
instrucción y, si hace falta, se reejecuta a sí mismo con el intérprete
correcto. Si el venv no existe, sigue con el del sistema: es mejor intentarlo y
fallar con el error de verdad que negarse a arrancar.

    from entorno import usar_venv
    usar_venv()
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PYTHON = BASE / ".venv" / "bin" / "python"


def usar_venv() -> None:
    """Reejecuta el script actual con el Python del venv si no es el que corre."""
    if not PYTHON.exists():
        return
    if Path(sys.executable).resolve() == PYTHON.resolve():
        return
    os.execv(str(PYTHON), [str(PYTHON), *sys.argv])
