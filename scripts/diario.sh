#!/usr/bin/env bash
# Pasada diaria. La lanza cron al encender el ordenador y, durante el día, cada
# cuarto de hora, hasta que una pasada sale bien. No está pensado para
# ejecutarse a mano, aunque puede hacerse: es idempotente.
#
#   ./diario.sh          fuerza la pasada de hoy, aunque ya se hubiera hecho
#   ./diario.sh --auto   como lo llama cron: no repite si el día ya está hecho
#
# El registro queda en registro/diario-<fecha>.log

set -euo pipefail

# Cron arranca con un entorno mínimo: ni PATH de usuario, ni sesión gráfica. Sin
# esto no se encuentra el CLI notebooklm ni salen los avisos en pantalla.
export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:/usr/bin:/bin"
export DISPLAY="${DISPLAY:-:0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

BASE="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
REGISTRO="$BASE/registro"
HOY="$(date +%F)"
MARCA="$REGISTRO/.hecho-$HOY"
LOG="$REGISTRO/diario-$HOY.log"

AUTO=0
[ "${1:-}" = "--auto" ] && AUTO=1

mkdir -p "$REGISTRO"

# Ya hecho hoy: los disparos del resto del día no hacen nada ni dejan ruido.
# Solo se anota un rastro de una línea, sin el cual no habría forma de saber si
# cron llegó a dispararse: el syslog del sistema no es legible para el usuario.
if [ "$AUTO" = "1" ] && [ -f "$MARCA" ]; then
  printf '%s  %s ya hecho\n' "$(date '+%F %T')" "$HOY" >> "$REGISTRO/disparos.log"
  tail -n 200 "$REGISTRO/disparos.log" > "$REGISTRO/disparos.log.tmp" \
    && mv "$REGISTRO/disparos.log.tmp" "$REGISTRO/disparos.log"
  exit 0
fi

exec >>"$LOG" 2>&1

# Cerrojo: al encender coinciden el disparo de @reboot y el del cuarto de hora,
# y la pasada tarda un rato, así que la marca aún no existe cuando llega el
# segundo. Sin esto se exportaría dos veces a la vez.
exec 9>"$REGISTRO/diario.lock"
flock -n 9 || exit 0

# Al encender, cron dispara antes de que haya red o sesión gráfica. Se espera a
# las dos, pero sin bloquear para siempre: si no llegan, se sigue y que falle
# con su registro y su aviso.
esperar() {   # esperar <descripción> <segundos> <orden...>
  local que="$1" limite="$2"; shift 2
  local t=0
  while ! "$@" >/dev/null 2>&1; do
    if [ "$t" -ge "$limite" ]; then
      printf '%s  sin %s tras %ss; se continúa igualmente\n' "$(date '+%F %T')" "$que" "$limite"
      return 1
    fi
    sleep 5; t=$((t + 5))
  done
  [ "$t" -gt 0 ] && printf '%s  %s disponible tras %ss\n' "$(date '+%F %T')" "$que" "$t"
  return 0
}
esperar "red" 300 getent hosts notebook.google.com || true
esperar "sesión gráfica" 120 xset q || true

# La documentación de eXeLearning va aparte de las conversaciones y cambia a su
# propio ritmo, así que se sincroniza siempre, pero un fallo suyo no invalida el
# archivado del día: se anota y se reintenta mañana.
sincronizar_exelearning() {
  python3 "$BASE/scripts/exelearning.py" && return 0
  reparar "la sincronización de la documentación de eXeLearning falló" &&
    python3 "$BASE/scripts/exelearning.py" && return 0
  printf '%s  eXeLearning sigue fallando; se reintentará mañana\n' "$(date '+%F %T')"
}

# Mirar si ha aparecido documentación nueva es distinto de sincronizar la que ya
# se conoce: aquello compara las huellas de una lista fija, y esto recorre el
# repositorio entero para ver si hay documentos que no están en ninguna lista. Ni
# una cosa cubre a la otra, y como el recuento no cuesta nada se hace también a
# diario: esperar al mes siguiente solo conseguiría que el cuaderno se perdiera
# durante semanas algo que ya está publicado.
#
# Cuando encuentra algo, decidir qué hacer con ello exige leerlo, así que ese
# juicio se le pide a un Claude sin sesión interactiva. Lo que decida queda en las
# listas, en la bitácora y en un commit. Si no encuentra nada, no hace nada.
revisar_exelearning() {
  python3 "$BASE/scripts/revisar-exelearning.py" >/dev/null || {
    printf '%s  la revisión de eXeLearning falló; se reintenta mañana\n' "$(date '+%F %T')"
    return 0
  }
  python3 "$BASE/scripts/decidir-exelearning.py" ||
    printf '%s  la decisión automática falló; se reintenta mañana\n' "$(date '+%F %T')"
}

# Cuando algo falla no hay nadie delante, así que en vez de dejar un cartel
# esperando se le da el problema a una IA con el registro, la versión del CLI, las
# notas de la última publicación y las incidencias abiertas del proyecto. Puede
# leer y editar los scripts y ejecutar las comprobaciones en seco, nada más: no
# puede borrar fuentes ni tocar los datos. Si lo arregla, se reintenta la pasada.
reparar() {   # reparar <motivo>
  printf '%s  fallo: %s. Buscando solución…\n' "$(date '+%F %T')" "$1"
  python3 "$BASE/scripts/reparar.py" --motivo "$1" --registro "$LOG"
}

if python3 "$BASE/scripts/actualizar.py" || { reparar "el archivado de las conversaciones falló" &&
     python3 "$BASE/scripts/actualizar.py"; }; then
  sincronizar_exelearning
  revisar_exelearning
  # La marca se pone solo si la pasada terminó bien. Si falló, los disparos del
  # cuarto de hora seguirán reintentando: un corte de red pasajero se arregla
  # solo sin que nadie tenga que enterarse.
  # Y por último, si ha salido versión nueva del CLI de NotebookLM: se instala, se
  # comprueba que todo sigue en pie y, si la nueva rompe algo, se vuelve sola a la
  # anterior. Va al final y sin condicionar nada, con el día ya archivado.
  python3 "$BASE/scripts/actualizar-cli.py" || true

  # Y el parte del día por Telegram. Va al final, cuando ya se sabe todo lo que
  # ha pasado, y es lo único que se manda los días en que no ocurre nada: sin
  # esto, un día normal sería indistinguible de un día en que cron no llegó a
  # dispararse.
  python3 "$BASE/scripts/resumen-diario.py" >/dev/null 2>&1 || true
  touch "$MARCA"
  find "$REGISTRO" -maxdepth 1 -name '.hecho-*' -mtime +7 -delete
  find "$REGISTRO" -maxdepth 1 -name 'diario-*.log' -mtime +60 -delete
  exit 0
fi

# Si se llega aquí, ni la pasada ni la reparación salieron bien. El aviso ya lo
# ha mandado reparar.py por Telegram; aquí solo queda el rastro y el reintento.
printf '%s  la pasada falló y no se pudo reparar; se reintentará en el siguiente disparo\n' "$(date '+%F %T')"
exit 1
