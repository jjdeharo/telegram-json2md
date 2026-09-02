#!/usr/bin/env python3
"""Crea el bot de avisos hablando con @BotFather, y lo deja configurado.

Telegram no notifica los mensajes que uno se escribe a sí mismo, así que los
avisos tienen que venir de un bot. Crear uno se hace conversando con @BotFather,
y eso puede hacerse igual de bien desde la sesión ya autorizada aquí que a mano.

Después le manda /start al bot recién creado —Telegram exige que la conversación
la inicie la persona, no el bot— y guarda el token en config.json.

    python3 scripts/crear-bot.py
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CONFIG = BASE / "config.json"

NOMBRE = "Memoria de Telegram"
# Se prueban por orden hasta encontrar uno libre: los usuarios de bot son únicos
# en todo Telegram y los obvios suelen estar cogidos.
USUARIOS = ["memoria_jjdeharo_bot", "memoriatelegram_jjdeharo_bot",
            "jjdeharo_memoria_bot", "avisos_jjdeharo_bot"]


async def desbloquear(cliente, quien: str) -> None:
    """BotFather puede estar bloqueado de hace años; sin desbloquearlo no hay bot."""
    from telethon.tl.functions.contacts import UnblockRequest
    try:
        await cliente(UnblockRequest(await cliente.get_input_entity(quien)))
        print(f"  se ha desbloqueado a @{quien}")
    except Exception:  # noqa: BLE001
        pass


async def conversar(cliente, texto: str, espera: float = 4.0) -> str:
    """Manda algo a BotFather y devuelve su respuesta."""
    from telethon.errors.rpcerrorlist import YouBlockedUserError
    try:
        await cliente.send_message("BotFather", texto)
    except YouBlockedUserError:
        await desbloquear(cliente, "BotFather")
        await cliente.send_message("BotFather", texto)
    await asyncio.sleep(espera)
    mensajes = await cliente.get_messages("BotFather", limit=1)
    return mensajes[0].text if mensajes else ""


async def crear(cliente) -> tuple[str, str]:
    respuesta = await conversar(cliente, "/newbot")
    if "name" not in respuesta.lower():
        raise RuntimeError(f"BotFather no pide el nombre; responde: {respuesta[:200]}")

    respuesta = await conversar(cliente, NOMBRE)
    if "username" not in respuesta.lower():
        raise RuntimeError(f"BotFather no pide el usuario; responde: {respuesta[:200]}")

    for usuario in USUARIOS:
        print(f"  probando @{usuario}…")
        respuesta = await conversar(cliente, usuario, espera=5.0)
        token = re.search(r"(\d{6,}:[A-Za-z0-9_-]{30,})", respuesta)
        if token:
            return usuario, token.group(1)
        if "taken" not in respuesta.lower() and "already" not in respuesta.lower():
            raise RuntimeError(f"respuesta inesperada de BotFather: {respuesta[:300]}")
        print("     ocupado")
    raise RuntimeError("todos los nombres de usuario probados están ocupados")


async def main() -> int:
    from telethon import TelegramClient

    with open(CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    if config.get("bot_avisos", {}).get("token"):
        print("ya hay un bot configurado; no se crea otro")
        return 0

    cliente = TelegramClient(str(BASE / "sesion" / "telegram"),
                             config["api_id"], config["api_hash"])
    await cliente.start()
    try:
        print("hablando con @BotFather…")
        usuario, token = await crear(cliente)
        print(f"bot creado: @{usuario}")

        # Telegram no deja que un bot escriba primero: la conversación tiene que
        # abrirla la persona. Se abre desde aquí, que es su propia cuenta.
        print("abriendo la conversación con el bot…")
        await cliente.send_message(usuario, "/start")
        await asyncio.sleep(3)
    finally:
        await cliente.disconnect()

    import urllib.request
    with urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/getUpdates", timeout=60) as r:
        novedades = json.load(r)
    conversaciones = [u["message"]["chat"]["id"]
                      for u in novedades.get("result", []) if "message" in u]
    if not conversaciones:
        print("el bot aún no ve la conversación; reintentando…")
        await asyncio.sleep(5)
        with urllib.request.urlopen(
                f"https://api.telegram.org/bot{token}/getUpdates", timeout=60) as r:
            conversaciones = [u["message"]["chat"]["id"]
                              for u in json.load(r).get("result", []) if "message" in u]
    if not conversaciones:
        raise RuntimeError("el bot no encuentra la conversación; abre @%s y pulsa Empezar"
                           % usuario)

    config["bot_avisos"] = {"usuario": usuario, "token": token, "chat_id": conversaciones[0]}
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    CONFIG.chmod(0o600)
    print(f"configurado: @{usuario} → conversación {conversaciones[0]}")

    sys.path.insert(0, str(BASE / "scripts"))
    from informar import informar
    informar("Listo. A partir de ahora los avisos te llegan por aquí, **con "
             "notificación en el móvil**, en vez de quedarse mudos en Mensajes "
             "guardados.")
    print("aviso de prueba enviado por el bot")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
