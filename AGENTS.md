# Guía para agentes

Este repositorio archiva las conversaciones de tres grupos de Telegram y
mantiene con ellas tres notebooks de NotebookLM. Todo el proceso está
automatizado y descrito en:

- [README.md](README.md) — qué es, cómo se usa, estructura.
- [docs/automatizacion.md](docs/automatizacion.md) — el flujo diario y qué hacer
  cuando algo falla. **Es la fuente de verdad del automatismo.**
- [docs/formato-markdown.md](docs/formato-markdown.md) — el formato del Markdown.

Dos reglas que no hay que romper:

1. **Nunca versionar datos.** `salida/`, `datos/`, `sesion/`, `config.json` y
   `registro/` contienen credenciales o mensajes de personas reales, y el
   repositorio es público.
2. **Al subir a NotebookLM, primero la nueva y después borrar la vieja.** Nunca
   al revés: un fallo a mitad debe dejar un duplicado, no un notebook sin el mes.
