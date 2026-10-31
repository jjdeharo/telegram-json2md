#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Guarda el registro de administradores de los grupos antes de que caduque.

Telegram solo conserva 48 horas de ese registro. Para saber qué borra su
antispam (activado el 31-10-2026) y qué siguen borrando a mano los
administradores, la pasada diaria copia aquí los borrados y las expulsiones de
los cuatro grupos, sin repetir los que ya tenía. Ver docs/adr/0003.

Salida: datos/registro-admin/<grupo>.jsonl, una línea por acción.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CONFIG = BASE / "config.json"
SESION = BASE / "sesion" / "telegram"
DESTINO = BASE / "datos" / "registro-admin"

# Los cuatro grupos que cubren los bots, aunque EduMedia-IAG no se archive.
GRUPOS = ["ChatGPTedu", "vceduca", "EduMediaIAG", "exelearning"]


def nombre(e) -> str | None:
    if e is None:
        return None
    n = " ".join(x for x in (getattr(e, "first_name", None), getattr(e, "last_name", None)) if x)
    n = n or getattr(e, "title", None) or str(e.id)
    u = getattr(e, "username", None)
    return f"{n} (@{u})" if u else n


async def guardar(cliente, grupo: str) -> int:
    ruta = DESTINO / f"{grupo}.jsonl"
    vistos: set[int] = set()
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                vistos.add(json.loads(linea)["id"])
    nuevos = []
    async for ev in cliente.iter_admin_log(grupo, delete=True, ban=True):
        if ev.id in vistos:
            continue
        d = {
            "id": ev.id,
            "fecha_utc": ev.date.isoformat(),
            "admin_id": ev.user_id,
            "admin": nombre(ev.user),
            "accion": type(ev.action).__name__.removeprefix("ChannelAdminLogEventAction"),
        }
        if ev.deleted_message and ev.old is not None:
            m = ev.old
            autor = None
            try:
                autor = await m.get_sender()
            except Exception:
                pass
            d.update({
                "autor_id": m.sender_id,
                "autor": nombre(autor),
                "autor_es_bot": getattr(autor, "bot", None),
                "mensaje_id": m.id,
                "mensaje_fecha_utc": m.date.isoformat() if m.date else None,
                "texto": m.message or "",
                "adjunto": type(m.media).__name__ if m.media else None,
            })
        elif hasattr(ev.action, "prev_participant"):
            p = ev.action.new_participant
            d["afectado_id"] = getattr(getattr(p, "peer", None), "user_id", None)
        nuevos.append(d)
    if nuevos:
        nuevos.sort(key=lambda x: x["fecha_utc"])
        with ruta.open("a", encoding="utf-8") as f:
            for d in nuevos:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return len(nuevos)


async def principal() -> int:
    from telethon import TelegramClient

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    DESTINO.mkdir(parents=True, exist_ok=True)
    cliente = TelegramClient(str(SESION), config["api_id"], config["api_hash"])
    await cliente.connect()
    try:
        if not await cliente.is_user_authorized():
            print("registro-admin: la sesión de Telegram no está autorizada")
            return 1
        fallos = 0
        for g in GRUPOS:
            try:
                print(f"registro-admin: {g}: {await guardar(cliente, g)} acciones nuevas")
            except Exception as e:  # un grupo que falla no impide los demás
                fallos += 1
                print(f"registro-admin: {g}: {type(e).__name__}: {e}")
        return 1 if fallos else 0
    finally:
        await cliente.disconnect()


if __name__ == "__main__":
    sys.exit(asyncio.run(principal()))
