# Música y publicación después de aprobar

## Decisión vigente — 1 noviembre 2026

## Conexión Buffer comprobada y envío preparado

Cuenta Free $0 sin prueba de pago, canal retovisual70, channelId 6ae78a17e29c69a1712b879a, organización 6ae7877f176d1861e6dbc27a. Correo verificado. Clave exclusiva BUFFER_API_KEY en GitHub Secrets, vence 1 noviembre2027; solo account:read/posts:read/posts:write. Los permisos TikTok adicionales fueron autorizados por el propietario; la clave de nuestra automatización no permite comentarios, analíticas ni cambios de cuenta. No exponer claves en código/logs/chat.

La comprobación de conexión cloud terminó SUCCESS: https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41340559597 . La primera comprobación falló por un campo de consulta no admitido, corregido antes de la ejecución exitosa; no fue un intento de publicación.

La prueba de borrador técnico terminó SUCCESS: https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41340856575 . Fixture de4s con música licenciada; Buffer conserva status draft, isAiGenerated true y URL del MP4. ID 6ae790131e69de2cfc10913e. No programado ni publicado. Esto comprueba creación y lectura de borrador; NO prueba todavía programación/publicación de un video real.

Envío en daily/publish.py, activación controlada por variable RV70_BUFFER_ENABLED. Tras APROBAR sha exacto del propietario, verificar comentario vigente, descargar/verificar paquete, reservar estado antes de cualquier envío, crear una copia pública SOLO del archivo aprobado en release rv70-publish-SHA para que Buffer pueda obtenerlo, verificar descarga pública por SHA, crear UNA publicación customScheduled19:00CDMX con avisoIA y crédito, releer ID/fecha/URL/etiqueta/modo. Ante respuesta ambigua, BUFFER_NEEDS_RECONCILIATION y aviso, sin reintentos de envío. Corregir genera otrohash y requiere aprobación nueva. No se envía si quedan menos15min para19:00; pedir otrafecha.

Los borradores de revisión permanecen privados. La distribución pública del MP4 final empieza después de su aprobación para publicar; no convertir el release privado en público. No usar enlaces firmados que caduquen. La aceptación definitiva del envío programado por esta ruta debe comprobarse en el primer archivo real aprobado.

buffer-reconciliar.yml consulta a19:25y20:25CDMX (cron best effort), nunca reenvía. Solo avisa en cambios accionables; status sent con externalLink se registra PUBLISHED_REPORTED_BUFFER, evidencia API, sin fingir comprobación visual de TikTok. Guardar siempre el ID antes de la relectura. El objetivo y horarios del canal están en7/semana, lunes-domingo19:00MexicoCity.

La primera programación real sigue pendiente de la aprobación de005v3, SHA de7f410f46eb2088043cc87f1f4fb337545689845abe8fbb933986f30d2a4d55. No reutilizar la aprobación del005v1 ni tocar004 programado previamente.

## Antecedente de preparación (estado anterior)

El usuario autorizó una pista gratuita alternativa con licencia comprobable al no acreditarse una fuente autorizada para integrar Inside Algorithm. Se descargó Cipher — Kevin MacLeod, ISRC USUAN1100844, desde el compositor. Su ficha indica CC BY 4.0; archivo y atribución constan en assets/music/license.json. La licencia permite copia y adaptación comercial con crédito, vínculo a la licencia y declaración de cambios. No atribuir esta licencia a la canción anterior.

La generación futura mezcla automáticamente Cipher a -24 dB, entrada 1 s y salida 2 s, después de verificar el máster de voz. Verifica decodificación, duración, imágenes idénticas, presencia de voz y pico sin saturación. El hash final corresponde al MP4 con música. La descripción incorpora el crédito obligatorio. La mezcla necesita revisión subjetiva del propietario; cambiar audio invalida cualquier aprobación del hash anterior.

Buffer Free vuelve a ser una ruta candidata: publicación automática de MP4, API incluida y hasta 10 publicaciones pendientes por canal; se libera un espacio por publicación. Falta iniciar sesión/crear cuenta Free, autorizar exclusivamente @retovisual70, crear/guardar una clave de API en secretos y comprobar la conexión. Su API exige una URL HTTPS pública y estable hasta publicar: los borradores privados GitHub no sirven. Definir una distribución de archivos aprobados antes de habilitar envíos; nunca publicar archivos pendientes de revisión para resolver ese requisito.

La conexión de publicación **no está activa**. APROBAR sigue registrando la decisión, sin enviar a Buffer. Antes de activarla: verificar identidad del canal y plan Free, exacto hash/fecha19:00, aviso IA, crédito, reserva por hash antes del envío, reconciliación ante respuestas ambiguas sin reintento ciego y consulta posterior del estado/URL real. No reutilizar sesiones locales ni depender del equipo encendido. Presupuesto adicional $0 MXN; no tarjeta, prueba de pago ni recarga automática.

Fuentes: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100844 ; https://creativecommons.org/licenses/by/4.0/ ; https://buffer.com/pricing ; https://developers.buffer.com/guides/hosting-media ; https://support.buffer.com/articles/using-tiktok-with-buffer-oGEroY9Of2

