# Reparaciones automáticas

Cuando la pasada diaria falla, una IA diagnostica y arregla sin esperar a
nadie. Aquí queda lo que encontró y lo que hizo. Si esto está vacío, es que
nunca se ha roto nada.

## 02/09/2026 06:50 · resuelto

**Fallo:** La sincronización de eXeLearning falló al listar las fuentes del cuaderno

**Informe**

Fallaba el paso que consulta las fuentes del cuaderno de eXeLearning: alguien había cambiado la orden `source list` por `source index`, que no existe en el CLI.
No era la sesión de Google (sigue válida) ni la versión del programa (la 0.8.1 es la última).
He devuelto la orden a `source list`; es el único cambio, una línea en `scripts/notebook.py`, y el código vuelve a estar igual que lo guardado.
Las dos comprobaciones en seco terminan bien: las conversaciones están al día y el cuaderno de eXeLearning tiene sus 47 documentos, sin nada pendiente.
Está resuelto; no hace falta que intervenga nadie.
