#!/usr/bin/env python3
"""Manda un aviso a los Mensajes guardados de Telegram de Juanjo.

Los carteles en pantalla solo sirven si hay alguien delante del ordenador, y esto
trabaja a las siete de la mañana. Para lo que de verdad hay que contar —que se
actualizó una herramienta, que se clasificó documentación nueva, que algo se
rompió— se usa el propio Telegram, que ya está autorizado aquí y le llega al
móvil.

Va a «Mensajes guardados» (el chat con uno mismo): ni molesta a nadie ni depende
de otro servicio.

    python3 scripts/informar.py "texto del aviso"
    echo "texto" | python3 scripts/informar.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CONFIG = BASE / "config.json"
SESION = BASE / "sesion" / "telegram"
BITACORA = BASE / "registro" / "avisos.log"


async def _enviar(texto: str) -> None:
    from telethon import TelegramClient

    with open(CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    cliente = TelegramClient(str(SESION), config["api_id"], config["api_hash"])
    await cliente.start()
    try:
        await cliente.send_message("me", texto)
    finally:
        await cliente.disconnect()


def informar(texto: str) -> bool:
    """Envía el aviso y lo anota. Nunca revienta: un aviso no vale una pasada."""
    marca = f"{datetime.now():%Y-%m-%d %H:%M}"
    mensaje = f"🗂️ *Memoria de Telegram* · {marca}\n\n{texto}"

    BITACORA.parent.mkdir(parents=True, exist_ok=True)
    with open(BITACORA, "a", encoding="utf-8") as f:
        f.write(f"{marca}  {texto.splitlines()[0]}\n")

    try:
        asyncio.run(_enviar(mensaje))
        return True
    except Exception as error:  # noqa: BLE001
        with open(BITACORA, "a", encoding="utf-8") as f:
            f.write(f"{marca}  (no se pudo enviar a Telegram: {error})\n")
        return False


if __name__ == "__main__":
    texto = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    texto = texto.strip()
    if not texto:
        print("nada que informar", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(0 if informar(texto) else 1)
