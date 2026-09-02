#!/usr/bin/env python3
"""Decide sola qué hacer con la documentación nueva del repositorio de eXeLearning.

La revisión mensual detecta que han aparecido documentos que nadie ha clasificado,
pero clasificarlos exige leerlos: la decisión depende de a quién sirve el texto, no
de su ruta ni de su nombre. `doc/development/profiling.md` parece documentación del
programa y resulta ser instrumentación de desarrollo; `doc/conventions.md` parece
normas internas y resulta documentar comportamientos intencionados del programa,
que es justo lo que hace falta para responder «no es un fallo, se hizo así».

Así que ese juicio se le pide a un Claude sin sesión interactiva, se valida lo que
responde y se escribe en las listas del sincronizador. Queda registrado con su
motivo, y es reversible: cada decisión es una línea en una lista.

    python3 scripts/decidir-exelearning.py            # decide y sincroniza
    python3 scripts/decidir-exelearning.py --probar   # decide y enseña, sin tocar nada
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

import exelearning  # noqa: E402

SCRIPT_SINCRONIZADOR = BASE / "scripts" / "exelearning.py"
AVISAR = BASE / "scripts" / "avisar.sh"
# La bitácora va versionada, no en registro/: es la respuesta a «¿ha actuado esto
# alguna vez, y qué hizo?», y debe sobrevivir a la limpieza de registros y poder
# consultarse también desde GitHub.
BITACORA = BASE / "docs" / "decisiones-automaticas.md"

# Cuánto se le enseña de cada documento. Con el principio basta: el propósito y el
# público de un documento técnico se declaran en las primeras líneas, y mandarlos
# enteros dispararía el coste sin mejorar la decisión.
ASOMO = 2500

CRITERIO = """Estás clasificando documentación del repositorio de eXeLearning para un cuaderno
de NotebookLM. Ese cuaderno responde a USUARIOS de eXeLearning (profesores que
crean materiales educativos), pero con criterio de programador: debe poder
explicar POR QUÉ el programa se comporta como lo hace.

Para cada documento decide una de estas dos opciones:

- "incluir": explica el programa, su formato de archivo, su instalación, su
  despliegue o alguno de sus comportamientos. Sirve para diagnosticar el problema
  de alguien que usa eXeLearning. En caso de duda entre este y el siguiente, mira
  si el documento describe algo que un usuario pueda llegar a ver o sufrir.
- "excluir": solo explica cómo se COLABORA en el repositorio —abrir pull
  requests, estrategia de ramas, ejecutar las pruebas, montar el entorno de
  desarrollo, instrumentación para depurar— o es un papel de trabajo interno
  (propuesta, investigación, lista de tareas), o son instrucciones dirigidas a
  una IA que TRABAJA SOBRE EL CÓDIGO del proyecto, como AGENTS.md o CLAUDE.md.

Cuidado con esa última: se refiere a quien desarrolla eXeLearning. Un documento
que explique el formato de archivo NO se excluye por estar dirigido a modelos de
lenguaje o a generadores automáticos: sigue describiendo cómo funciona el
formato, y eso es exactamente lo que hace falta para diagnosticar un archivo que
no abre.

Si un documento pertenece a una familia de documentos cortos que ya se agrupan en
uno solo (por ejemplo, las decisiones de arquitectura), no hace falta que hagas
nada: un patrón existente ya los recoge. Clasifícalo igualmente por su contenido.

