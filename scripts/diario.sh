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
esperar "red" 300 getent hosts notebooklm.google.com || true
esperar "sesión gráfica" 120 xset q || true

if python3 "$BASE/scripts/actualizar.py"; then
  # La marca se pone solo si la pasada terminó bien. Si falló, los disparos del
  # cuarto de hora seguirán reintentando: un corte de red pasajero se arregla
  # solo sin que nadie tenga que enterarse.
  touch "$MARCA"
  find "$REGISTRO" -maxdepth 1 -name '.hecho-*' -mtime +7 -delete
  find "$REGISTRO" -maxdepth 1 -name 'diario-*.log' -mtime +60 -delete
  exit 0
fi

printf '%s  la pasada falló; se reintentará en el siguiente disparo\n' "$(date '+%F %T')"
exit 1
