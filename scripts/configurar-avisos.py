#!/usr/bin/env python3
"""Configura el bot que manda los avisos, para que suenen en el móvil.

Telegram no notifica los mensajes que uno se escribe a sí mismo, así que los
avisos en «Mensajes guardados» quedan mudos. Un bot sí notifica.

Antes de ejecutar esto, dos minutos en Telegram:

  1. Habla con @BotFather y manda /newbot.
  2. Ponle nombre (p. ej. «Memoria de Telegram») y un usuario acabado en «bot»
     (p. ej. memoria_jjdeharo_bot).
  3. BotFather devuelve un token con esta pinta: 123456789:AAE...
  4. Busca tu bot por ese usuario, ábrelo y pulsa EMPEZAR. Sin ese paso el bot no
     puede escribirte: Telegram exige que la conversación la inicie la persona.

Después:

    python3 scripts/configurar-avisos.py 123456789:AAE...

Encuentra solo tu identificador de conversación, lo guarda en config.json (que no
se versiona) y manda un aviso de prueba.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CONFIG = BASE / "config.json"


def api(token: str, metodo: str, **parametros):
    url = f"https://api.telegram.org/bot{token}/{metodo}"
    if parametros:
        url += "?" + urllib.parse.urlencode(parametros)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    token = sys.argv[1].strip()

    quien = api(token, "getMe")
    if not quien.get("ok"):
        print(f"El token no vale: {quien.get('description')}")
        return 1
    print(f"bot: @{quien['result']['username']}")

    novedades = api(token, "getUpdates")
    conversaciones = {u["message"]["chat"]["id"]: u["message"]["chat"]
                      for u in novedades.get("result", []) if "message" in u}
    if not conversaciones:
        print("\nEl bot no ha recibido ningún mensaje todavía.\n"
              "Abre su conversación en Telegram y pulsa EMPEZAR (o mándale un «hola»),\n"
              "y vuelve a ejecutar esto. Telegram no deja que un bot escriba primero.")
        return 1

    chat_id, quien_es = next(iter(conversaciones.items()))
    print(f"conversación encontrada: {quien_es.get('first_name','')} ({chat_id})")

    with open(CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    config["bot_avisos"] = {"token": token, "chat_id": chat_id}
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    CONFIG.chmod(0o600)

    sys.path.insert(0, str(BASE / "scripts"))
    from informar import informar
    informar("Avisos configurados. A partir de ahora te llegan por aquí, con "
             "notificación, en vez de a Mensajes guardados.")
    print("\nListo: te acabo de mandar un aviso de prueba por el bot.")
    return 0


if __name__ == "__main__":
    import urllib.parse  # noqa: E402
    raise SystemExit(main())
