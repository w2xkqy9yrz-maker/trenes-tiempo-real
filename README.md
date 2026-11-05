# 🚆 Trenes España — mapa público

[Ver web](https://w2xkqy9yrz-maker.github.io/trenes-tiempo-real/)

Mapa ferroviario independiente basado en datos públicos. No es un servicio oficial ni garantiza la posición de todos los trenes.

## Cómo funciona

1. GitHub Actions ejecuta `scripts/update.py` aproximadamente cada 5 minutos (la programación puede retrasarse).
2. El script consulta Renfe Cercanías, Renfe larga/media distancia y RadarDeTrenes **desde el servidor**, evitando los bloqueos CORS del navegador.
3. Escribe `data/trenes.json` con el estado de cada fuente, posiciones y fecha de generación.
4. `index.html` consulta ese archivo en GitHub Pages. No utiliza claves privadas.
5. OSIRIS se comprueba de manera experimental, **sin incorporar trenes** hasta confirmar la cobertura y el esquema de sus datos.

## Publicación

Subir `index.html`, `scripts/update.py`, `.github/workflows/update-trains.yml`, `data/trenes.json` y este README a la raíz de la rama `main`. En **Settings → Pages**, publicar desde `main` / raíz. En **Settings → Actions → General → Workflow permissions**, permitir **Read and write permissions** para que el workflow actualice el JSON. Ejecutar manualmente **Actions → Actualizar posiciones ferroviarias → Run workflow** para iniciar.

Si GitHub Pages está configurado para desplegar mediante GitHub Actions, usar el workflow de Pages apropiado o configurar publicación desde rama. GitHub puede retrasar o deshabilitar tareas programadas por inactividad.

## Limitaciones

- La cobertura depende de las fuentes; un tren ausente no está necesariamente cancelado.
- Las coordenadas pueden ser aproximadas o antiguas. Se excluyen datos con marca temporal de más de 2 horas.
- Los registros de diferentes fuentes se mantienen separados si no se puede probar que son el mismo tren, evitando deduplicaciones falsas.
- La integración de OSIRIS es un diagnóstico; no hay evidencia verificada de una flota española adicional.
- Si fallan todas las fuentes, se conservan datos previos etiquetados como antiguos; no se inventan posiciones.

Fuentes: [Renfe Data](https://data.renfe.com/) · [RadarDeTrenes](https://radardetrenes.com/docs) · [OSIRIS](https://www.osirisai.live/).
