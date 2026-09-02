#!/usr/bin/env python3
"""Actualiza el CLI de NotebookLM cuando sale una versión, y lo comprueba.

Todo el trato con NotebookLM pasa por `notebooklm-py`, que es una herramienta no
oficial: automatiza NotebookLM con las cookies de la sesión de Google. El día que
Google cambie algo por dentro, esto se romperá, y el arreglo llegará como una
versión nueva. Por eso interesa estar al día; no por las novedades.

Actualizar es la parte arriesgada, así que nunca se deja a medias: se actualiza,
se comprueba que el automatismo sigue en pie y, si la versión nueva lo rompe, se
vuelve sola a la anterior. Después informa por Telegram de lo que ha pasado.

    python3 scripts/actualizar-cli.py            # mirar y, si toca, actualizar
    python3 scripts/actualizar-cli.py --solo-ver # solo decir si hay novedad
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

from informar import informar  # noqa: E402

PAQUETE = "notebooklm-py"


def instalada() -> str:
    salida = subprocess.run(["notebooklm", "--version"], capture_output=True,
                            text=True, timeout=60).stdout
    encontrado = re.search(r"version (\d+\.\d+\.\d+)", salida)
    return encontrado.group(1) if encontrado else ""


def publicada() -> str:
    """La última versión estable en PyPI; las preliminares no cuentan."""
    with urllib.request.urlopen(f"https://pypi.org/pypi/{PAQUETE}/json", timeout=60) as r:
        return json.load(r)["info"]["version"]


def funciona() -> tuple[bool, str]:
    """¿Sigue en pie el automatismo? Lo dicen las órdenes, no las buenas palabras.

    Se comprueba de dentro afuera: primero que el CLI habla con Google, y luego
    las dos pasadas en seco completas, que es lo que de verdad hay que preservar.
    """
    pruebas = [
        (["notebooklm", "auth", "check", "--test", "--json"], "el CLI ya no habla con NotebookLM"),
        (["python3", str(BASE / "scripts" / "actualizar.py"), "--sin-subir"],
         "el archivado de las conversaciones falla"),
        (["python3", str(BASE / "scripts" / "exelearning.py"), "--sin-subir"],
         "la sincronización de eXeLearning falla"),
    ]
    for orden, queja in pruebas:
        if subprocess.run(orden, capture_output=True, timeout=1800).returncode != 0:
            return False, queja
    return True, ""


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--solo-ver", action="store_true",
                            help="decir si hay versión nueva, sin actualizar")
    args = analizador.parse_args()

    try:
        aqui, alli = instalada(), publicada()
    except Exception as error:  # noqa: BLE001
        print(f"no se pudo comprobar la versión del CLI: {error}")
        return 0   # que esto falle no debe estropear la pasada del día

    if not aqui or not alli or aqui == alli:
        print(f"CLI de NotebookLM al día ({aqui})")
        return 0

    print(f"hay versión nueva del CLI: {aqui} → {alli}")
    if args.solo_ver:
        return 0

    subprocess.run(["uv", "tool", "upgrade", PAQUETE], capture_output=True, timeout=900)
    ahora = instalada()
    if ahora != alli:
        informar(f"⚠️ No he podido actualizar el CLI de NotebookLM a la {alli}; "
                 f"sigue la {aqui} y todo funciona igual. Merece un vistazo.")
        return 1

    # El skill viene dentro del propio paquete: si no se reinstala, la
    # documentación que lee una IA se queda describiendo la versión anterior.
    subprocess.run(["notebooklm", "skill", "install"], capture_output=True, timeout=300)

    bien, queja = funciona()
    if bien:
        print(f"actualizado a {alli} y comprobado")
        informar(f"🔄 He actualizado el CLI de NotebookLM: {aqui} → {alli}.\n\n"
                 f"Comprobado después: el archivado y los tres cuadernos siguen "
                 f"funcionando. No hay nada que hacer.")
        return 0

    # La versión nueva rompe algo: se vuelve atrás sin pensarlo. Perder una
    # versión no cuesta nada; perder el archivado de varios días, sí.
    print(f"la {alli} rompe algo ({queja}); volviendo a la {aqui}")
    subprocess.run(["uv", "tool", "install", f"{PAQUETE}=={aqui}"], capture_output=True, timeout=900)
    subprocess.run(["notebooklm", "skill", "install"], capture_output=True, timeout=300)
    recuperado, _ = funciona()

    if recuperado:
        informar(f"↩️ La versión {alli} del CLI de NotebookLM rompía el archivo "
                 f"({queja}), así que he vuelto a la {aqui} y todo funciona otra vez.\n\n"
                 f"No hace falta que hagas nada; me quedo en la {aqui} hasta que "
                 f"salga una que funcione.")
        return 1

    # Ni con la vuelta atrás: esto ya no es cosa de versiones.
    informar(f"⚠️ La versión {alli} rompía el archivo y volver a la {aqui} tampoco "
             f"lo ha arreglado ({queja}). Voy a intentar diagnosticarlo.")
    subprocess.run([sys.executable, str(BASE / "scripts" / "reparar.py"),
                    "--motivo", f"actualizar el CLI a {alli} rompió el archivo y la "
                                f"vuelta a la {aqui} no lo arregló: {queja}"], timeout=3600)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