Responde SOLO con un JSON, sin texto alrededor ni ```:
[{"ruta": "...", "decision": "incluir|excluir", "motivo": "una frase"}]
"""


def cargar_revision():
    especificacion = importlib.util.spec_from_file_location(
        "revision", BASE / "scripts" / "revisar-exelearning.py")
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def preguntar(peticion: str) -> list[dict]:
    """Le pide el juicio a Claude sin sesión interactiva y devuelve su respuesta."""
    proceso = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--max-turns", "1"],
        input=peticion, capture_output=True, text=True, timeout=900)
    if proceso.returncode != 0:
        raise RuntimeError(f"claude falló: {(proceso.stderr or '').strip()[:300]}")

    respuesta = json.loads(proceso.stdout).get("result", "")
    # Suele venir envuelto en un bloque de código aunque se pida lo contrario.
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", respuesta.strip(), flags=re.S)
    return json.loads(limpio)


def aplicar(decisiones: list[dict]) -> dict[str, list[str]]:
    """Escribe las decisiones en las listas del sincronizador."""
    texto = SCRIPT_SINCRONIZADOR.read_text(encoding="utf-8")
    hechas = {"incluir": [], "excluir": []}

    for decision in decisiones:
        ruta, veredicto = decision["ruta"], decision["decision"]
        lista = "EXCLUIR" if veredicto == "excluir" else "INCLUIR"
        entrada = f'    "{ruta}",'
        if entrada in texto:
            continue
        comentario = f'  # {decision.get("motivo", "").strip()}'
        marca = f"{lista} = [\n"
        texto = texto.replace(
            marca, f"{marca}{entrada}{comentario}\n", 1)
        hechas[veredicto].append(ruta)

    if any(hechas.values()):
        cabecera = f"# Decisiones automáticas del {date.today():%d/%m/%Y}:"
        texto = texto.replace("INCLUIR = [\n", f"{cabecera}\nINCLUIR = [\n", 1) \
            if cabecera not in texto else texto
        SCRIPT_SINCRONIZADOR.write_text(texto, encoding="utf-8")
    return hechas


def anotar(decisiones: list[dict]) -> None:
    """Deja constancia en la bitácora de qué se decidió y por qué."""
    if not BITACORA.exists():
        BITACORA.write_text(
            "# Decisiones tomadas automáticamente\n\n"
            "Cada vez que aparece documentación nueva en el repositorio de eXeLearning,\n"
            "la clasifica una IA sin intervención de nadie. Aquí queda lo que decidió y\n"
            "por qué. Si esta lista está vacía, es que nunca ha hecho falta actuar.\n",
            encoding="utf-8")

    lineas = [f"\n## {date.today():%d/%m/%Y}\n"]
    for d in decisiones:
        destino = {"incluir": "→ al cuaderno", "excluir": "→ descartado"}[d["decision"]]
        lineas.append(f"- `{d['ruta']}` {destino}  \n  {d.get('motivo', '').strip()}")
    with open(BITACORA, "a", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def registrar_en_git(decisiones: list[dict]) -> None:
    """Commit de la decisión: el rastro más difícil de perder, y reversible.

    Solo se tocan el script y la bitácora; nada de datos. Si el árbol tuviera
    otros cambios a medias, no se commitea nada para no arrastrarlos.
    """
    pendiente = subprocess.run(["git", "-C", str(BASE), "status", "--porcelain"],
                               capture_output=True, text=True).stdout.split("\n")
    ajenos = [l for l in pendiente if l.strip()
              and not l.endswith(("scripts/exelearning.py", str(BITACORA.relative_to(BASE))))]
    if ajenos:
        print("  aviso: hay otros cambios sin commitear; no se hace commit automático")
        return

    resumen = ", ".join(f"{d['ruta']} → {d['decision']}" for d in decisiones)
    cuerpo = "\n".join(f"- {d['ruta']}: {d['decision']} — {d.get('motivo','').strip()}"
                       for d in decisiones)
    mensaje = (f"Clasificar automáticamente documentación nueva de eXeLearning\n\n"
               f"Aparecieron documentos que ninguna lista cubría. Se clasificaron sin\n"
               f"intervención humana, con el criterio de si explican el programa o solo\n"
               f"cómo se colabora en su repositorio:\n\n{cuerpo}\n")
    subprocess.run(["git", "-C", str(BASE), "add",
                    "scripts/exelearning.py", str(BITACORA.relative_to(BASE))], check=False)
    subprocess.run(["git", "-C", str(BASE), "commit", "-q", "-m", mensaje], check=False)
    print(f"  commit hecho: {resumen[:80]}")


def historial() -> int:
    """Enseña si esto ha actuado alguna vez, y qué hizo."""
    if not BITACORA.exists():
        print("Nunca ha actuado: no hay ninguna decisión automática registrada.")
        return 0
    print(BITACORA.read_text(encoding="utf-8"))
    veces = BITACORA.read_text(encoding="utf-8").count("\n- `")
    print(f"\n({veces} documento(s) clasificados automáticamente en total)")
    return 0