## Investigación anterior: música nativa (conservada como antecedente)

Decisión explícita del usuario, 1 noviembre 2026: «Quiero conservar la musica de TikTok pero que todo quede automatizado». Mantener Inside Algorithm — Cool Ember Sync desde la biblioteca nativa, -24 dB, fundidos 1/2 s, voz Alex, etiqueta IA y 19:00 America/Mexico_City. No sustituir por música original, descargar/reutilizar la pista fuera de TikTok, cambiar el tipo de cuenta ni publicar sin revisión exacta. Presupuesto adicional vigente: $0 MXN.

## Estado comprobado

GitHub genera, verifica y notifica. La aprobación guarda APPROVED_PENDING_TIKTOK, pero NO dispara una programación nativa. Video005 (vocales, SHA 7e24550833db3ae7fd31ca2be24c5fa12d68a7b76c75cd8783cf8abe20e229c7) está aprobado para 2 nov 19:00, pendiente de programar. El navegador interno local funcionó para004 y se guardó la música en TikTok; eso no prueba ejecución en nube con el PC apagado.

## Rutas investigadas y límites

- Buffer Free: API disponible y etiqueta IA; no acceso a la biblioteca musical TikTok. No satisface la decisión del usuario. No conectado ni activado; no se crearon claves, distribuciones públicas, cuentas ni gastos. Se descartó la preparación local del adaptador tras la decisión de conservar música nativa.
- Metricool: permite elegir música Top100 para videos solo con cuentas Business. No está comprobado que Inside Algorithm esté en ese catálogo. Su API para unir directamente GitHub con el servicio requiere Advanced/Custom. No cambiar la cuenta ni activar un plan para forzar esta ruta.
- TinyFish: navegador/agent en nube con perfiles; Agent $0.016/paso y Browser $0.002/minuto. No instalado/conectado. Los créditos iniciales o búsquedas gratuitas no prueban una operación diaria gratuita. No utilizar saldo, contratar ni activar recargas sin autorización.
- Browserbase: Free anuncia una hora de navegador y sesiones de hasta 15 minutos; los agentes incluidos son limitados. Puede servir para un piloto de navegación nativa, no para afirmar que alcanza todo el mes sin medición. No conectado; faltan cuenta, API y contexto de navegador autorizado. No contratar un plan de pago ni introducir tarjeta para probar.
- Browserless: Free anuncia 1000 unidades/mes, sesiones de máximo2min y persistencia de sesiones1día. No se probó TikTok. Esos límites pueden impedir una operación diaria fiable. No conectado.

## Piloto que falta realizar, con conexión una sola vez

1. Crear/iniciar sesión en un proveedor de navegador en nube con plan gratuito, sin tarjeta, con límite de gasto0. El usuario completa términos y autorización de cuenta. Guardar claves únicamente en secretos, con el acceso mínimo; no pedirlas en el chat.
2. Crear un contexto exclusivo para @retovisual70 e iniciar sesión allí. La sesión del navegador interno de ChatGPT/Chrome no se transfiere automáticamente. Guardar el contexto en el proveedor, no cookies en el repo público, releases ni logs. Reautenticación/retos de TikTok requieren intervención del propietario; no intentar eludirlos.
3. Prueba primero de solo lectura: perfil exacto, biblioteca y canción/artista/version02:03 disponibles. Después probar UNA carga autorizada, previa comprobación de duplicados. Los archivos se transfieren a la sesión por un mecanismo autorizado, sin publicar borradores ni exponer claves.
4. Reproducir la secuencia observada en Studio: cargar SHA exacto, caption, portada; Inside Algorithm/Cool Ember Sync; -24dB/fundidos1s y2s; guardar y reabrir para verificar; etiqueta IA checked; fecha19:00GMT−6; un solo clic Programar; esperar a que termine de procesar y comprobar fila con ID real y fecha. No asumir éxito por un clic.
5. Medir segundos de sesión, unidades y transferencia. Con una hora mensual, 30 videos requieren en promedio<=2min por sesión, sin contar conexión inicial ni intervenciones. Si no alcanza el límite gratuito, detener: no elevar presupuesto ni fingir sostenibilidad.
6. Solo después de un piloto terminal exitoso, enlazar el comentario APROBAR SHA con un workflow de programación nativa, bajo exclusión mutua. Registrar reserva antes de cargar. Ante resultado ambiguo, reconciliar la lista de TikTok y no repetir automáticamente. Confirmar por notificación con ID/fecha/hora; mantener aprobación ligada a la versión. Activación automática actualmente NO realizada.

## Fuentes primarias consultadas el 1 noviembre2026

- https://support.buffer.com/articles/using-tiktok-with-buffer-oGEroY9Of2
- https://buffer.com/pricing
- https://help.metricool.com/how-to-add-music-to-your-tiktok-posts-from-metricool-kap4e
- https://help.metricool.com/how-to-get-an-endpoint-in-metricool-to-make-api-calls-eclkf
- https://www.tinyfish.ai/pricing
- https://www.browserbase.com/pricing
- https://cloud.browserless.io/pricing
- https://docs.browserless.io/overview/unit-consumption
