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
import fnmatch
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
# Documentos escritos a mano que van al cuaderno. Van versionados, no en
# `material/`, porque no se generan de nada: si se pierden, se pierden. Cubren lo
# que se pregunta y no está documentado en ningún repositorio, como qué hace cada
# plataforma con un contenido de eXeLearning.
FUENTES = BASE / "fuentes"
AVISAR = BASE / "scripts" / "avisar.sh"

# Qué documentación entra en el cuaderno. El criterio es una sola pregunta:
# ¿ayuda a explicar el programa o su formato de archivo? Lo que solo explica
# cómo se colabora en el repositorio (pull requests, ramas, pruebas, entorno de
# desarrollo) se queda fuera: no puede responder a nadie y compite con lo útil
# a la hora de recuperar fragmentos.
# Decisiones automáticas del 03/09/2026:
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
    "public/CHANGELOG.md",           # qué trae cada versión: se pregunta en cada salida
    "public/files/perm/idevices/base/lomloe/README.md",   # el iDevice de currículo
]

# Documentación que se deja fuera a propósito. Está aquí escrita, y no solo
# ausente de INCLUIR, para que la revisión periódica pueda distinguir entre «esto
# se descartó en su día» y «esto es nuevo y hay que decidir qué hacer con ello».
EXCLUIR = [
    "doc/development/c10k-benchmark.md",  # Versión en inglés del mismo informe interno de benchmark, orientado a quien desarrolla y prueba el servidor, no a diagnosticar problemas de uso.
    "doc/development/c10k-benchmark.es.md",  # Informe interno de investigación de rendimiento con metodología de laboratorio y herramientas de carga, no describe comportamientos que sufra un usuario.
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
    "public/app/**/*.md",            # librerías empaquetadas dentro de la aplicación
    "public/libs/**/*.md",           # ídem, con sus changelogs y licencias
    "public/files/perm/idevices/base/lomloe/ES-VC-descriptors-alignment.md",  # dataset
]

# El ecosistema alrededor del programa. Lo más preguntado del grupo no es cómo se
# usa eXeLearning, que el manual cubre bien, sino cómo se saca el contenido de él
# y se pone donde el alumnado lo use: los plugins de Moodle, el visor, las
# utilidades. Nada de eso vive en el repositorio principal.
#
# El criterio para elegir qué se trae de cada uno es el mismo de siempre: lo que
# explica qué hace la herramienta y cómo se usa, no cómo se colabora en su
# repositorio. Las rutas están en `repos_complementarios`, en config.json; el que
# no esté configurado se salta con un aviso.
COMPLEMENTARIOS = {
    "mod_exescorm": ["README.md", "CHANGELOG.md"],
    "mod_exeweb": ["README.md", "CHANGELOG.md"],
    "wp-exelearning": ["README.md", "docs/SHORTCODES.md", "docs/HOOKS.md",
                       "docs/architecture/README.md"],
    "exeviewer": ["README_es.md", "CHANGELOG.md"],
    "execonvert": ["README.md", "CHANGELOG.md"],
    "edex": ["README.md"],
    "hackexe4": ["README.md"],
    "visor-webzip": ["README.md"],
}

# Las decisiones de arquitectura explican por qué el programa hace lo que hace,
# pero son veinte archivos cortos: como fuentes sueltas se pisan entre ellas, así
# que van en un único documento.
CONSOLIDAR = {
    "exelearning-doc-architecture-decisiones.md": (
        "doc/architecture/adr/*.md",
        "Decisiones de arquitectura (ADR)",
        "Cada decisión lleva su propio campo `status`: `Proposed` es una propuesta "
        "—puede que ni siquiera se llegue a hacer—, `Accepted` está aprobada. "
        "Ninguno de los dos significa que esté publicada.",
    ),
}

# El cuaderno describe el programa **publicado**: la documentación técnica se
# toma del último tag, no de `main`, para que no explique funciones que quien
# pregunta todavía no tiene. Lo que está por llegar vive concentrado en dos
# sitios, y estos sí se toman de la rama de desarrollo: el CHANGELOG, cuya
# sección `Unreleased` es justamente eso, y los ADR, que son decisiones sobre lo
# que vendrá y avisan de ello en su cabecera.
DESDE_DESARROLLO = {"public/CHANGELOG.md"}

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


