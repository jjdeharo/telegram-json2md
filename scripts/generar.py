#!/usr/bin/env python3
"""Convierte los JSON exportados en salida/<carpeta>/conversacion-YYYY-MM.md.

La conversión en sí (hilos, días, formato) la hace procesar_telegram.py, que es
la herramienta de siempre: aquí solo se elige qué mes de qué grupo se regenera
y se mantiene el índice. Así los Markdown nuevos salen exactamente igual que
los que ya están en los notebooks.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from procesar_telegram import generar_markdown, obtener_tipo_chat_legible

BASE = Path(__file__).resolve().parent.parent
DATOS = BASE / "datos"
SALIDA = BASE / "salida"


def huella(contenido: str) -> str:
    """Huella del Markdown de un mes.

    Se compara contra la huella de lo ÚLTIMO SUBIDO, que guarda estado.json, y
    no contra la versión anterior del fichero: el fichero local puede haberse
    regenerado sin que el notebook se haya enterado (una pasada con --sin-subir,
    una subida que falló), y en ese caso hay que subir igualmente. Es también lo
    que evita resubir un mes los días en que el grupo no ha tenido mensajes.
    """
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def generar_mes(grupo: dict, mes: str) -> dict:
    """Regenera el Markdown de un mes. Devuelve su ruta y su huella."""
    origen = DATOS / f"{grupo['prefijo']}-{mes}.json"
    destino = SALIDA / grupo["carpeta"] / f"conversacion-{mes}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)

    with open(origen, encoding="utf-8") as f:
        datos = json.load(f)

    info = {k: datos[k] for k in ("name", "type", "id") if k in datos}
    contenido = generar_markdown(datos.get("messages", []), info)

    # Un mes sin ningún mensaje aprovechable no llega a escribirse: un .md con
    # solo la cabecera no aporta nada al notebook y ensucia el índice.
    cuerpo = contenido.strip()
    if not cuerpo or len(cuerpo.splitlines()) <= 2:
        return {"mes": mes, "ruta": destino, "vacio": True, "huella": ""}

    destino.write_text(contenido, encoding="utf-8")
    return {"mes": mes, "ruta": destino, "vacio": False, "huella": huella(contenido)}


def titulo_grupo(grupo: dict) -> str:
    """Nombre y tipo del grupo, leídos de la última exportación disponible."""
    jsons = sorted(DATOS.glob(f"{grupo['prefijo']}-*.json"))
    if jsons:
        try:
            with open(jsons[-1], encoding="utf-8") as f:
                datos = json.load(f)
            nombre = datos.get("name", grupo["carpeta"])
            tipo = obtener_tipo_chat_legible(datos.get("type", ""))
            return f"{nombre} ({tipo})" if tipo else nombre
        except (json.JSONDecodeError, OSError):
            pass
    return grupo["carpeta"]


def generar_indice(grupos: list[dict]) -> Path:
    """Rehace salida/INDICE.md con todos los meses de los tres grupos."""
    lineas = [
        "# Conversaciones de Telegram",
        "",
        "Índice generado automáticamente. Un archivo por grupo y mes.",
        "",
    ]
    for grupo in grupos:
        carpeta = SALIDA / grupo["carpeta"]
        meses = sorted(carpeta.glob("conversacion-*.md"))
        if not meses:
            continue
        lineas.append(f"## {titulo_grupo(grupo)}")
        lineas.append("")
        for archivo in meses:
            mes = archivo.stem.replace("conversacion-", "")
            lineas.append(f"- [{mes}](./{grupo['carpeta']}/{archivo.name})")
        lineas.append("")

    destino = SALIDA / "INDICE.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas), encoding="utf-8")
    return destino
