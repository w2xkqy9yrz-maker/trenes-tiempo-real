# 🚆 Trenes España en Tiempo Real

**Mapa interactivo para explorar la circulación ferroviaria en España.** Una web pública, gratuita y adaptable a móviles, creada para consultar trenes y recorridos desde el navegador.

🌐 **[Abrir el mapa de trenes](https://w2xkqy9yrz-maker.github.io/trenes-tiempo-real/)**

> **Estado del proyecto:** en desarrollo y validación. La disponibilidad, precisión y frecuencia de actualización de los datos dependen de los servicios externos. La web no es un servicio oficial de Renfe ni de Adif.

## 🗺️ Funcionalidades

- Mapa interactivo de España con diseño oscuro.
- Consulta de trenes proporcionados por una fuente externa de información ferroviaria.
- Búsqueda por tren, origen o destino y filtros por categoría, según los datos disponibles.
- Selección de trenes para consultar su información y, cuando la fuente lo permite, sus paradas y recorrido.
- Actualización periódica de los datos y avisos sobre el estado de la conexión.
- Interfaz adaptada a ordenador, tableta y móvil.

**Importante:** no todos los servicios ferroviarios tienen necesariamente cobertura. Las posiciones pueden ser observadas o estimadas según la fuente; las velocidades, retrasos y horarios solo deben considerarse disponibles cuando el proveedor los facilite. Una posición mostrada en el mapa no garantiza seguimiento GPS directo.

## 🧰 Tecnologías

| Tecnología | Uso |
| --- | --- |
| HTML, CSS y JavaScript | Interfaz y lógica de la aplicación |
| [Leaflet](https://leafletjs.com/) | Mapa interactivo |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Cartografía base |
| [RadarDeTrenes](https://radardetrenes.com/docs) | API externa de información ferroviaria |
| GitHub Pages | Alojamiento estático de la web |

## 🚀 Cómo utilizar la web

1. Abre el [mapa público](https://w2xkqy9yrz-maker.github.io/trenes-tiempo-real/).
2. Espera a que se carguen los datos disponibles.
3. Utiliza los filtros o el buscador para encontrar un servicio.
4. Selecciona un tren para consultar los detalles que proporcione la fuente.
5. Comprueba el estado de conexión y la última actualización antes de interpretar su posición.

## 💻 Ejecutar el proyecto

No requiere instalación ni compilación. Basta con abrir `index.html` en un navegador moderno. Para probar llamadas a servicios externos en un entorno local, puede ser preferible servir la carpeta mediante un servidor HTTP local.

Para publicarlo en GitHub Pages, activa **Settings → Pages → Deploy from a branch**, selecciona `main` y la carpeta `/ (root)`.

## 🔎 Fuentes y limitaciones

La aplicación consulta un servicio externo y no controla su cobertura, continuidad, límites de uso ni exactitud. Puede haber trenes ausentes, posiciones aproximadas o información desactualizada. Las incidencias y horarios oficiales deben contrastarse con los canales de los operadores.

- [Renfe](https://www.renfe.com/)
- [Adif](https://www.adif.es/)
- [Documentación de RadarDeTrenes](https://radardetrenes.com/docs)

Los nombres de operadores se utilizan con fines descriptivos. Este proyecto es independiente y no está afiliado oficialmente a ellos.

## 🛠️ Próximas mejoras

- [ ] Verificar la cobertura real de cada categoría de tren.
- [ ] Mejorar la visualización de recorridos y paradas.
- [ ] Añadir favoritos y opciones de accesibilidad.
- [ ] Incorporar avisos de incidencias verificadas, si existe una fuente compatible.
- [ ] Optimizar rendimiento y experiencia móvil.

## 🤝 Contribuciones

Puedes proponer mejoras o comunicar errores mediante las **Issues** del repositorio.

---

**Proyecto independiente de visualización ferroviaria.** No utilizar como única fuente para tomar decisiones de viaje.