def titulo_de(ruta_relativa: str, prefijo: str = "exelearning") -> str:
    """doc/elpx-format/idevices/catalog.md → exelearning-doc-elpx-format-idevices-catalog.md

    Los nombres se aplanan porque NotebookLM no tiene carpetas: el título es lo
    único que sitúa un documento, así que conserva la ruta. El prefijo dice de
    qué repositorio viene, que es lo que distingue el programa de su ecosistema.
    """
    return f"{prefijo}-" + ruta_relativa[:-3].replace("/", "-") + ".md"


def archivos_del_tag(repo: Path, version: str) -> list[str]:
    """Todo lo que hay en la versión publicada, para resolver los patrones ahí.

    Los patrones no se pueden resolver contra el disco: en el disco está `main`,
    y un archivo que solo exista allí acabaría subido como si estuviera publicado.
    """
    return subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", version],
                          capture_output=True, text=True).stdout.split("\n")


def recoger(repo: Path, patrones: list[str], prefijo: str,
            version: str | None = None) -> dict[str, str]:
    """{título: contenido} de los patrones que se resuelven dentro de un repositorio.

    Con `version`, el contenido se toma de esa etiqueta —la última publicada— y no
    del árbol de trabajo, salvo para lo que está en DESDE_DESARROLLO.
    """
    documentos = {}
    inventario = archivos_del_tag(repo, version) if version else []
    for patron in patrones:
        if version and patron not in DESDE_DESARROLLO:
            if "*" in patron:
                suelto = patron.replace("**/", "")
                rutas = sorted(r for r in inventario if fnmatch.fnmatch(r, suelto))
            else:
                rutas = [patron] if patron in inventario else []
            if not rutas:
                registrar(f"  {prefijo}:{patron}: todavía no está en la {version}")
                continue
            for relativa in rutas:
                documentos[titulo_de(relativa, prefijo)] = subprocess.run(
                    ["git", "-C", str(repo), "show", f"{version}:{relativa}"],
                    capture_output=True, text=True).stdout
            continue
        rutas = sorted(repo.glob(patron)) if "*" in patron else [repo / patron]
        for ruta in rutas:
            if not ruta.is_file():
                registrar(f"  aviso: no existe {prefijo}:{patron}")
                continue
            relativa = str(ruta.relative_to(repo))
            documentos[titulo_de(relativa, prefijo)] = ruta.read_text(encoding="utf-8")
    return documentos


def estado_desarrollo(repo: Path) -> tuple[str, int]:
    """Última versión publicada, y cuántos commits lleva la rama por delante.

    La documentación se sincroniza desde `main`, así que describe un programa que
    todavía no está en manos de nadie. Quien lea estas fuentes necesita saberlo,
    y necesita saber cuánto: no es lo mismo ir dos commits por delante que
    cincuenta.
    """
    def git(*orden: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *orden],
                              capture_output=True, text=True).stdout.strip()

    version = git("describe", "--tags", "--abbrev=0") or "desconocida"
    adelanto = git("rev-list", f"{version}..HEAD", "--count") if version != "desconocida" else ""
    return version, int(adelanto) if adelanto.isdigit() else 0


def aviso_publicado(version: str, adelanto: int) -> list[str]:
    """Lo que hay que saber del cuaderno en conjunto: describe lo publicado."""
    cuanto = (f" El desarrollo va {adelanto} commit(s) por delante, y eso no"
              if adelanto else " Lo que se esté desarrollando no")
    return [
        f"> **La documentación técnica de aquí es la de la {version}**, la última",
        "> versión publicada y la que tiene instalada quien pregunta: se toma de",
        f"> esa etiqueta y no de la rama de desarrollo.{cuanto}",
        "> está en estas fuentes, con dos excepciones a propósito:",
        "> `exelearning-public-CHANGELOG`, cuya sección `Unreleased` es lo que",
        "> falta por publicar, y `exelearning-doc-architecture-decisiones`, que",
        "> recoge decisiones aún por hacer. Fuera de esas dos, si algo no está",
        "> documentado aquí, es que todavía no ha salido.",
    ]


