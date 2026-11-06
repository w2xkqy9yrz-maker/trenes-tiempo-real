# Vía · Trenes en tiempo real

**Una web creada con la ayuda de [Codex, de OpenAI](https://openai.com/codex/), a partir de las ideas y decisiones de su responsable, para consultar información ferroviaria de España y mejorarla entre todos.**

Este es el repositorio público del proyecto. Puedes descargar el código, estudiar cómo funciona, hacer una copia para desarrollar mejoras y enviarlas al responsable mediante una **pull request**. También puedes proponer ideas o comunicar errores sin programar. Las contribuciones se revisan antes de incorporarlas a la web pública.

[**Abrir la web**](https://w2xkqy9yrz-maker.github.io/trenes-tiempo-real/) · [**Descargar el código ZIP**](https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real/archive/refs/heads/main.zip) · [**Proponer una mejora o comunicar un error**](https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real/issues/new) · [**Cómo colaborar**](CONTRIBUTING.md)

## Qué puedes hacer en la web

- **Mapa:** consultar los trenes con coordenadas publicadas y distinguir las posiciones antiguas.
- **Trenes en servicio:** buscar por tren, línea o estación, filtrar y consultar recorridos, paradas, horarios y previsiones cuando existen.
- **Incidencias:** leer los avisos presentes en el canal abierto de Cercanías y Rodalies de Renfe.
- **Notificaciones:** elegir qué avisos quieres recibir, seguir un servicio, línea o número de tren, añadir sonido o notificaciones del navegador, o **no recibir ninguna**. Las preferencias se guardan en tu navegador y empiezan desactivadas.
- **Actualización:** consulta automática cada cinco minutos mientras la web está abierta y botón para volver a consultar los datos disponibles.

La web utiliza datos publicados por Renfe, no trenes simulados. Es un proyecto independiente, sin afiliación con Renfe, Adif u OpenAI. Codex se ha utilizado para desarrollar el proyecto; las posiciones, horarios y avisos proceden de las fuentes ferroviarias indicadas abajo.

## Descargar y probar en tu ordenador

Necesitas **Python 3.10 o posterior** y conexión a Internet. El servidor local utiliza únicamente la biblioteca estándar de Python.

1. Descarga el [ZIP del proyecto](https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real/archive/refs/heads/main.zip) y descomprímelo. También puedes clonarlo:

   ```sh
   git clone https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real.git
   cd trenes-tiempo-real
   ```

2. Abre una terminal dentro de la carpeta del proyecto y ejecuta:

   ```sh
   python3 scripts/serve.py
   ```

3. Visita **http://127.0.0.1:8080**. No abras `index.html` con doble clic: el mapa, los datos y los módulos necesitan un servidor web.

Para ejecutar las pruebas, utiliza **Node.js 20 o posterior**:

```sh
npm test
```

No hace falta instalar dependencias npm para estas pruebas. Las instrucciones de actualización de datos, GitHub Pages y el intermediario opcional de Cloudflare están en la [guía técnica](docs/GUIA_TECNICA.md).

## Enviar mejoras para la web pública

### Si tienes una idea o encuentras un error

Abre una [issue](https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real/issues/new). Explica qué ocurre o qué propones, qué esperabas y, si procede, la línea o tren y la fecha y hora. Puedes adjuntar una captura sin datos personales. **No necesitas saber programar.**

### Si quieres modificar el código

1. Pulsa **Fork** en este repositorio para crear tu copia.
2. Crea una rama para tu mejora, realiza los cambios y compruébalos localmente.
3. Ejecuta `npm test` cuando modifiques el funcionamiento de la aplicación.
4. Abre una [pull request](https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real/compare) desde tu rama hacia la rama **`main` de este repositorio original**.
5. Describe el problema, la solución y cómo la has probado. Para cambios visuales, añade una captura.

El responsable del proyecto revisará la propuesta y podrá pedir ajustes, aceptarla o descartarla. **Enviar una mejora no la publica automáticamente.** Cuando una propuesta se integra en `main`, el flujo de GitHub Actions prepara los datos y despliega la nueva versión en la web original, si finaliza correctamente.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para los detalles. Puedes contribuir con código, documentación, accesibilidad, traducciones, pruebas o nuevas fuentes oficiales de datos.

## Cobertura y límites

El proyecto integra las fuentes abiertas de **Renfe para Cercanías y Rodalies, media distancia, larga distancia y alta velocidad**. Solo aparecen los vehículos y campos que esas fuentes publican. No representa todos los trenes de España ni incluye actualmente Portugal, FGC, Euskotren, Iryo, Ouigo u otros operadores.

La publicación del GPS de media y larga distancia se anuncia cada **15 minutos**. La consulta de la web cada cinco minutos no hace que el operador publique antes. En modo instantánea, el botón vuelve a leer el último archivo de GitHub Actions; sus ejecuciones pueden retrasarse. La pantalla muestra la antigüedad y los errores de las fuentes.

Las rutas dibujadas unen estaciones de forma esquemática. Las notificaciones dependen de datos recientes y de la web abierta; una detención observada puede ser una parada normal. Esta herramienta informa sobre viajes y **no es un sistema de seguridad ferroviaria**.

## Estructura del proyecto

| Ruta | Contenido |
| --- | --- |
| `web/` | Interfaz, mapa, lógica de notificaciones y archivos públicos. |
| `web/data/` | Catálogo de horarios e instantáneas de datos. |
| `scripts/` | Descarga de datos oficiales y servidor local. |
| `worker/` | Intermediario opcional de Cloudflare para consultas directas. |
| `tests/` | Pruebas automatizadas del tratamiento de datos y notificaciones. |
| `.github/workflows/pages.yml` | Actualización de datos y despliegue en GitHub Pages. |
| `docs/GUIA_TECNICA.md` | Configuración, funcionamiento y límites detallados. |

## Fuentes y reconocimiento

**Origen de los datos: Renfe Operadora**, con atribución [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).

- [GPS de Cercanías](https://data.renfe.com/dataset/ubicacion-vehiculos).
- [GPS de alta velocidad, larga y media distancia](https://data.renfe.com/dataset/posicion-vehiculos-av-ld-md).
- [Horarios de Cercanías y Rodalies](https://data.renfe.com/dataset/horarios-cercanias).
- [Horarios de alta velocidad, larga y media distancia](https://data.renfe.com/dataset/horarios-de-alta-velocidad-larga-distancia-y-media-distancia).
- [Incidencias y avisos](https://data.renfe.com/dataset/incidencias-avisos).

Mapa con [Leaflet](https://leafletjs.com/) y cartografía de [OpenStreetMap](https://www.openstreetmap.org/copyright). La licencia de Leaflet se incluye en `web/vendor/LEAFLET-LICENSE.txt`. Las condiciones y atribuciones de los datos y bibliotecas de terceros siguen siendo aplicables a las contribuciones.

Desarrollada con ayuda de **Codex**. Mantenimiento y revisión de contribuciones: [@w2xkqy9yrz-maker](https://github.com/w2xkqy9yrz-maker).
