#!/usr/bin/env python3
"""Cuando la pasada diaria falla, busca la solución en vez de limitarse a avisar.

Casi todo lo que puede romperse aquí depende de una herramienta no oficial
—`notebooklm-py`, que automatiza NotebookLM con las cookies de Google— y de un
repositorio ajeno que cambia solo. Cuando eso pasa a las siete de la mañana no
hay nadie delante, y dejar el fallo esperando a que alguien lea un cartel es
perder días de archivo.

Así que se le da el problema a un Claude sin sesión interactiva, con el registro
del fallo, la versión instalada, las notas de la versión nueva y las incidencias
abiertas del proyecto. Puede leer y editar los scripts y ejecutar las
comprobaciones, y nada más: la lista de herramientas permitidas es corta a
propósito.

    python3 scripts/reparar.py --motivo "actualizar.py falló" --registro ruta.log
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

from informar import informar  # noqa: E402

BITACORA = BASE / "docs" / "reparaciones.md"
PROYECTO = "teng-lin/notebooklm-py"

# Lo único que puede hacer. Ni borrar fuentes de NotebookLM —el daño irreversible
# de este sistema—, ni `git push`, ni tocar datos: solo leer, editar los scripts y
# ejecutar las comprobaciones en seco.
HERRAMIENTAS = [
    "Read", "Grep", "Glob", "Edit",
    "Bash(python3 scripts/actualizar.py --sin-subir)",
    "Bash(python3 scripts/exelearning.py --sin-subir)",
    "Bash(python3 scripts/actualizar-cli.py --solo-ver)",
    "Bash(notebooklm auth check:*)",
    "Bash(notebooklm source list:*)",
    "Bash(notebooklm --version)",
    "Bash(notebooklm --help)",
    "Bash(uv tool upgrade notebooklm-py)",
    "Bash(uv tool install notebooklm-py:*)",
    "Bash(git -C . diff:*)",
    "Bash(git -C . log:*)",
    "Bash(tail:*)",
    "WebFetch",
]

ENCARGO = """Eres el encargado de mantener en pie un archivo automático que cada mañana
guarda las conversaciones de tres grupos de Telegram y las sube como fuentes a
tres cuadernos de NotebookLM. La pasada de hoy ha fallado y no hay nadie
delante: tu trabajo es averiguar por qué y arreglarlo si puedes.

## Qué ha pasado

{motivo}

### Registro del fallo

```
{registro}
```

### Entorno

- CLI de NotebookLM instalado: {instalada}. Última publicada: {publicada}.
- Repositorio del CLI: https://github.com/{proyecto} (herramienta NO oficial: se
  rompe cuando Google cambia NotebookLM por dentro).
{notas}
{incidencias}

## Cómo trabajar

1. Diagnostica antes de tocar nada. Lee el registro y reproduce el fallo con las
   comprobaciones en seco (`--sin-subir`), que no modifican nada.
2. Las causas más probables, por orden: sesión de NotebookLM caducada (no puedes
   arreglarla: requiere navegador), versión del CLI que cambió una orden o una
   respuesta, red, o un cambio en el repositorio de eXeLearning.
3. Si la causa es el CLI, prueba a actualizarlo y vuelve a comprobar. Si la
   versión nueva es la que rompe, vuelve a la anterior con
   `uv tool install notebooklm-py==<versión>`.
4. Si hay que tocar código, cambia lo MÍNIMO y solo en `scripts/`. No cambies el
   formato del Markdown que se genera: los meses ya subidos siguen ese formato y
   cualquier cambio los daría todos por modificados.
5. Comprueba que has arreglado algo antes de decir que lo has arreglado: las dos
   comprobaciones en seco deben terminar bien.

## Lo que no puedes hacer

- Borrar fuentes de NotebookLM ni tocar `datos/`, `salida/` ni `material/`.
- Subir nada a GitHub.
- Dar por buena una solución que no hayas verificado.
- Si no puedes arreglarlo, dilo claramente. Un diagnóstico honesto vale más que
  un apaño: alguien lo leerá y actuará.

## Qué responder