def aviso_desarrollo(version: str, adelanto: int) -> list[str]:
    """El párrafo que separa lo que ya está publicado de lo que aún no."""
    cuanto = (f"hoy {adelanto} commit(s) por delante de la **{version}**"
              if adelanto else f"hoy a la altura de la **{version}**")
    return [
        "> **Ojo: esto no describe el programa publicado.** Estas fuentes se",
        f"> sincronizan desde la rama de desarrollo, {cuanto},",
        "> que es la última versión publicada y la que tiene instalada quien",
        "> pregunta. Lo que aquí se cuenta puede no haber salido todavía. Para",
        "> saber qué está ya disponible, la referencia es",
        "> `exelearning-public-CHANGELOG`: su sección `Unreleased` es justamente",
        "> lo que falta por publicar.",
    ]


def reunir_documentos(repo: Path, extras: dict[str, Path]) -> dict[str, str]:
    """Devuelve {título: contenido} de todo lo que debe estar en el cuaderno."""
    version, adelanto = estado_desarrollo(repo)
    documentos = recoger(repo, INCLUIR, "exelearning",
                         version if version != "desconocida" else None)

    for prefijo, ruta_repo in extras.items():
        documentos.update(recoger(ruta_repo, COMPLEMENTARIOS[prefijo], prefijo))

    for titulo, (patron, encabezado, nota) in CONSOLIDAR.items():
        partes = [f"# {encabezado}\n",
                  "\n".join(aviso_desarrollo(version, adelanto) + [f"> {nota}"]) + "\n"]
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
    version, adelanto = estado_desarrollo(repo)
    lineas = [
        "# Índice del cuaderno de eXeLearning",
        "",
        "Documentación técnica de eXeLearning, sincronizada desde el repositorio",
        "oficial, y la de las herramientas que lo rodean. El manual de usuario va",
        "aparte, en `manual-exelearning-4.0.1.md`.",
        "",
        *aviso_publicado(version, adelanto),
        "",
        "Las fuentes llevan el nombre del proyecto por delante: `exelearning-` es el",
        "programa; `mod_exescorm-`, `mod_exeweb-` y `wp-exelearning-` son los plugins",
        "con los que se publica; `exeviewer-`, `visor-webzip-`, `edex-`, `execonvert-`",
        "y `hackexe4-`, las herramientas de alrededor.",
        "",
        "## Cómo usar estas fuentes",
        "",
        "- **Preguntas de uso** (cómo hago X): el manual.",
        "- **Problemas con un archivo .elp/.elpx** (importar, exportar, contenido que",
        "  se pierde): las fuentes `doc-elpx-format-*`, empezando por",
        "  `idevices-catalog` e `idevices-patterns`.",
        "- **Instalación y servidores**: `doc-install`, `doc-deployment`,",
        "  `doc-deploy-README`, `doc-high-availability`.",
        "- **Qué trae cada versión, y si un fallo ya está corregido**:",
        "  `exelearning-public-CHANGELOG`, que llega hasta la última publicada.",
        "- **Publicar en Moodle**: `mod_exescorm-README` y `mod_exeweb-README` son los",
        "  plugins oficiales. Cuando alguien dice que su aula virtual rechaza un",
        "  exportado de la 4.x, casi siempre es que la plataforma lleva la versión",
        "  antigua del módulo y solo la administración puede actualizarla.",
        # El contrato del runtime solo se cita si está: es documentación que se
        # adelantó a la versión publicada, y una remisión a una fuente ausente
        # manda a buscar lo que no hay.
        *(["  El contrato del runtime está en "
           "`doc-development-scorm12-runtime-contract`."]
          if "exelearning-doc-development-scorm12-runtime-contract.md" in documentos
          else []),
        "- **Publicar en WordPress**: `wp-exelearning-*`.",
        "- **Qué hace cada plataforma con un contenido de eXeLearning** (Moodle,",
        "  Procomún, EducaMadrid, Junta de Andalucía, GitHub Pages):",
        "  `exelearning-en-cada-plataforma`, que es donde está reunido y fechado lo",
        "  que en las conversaciones aparece disperso.",
        "- **Compartir sin aula virtual**: `exeviewer-README_es` (se instala como",
        "  aplicación y funciona sin conexión) y `visor-webzip-README`.",
        "- **Estilos propios**: `doc-development-styles` y `edex-README`, el editor.",
        "- **Convertir entre formatos** (.elp, .elpx, .docx, .md, .pdf):",
        "  `execonvert-README`.",
        "- **Ampliar lo que hacen los iDevices** pegando HTML, CSS o JS:",
        "  `hackexe4-README` y la hoja de HackeXe.",
        "- **Currículo, competencias y DUA**: el iDevice de fundamentación curricular,",
        "  en `exelearning-public-files-perm-idevices-base-lomloe-README`.",
        "- **Comportamientos raros pero intencionados**: `KNOWN_ISSUES`,",
        "  `doc-conventions`, `doc-architecture-decisiones`.",
        "- **Al pasar de la 3.x a la 4.x**: `UPGRADE`.",
        "- **Si algo solo aparece en `doc-architecture-decisiones` o en la sección",
        "  `Unreleased` del CHANGELOG**, está por llegar: hay que decirlo así, no",
        "  explicar cómo usarlo. El resto de fuentes describen lo ya publicado.",
        "",
        "Las rutas que aparecen en la documentación técnica son del árbol de código",
        "del proyecto. No sirven para quien ha instalado el programa: a esa persona",
        "hay que responderle con menús y opciones de la aplicación, no con rutas.",
        "",
        "## Fuentes disponibles",
        "",
    ]
    lineas += [f"- `{t}`" for t in sorted(documentos)]
    return "exelearning-indice.md", "\n".join(lineas) + "\n"


