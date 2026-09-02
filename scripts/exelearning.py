#!/usr/bin/env python3
"""Sincroniza la documentación de eXeLearning con su cuaderno de NotebookLM.

El cuaderno «Karla» responde a usuarios de eXeLearning, pero con criterio de
programador: además del manual, lleva la documentación técnica del proyecto para
poder explicar POR QUÉ el programa se comporta como lo hace. Eso solo sirve si
está al día, y a mano se quedó cuatro meses atrás.

    python3 scripts/exelearning.py            # sincroniza con el repo
    python3 scripts/exelearning.py --manual   # además, rehace el manual desde la web
    python3 scripts/exelearning.py --sin-subir

El repositorio de eXeLearning se actualiza con `git pull` antes de nada.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

import notebook  # noqa: E402

CONFIG = BASE / "config.json"
ESTADO = BASE / "estado.json"
MATERIAL = BASE / "material" / "exelearning"
AVISAR = BASE / "scripts" / "avisar.sh"

# Qué documentación entra en el cuaderno. El criterio es una sola pregunta:
# ¿ayuda a explicar el programa o su formato de archivo? Lo que solo explica
# cómo se colabora en el repositorio (pull requests, ramas, pruebas, entorno de
# desarrollo) se queda fuera: no puede responder a nadie y compite con lo útil
# a la hora de recuperar fragmentos.
INCLUIR = [
    "README.md",
    "KNOWN_ISSUES.md",
    "UPGRADE.md",
    "doc/index.md",
    "doc/overview.md",
    "doc/install.md",
    "doc/deployment.md",
    "doc/deploy/README.md",
    "doc/high-availability.md",
    "doc/profile-avatars.md",
    "doc/architecture.md",
    "doc/conventions.md",
    "doc/contentv3-format.md",
    "doc/elpx-format.md",
    "doc/elpx-format/**/*.md",
    "doc/development/authentication.md",
    "doc/development/customization.md",
    "doc/development/embedding.md",
    "doc/development/installers.md",
    "doc/development/internationalization.md",
    "doc/development/real-time.md",
    "doc/development/rest-api.md",
    "doc/development/scorm12-runtime-contract.md",
    "doc/development/styles.md",
]

# Documentación que se deja fuera a propósito. Está aquí escrita, y no solo
# ausente de INCLUIR, para que la revisión periódica pueda distinguir entre «esto
# se descartó en su día» y «esto es nuevo y hay que decidir qué hacer con ello».
EXCLUIR = [
    "AGENTS.md",                     # instrucciones para una IA que toca el código
    "CLAUDE.md",                     # ídem
    "SECURITY.md",                   # política de seguridad del proyecto
    "THIRD-PARTY-NOTICES.md",        # listado de licencias
    "doc/architecture/migration-map.md",   # tabla de identificadores retirados
    "doc/architecture/adr/**/*.md",   # entran, pero consolidados en un solo documento
    "doc/architecture/changes/**/*.md",    # papeles de trabajo: propuestas, investigación
    "doc/architecture/sdd/**/*.md",        # ídem
    "doc/development/contributing.md",     # cómo abrir un pull request
    "doc/development/environment.md",      # montar el entorno de desarrollo
    "doc/development/profiling.md",        # instrumentación para depurar
    "doc/development/testing.md",          # cómo ejecutar las pruebas
    "doc/development/version-control.md",  # estrategia de ramas
]

# Las decisiones de arquitectura explican por qué el programa hace lo que hace,
# pero son veinte archivos cortos: como fuentes sueltas se pisan entre ellas, así
# que van en un único documento.
CONSOLIDAR = {
    "exelearning-doc-architecture-decisiones.md": ("doc/architecture/adr/*.md",
                                                   "Decisiones de arquitectura (ADR)"),
}

# Fuentes de la etapa manual que hay que retirar. Todo se sube ahora en Markdown,
# así que cualquier .docx del proyecto es una versión superada: se reconocen por
# la forma del título en vez de enumerarlos, para que no haga falta tocar esta
# lista cada vez. Los PDF pedagógicos y la hoja de HackeXe no se tocan.
LEGADO_EXPLICITO = {
    "styles.docx",
    "tinymce-editor-compatibility.docx",
    "manual_exe3.pdf",          # manual de la 3.0, sustituido por el de la 4.0.1
}


def es_legado(titulo: str) -> bool:
    return titulo in LEGADO_EXPLICITO or (
        titulo.startswith("exelearning-") and titulo.endswith(".docx")
    )


def registrar(mensaje: str = "") -> None:
    print(mensaje, flush=True)


def avisar(orden: str, *argumentos: str) -> None:
    try:
        subprocess.run([str(AVISAR), orden, *argumentos], timeout=15,
                       capture_output=True, check=False)
    except (OSError, subprocess.SubprocessError):
        pass


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def titulo_de(ruta_relativa: str) -> str:
    """doc/elpx-format/idevices/catalog.md → exelearning-doc-elpx-format-idevices-catalog.md

    Los nombres se aplanan porque NotebookLM no tiene carpetas: el título es lo
    único que sitúa un documento, así que conserva la ruta.
    """
    return "exelearning-" + ruta_relativa[:-3].replace("/", "-") + ".md"


def reunir_documentos(repo: Path) -> dict[str, str]:
    """Devuelve {título: contenido} de todo lo que debe estar en el cuaderno."""
    documentos = {}

    for patron in INCLUIR:
        rutas = sorted(repo.glob(patron)) if "*" in patron else [repo / patron]
        for ruta in rutas:
            if not ruta.is_file():
                registrar(f"  aviso: no existe {ruta.relative_to(repo)}")
                continue
            relativa = str(ruta.relative_to(repo))
            documentos[titulo_de(relativa)] = ruta.read_text(encoding="utf-8")

    for titulo, (patron, encabezado) in CONSOLIDAR.items():
        partes = [f"# {encabezado}\n"]
        for ruta in sorted(repo.glob(patron)):
            if ruta.name in ("README.md", "template.md") or "template" in ruta.name:
                continue
            partes.append(f"\n---\n\n<!-- {ruta.relative_to(repo)} -->\n")
            partes.append(ruta.read_text(encoding="utf-8").strip())
        if len(partes) > 1:
            documentos[titulo] = "\n".join(partes) + "\n"

    return documentos


def escribir_indice(documentos: dict[str, str], repo: Path) -> tuple[str, str]:
    """Un índice para que el cuaderno sepa qué tiene y a qué responde cada cosa."""
    version = subprocess.run(["git", "-C", str(repo), "describe", "--tags", "--abbrev=0"],
                             capture_output=True, text=True).stdout.strip() or "desconocida"
    lineas = [
        "# Índice del cuaderno de eXeLearning",
        "",
        f"Documentación técnica de eXeLearning **{version}**, sincronizada desde el",
        "repositorio oficial. El manual de usuario va aparte, en",
        "`manual-exelearning-4.0.1.md`.",
        "",
        "## Cómo usar estas fuentes",
        "",
        "- **Preguntas de uso** (cómo hago X): el manual.",
        "- **Problemas con un archivo .elp/.elpx** (importar, exportar, contenido que",
        "  se pierde): las fuentes `doc-elpx-format-*`, empezando por",
        "  `idevices-catalog` e `idevices-patterns`.",
        "- **Instalación y servidores**: `doc-install`, `doc-deployment`,",
        "  `doc-deploy-README`, `doc-high-availability`.",
        "- **SCORM en Moodle**: `doc-development-scorm12-runtime-contract`.",
        "- **Comportamientos raros pero intencionados**: `KNOWN_ISSUES`,",
        "  `doc-conventions`, `doc-architecture-decisiones`.",
        "- **Al pasar de la 3.x a la 4.x**: `UPGRADE`.",
        "",
        "## Fuentes disponibles",
        "",
    ]
    lineas += [f"- `{t}`" for t in sorted(documentos)]
    return "exelearning-indice.md", "\n".join(lineas) + "\n"


def sincronizar(config: dict, estado: dict, subir: bool) -> int:
    grupo = next(g for g in config["grupos"] if g["prefijo"] == "exelearning")
    cuaderno = grupo["notebook"]
    repo = Path(config["repo_exelearning"]).expanduser()

    registrar("actualizando el repositorio de eXeLearning…")
    subprocess.run(["git", "-C", str(repo), "pull", "--quiet"], check=False, timeout=300)

    documentos = reunir_documentos(repo)
    titulo_indice, contenido_indice = escribir_indice(documentos, repo)
    documentos[titulo_indice] = contenido_indice

    # El manual consolidado no viene del repositorio: se conserva el que haya.
    MATERIAL.mkdir(parents=True, exist_ok=True)
    for manual in MATERIAL.glob("manual-*.md"):
        documentos[manual.name] = manual.read_text(encoding="utf-8")

    registrar(f"{len(documentos)} documentos deben estar en el cuaderno")

    for titulo, contenido in documentos.items():
        (MATERIAL / titulo).write_text(contenido, encoding="utf-8")

    propio = estado.setdefault("exelearning", {}).setdefault("fuentes", {})
    presentes = {f["title"]: f["id"] for f in notebook.fuentes(cuaderno)}

    nuevas = altas = cambios = retiradas = 0
    for titulo, contenido in sorted(documentos.items()):
        actual = huella(contenido)
        if titulo in presentes and propio.get(titulo, {}).get("huella") == actual:
            continue
        nuevo = titulo not in presentes
        if not subir:
            registrar(f"  {'+' if nuevo else '~'} {titulo} (sin subir)")
            if nuevo:
                altas += 1
            else:
                cambios += 1
            continue
        registrar(f"  {'+ añadiendo' if nuevo else '~ actualizando'} {titulo}")
        efecto = notebook.sustituir_fuente(cuaderno, MATERIAL / titulo, registrar)
        if efecto["lista"]:
            propio[titulo] = {"huella": actual, "fuente": efecto["subida"]}
        nuevas += 1
        if nuevo:
            altas += 1
        else:
            cambios += 1

    # Retirada de lo que sobra: las fuentes de la etapa manual, y cualquier
    # documento que este script gestionara antes y ya no esté en el repositorio.
    sobran = [t for t in presentes
              if t not in documentos and (es_legado(t) or t in propio)]
    for titulo in sorted(sobran):
        if not subir:
            registrar(f"  - {titulo} (sin retirar)")
            retiradas += 1
            continue
        registrar(f"  - retirando {titulo}")
        try:
            notebook._cli("source", "delete", presentes[titulo], "-n", cuaderno, "--yes")
            propio.pop(titulo, None)
            retiradas += 1
        except notebook.ErrorNotebook as error:
            registrar(f"    aviso: no se pudo retirar: {error}")

    registrar(f"resumen: {altas} nueva(s), {cambios} actualizada(s), {retiradas} retirada(s)")
    return nuevas + retiradas


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--manual", action="store_true",
                            help="rehacer antes el manual de usuario desde la web")
    analizador.add_argument("--sin-subir", dest="subir", action="store_false",
                            help="ver qué cambiaría sin tocar NotebookLM")
    args = analizador.parse_args()

    with open(CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {"grupos": {}}

    if args.manual:
        registrar("reconstruyendo el manual de usuario…")
        subprocess.run([sys.executable, str(BASE / "scripts" / "manual_exelearning.py")],
                       check=True, timeout=1800)

    try:
        if args.subir:
            notebook.comprobar_acceso()
        hechos = sincronizar(config, estado, args.subir)
    except Exception as error:  # noqa: BLE001
        registrar(f"ERROR: {type(error).__name__}: {error}")
        avisar("error", "Cuaderno de eXeLearning: fallo", str(error))
        return 1
    finally:
        with open(ESTADO, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)

    if hechos and args.subir:
        avisar("fin", f"Cuaderno de eXeLearning al día ({hechos} cambio(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
