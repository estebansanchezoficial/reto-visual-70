# Catálogo de ejercicios y control de repeticiones

Versión 1, 2 de noviembre de 2026. 30 selecciones de tres niveles (90 ejercicios), repartidas entre diez temas matemáticos. El PDF es una copia legible del JSON que consume la producción; no se extrae contenido de un PDF distinto en cada ejecución.

Primera entrega del catálogo comprobada: video 006 v4, paquete `algebra-01`, listo para revisión en [Issue 6](https://github.com/estebansanchezoficial/reto-visual-70/issues/6). [Producción y QA en nube: SUCCESS](https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41506993233). MP4 de 3.186.601 bytes, SHA-256 `2101eae722368e62de4eeb989c00f94675326eeb529a3dc208601d72404ab5fc`, 70 segundos, tres soluciones de cinco segundos. Comparado contra diez planes históricos. Descarga final verificada; pendiente de aprobación, sin programación ni publicación. La v3 anterior quedó sustituida.

41 pruebas locales completas pasaron; las pruebas de selección/catálogo también pasaron en el runner Linux antes de producir. El primer intento `41506679658` falló antes de generar/reservar v4 por una referencia de borrador alterada al editar metadatos. Se restauró la etiqueta conservando su ID/archivos y se revisó el estado antes de lanzar `41506993233`; no hubo intento de transporte a Buffer. El aviso de fallo Issue 7 quedó cerrado tras verificar la entrega correcta.

[Abrir o descargar el catálogo con soluciones](catalogo-acertijos-v1.pdf)

Los planteamientos, parámetros y explicaciones son originales. El libro *Amusements in Mathematics*, de Dudeney, se consultó como referencia temática, sin copiar textos, traducciones ni dibujos. No se afirma licencia mexicana de una edición externa. Los niveles son relativos por tema y no certifican cobertura de un programa escolar: incluyen fundamentos de secundaria y preparatoria.

## Producción

- Selecciona un paquete no usado, con básico, intermedio y avanzado.
- Alterna temas evitando los últimos cinco registros de revisión y la dinámica rechazada.
- Compara cada ejercicio con **todos** los planes históricos, incluyendo versiones rechazadas/sustituidas. No basta un hash nuevo del video o un cambio de orden/opciones/ID.
- Resuelve con aritmética exacta y valida opciones, respuesta y texto antes del render.
- Presenta cada solución durante cinco segundos al final de su nivel, con resultado narrado y explicación en pantalla.
- Conserva avatar, voz, música autorizada y aviso de IA. Cada nuevo MP4 necesita aprobación de su propio SHA-256.
- El catálogo es finito. Al agotarse o no encontrar un tema distinto, se detiene y avisa; no recicla ni inventa ejercicios sin revisar. Las correcciones consumen selecciones, por lo que 30 selecciones no garantizan 30 días.

Los cambios fuera del catálogo matemático requieren intervención. Pedir otro tema no debe producir una falsa confirmación. El control impide repetir ejercicios exactos definidos por sus parámetros; la variedad conceptual y dificultad siguen sujetas a revisión humana. Tres variantes de un tema pueden compartir técnica, separadas por otros temas.

## Archivos y pruebas

- `daily/puzzle-catalog.json`: contenido original, IDs, niveles, parámetros, opciones y explicaciones.
- `daily/catalog.py`: resolución exacta, validación, selección finita y firma por ejercicio.
- `scripts/build_puzzle_catalog.py`: autoría reproducible del catálogo.
- `scripts/export_catalog_pdf.py`: exportación opcional con ReportLab.
- `tests/test_catalog.py`: comprobación de respuestas, probabilidades por enumeración, combinatoria, versiones rechazadas, IDs modificados y nivel matemático solicitado.

La selección matemática reemplaza la rotación automática de colores/vocales/cálculos sencillos/patrones. Los formatos antiguos siguen siendo legibles para comparar el historial.