def actualizar_repo(repo: Path, nombre: str) -> None:
    """`git pull`, salvo que haya trabajo sin guardar: varios de estos
    repositorios son de Juanjo y puede estar editándolos ahora mismo."""
    sucio = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=60).stdout.strip()
    if sucio:
        registrar(f"  {nombre}: con cambios locales, no se actualiza")
        return
    subprocess.run(["git", "-C", str(repo), "pull", "--quiet"], check=False, timeout=300)


def repos_complementarios(config: dict) -> dict[str, Path]:
    """Los del ecosistema que están configurados y existen en el disco."""
    configurados = config.get("repos_complementarios", {})
    encontrados = {}
    for prefijo in COMPLEMENTARIOS:
        ruta = configurados.get(prefijo)
        if not ruta:
            registrar(f"  aviso: {prefijo} no está en repos_complementarios")
            continue
        ruta = Path(ruta).expanduser()
        if not ruta.is_dir():
            registrar(f"  aviso: {prefijo} no está en el disco ({ruta})")
            continue
        encontrados[prefijo] = ruta
    return encontrados


def sincronizar(config: dict, estado: dict, subir: bool) -> int:
    grupo = next(g for g in config["grupos"] if g["prefijo"] == "exelearning")
    cuaderno = grupo["notebook"]
    repo = Path(config["repo_exelearning"]).expanduser()

    registrar("actualizando los repositorios…")
    actualizar_repo(repo, "exelearning")
    extras = repos_complementarios(config)
    for prefijo, ruta in extras.items():
        actualizar_repo(ruta, prefijo)

    documentos = reunir_documentos(repo, extras)
    titulo_indice, contenido_indice = escribir_indice(documentos, repo)
    documentos[titulo_indice] = contenido_indice

    # El manual consolidado no viene del repositorio: se conserva el que haya.
    MATERIAL.mkdir(parents=True, exist_ok=True)
    for manual in MATERIAL.glob("manual-*.md"):
        documentos[manual.name] = manual.read_text(encoding="utf-8")

    # Y los documentos escritos a mano, que sí están versionados.
    for propia in sorted(FUENTES.glob("*.md")):
        documentos[propia.name] = propia.read_text(encoding="utf-8")

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
