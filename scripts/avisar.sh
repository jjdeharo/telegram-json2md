#!/usr/bin/env bash
# Avisos en pantalla del proceso diario.
#
# El proceso lo arranca cron, no Juanjo, así que sin avisos no hay forma de
# saber que está ocurriendo. Dura un par de minutos, de modo que los pasos van
# como una sola notificación que se reescribe en su sitio —nunca una pila de
# avisos apilándose— y solo el fallo deja un cartel fijo, que es lo único que
# hay que ver aunque no se esté delante en ese momento.
#
#   avisar.sh paso <mensaje>            notificación que reemplaza a la anterior
#   avisar.sh fin <mensaje>             igual, pero se desvanece sola
#   avisar.sh error <título> <mensaje>  cartel fijo, con sonido, hasta que se lea
#   avisar.sh retirar                   quita la notificación en curso

set -euo pipefail

TITULO="Memoria de Telegram"
ICONO_OK=dialog-information
ICONO_MAL=dialog-error
SONIDOS=/usr/share/sounds/freedesktop/stereo

# El identificador de la notificación viva. Guardarlo es lo que permite
# reemplazarla con -r en vez de acumular una por paso.
ESTADO="/tmp/memoria-telegram-avisar-$UID.notif"

export DISPLAY="${DISPLAY:-:0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$UID}"

# Sin sesión gráfica no hay a quién avisar, pero eso no es motivo para tumbar
# el proceso: los mensajes van también al registro.
command -v notify-send >/dev/null 2>&1 || exit 0

# Limpia el marcado que el demonio de notificaciones interpretaría como HTML.
limpiar() { printf '%s' "$1" | tr -d '<>&'; }

notificar() {   # notificar <urgencia> <icono> <expira_ms> <título> <cuerpo>
  local urgencia="$1" icono="$2" expira="$3" titulo="$4" cuerpo="$5"
  local anterior="" nuevo=""
  [ -f "$ESTADO" ] && anterior="$(cat "$ESTADO" 2>/dev/null || true)"

  # -p devuelve el id de la notificación; -r reutiliza el de la anterior.
  nuevo="$(notify-send -p ${anterior:+-r "$anterior"} \
            -u "$urgencia" -i "$icono" -t "$expira" \
            -a "$TITULO" "$titulo" "$cuerpo" 2>/dev/null || true)"
  [ -n "$nuevo" ] && printf '%s' "$nuevo" > "$ESTADO"
  return 0
}

sonar() {
  local s="$SONIDOS/${1:-dialog-warning}.oga"
  [ -f "$s" ] || return 0
  setsid paplay "$s" >/dev/null 2>&1 &
}

orden="${1:-}"; shift || true

case "$orden" in
  paso)
    notificar normal "$ICONO_OK" 0 "$TITULO" "$(limpiar "${1:-}")"
    ;;
  fin)
    notificar low "$ICONO_OK" 10000 "$TITULO" "$(limpiar "${1:-}")"
    rm -f "$ESTADO"
    ;;
  error)
    # expira=0 es "hasta que se cierre a mano": un fallo a las siete de la
    # mañana tiene que seguir en pantalla cuando Juanjo llegue al ordenador.
    notificar critical "$ICONO_MAL" 0 "$(limpiar "${1:-Error}")" "$(limpiar "${2:-}")"
    rm -f "$ESTADO"
    sonar dialog-warning
    ;;
  retirar)
    if [ -f "$ESTADO" ]; then
      notificar low "$ICONO_OK" 1 "$TITULO" ""
      rm -f "$ESTADO"
    fi
    ;;
  *)
    printf 'uso: %s {paso|fin|error|retirar} ...\n' "${0##*/}" >&2
    exit 2
    ;;
esac
