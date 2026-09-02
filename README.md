# Memoria de Telegram

Archiva las conversaciones de tres supergrupos públicos de Telegram como
Markdown mensual y mantiene ese Markdown como fuente de un notebook de
NotebookLM por grupo, de modo que cada notebook es un agente que conoce lo que
se ha hablado en su grupo.

**Se actualiza solo, cada día**: el ordenador exporta el día anterior, lo añade
al archivo del mes en curso y refresca la fuente del notebook correspondiente.

| Grupo | Telegram | Carpeta de salida |
|---|---|---|
| ChatGPT-IA-edu | [@ChatGPTedu](https://t.me/ChatGPTedu) | `salida/chatgpt-ia-edu/` |
| eXeLearning | [@exelearning](https://t.me/exelearning) | `salida/exelearning/` |
| Vibe Coding Educativo | [@vceduca](https://t.me/vceduca) | `salida/vibe-coding-educativo/` |

> **Los datos no están en este repositorio.** Las conversaciones contienen
> mensajes con nombre y apellidos de cientos de personas, y este repositorio es
> público: `salida/`, `datos/`, la sesión de Telegram y `config.json` se quedan
> en el ordenador. El índice de lo archivado está en `salida/INDICE.md`.

## Uso

Normalmente no hay que hacer nada: lo lanza el temporizador. A mano:

```bash
python3 scripts/actualizar.py                     # lo pendiente hasta ayer
python3 scripts/actualizar.py --desde 2026-08-01  # rehacer desde una fecha
python3 scripts/actualizar.py --solo vceduca      # un solo grupo
python3 scripts/actualizar.py --sin-subir         # generar sin tocar NotebookLM
```

Instalar o quitar el disparo automático:

```bash
scripts/instalar.sh            # @reboot + cada 15 min de 7:00 a 23:59
scripts/instalar.sh --quitar
```

El detalle del funcionamiento diario está en
[docs/automatizacion.md](docs/automatizacion.md); el formato del Markdown que se
genera, en [docs/formato-markdown.md](docs/formato-markdown.md).

Para operarlo con una IA hay una skill lista en
[`skills/memoria-telegram/`](skills/memoria-telegram/SKILL.md). Enlazándola desde
la carpeta de skills del agente queda disponible sin más:

```bash
ln -sfn "$PWD/skills/memoria-telegram" ~/.claude/skills/memoria-telegram
```

## Estructura

```
scripts/
  actualizar.py         orquestador: exporta, genera y sube. Punto de entrada
  exportar.py           Telegram → datos/<grupo>-YYYY-MM.json
  generar.py            JSON → salida/<grupo>/conversacion-YYYY-MM.md + índice
  procesar_telegram.py  la conversión en sí: hilos, días, formato
  notebook.py           alta y baja de fuentes en NotebookLM
  avisar.sh             avisos en pantalla
  diario.sh             la pasada diaria, tal como la lanza cron
  instalar.sh           instala o retira el disparo en el crontab
web/                    conversor JSON → Markdown en el navegador, sin instalar nada
docs/                   cómo funciona el automatismo y qué formato produce
skills/memoria-telegram instrucciones para que una IA opere todo esto
config.json             credenciales y grupos (NO se versiona)
config.json.ejemplo     plantilla de lo anterior
datos/    salida/       exportaciones y conversaciones (NO se versionan)
sesion/   estado.json   sesión de Telegram y última fecha procesada (NO se versionan)
registro/               registros de cada pasada (NO se versiona)
```

## Puesta en marcha en un ordenador nuevo

```bash
cp config.json.ejemplo config.json && chmod 600 config.json  # y rellenarlo
pip install telethon "notebooklm-py[browser]"
notebooklm login                    # autoriza NotebookLM
python3 -c "from telethon import TelegramClient"             # comprobación
python3 scripts/actualizar.py --sin-subir                    # primera prueba
scripts/instalar.sh
```

La primera ejecución de Telethon pedirá el código de Telegram y dejará la sesión
autorizada en `sesion/telegram.session`; a partir de ahí no vuelve a pedir nada.

## El conversor del navegador

`web/index.html` es una herramienta aparte y autónoma: se abre en el navegador,
se le sueltan los JSON exportados de Telegram y produce el mismo Markdown, sin
instalar nada ni subir los datos a ningún sitio. Ver [web/README.md](web/README.md).
