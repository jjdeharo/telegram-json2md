#!/usr/bin/env python3
"""Avisa cuando sale una versión nueva del CLI de NotebookLM.

Todo el trato con NotebookLM pasa por `notebooklm-py`, que es una herramienta no
oficial: automatiza NotebookLM con las cookies de la sesión de Google. El día que
Google cambie algo por dentro, esto se romperá, y **el arreglo llegará como una
versión nueva**. Por eso interesa enterarse, no por las novedades.

Solo avisa: actualizar exige comprobar después que el automatismo sigue en pie, y
eso no se hace solo. El procedimiento está en docs/automatizacion.md.

    python3 scripts/comprobar-cli.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ESTADO = BASE / "estado.json"
AVISAR = BASE / "scripts" / "avisar.sh"
PAQUETE = "notebooklm-py"


def instalada() -> str:
    salida = subprocess.run(["notebooklm", "--version"], capture_output=True,
                            text=True, timeout=60).stdout
    encontrado = re.search(r"version (\d+\.\d+\.\d+)", salida)
    return encontrado.group(1) if encontrado else ""


def publicada() -> str:
    """La última versión estable en PyPI (las preliminares no cuentan)."""
    with urllib.request.urlopen(f"https://pypi.org/pypi/{PAQUETE}/json", timeout=60) as r:
        return json.load(r)["info"]["version"]


def main() -> int:
    try:
        aqui, alli = instalada(), publicada()
    except Exception as error:  # noqa: BLE001
        print(f"no se pudo comprobar la versión del CLI: {error}")
        return 0   # que esto falle no debe estropear la pasada del día

    if not aqui or not alli or aqui == alli:
        print(f"CLI de NotebookLM al día ({aqui})")
        return 0

    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    herramientas = estado.setdefault("herramientas", {})
    # Se avisa una vez por versión: repetirlo cada mañana convertiría el aviso en
    # ruido, y al tercer día ya nadie lo lee.
    if herramientas.get("cli_avisado") == alli:
        print(f"CLI de NotebookLM: {alli} disponible (ya avisado)")
        return 0

    mensaje = (f"Hay una versión nueva del CLI de NotebookLM: {aqui} → {alli}. "
               f"Actualizar y comprobar: docs/automatizacion.md")
    print(mensaje)
    subprocess.run([str(AVISAR), "paso", mensaje], capture_output=True, check=False)

    herramientas["cli_avisado"] = alli
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
