# Resultado de producción local — 29 de octubre de 2026

Estado: GENERADO, VALIDADO TÉCNICAMENTE, PENDIENTE DE REVISIÓN EDITORIAL Y APROBACIÓN DE PUBLICACIÓN.

El usuario solicitó avanzar con todo lo necesario para iniciar el contenido publicable. Se realizaron el fragmento B y el piloto C localmente en Windows. No se ejecutaron nuevos workflows GitHub ni se modificó la prueba A. No se publicó contenido.

## Mediciones reales

| Métrica | B, 10 segundos | C, piloto de 70 segundos |
|---|---:|---:|
| Fotogramas | 300 | 2100 |
| Render de Python + FFmpeg | 10.984 s | 70.579 s |
| Suma RSS máxima muestreada | 300408832 bytes | 398225408 bytes |
| Tamaño MP4 | 141590 bytes | 847050 bytes |

Entorno: Windows local, Python 3.12, Pillow 12.0.0, FFmpeg/FFprobe 9.0.2 de Gyan ya instalados. Son versiones diferentes de las verificadas en GitHub Actions. Los JSON locales registran la versión y los datos de FFprobe completos.

SHA-256 del piloto exacto: `04745a5ac9160588c8a5f33f93ed08d7ee3af4afb20e3b94b2413e6e5a0b04f3`.

SHA-256 de B: `c60f874c32304bfa53e4d4cc706bf224c738d9e94607b555598d15b32050988a`.

La suma RSS incluye Python y sus hijos, muestreada cada 100 ms; puede contar páginas compartidas más de una vez y omitir picos breves. Excluye la verificación posterior. No equivale al pico exacto de RAM física del sistema. En ambos renders quedó por debajo de la meta de 2 GiB. La carpeta de salida completa antes de agregar texto de publicación ocupó 2249363 bytes, por debajo de 1 GiB. El render completo quedó por debajo de 15 minutos. No se midió esta producción en GitHub.

## Comprobaciones

- Cuatro pruebas unitarias correctas: límites y duración de escenas, única respuesta retirada, ocultación completa del tablero y restauración de la solución.
- FFprobe contó todos los fotogramas y verificó 1080 × 1920, 30 FPS, H.264, yuv420p, duración exacta y un único stream de video sin audio.
- FFmpeg decodificó ambos MP4 completos sin errores.
- Se extrajeron 14 fotogramas del MP4 final, cubriendo todas las fases y las tres respuestas; se compararon contra el diseño. Máximo error RGB medio: 1.4097/255, por compresión y conversión de color.
- Se inspeccionó visualmente la hoja de contacto extraída del MP4 final. Sin desbordamientos de texto observados; 4/6/8 objetos iniciales y las tres soluciones visibles.
- No se vio el video completo en reproducción humana continua ni se comprobó la previsualización de TikTok. Esa revisión de legibilidad, ritmo y overlays sigue pendiente antes de publicar.
- Tipografía Barlow con SIL OFL 1.1 conservada; figuras originales del código. No se utilizó la voz de referencia ni música.

## Entrega local

Carpeta: `output/piloto-001-v1/`.

- `piloto-001-v1.mp4`: archivo exacto para revisión.
- `portada-001.jpg`: portada vertical.
- `piloto-001-v1.json`: hash, versiones, métricas, escenas y FFprobe.
- `prueba-b-10s.mp4` y `.json`: validación inicial.
- `revision-video.jpg` y `.json`: fotogramas extraídos y resultados de comparación.
- `PUBLICACION.txt`: texto listo para copiar, sin envío realizado.

Los binarios de salida no se suben al repositorio público; el código, las fuentes con licencia y los documentos permiten reproducirlos. La carpeta output y el entorno .venv están excluidos de Git.

Presupuesto adicional utilizado en servicios de producción: $0 MXN. Render local con herramientas disponibles; sin API de pago ni almacenamiento en Actions. Esto no constituye medición del costo eléctrico local.

Pendiente final: revisión del piloto concreto por el usuario y aprobación de publicación asociada a su SHA-256; verificar cuenta @retovisual70 y vista previa de TikTok al publicar. No hay integración de TikTok, automatización recurrente, publicación o programación. La elegibilidad de Creator Rewards sigue pendiente y este piloto no acredita monetización.
