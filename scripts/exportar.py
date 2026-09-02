#!/usr/bin/env python3
"""Exporta de Telegram los mensajes de un mes a datos/<prefijo>-YYYY-MM.json.

Se exporta el mes natural completo, no solo el día pendiente. Cuesta unos
segundos más y a cambio el proceso es idempotente: si una pasada se quedó a
medias, o el ordenador estuvo apagado una semana, la siguiente reconstruye el
mes entero sin casos especiales ni huecos.

El formato del JSON es el mismo que producían las exportaciones anteriores,
para que los Markdown ya generados y los nuevos sean indistinguibles.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATOS = BASE / "datos"


def limites_del_mes(anio: int, mes: int) -> tuple[datetime, datetime]:
    """Devuelve [primer instante del mes, primer instante del siguiente)."""
    inicio = datetime(anio, mes, 1, tzinfo=timezone.utc)
    if mes == 12:
        fin = datetime(anio + 1, 1, 1, tzinfo=timezone.utc)
    else:
        fin = datetime(anio, mes + 1, 1, tzinfo=timezone.utc)
    return inicio, fin


def ruta_json(prefijo: str, mes: str) -> Path:
    return DATOS / f"{prefijo}-{mes}.json"


def _mensaje_a_dict(mensaje) -> dict:
    """Convierte un mensaje de Telethon al esquema de las exportaciones."""
    datos = {
        "id": mensaje.id,
        "type": "service" if mensaje.action else "message",
        "date": mensaje.date.isoformat(),
        "date_unixtime": str(int(mensaje.date.timestamp())),
        "text": mensaje.text or "",
        "text_entities": [],
    }

    # El identificador del mensaje al que responde es lo que permite
    # reconstruir los hilos al generar el Markdown.
    responde_a = getattr(mensaje, "reply_to_msg_id", None)
    if responde_a is None and getattr(mensaje, "reply_to", None):
        responde_a = getattr(mensaje.reply_to, "reply_to_msg_id", None)
    datos["reply_to_message_id"] = responde_a

    remitente = mensaje.sender
    if remitente is not None:
        nombre = getattr(remitente, "first_name", None) or getattr(remitente, "title", None)
        if nombre and getattr(remitente, "last_name", None):
            nombre = f"{nombre} {remitente.last_name}"
        if nombre:
            datos["from"] = nombre
            datos["from_id"] = str(remitente.id)

    return datos


async def exportar_mes(cliente, grupo: dict, mes: str, hasta: datetime | None = None) -> dict:
    """Exporta un mes de un grupo y lo escribe en datos/. Devuelve un resumen.

    `hasta` acota el final (exclusivo) para no exportar el día en curso, que
    todavía no ha terminado y se subiría a medias.
    """
    anio, num_mes = (int(x) for x in mes.split("-"))
    inicio, fin = limites_del_mes(anio, num_mes)
    if hasta is not None and hasta < fin:
        fin = hasta

    entidad = await cliente.get_entity(grupo["usuario"])

    mensajes = []
    # reverse=True recorre del más antiguo al más nuevo desde offset_date, que
    # es el orden natural para acotar por el final y cortar en cuanto se pasa.
    async for mensaje in cliente.iter_messages(entidad, offset_date=inicio, reverse=True):
        if mensaje.date >= fin:
            break
        if mensaje.date < inicio:
            continue
        mensajes.append(_mensaje_a_dict(mensaje))

    exportacion = {
        "name": getattr(entidad, "title", grupo["usuario"]),
        "type": "public_supergroup",
        "id": entidad.id,
        "messages": mensajes,
    }

    destino = ruta_json(grupo["prefijo"], mes)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(exportacion, f, ensure_ascii=False, indent=1)

    utiles = sum(1 for m in mensajes if m["type"] == "message" and m["text"])
    return {"mes": mes, "total": len(mensajes), "utiles": utiles, "ruta": destino}
