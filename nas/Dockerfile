# Memoria de Telegram, para que la pasada diaria no dependa del portátil.
#
# Todo lo que el automatismo necesita va aquí dentro: git, el entorno de Python,
# el CLI de NotebookLM y Claude. Lo que queda fuera —el repositorio, los datos,
# las sesiones— se monta desde /volume1/docker/memoria-telegram, de modo que
# reconstruir la imagen no toca nada de lo que importa.
FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Madrid \
    LANG=es_ES.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git tzdata tini procps less ripgrep \
      python3 python3-venv \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

# El usuario del contenedor es el mismo uid que el del NAS: así lo que escriba
# en los volúmenes montados le sigue perteneciendo a Juanjo fuera.
RUN useradd -u 1000 -m -s /bin/bash jjdeharo

# uv, fuera del home: el home es un volumen y la imagen tiene que traer sus
# herramientas puestas. UV_TOOL_DIR va en el entorno para que
# actualizar-cli.py encuentre lo mismo que se instaló aquí. Al reconstruir la
# imagen, el CLI vuelve a la versión de esta capa; la pasada diaria lo sube.
ENV UV_TOOL_DIR=/opt/uv/tools \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_INSTALL_DIR=/usr/local/bin \
    PATH=/usr/local/bin:/usr/bin:/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && uv tool install "notebooklm-py[browser,headless]" \
 && chown -R 1000:1000 /opt/uv

# Claude Code, que es quien repara la pasada cuando falla y quien decide qué
# hacer con la documentación nueva de eXeLearning. El instalador nativo no
# necesita Node; se instala en un home propio, /opt/claude.
# La versión se fija aquí porque Claude Code no se actualiza solo dentro del
# contenedor y un modelo nuevo puede exigir una versión mínima. Para subirla,
# se cambia este valor y se reconstruye: ver docs/adr/0001-modelo-de-claude-fijo.md.
ARG CLAUDE_CODE_VERSION=2.1.289
RUN mkdir -p /opt/claude \
 && curl -fsSL https://claude.ai/install.sh | HOME=/opt/claude bash -s "${CLAUDE_CODE_VERSION:-2.1.289}" \
 && ln -s /opt/claude/.local/bin/claude /usr/local/bin/claude \
 && chown -R 1000:1000 /opt/claude

COPY bucle.sh /usr/local/bin/bucle.sh
RUN chmod +x /usr/local/bin/bucle.sh

USER 1000
WORKDIR /proyecto
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/local/bin/bucle.sh"]
