#!/usr/bin/env python3
"""Pone al día las conversaciones de los grupos y sus fuentes en NotebookLM.

Se ejecuta una vez al día, normalmente lanzado por scripts/diario.sh. Trabaja
siempre sobre días terminados —hasta ayer inclusive—, porque un día a medias se
subiría incompleto y habría que rehacerlo igualmente al día siguiente.

    python3 scripts/actualizar.py                    # lo pendiente hasta ayer
    python3 scripts/actualizar.py --desde 2026-08-01 # rehacer desde una fecha
    python3 scripts/actualizar.py --solo vceduca     # un solo grupo
    python3 scripts/actualizar.py --sin-subir        # sin tocar NotebookLM
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

import exportar  # noqa: E402
import generar  # noqa: E402
import notebook  # noqa: E402
import podar  # noqa: E402

CONFIG = BASE / "config.json"
ESTADO = BASE / "estado.json"
SESION = BASE / "sesion" / "telegram"
AVISAR = BASE / "scripts" / "avisar.sh"


def registrar(mensaje: str = "") -> None:
    """Una línea con hora al registro. Es lo que queda cuando algo falló de
    madrugada y nadie estaba delante."""
    if mensaje:
        print(f"{datetime.now():%H:%M:%S}  {mensaje}", flush=True)
    else:
        print(flush=True)


def avisar(orden: str, *argumentos: str) -> None:
    """Aviso en pantalla. Nunca interrumpe el proceso: sin sesión gráfica el
    trabajo debe seguir, que para eso queda el registro."""
    try:
        subprocess.run([str(AVISAR), orden, *argumentos], timeout=15,
                       capture_output=True, check=False)
    except (OSError, subprocess.SubprocessError):
        pass


def paso(mensaje: str) -> None:
    registrar(mensaje)
    avisar("paso", mensaje)


def cargar_config() -> dict:
    if not CONFIG.exists():
        raise SystemExit(
            f"Falta {CONFIG.name}. Copia config.json.ejemplo y rellena tus datos."
        )
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def cargar_estado() -> dict:
    if ESTADO.exists():
        try:
            with open(ESTADO, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            registrar("aviso: estado.json ilegible; se empieza de cero")
    return {"grupos": {}}


def guardar_estado(estado: dict) -> None:
    estado["actualizado"] = datetime.now().isoformat(timespec="seconds")
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def meses_entre(desde: date, hasta: date) -> list[str]:
    """Los meses naturales que tocan el rango, como 'YYYY-MM'."""
    meses, anio, mes = [], desde.year, desde.month
    while (anio, mes) <= (hasta.year, hasta.month):
        meses.append(f"{anio}-{mes:02d}")
        anio, mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
    return meses


def inicio_por_defecto(grupo: dict, hasta: date) -> date:
    """Desde dónde empezar cuando no hay estado previo.

    Se retrocede al día 1 del último mes que ya tenga Markdown y se rehace ese
    mes entero: cuesta una exportación de más y a cambio cierra el hueco de un
    mes que se hubiera quedado a medias.
    """
    carpeta = generar.SALIDA / grupo["carpeta"]
    meses = sorted(p.stem.replace("conversacion-", "") for p in carpeta.glob("conversacion-*.md"))
    if meses:
        anio, mes = (int(x) for x in meses[-1].split("-"))
        return date(anio, mes, 1)
    return date(hasta.year, hasta.month, 1)


async def procesar_grupo(cliente, grupo: dict, estado: dict, hasta: date,
                         desde_forzado: date | None, subir: bool) -> dict:
    """Pone al día un grupo. Devuelve el resumen de lo hecho."""
    prefijo = grupo["prefijo"]
    previo = estado["grupos"].setdefault(prefijo, {"meses": {}})

    if desde_forzado is not None:
        desde = desde_forzado
    elif previo.get("ultimo_dia"):
        desde = date.fromisoformat(previo["ultimo_dia"]) + timedelta(days=1)
    else:
        desde = inicio_por_defecto(grupo, hasta)

    if desde > hasta:
        registrar(f"  {prefijo}: al día, nada que hacer")
        return {"grupo": prefijo, "meses": [], "subidas": 0}

    meses = meses_entre(desde, hasta)
    paso(f"{grupo['usuario']}: exportando {' '.join(meses)}")

    # Tope exclusivo: el arranque de hoy. Así el día en curso nunca entra.
    fin = datetime.combine(hasta + timedelta(days=1), datetime.min.time(), timezone.utc)

    resumen = {"grupo": prefijo, "meses": [], "subidas": 0}
    for mes in meses:
        exportado = await exportar.exportar_mes(cliente, grupo, mes, hasta=fin)
        registrar(f"  {mes}: {exportado['utiles']} mensajes con texto")

        generado = generar.generar_mes(grupo, mes)
        if generado["vacio"]:
            registrar(f"  {mes}: sin contenido, no se genera Markdown")
            continue

        # Lo que decide si hay que subir es la comparación con lo último que se
        # subió de verdad, no con la versión anterior del fichero: si el .md se
        # regeneró sin subirse, el notebook sigue desactualizado.
        subido = previo["meses"].get(mes, {}).get("huella")
        if generado["huella"] == subido:
            registrar(f"  {mes}: sin cambios, el notebook ya está al día")
            resumen["meses"].append({"mes": mes, "cambio": False})
            continue

        if not subir:
            registrar(f"  {mes}: Markdown actualizado (sin subir, --sin-subir)")
            resumen["meses"].append({"mes": mes, "cambio": True, "subido": False})
            continue

        paso(f"{grupo['usuario']}: subiendo {generado['ruta'].name} a NotebookLM")
        efecto = notebook.sustituir_fuente(grupo["notebook"], generado["ruta"], registrar)
        registrar(f"  {mes}: subido ({efecto['retiradas']} versión previa retirada)")

        # La huella se anota solo si la fuente quedó realmente sustituida. Si el
        # indexado no terminó, el mes se reintenta en la pasada siguiente.
        if efecto["lista"]:
            previo["meses"][mes] = {"huella": generado["huella"], "fuente": efecto["subida"]}
        resumen["meses"].append({"mes": mes, "cambio": True, "subido": True})
        resumen["subidas"] += 1

    previo["ultimo_dia"] = hasta.isoformat()
    return resumen


async def principal(args) -> int:
    from telethon import TelegramClient

    config = cargar_config()
    estado = cargar_estado()

    grupos = config["grupos"]
    if args.solo:
        grupos = [g for g in grupos if g["prefijo"] == args.solo]
        if not grupos:
            raise SystemExit(f"No hay ningún grupo con prefijo '{args.solo}'")

    hasta = date.fromisoformat(args.hasta) if args.hasta else date.today() - timedelta(days=1)
    desde = date.fromisoformat(args.desde) if args.desde else None

    registrar(f"=== actualización hasta {hasta} ===")

    # Las dos sesiones se comprueban antes de empezar: descubrir a mitad que
    # NotebookLM ha caducado deja el trabajo hecho a medias y sin subir.
    if args.subir:
        cuenta = notebook.comprobar_acceso()
        registrar(f"NotebookLM: sesión válida ({cuenta})")

    cliente = TelegramClient(str(SESION), config["api_id"], config["api_hash"])
    await cliente.start()
    if not await cliente.is_user_authorized():
        raise SystemExit("La sesión de Telegram no está autorizada.")

    fallos, resumenes = [], []
    try:
        for grupo in grupos:
            try:
                resumenes.append(
                    await procesar_grupo(cliente, grupo, estado, hasta, desde, args.subir)
                )
            except Exception as error:  # noqa: BLE001
                # Un grupo caído no debe llevarse por delante a los otros dos.
                registrar(f"  ERROR en {grupo['prefijo']}: {type(error).__name__}: {error}")
                fallos.append(f"{grupo['usuario']}: {error}")
    finally:
        await cliente.disconnect()
        guardar_estado(estado)

    indice = generar.generar_indice(config["grupos"])
    registrar(f"índice regenerado: {indice.relative_to(BASE)}")

    # Poda de lo redundante, para que el repositorio no engorde sin freno.
    comprimidas = podar.comprimir_exportaciones()
    retirados = podar.podar_estado(estado)
    if comprimidas or retirados:
        registrar(f"poda: {len(comprimidas)} exportación(es) comprimida(s), "
                  f"{retirados} mes(es) fuera de estado.json")
        guardar_estado(estado)

    subidas = sum(r["subidas"] for r in resumenes)
    if fallos:
        avisar("error", "Memoria de Telegram: fallo",
               "\n".join(fallos) + "\n\nDetalle en registro/.")
        registrar(f"=== terminado con {len(fallos)} fallo(s) ===")
        return 1

    if subidas:
        avisar("fin", f"Al día hasta el {hasta:%d/%m}. "
                      f"{subidas} conversación(es) actualizada(s) en NotebookLM.")
    else:
        avisar("fin", f"Al día hasta el {hasta:%d/%m}. Sin novedades que subir.")
    registrar(f"=== terminado: {subidas} subida(s) ===")
    return 0


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--desde", metavar="YYYY-MM-DD",
                            help="rehacer desde esta fecha, ignorando el estado")
    analizador.add_argument("--hasta", metavar="YYYY-MM-DD",
                            help="último día a procesar (por omisión, ayer)")
    analizador.add_argument("--solo", metavar="PREFIJO",
                            help="procesar solo ese grupo")
    analizador.add_argument("--sin-subir", dest="subir", action="store_false",
                            help="generar los Markdown sin tocar NotebookLM")
    args = analizador.parse_args()

    try:
        return asyncio.run(principal(args))
    except KeyboardInterrupt:
        registrar("interrumpido")
        return 130
    except Exception as error:  # noqa: BLE001
        registrar(f"ERROR: {type(error).__name__}: {error}")
        avisar("error", "Memoria de Telegram: fallo", str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
