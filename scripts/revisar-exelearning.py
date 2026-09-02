#!/usr/bin/env python3
"""Revisión periódica del cuaderno de eXeLearning: lo que el script no decide solo.

La sincronización diaria mantiene al día los documentos de una lista fija. Lo que
no puede hacer sola es darse cuenta de que **la lista se ha quedado corta**: que
ha aparecido documentación nueva en el repositorio, que una carpeta entera se ha
renombrado o que hay un manual de usuario más reciente. Eso fue justo lo que pasó
entre mayo y septiembre de 2026, cuando apareció todo el subárbol `elpx-format`
—37.500 palabras sobre el formato de archivo— y nadie se enteró.

Este script no cambia nada: mira y escribe un informe para decidir.

    python3 scripts/revisar-exelearning.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

import exelearning  # noqa: E402
import notebook  # noqa: E402

INFORME = BASE / "registro" / f"revision-exelearning-{date.today():%Y-%m}.md"

# Carpetas del repositorio que no contienen documentación del programa: código,
# recursos, pruebas, y todo lo oculto (instrucciones de agentes, plantillas de
# GitHub), que va dirigido a quien desarrolla y no a quien usa eXeLearning.
FUERA = ("node_modules", ".git", "test", "public", "tools", "views", "translations")


def documentacion_del_repo(repo: Path) -> list[str]:
    """Los .md del repositorio que son candidatos a entrar en el cuaderno."""
    encontrados = []
    for ruta in repo.rglob("*.md"):
        partes = ruta.relative_to(repo).parts
        if partes[0] in FUERA or any(p.startswith(".") for p in partes[:-1]):
            continue
        encontrados.append(str(ruta.relative_to(repo)))
    return sorted(encontrados)


def expandir(repo: Path, patrones) -> set[str]:
    """Los archivos que cubren esos patrones, resueltos contra el repositorio.

    Se resuelven globbing de verdad, no comparando cadenas: es exactamente lo que
    hace el sincronizador, así que la revisión no puede discrepar de él.
    """
    cubiertos = set()
    for patron in patrones:
        for ruta in repo.glob(patron):
            if ruta.is_file():
                cubiertos.add(str(ruta.relative_to(repo)))
    return cubiertos


def main() -> int:
    with open(BASE / "config.json", encoding="utf-8") as f:
        config = json.load(f)
    repo = Path(config["repo_exelearning"]).expanduser()
    cuaderno = next(g for g in config["grupos"] if g["prefijo"] == "exelearning")["notebook"]

    subprocess.run(["git", "-C", str(repo), "pull", "--quiet"], check=False, timeout=300)
    version = subprocess.run(["git", "-C", str(repo), "describe", "--tags", "--abbrev=0"],
                             capture_output=True, text=True).stdout.strip()

    # Toda la documentación del repositorio, y con qué se corresponde
    todos = documentacion_del_repo(repo)
    consolidados = expandir(repo, [patron for patron, _ in exelearning.CONSOLIDAR.values()])
    incluidos = sorted(expandir(repo, exelearning.INCLUIR) | consolidados)
    excluidos = sorted(expandir(repo, exelearning.EXCLUIR) - set(incluidos))
    sin_decidir = [r for r in todos if r not in incluidos and r not in excluidos]

    # Entradas de INCLUIR que ya no encuentran ningún archivo
    huerfanos = [p for p in exelearning.INCLUIR
                 if "*" not in p and not (repo / p).is_file()]

    # ¿Hay un manual nuevo? Se compara la portada con la de la última revisión.
    estado_ruta = BASE / "estado.json"
    estado = json.loads(estado_ruta.read_text(encoding="utf-8")) if estado_ruta.exists() else {}
    propio = estado.setdefault("exelearning", {})
    try:
        with urllib.request.urlopen(exelearning_manual_url(), timeout=60) as r:
            portada = hashlib.sha256(r.read()).hexdigest()
    except Exception as error:  # noqa: BLE001
        portada, manual_cambiado = "", f"no se pudo comprobar ({error})"
    else:
        manual_cambiado = ("sí, la portada ha cambiado" if propio.get("portada_manual") not in (None, portada)
                           else "no")
        propio["portada_manual"] = portada

    fuentes = notebook.fuentes(cuaderno)

    lineas = [
        f"# Revisión del cuaderno de eXeLearning — {date.today():%d/%m/%Y}",
        "",
        f"- Versión del repositorio: **{version or 'desconocida'}**",
        f"- Fuentes en el cuaderno: **{len(fuentes)}** de 300 (plan Pro)",
        f"- Documentos sincronizados: **{len(incluidos)}**",
        f"- ¿Manual de usuario nuevo?: **{manual_cambiado}**",
        "",
    ]

    if sin_decidir:
        lineas += [
            "## Documentación sin decidir",
            "",
            "Está en el repositorio y no la cubre ni `INCLUIR` ni `EXCLUIR`. Decide",
            "una por una: si explica el programa o su formato, va a `INCLUIR`; si",
            "solo explica cómo se colabora en el repositorio, a `EXCLUIR`.",
            "",
        ] + [f"- `{r}`" for r in sin_decidir] + [""]
    else:
        lineas += ["## Documentación sin decidir", "", "Ninguna: la lista está completa.", ""]

    if huerfanos:
        lineas += [
            "## Entradas de `INCLUIR` que ya no existen",
            "",
            "El archivo se ha borrado o renombrado en el repositorio. Quítalas de la",
            "lista, o apunta a su nueva ruta.",
            "",
        ] + [f"- `{r}`" for r in huerfanos] + [""]

    if manual_cambiado.startswith("sí"):
        lineas += [
            "## El manual de usuario ha cambiado",
            "",
            "Rehazlo y vuelve a sincronizar:",
            "",
            "```bash",
            "python3 scripts/manual_exelearning.py",
            "python3 scripts/exelearning.py",
            "```",
            "",
            "Comprueba también en https://descargas.intef.es/cedec/exe_learning/Manuales/",
            "si hay una carpeta de manual más reciente; si la hay, actualiza `RAIZ` en",
            "`scripts/manual_exelearning.py`.",
            "",
        ]

    lineas += [
        "## Fuera a propósito",
        "",
        f"{len(excluidos)} documentos, listados en `EXCLUIR` dentro de",
        "`scripts/exelearning.py`. Repásalos solo si cambia el criterio.",
        "",
    ]

    INFORME.parent.mkdir(parents=True, exist_ok=True)
    INFORME.write_text("\n".join(lineas), encoding="utf-8")
    with open(estado_ruta, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)

    print("\n".join(lineas))
    print(f"\n→ informe en {INFORME.relative_to(BASE)}")

    pendiente = bool(sin_decidir or huerfanos or manual_cambiado.startswith("sí"))
    if pendiente:
        subprocess.run([str(BASE / "scripts" / "avisar.sh"), "paso",
                        f"Revisión de eXeLearning: hay cosas que decidir. "
                        f"Informe en registro/{INFORME.name}"],
                       capture_output=True, check=False)
    return 0


def exelearning_manual_url() -> str:
    """La dirección del manual, leída del generador para no repetirla aquí."""
    texto = (BASE / "scripts" / "manual_exelearning.py").read_text(encoding="utf-8")
    for linea in texto.splitlines():
        if linea.startswith("RAIZ = "):
            return linea.split('"')[1]
    raise RuntimeError("no se encontró RAIZ en manual_exelearning.py")


if __name__ == "__main__":
    raise SystemExit(main())
