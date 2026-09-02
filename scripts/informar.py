#!/usr/bin/env python3
"""Manda un aviso por Telegram a Juanjo.

Los carteles en pantalla solo sirven si hay alguien delante del ordenador, y esto
trabaja a las siete de la mañana. Para lo que de verdad hay que contar —que se
actualizó una herramienta, que se clasificó documentación nueva, que algo se
rompió— se usa Telegram, que le llega al móvil.

Lo manda **el bot «Claude IA»**, y no la cuenta de Juanjo, por un motivo concreto:
Telegram no notifica los mensajes que uno se escribe a sí mismo, así que un aviso
en «Mensajes guardados» se queda ahí sin avisar de nada. Un mensaje de un bot sí
suena.

Ese bot no es de este proyecto: es el canal por el que Claude le escribe desde
cualquier sesión, y sus credenciales viven en `~/.claude/telegram-claude-ia.json`.
Si faltaran, el aviso cae a «Mensajes guardados»: no notifica, pero no se pierde.
Para rehacerlo:

    python3 ~/.claude/scripts/crear-bot-claude.py

Uso:

    python3 scripts/informar.py "texto del aviso"
    echo "texto" | python3 scripts/informar.py
"""

from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CONFIG = BASE / "config.json"
SESION = BASE / "sesion" / "telegram"
BITACORA = BASE / "registro" / "avisos.log"
BOT_GLOBAL = Path.home() / ".claude" / "telegram-claude-ia.json"


def _bot() -> dict:
    """Las credenciales del bot «Claude IA», que es el canal de todo lo mío.

    Vive fuera de este repositorio, en ~/.claude/, porque no es de este proyecto:
    es por donde Claude le escribe a Juanjo desde cualquier sesión. Si algún día
    no estuviera, se mira aquí por compatibilidad y, en último extremo, el aviso
    se manda a «Mensajes guardados», que llega aunque no notifique.
    """
    for ruta, clave in ((BOT_GLOBAL, None), (CONFIG, "bot_avisos")):
        if not ruta.exists():
            continue
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        bot = datos.get(clave) if clave else datos
        if bot and bot.get("token") and bot.get("chat_id"):
            return bot
    return {}


def _por_bot(texto: str, bot: dict) -> None:
    """Vía la API de bots: un HTTPS y nada más, sin dependencias."""
    datos = urllib.parse.urlencode({
        "chat_id": bot["chat_id"], "text": texto, "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
    }).encode()
    peticion = urllib.request.Request(
        f"https://api.telegram.org/bot{bot['token']}/sendMessage", data=datos)
    with urllib.request.urlopen(peticion, timeout=60) as r:
        respuesta = json.load(r)
    if not respuesta.get("ok"):
        raise RuntimeError(respuesta.get("description", "error desconocido"))


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
    # Negrita en el formato que entienden tanto Telethon como la API de bots.
    mensaje = f"🗂️ *Memoria de Telegram* · {marca}\n\n{texto}"

    BITACORA.parent.mkdir(parents=True, exist_ok=True)
    with open(BITACORA, "a", encoding="utf-8") as f:
        f.write(f"{marca}  {texto.splitlines()[0]}\n")

    try:
        bot = _bot()
        if bot:
            _por_bot(mensaje, bot)
        else:
            # Sin bot no hay notificación —Telegram no avisa de lo que uno se
            # escribe a sí mismo—, pero el aviso no se pierde.
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
