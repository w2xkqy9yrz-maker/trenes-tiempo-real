[← Volver al README](../README.md)

# Guía técnica de Vía · Trenes en tiempo real

Web publicada en [GitHub Pages](https://w2xkqy9yrz-maker.github.io/trenes-tiempo-real/). Mapa de España peninsular, listado con buscador, detalle con GPS, estaciones, horario, previsiones publicadas, andén e incidencias. Diseño adaptable al móvil. Consulta automática cada cinco minutos mientras la página está abierta y botón manual.

## Publicarla en tu repositorio

1. Conserva el repositorio **trenes-tiempo-real**. No es necesario borrar el repositorio ni su historial. Puedes sustituir sus archivos por el contenido de esta carpeta.
2. Sube **el contenido completo**, incluidas las carpetas `.github`, `scripts`, `worker` y `web`, a la rama `main`. No metas la carpeta contenedora dentro de otra carpeta del repositorio. Si usas la interfaz de GitHub, verifica que `.github/workflows/pages.yml` también se haya subido; las carpetas que empiezan por punto pueden quedar ocultas en Finder.
3. En GitHub, entra en **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. En **Actions**, abre **Actualizar datos y publicar web** y pulsa **Run workflow** si no se ha iniciado al subir los archivos. Espera a que los trabajos `build` y `deploy` terminen correctamente.
5. La web se publica en la dirección anterior, con el nombre del repositorio intacto.

El repositorio original ya está publicado mediante GitHub Actions. Estas instrucciones también sirven para desplegar una copia propia; adapta las direcciones al propietario y repositorio de tu copia.

## Activar consultas directas a Renfe (recomendado)

GitHub Pages sirve archivos estáticos y las respuestas de Renfe probadas no incluían el permiso CORS necesario para leerlas directamente desde otro dominio. El pequeño servicio `worker/index.js` consulta únicamente cinco URL fijas de Renfe y devuelve JSON al navegador.

1. En una cuenta de Cloudflare con Workers disponible, despliega la carpeta `worker`. Desde una terminal dentro de esa carpeta: `npx wrangler deploy`. Completa el inicio de sesión de Cloudflare cuando lo solicite. Revisa las condiciones y límites de tu cuenta antes de activar el servicio.
2. Copia la URL HTTPS `workers.dev` que devuelva el despliegue.
3. En `web/config.js`, cambia la propiedad `apiBase` por esa URL como texto. Por ejemplo, usando **tu URL real**:

   ```js
   window.TRAINS_CONFIG = { apiBase: 'https://TU-WORKER.TU-SUBDOMINIO.workers.dev' };
   ```

4. Sube el cambio a GitHub y espera a la publicación. La barra de estado debe indicar **Conexión al servicio de datos**.

`ALLOWED_ORIGIN` en `worker/wrangler.toml` está configurado para `https://w2xkqy9yrz-maker.github.io`. Si cambias el dominio de la web, actualiza ese valor y vuelve a desplegar el Worker. No se necesitan claves de Renfe. La restricción de origen evita lecturas de otros sitios desde navegadores; no es un sistema de autenticación ni evita todo uso externo. El servicio aplica un tiempo máximo de espera por fuente y comunica los fallos por separado.

Con el Worker, el botón y el temporizador vuelven a consultar las fuentes (caché de origen del Worker: hasta 20 segundos). Cada visitante consulta al abrir, al pulsar el botón y cada cinco minutos. Los navegadores pueden suspender los temporizadores de pestañas en segundo plano; se vuelve a consultar al recuperar la pestaña si han pasado cinco minutos.

Sin Worker, la web funciona con `web/data/realtime.json`, publicado por GitHub Actions con un cron solicitado cada cinco minutos. El botón **solo relee la última instantánea publicada**, y lo indica en pantalla. GitHub puede retrasar u omitir ejecuciones; en repositorios públicos desactiva los cron tras 60 días sin actividad. No es un servicio con frecuencia garantizada. Véase [documentación de GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Verla en tu ordenador

Desde esta carpeta, con Python 3.10 o posterior:

```sh
python3 scripts/serve.py
```

Abre `http://127.0.0.1:8080`. La configuración incluida detecta localhost y utiliza la API local que descarga datos reales de Renfe. Necesita acceso a Internet. Si ejecutas un servidor estático sencillo en lugar de `serve.py`, la API local no estará disponible y se usará la instantánea de respaldo.

Para reconstruir horarios y posiciones:

```sh
python3 scripts/collect.py --catalog
```

Para actualizar solo posiciones, previsiones e incidencias:

```sh
python3 scripts/collect.py
```

Los ZIP oficiales de horarios se guardan temporalmente en `.cache/` y se renuevan tras doce horas. No se sube esa caché. El catálogo conserva viajes con servicio ayer, hoy y mañana según `calendar.txt` y `calendar_dates.txt`, para incluir servicios nocturnos. Los horarios se distribuyen en 64 archivos por versión y se descargan cuando se selecciona un tren. Las horas GTFS superiores a 24 se muestran como el día siguiente.

## Cobertura y precisión

- **Integrado:** fuentes abiertas de Renfe para Cercanías y Rodalies, AV, media y larga distancia, horarios y avisos del canal abierto de Cercanías. Solo se muestran vehículos presentes en esas fuentes.
- **Sin integración:** Portugal, FGC, Euskotren, Iryo, Ouigo y otros operadores. No se ofrece cobertura total de todos los trenes o comunidades.
- **Frecuencia oficial:** GPS de Cercanías cada 20 segundos; GPS AV/LD/MD cada 15 minutos; previsiones AV/LD/MD cada 30 segundos; avisos cada 20 segundos. Consultar cada cinco minutos no acelera la publicación de Renfe.
- **Antigüedad:** se considera antiguo un GPS de Cercanías con más de 3 minutos o AV/LD/MD con más de 20. Son umbrales de esta aplicación. Las posiciones antiguas se distinguen en gris y no se cuentan como GPS reciente. Un fallo de fuente también marca sus vehículos como no confirmados.
- Si falta la hora individual del GPS, se usa la hora del conjunto **indicándolo**. No es una garantía de la antigüedad de cada posición individual.
- No se simulan posiciones ni movimiento. Se muestra el estado que publica el operador. Estar en el listado no asegura que el tren esté en marcha en ese instante. Existe un filtro de estado en movimiento y otro de GPS reciente.
- Las entidades de un mismo vehículo se agrupan para evitar duplicados. Si el viaje no coincide exactamente con el catálogo vigente, se informa sin inventar recorrido ni horarios. No se empareja por mera similitud del número.
- La ruta dibujada es una unión **esquemática** de estaciones, no la geometría de la vía. Cada parada diferencia horario programado y previsión en tiempo real cuando existe.
- Las incidencias se filtran por sus periodos de vigencia. La ausencia de avisos no implica normalidad del servicio; no hay un canal nacional completo de todos los operadores integrado.
- Si fallan fuentes individuales, se conservan los últimos datos disponibles en la sesión o en el colector y se avisa. Si todas fallan en la recogida de GitHub Actions, se detiene la publicación para conservar la web anterior.

## Fuentes y atribución

Origen de los datos: **Renfe Operadora**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Proyecto independiente, sin afiliación con Renfe.

- [Ubicación de Cercanías](https://data.renfe.com/dataset/ubicacion-vehiculos)
- [GPS AV, LD y MD](https://data.renfe.com/dataset/posicion-vehiculos-av-ld-md)
- [Horarios de Cercanías y Rodalies](https://data.renfe.com/dataset/horarios-cercanias)
- [Horarios AV, LD y MD](https://data.renfe.com/dataset/horarios-de-alta-velocidad-larga-distancia-y-media-distancia)
- [Incidencias y avisos](https://data.renfe.com/dataset/incidencias-avisos)
- [Cloudflare Wrangler: despliegue](https://developers.cloudflare.com/workers/wrangler/commands/#deploy)

Mapa: [OpenStreetMap](https://www.openstreetmap.org/copyright). Leaflet 1.9.4 incluido localmente con su licencia en `web/vendor/LEAFLET-LICENSE.txt`. Tipografías DM Sans y Manrope desde Google Fonts, con fuentes del sistema como alternativa. Los mapas requieren conexión a los servidores de teselas; los errores de carga no impiden utilizar el listado.

## Comprobaciones realizadas

`npm test` ejecuta pruebas de deduplicación, posiciones ausentes, antigüedad, vigencia de alertas y fallos parciales del intermediario. `node --test` requiere Node.js 20 o posterior. También se comprueba que las entradas del catálogo resuelvan al archivo de horarios correcto y que sus estaciones existan. Algunos viajes del GTFS no contienen paradas; se muestran sin inventarlas. La lógica del Worker se comprueba localmente; no se ha desplegado en Cloudflare.

En la prueba del 6 de noviembre de 2026 se recibieron las cinco fuentes sin error y se asociaron horarios a 591 de 592 vehículos únicos; 113 estaban en líneas Rodalies. Son cifras de esa instantánea, no una promesa de cobertura. Se verificaron en navegador mapa, búsqueda de un R1, descarga de todas sus paradas, previsión publicada, incidencias, botón de actualización y disposición móvil de 390 px sin desbordamiento horizontal.

La publicación remota y el workflow se verificaron correctamente el 6 de noviembre de 2026, incluida la pestaña Notificaciones.

## Notificaciones personales

La pestaña **Notificaciones** permite no recibir ningún aviso (estado inicial) o activar los tipos elegidos: incidencias oficiales nuevas o modificadas, cancelaciones, retrasos a partir de 5/10/15/30 minutos, detenciones observadas en datos nuevos y pérdida de datos recientes. Hay filtros propios por servicio, línea exacta y número exacto de tren, conservando ceros iniciales. Los filtros de esta pestaña son independientes del buscador del mapa.

Las preferencias se guardan en `localStorage` de este navegador y origen. No requieren cuenta ni se envían a un servidor; otros dispositivos no las comparten. Si el almacenamiento está bloqueado, se aplican a la sesión y se informa. El interruptor principal desactiva todos los envíos y sonidos, aunque se conserven las selecciones para una próxima activación. Se puede vaciar el historial de la sesión.

Los avisos aparecen dentro de la web y en el historial, con fecha de origen y detección. Se agrupan las ráfagas para evitar múltiples sonidos. El sonido es opcional y puede necesitar el botón **Probar aviso** tras recargar. Las notificaciones del sistema se solicitan únicamente al pulsar el botón específico y necesitan permiso del navegador. Se usa un service worker limitado a mostrar notificaciones y gestionar sus clics; no almacena ni intercepta los datos de la web.

**La web debe permanecer abierta** para detectar cambios. No se implementa un servidor de Web Push ni avisos con la web cerrada. El navegador, las preferencias del sistema, la suspensión de pestañas y los retrasos de los datos pueden impedir o demorar el aviso. Documentación técnica: [permiso de notificaciones](https://developer.mozilla.org/en-US/docs/Web/API/Notification/requestPermission_static) y [notificaciones con service worker](https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification).

El motor toma una referencia inicial al activar o modificar preferencias y no reproduce incidencias anteriores. Solo compara cancelaciones y retrasos cuando hay datos recientes y marcas de origen que avanzan. Deduplica los avisos oficiales por identificador y contenido; no interpreta la desaparición de un aviso como uno nuevo. Los avisos filtrados por tren pueden corresponder a su línea o estación publicada, y no siempre a ese tren exclusivamente. No se envían avisos oficiales sin relación comprobable con un filtro.

Una **detención observada** requiere el estado `STOPPED_AT`, coordenadas próximas, la misma parada y viaje, y horas GPS individuales nuevas y recientes. El umbral mide la separación entre observaciones de ese estado, no prueba que estuviera parado continuamente entre ellas. Una posición congelada, la mera hora del conjunto o la pérdida de datos no generan una detención. Se restablece el seguimiento de parada ante movimiento, cambio de estación, viaje o posición, o una separación excesiva entre observaciones. La aplicación no evalúa peligros ni sustituye los sistemas de seguridad ferroviaria.

Se añadieron pruebas de desactivación total, primera carga sin avalancha, filtros, guardado inválido, cancelaciones, retrasos, avisos oficiales modificados, falta de datos, detenciones con nuevas marcas de GPS y exclusión de GPS congelado. Total: **19 pruebas automatizadas**, además de la revisión de interfaz en ordenador y móvil. La entrega real al sistema operativo queda sujeta al permiso y compatibilidad del navegador del visitante.
