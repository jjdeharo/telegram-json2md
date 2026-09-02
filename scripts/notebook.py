#!/usr/bin/env python3
"""Actualiza en NotebookLM la fuente de un mes, a través del CLI `notebooklm`.

Una fuente de NotebookLM no se puede editar: para reflejar el día nuevo hay que
sustituirla. El orden importa y es siempre el mismo —subir la nueva, esperar a
que quede indexada, y solo entonces borrar la vieja—, de modo que un fallo a
mitad deja el mes duplicado un rato, que es molesto pero inofensivo, en vez de
dejar al notebook sin ese mes, que sí sería una pérdida.
"""

from __future__ import annotations

import json
import subprocess


class ErrorNotebook(RuntimeError):
    pass


def _cli(*argumentos: str, tiempo: int = 300) -> dict:
    """Ejecuta el CLI en modo JSON y devuelve la respuesta."""
    orden = ["notebooklm", *argumentos, "--json"]
    proceso = subprocess.run(orden, capture_output=True, text=True, timeout=tiempo)
    if proceso.returncode != 0:
        detalle = (proceso.stderr or proceso.stdout or "").strip().splitlines()
        raise ErrorNotebook(f"{' '.join(orden)} → {detalle[-1] if detalle else 'sin detalle'}")
    try:
        return json.loads(proceso.stdout)
    except json.JSONDecodeError as error:
        raise ErrorNotebook(f"respuesta ilegible de {' '.join(orden)}: {error}") from error


def comprobar_acceso() -> str:
    """Verifica que la sesión de NotebookLM sigue siendo válida.

    Con --test se hace una llamada real: sin él, un fichero de cookies caducado
    pero bien formado pasaría la comprobación y el fallo aparecería más tarde,
    ya con medio proceso hecho.
    """
    estado = _cli("auth", "check", "--test", tiempo=60)
    if estado.get("status") != "ok" or not estado.get("checks", {}).get("token_fetch"):
        raise ErrorNotebook("la sesión de NotebookLM ha caducado; ejecuta: notebooklm login")
    return estado.get("account", {}).get("email", "")


def fuentes(notebook: str) -> list[dict]:
    return _cli("source", "list", "-n", notebook, tiempo=120).get("sources", [])


def buscar_fuente(notebook: str, titulo: str) -> list[str]:
    """Identificadores de las fuentes que se llaman así (normalmente una)."""
    return [f["id"] for f in fuentes(notebook) if f.get("title") == titulo]


def sustituir_fuente(notebook: str, ruta, registrar=print) -> dict:
    """Sube el .md y retira las versiones anteriores del mismo mes."""
    titulo = ruta.name
    viejas = buscar_fuente(notebook, titulo)

    nueva = _cli("source", "add", str(ruta), "-n", notebook, "--title", titulo)
    id_nueva = nueva.get("source", {}).get("id")
    if not id_nueva:
        raise ErrorNotebook(f"NotebookLM no devolvió identificador al subir {titulo}")

    # Si la indexación falla o tarda demasiado, las viejas se quedan: es
    # preferible un duplicado a un notebook sin ese mes.
    listo = subprocess.run(
        ["notebooklm", "source", "wait", id_nueva, "-n", notebook, "--timeout", "300"],
        capture_output=True, text=True,
    ).returncode == 0

    if not listo:
        registrar(f"    aviso: {titulo} aún se está indexando; no se retira la versión anterior")
        return {"subida": id_nueva, "retiradas": 0, "lista": False}

    retiradas = 0
    for id_vieja in viejas:
        try:
            _cli("source", "delete", id_vieja, "-n", notebook, "--yes", tiempo=120)
            retiradas += 1
        except ErrorNotebook as error:
            registrar(f"    aviso: no se pudo retirar la versión anterior de {titulo}: {error}")

    return {"subida": id_nueva, "retiradas": retiradas, "lista": True}
