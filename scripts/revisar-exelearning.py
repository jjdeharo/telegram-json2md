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
#
# Son prefijos de ruta, no carpetas de primer nivel, y esa distinción importa:
# `public/` estuvo entero fuera de la revisión y con él quedó invisible
# `public/CHANGELOG.md`, que es lo que responde a «acabo de instalar la 4.0.3,
# ¿qué trae?». Lo que sobra de `public/` son las librerías empaquetadas, no todo.
FUERA = ("node_modules/", ".git/", "test/", "tools/", "views/", "translations/",
         "public/app/", "public/libs/")


def documentacion_del_repo(repo: Path) -> list[str]:
    """Los .md del repositorio que son candidatos a entrar en el cuaderno."""
    encontrados = []
    for ruta in repo.rglob("*.md"):
        relativa = ruta.relative_to(repo)
        if relativa.as_posix().startswith(FUERA):
            continue
        if any(p.startswith(".") for p in relativa.parts[:-1]):
            continue
        encontrados.append(str(relativa))
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


# Material que no sale de ningún repositorio: publicaciones de CEDEC y hojas de
# ayuda que alguien subió a mano en su día. Nada las vigilaba, y así la guía de
# REA de 2019 se pasó siete años en el cuaderno explicando eXeLearning 2.9 —dos
# generaciones por detrás del programa que usa quien pregunta—, hasta que se le
# preguntó a Karla por ella.
#
# De cada una se guarda de cuándo es y qué mirar para saber si ha cambiado:
#
# - `vigilar` es la dirección cuya huella se compara con la de la revisión
#   anterior. Para los recursos hechos con eXeLearning se apunta a su
#   `content.xml`, que cambia cuando se reedita el material y no cuando el sitio
#   se retoca por fuera.
# - `solo_vive` marca lo que únicamente se comprueba que siga en pie: una entrada
#   de blog cambia sola —comentarios, plantilla— y compararla daría un aviso cada
#   semana; el wiki de HackeXe lo edita Juanjo, que ya sabe cuándo lo toca.
# - `pagina` es dónde mirar si hay una edición nueva, para el informe.
MATERIAL_EXTERNO = {
    "guia-rea-exelearning-2026.md": {
        "que_es": "Guía de creación de REA con eXeLearning (2026), de CEDEC",
        "desde": "junio de 2026",
        "vigilar": "https://descargas.intef.es/cedec/proyectoedia/guias/contenidos/"
                   "guia-de-creacion-de-rea-con-exelearning-2026_web/content.xml",
        "pagina": "https://cedec.intef.es/guia-de-creacion-de-rea-con-exelearning-2026-"
                  "un-recorrido-paso-a-paso/",
        "rehacer": "docs/cuaderno-exelearning.md explica cómo se rehizo desde el .elpx",
    },
    "Requisitos de calidad de Situaciones de Aprendizaje (REA).pdf": {
        "que_es": "Requisitos de calidad de SdA-REA, de CEDEC",
        "desde": "junio de 2025",
        "vigilar": "https://descargas.intef.es/cedec/protocoloexe/calidad_rea/content.xml",
        "pagina": "https://cedec.intef.es/requisitos-de-calidad-de-rea-como-"
                  "situaciones-de-aprendizaje/",
    },
    "recomendaciones-accesibilidad-cedec.md": {
        "que_es": "12 recomendaciones para elaborar materiales accesibles e inclusivos",
        "desde": "junio de 2020",
        "vigilar": "https://cedec.intef.es/12-recomendaciones-para-elaborar-"
                   "materiales-accesibles-e-inclusivos/",
        "solo_vive": True,
    },
    "HackeXe4 - Hoja 1": {
        "que_es": "Hoja de HackeXe 4, de Juanjo",
        "desde": "sin edición datada",
        "vigilar": "https://hackexe.tiddlyhost.com/",
        "solo_vive": True,
    },
}


def revisar_material_externo(propio: dict, presentes: set[str]) -> tuple[list[str], bool]:
    """Comprueba que el material de fuera sigue en pie, y si su original cambió.

    Devuelve las líneas del informe y si hay algo que decidir. No cambia nada:
    resubir una publicación ajena exige leerla antes.
    """
    huellas = propio.setdefault("material_externo", {})
    filas, pendiente = [], False

    for titulo, ficha in MATERIAL_EXTERNO.items():
        avisos = []
        if titulo not in presentes:
            avisos.append("**ya no está en el cuaderno**")
            pendiente = True
        try:
            with urllib.request.urlopen(ficha["vigilar"], timeout=60) as r:
                huella = hashlib.sha256(r.read()).hexdigest()
        except Exception as error:  # noqa: BLE001
            avisos.append(f"no se pudo comprobar el original ({error})")
            pendiente = True
        else:
            if not ficha.get("solo_vive"):
                if huellas.get(titulo) not in (None, huella):
                    avisos.append("**el original ha cambiado**: hay que rehacerlo")
                    pendiente = True
                huellas[titulo] = huella
        filas.append((titulo, ficha, avisos))

    lineas = ["## Material subido a mano", "",
              "Publicaciones que no salen de ningún repositorio: si su original se",
              "reedita, aquí no se entera nadie salvo que se mire.", ""]
    for titulo, ficha, avisos in filas:
        estado = "; ".join(avisos) if avisos else "sin cambios"
        lineas.append(f"- `{titulo}` — {ficha['que_es']} ({ficha['desde']}): {estado}")
        if avisos and ficha.get("pagina"):
            lineas.append(f"  - comprueba si hay edición nueva en {ficha['pagina']}")
        if avisos and ficha.get("rehacer"):
            lineas.append(f"  - {ficha['rehacer']}")
    lineas.append("")
    return lineas, pendiente


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
    consolidados = expandir(repo, [patron for patron, *_ in exelearning.CONSOLIDAR.values()])
    incluidos = sorted(expandir(repo, exelearning.INCLUIR) | consolidados)
    excluidos = sorted(expandir(repo, exelearning.EXCLUIR) - set(incluidos))
    sin_decidir = [r for r in todos if r not in incluidos and r not in excluidos]

    # Entradas que ya no encuentran ningún archivo, aquí y en el ecosistema. De
    # los repositorios complementarios no se buscan documentos nuevos —serían
    # decenas y casi todos de desarrollo—, pero sí que lo elegido siga estando.
    huerfanos = [p for p in exelearning.INCLUIR
                 if "*" not in p and not (repo / p).is_file()]
    for prefijo, ruta_repo in exelearning.repos_complementarios(config).items():
        huerfanos += [f"{prefijo}:{p}" for p in exelearning.COMPLEMENTARIOS[prefijo]
                      if "*" not in p and not (ruta_repo / p).is_file()]

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
        # Bandera para que el paso que sí actúa lo rehaga: esta revisión solo mira.
        if manual_cambiado.startswith("sí"):
            propio["manual_pendiente"] = True

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
            "## Entradas que ya no existen",
            "",
            "El archivo se ha borrado o renombrado en su repositorio. Quítalas de",
            "`INCLUIR` o de `COMPLEMENTARIOS`, o apunta a su nueva ruta.",
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

    material, material_pendiente = revisar_material_externo(
        propio, {f["title"] for f in fuentes})
    lineas += material

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

    pendiente = bool(sin_decidir or huerfanos or material_pendiente
                     or manual_cambiado.startswith("sí"))
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
