# Trenes España — mapa público de posiciones disponibles

Web estática para GitHub Pages. El mapa **no garantiza todos los trenes españoles ni posiciones GPS en directo**: muestra únicamente posiciones recientes que las fuentes accesibles hayan publicado. Sin datos, muestra un mapa vacío y el estado de las fuentes. No genera posiciones ficticias.

## Instalación limpia

1. **Haz copia** del repositorio anterior antes de sustituirlo. Para una instalación completamente limpia, crea un repositorio público nuevo (por ejemplo `trenes-espana-v2`) y no borres el anterior hasta validar el nuevo.
2. Descomprime el ZIP. **Sube el contenido de la carpeta**, no la carpeta contenedora, a la raíz del repositorio. Deben quedar `index.html`, `data/trenes.json`, `scripts/update.py`, `tests/test_update.py` y `.github/workflows/update-trains.yml`.
3. Si el Mac oculta `.github`, pulsa **Cmd + Shift + .** en Finder. Alternativamente, en GitHub usa **Add file → Create new file** y pega el workflow en la ruta exacta `.github/workflows/update-trains.yml`.
4. En **Settings → Actions → General → Workflow permissions**, selecciona **Read and write permissions** y guarda.
5. En **Settings → Pages**, selecciona **Deploy from a branch**, rama `main`, carpeta `/(root)` y guarda.
6. En **Actions → Actualizar posiciones ferroviarias → Run workflow**, selecciona `main` y ejecuta. Abre `Consultar fuentes` para ver el número de trenes obtenidos y posibles errores.
7. Comprueba `data/trenes.json` y después la web de Pages. El primer despliegue puede tardar unos minutos. La URL será `https://USUARIO.github.io/REPOSITORIO/`.

## Diagnóstico y límites

- Renfe: si el feed devuelve solo `header`, no publica entidades de vehículos en esa respuesta. El programa lo muestra explícitamente.
- RadarDeTrenes: puede devolver cero registros. Se informa sin inventar datos.
- OSIRIS: **no se incorpora** porque no hay un endpoint verificado que publique posiciones de trenes españoles. El error HTTP 400 observado no se considera una fuente útil.
- GitHub Actions tiene un intervalo mínimo programado de cinco minutos, sujeto a retrasos. **No es tiempo real de segundos**.
- Si no llegan posiciones nuevas, se conserva la última captura y se marca como **antigua**; nunca se presenta como actual.
- Las fuentes pueden cambiar formatos, limitar el acceso o retirar datos. Ninguna prueba local puede garantizar su disponibilidad futura.

## Pruebas

`python -m unittest discover -s tests -v`

El workflow ejecuta las pruebas **antes** de consultar y publicar. Para la web se necesita conexión a OpenStreetMap/Leaflet; los mapas base dependen de terceros.

## Seguridad y privacidad

No se usan claves secretas, no se ejecuta código recibido de las API y la web inserta datos externos como texto (no HTML). No añadir tokens al repositorio público.
