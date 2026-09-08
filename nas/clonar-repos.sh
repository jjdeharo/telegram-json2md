#!/usr/bin/env bash
# Clona en /repos los repositorios que el sincronizador de eXeLearning lee.
# Por HTTPS y anónimo: aquí solo se lee. Se puede volver a lanzar sin miedo.
set -u
cd /repos || exit 1
clonar() {  # clonar <destino> <url> [--filter=blob:none]
  local destino="$1" url="$2"; shift 2
  [ -d "$destino/.git" ] && { echo "ya está: $destino"; return 0; }
  echo "clonando $destino…"
  git clone -q "$@" "$url" "$destino" || echo "FALLÓ: $destino"
}
clonar exelearning                 https://github.com/exelearning/exelearning.git --filter=blob:none
clonar mod_exescorm                https://github.com/exelearning/mod_exescorm.git
clonar mod_exeweb                  https://github.com/exelearning/mod_exeweb.git
clonar wp-exelearning              https://github.com/exelearning/wp-exelearning.git
clonar exeviewer                   https://github.com/exelearning/exeviewer.git
clonar eXeConvert                  https://github.com/eXeConvert/eXeConvert.github.io.git
clonar exe-style-editor.github.io  https://github.com/eXe-style-editor/eXe-style-editor.github.io.git
clonar hackexe4                    https://github.com/hackexe4/hackexe4.github.io.git
clonar visor-webzip.github.io      https://github.com/visor-webzip/visor-webzip.github.io.git
echo "hecho"