Termina con un informe de CINCO LÍNEAS COMO MUCHO, en español llano, para que lo
lea alguien en el móvil que no está delante del ordenador. Di qué fallaba, qué
has hecho y si está resuelto o hace falta que intervenga una persona. Nada de
jerga ni de rutas largas si puedes evitarlas.
"""


def texto(orden: list[str], limite: int = 4000) -> str:
    try:
        salida = subprocess.run(orden, capture_output=True, text=True, timeout=120)
        return (salida.stdout or salida.stderr or "")[-limite:]
    except (OSError, subprocess.SubprocessError):
        return ""


def de_internet(url: str, limite: int = 3000) -> str:
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read().decode("utf-8", "replace")[:limite]
    except Exception:  # noqa: BLE001
        return ""


def contexto_del_proyecto() -> tuple[str, str, str]:
    """Versión publicada, notas de la última versión e incidencias abiertas."""
    publicada, notas, incidencias = "desconocida", "", ""
    try:
        datos = json.loads(de_internet("https://pypi.org/pypi/notebooklm-py/json", 200_000))
        publicada = datos["info"]["version"]
    except Exception:  # noqa: BLE001
        pass
    try:
        suelto = json.loads(de_internet(
            f"https://api.github.com/repos/{PROYECTO}/releases/latest", 200_000))
        cuerpo = (suelto.get("body") or "")[:1500]
        if cuerpo:
            notas = f"\n### Notas de {suelto.get('tag_name','')}\n\n{cuerpo}\n"
    except Exception:  # noqa: BLE001
        pass
    try:
        abiertas = json.loads(de_internet(
            f"https://api.github.com/repos/{PROYECTO}/issues?state=open&per_page=15", 200_000))
        titulos = [f"- #{i['number']} {i['title']}" for i in abiertas if "pull_request" not in i]
        if titulos:
            incidencias = "\n### Incidencias abiertas del CLI\n\n" + "\n".join(titulos[:12]) + "\n"
    except Exception:  # noqa: BLE001
        pass
    return publicada, notas, incidencias


def anotar(motivo: str, informe: str, arreglado: bool) -> None:
    if not BITACORA.exists():
        BITACORA.write_text(
            "# Reparaciones automáticas\n\n"
            "Cuando la pasada diaria falla, una IA diagnostica y arregla sin esperar a\n"
            "nadie. Aquí queda lo que encontró y lo que hizo. Si esto está vacío, es que\n"
            "nunca se ha roto nada.\n", encoding="utf-8")
    with open(BITACORA, "a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.now():%d/%m/%Y %H:%M} · "
                f"{'resuelto' if arreglado else 'sin resolver'}\n\n"
                f"**Fallo:** {motivo}\n\n{informe.strip()}\n")


def comprobaciones_pasan() -> bool:
    """La verdad sobre si está arreglado no la dice la IA: la dicen las órdenes."""
    for orden in (["python3", str(BASE / "scripts" / "actualizar.py"), "--sin-subir"],
                  ["python3", str(BASE / "scripts" / "exelearning.py"), "--sin-subir"]):
        if subprocess.run(orden, capture_output=True, timeout=1800).returncode != 0:
            return False
    return True


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--motivo", required=True)
    analizador.add_argument("--registro", help="archivo con la salida del fallo")
    analizador.add_argument("--probar", action="store_true",
                            help="preparar el encargo y enseñarlo, sin llamar a nadie")
    args = analizador.parse_args()

    registro = ""
    if args.registro and Path(args.registro).exists():
        registro = Path(args.registro).read_text(encoding="utf-8", errors="replace")[-6000:]

    publicada, notas, incidencias = contexto_del_proyecto()
    encargo = ENCARGO.format(
        motivo=args.motivo, registro=registro or "(sin registro)",
        instalada=texto(["notebooklm", "--version"], 100).strip() or "?",
        publicada=publicada, proyecto=PROYECTO, notas=notas, incidencias=incidencias)

    if args.probar:
        print(encargo)
        return 0

    print("pidiendo diagnóstico y reparación…")
    proceso = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--max-turns", "40",
         "--permission-mode", "acceptEdits", "--allowedTools", *HERRAMIENTAS],
        input=encargo, capture_output=True, text=True, timeout=3600, cwd=str(BASE))

    if proceso.returncode != 0:
        informe = f"No se pudo ni intentar la reparación: {(proceso.stderr or '')[-300:]}"
        arreglado = False
    else:
        informe = json.loads(proceso.stdout).get("result", "").strip()
        # Lo que diga la IA es su versión; la comprobación manda.
        arreglado = comprobaciones_pasan()

    print(informe)
    anotar(args.motivo, informe, arreglado)

    cabecera = ("✅ Se rompió algo y ya está arreglado" if arreglado
                else "⚠️ Se rompió algo y NO he podido arreglarlo")
    informar(f"{cabecera}\n\n{informe}")
    return 0 if arreglado else 1


if __name__ == "__main__":
    raise SystemExit(main())