def limpiar_huerfanas(repo: Path) -> list[str]:
    """Quita de INCLUIR las rutas cuyo archivo ya no existe.

    No hay nada que juzgar aquí: si el archivo se borró o se renombró, la entrada
    sobra. Dejarla no rompe la sincronización, pero ensucia la revisión de todos
    los meses siguientes con un aviso que nadie va a atender.
    """
    texto = SCRIPT_SINCRONIZADOR.read_text(encoding="utf-8")
    quitadas = []
    for patron in exelearning.INCLUIR:
        if "*" in patron or (repo / patron).is_file():
            continue
        nuevo = re.sub(rf'^ *"{re.escape(patron)}",.*\n', "", texto, flags=re.M)
        if nuevo != texto:
            texto, _ = nuevo, quitadas.append(patron)
    if quitadas:
        SCRIPT_SINCRONIZADOR.write_text(texto, encoding="utf-8")
    return quitadas


def rehacer_manual_si_toca() -> bool:
    """Reconstruye el manual de usuario si la revisión vio que había uno nuevo."""
    ruta_estado = BASE / "estado.json"
    if not ruta_estado.exists():
        return False
    estado = json.loads(ruta_estado.read_text(encoding="utf-8"))
    if not estado.get("exelearning", {}).get("manual_pendiente"):
        return False

    print("el manual de usuario ha cambiado; reconstruyéndolo…")
    hecho = subprocess.run([sys.executable, str(BASE / "scripts" / "manual_exelearning.py")],
                           timeout=1800).returncode == 0
    if hecho:
        estado["exelearning"].pop("manual_pendiente", None)
        ruta_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    return hecho


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--probar", action="store_true",
                            help="enseñar las decisiones sin escribirlas ni sincronizar")
    analizador.add_argument("--historial", action="store_true",
                            help="ver si ha actuado alguna vez, y qué decidió")
    args = analizador.parse_args()

    if args.historial:
        return historial()

    revision = cargar_revision()
    with open(BASE / "config.json", encoding="utf-8") as f:
        repo = Path(json.load(f)["repo_exelearning"]).expanduser()

    manual_rehecho = rehacer_manual_si_toca()
    huerfanas = limpiar_huerfanas(repo)
    for patron in huerfanas:
        print(f"  retirada de la lista (ya no existe): {patron}")

    todos = revision.documentacion_del_repo(repo)
    incluidos = revision.expandir(repo, exelearning.INCLUIR) | revision.expandir(
        repo, [patron for patron, _ in exelearning.CONSOLIDAR.values()])
    excluidos = revision.expandir(repo, exelearning.EXCLUIR)
    pendientes = [r for r in todos if r not in incluidos and r not in excluidos]

    if not pendientes:
        print("no hay documentación nueva que clasificar")
        if manual_rehecho or huerfanas:
            subprocess.run([sys.executable, str(SCRIPT_SINCRONIZADOR)], check=False, timeout=3600)
        return 0

    print(f"{len(pendientes)} documento(s) sin clasificar; preguntando…")
    partes = [CRITERIO, "\nDocumentos:\n"]
    for ruta in pendientes:
        texto = (repo / ruta).read_text(encoding="utf-8", errors="replace")[:ASOMO]
        partes.append(f"\n--- {ruta} ---\n{texto}\n")

    decisiones = preguntar("".join(partes))

    # Validación: solo se acepta lo que se preguntó y con un veredicto conocido.
    # Un fallo de la IA no debe poder meter rutas inventadas en la lista.
    validas = [d for d in decisiones
               if d.get("ruta") in pendientes
               and d.get("decision") in ("incluir", "excluir")]
    if len(validas) != len(decisiones):
        print(f"  aviso: se descartan {len(decisiones) - len(validas)} respuesta(s) no válida(s)")
    sin_respuesta = [r for r in pendientes if r not in {d["ruta"] for d in validas}]
    if sin_respuesta:
        print(f"  aviso: sin decidir, quedan para la próxima: {', '.join(sin_respuesta)}")

    for d in validas:
        print(f"  {d['decision']:<11} {d['ruta']}\n              → {d.get('motivo','')}")

    if args.probar:
        print("\n(--probar: no se ha escrito nada)")
        return 0

    hechas = aplicar(validas)
    anotar(validas)
    nuevas = len(hechas["incluir"])
    print(f"\naplicado: {nuevas} al cuaderno, {len(hechas['excluir'])} descartado(s)")

    registrar_en_git(validas)
    subprocess.run([sys.executable, str(SCRIPT_SINCRONIZADOR)], check=False, timeout=3600)

    resumen = (f"Documentación nueva de eXeLearning: {nuevas} al cuaderno, "
               f"{len(hechas['excluir'])} descartada(s).")
    subprocess.run([str(AVISAR), "fin", resumen], capture_output=True, check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
