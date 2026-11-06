# Cómo colaborar en Vía

Gracias por ayudar a mejorar la información ferroviaria disponible para todos. El proyecto se ha desarrollado con ayuda de Codex y acepta propuestas tanto de personas que programan como de quienes utilizan la web.

## Ideas y errores, sin programar

Abre una [issue en el repositorio original](https://github.com/w2xkqy9yrz-maker/trenes-tiempo-real/issues/new). Incluye:

- Qué ocurre o qué te gustaría mejorar.
- Cómo reproducir el problema y qué esperabas ver.
- Navegador y dispositivo; fecha, hora y tren o línea si son relevantes.
- Capturas sin datos personales, contraseñas ni tokens.

Un dato antiguo o ausente puede proceder del operador. Incluye la hora de origen que muestra la web para ayudar a distinguirlo de un error de la aplicación.

## Proponer un cambio de código

1. Crea un **fork** del repositorio y clona tu copia.
2. Crea una rama con un nombre descriptivo, por ejemplo `mejora-buscador`.
3. Consulta el [README](README.md) y la [guía técnica](docs/GUIA_TECNICA.md) para ejecutar el proyecto.
4. Implementa una mejora concreta por propuesta. Evita mezclar cambios de diseño, datos y configuración sin relación entre sí.
5. Comprueba el resultado en ordenador y móvil si modificas la interfaz. Ejecuta `npm test` si cambias lógica, e incluye pruebas de los casos relevantes.
6. Sube la rama a tu fork y abre una pull request con destino a **`w2xkqy9yrz-maker/trenes-tiempo-real`, rama `main`**.

En la descripción de la pull request, cuenta qué problema resuelve, qué cambia y cómo lo has probado. Añade capturas para cambios visuales y documenta las limitaciones o requisitos nuevos. Si utilizas Codex u otra herramienta de IA, puedes indicarlo; revisa el código y comprueba que las afirmaciones y resultados sean correctos antes de enviarlo.

## Criterios para los cambios

- Mantén la interfaz comprensible, accesible y en español; documenta cualquier ampliación de idiomas.
- No presentes como actuales posiciones antiguas ni conviertas un fallo de datos en una incidencia confirmada.
- Si añades un operador o una fuente, enlaza su documentación oficial e indica cobertura, frecuencia, condiciones de uso y necesidad de credenciales.
- Conserva la opción de **no recibir ninguna notificación**. No solicites permisos del navegador automáticamente.
- No subas contraseñas, tokens, `.cache/`, `node_modules/` ni cambios masivos en los datos generados ajenos a la propuesta.
- Conserva las atribuciones de Renfe, Leaflet, OpenStreetMap y cualquier otra fuente utilizada.

## Revisión e incorporación a la web

El responsable revisa las pull requests, puede solicitar ajustes y decide cuáles incorporar. La aceptación no está garantizada y no hay un plazo de respuesta comprometido.

Un fork o una pull request **no modifican por sí mismos la web original**. Tras la revisión y la integración en `main`, GitHub Actions prepara y publica la versión. La actualización solo estará disponible cuando el despliegue termine correctamente. Las ideas presentadas en issues pueden dar lugar a cambios posteriores, pero no ejecutan cambios automáticos.
