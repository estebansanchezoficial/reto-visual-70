# Operación diaria en nube y publicación tras aprobar

Estado del 1 noviembre2026: Buffer Free conectado exclusivamente a @retovisual70, correo verificado y clave en GitHub Secrets. RV70_BUFFER_ENABLED=true habilita el envío condicionado a aprobación. Presupuesto adicional0MXN. YouTube y sus tareas permanecen separados.

## Revisión desde el teléfono

1. Producción08:07 y aviso09:00, Ciudad de México. GitHub cron y el push pueden retrasarse. Configurada una entrega diaria; otra entrega pendiente bloquea nueva generación.
2. Abre reviews/video-NNN.md desde el aviso y mira el MP4 completo. Descarga privada mediante login de GitHub; Chrome/Safari debe tener sesión de estebansanchezoficial, aunque GitHub Mobile ya esté conectado. Una descarga en PC no prueba acceso móvil.
3. Comenta APROBAR y el SHA-256 completo del archivo vigente. Solo se acepta al propietario. La revisión técnica no sustituye tu revisión del video.
4. revision-movil.yml inicia buffer-programar.yml. Comprueba comentario vigente, vuelve a descargar y verificar hash, reserva el envío y programa una sola vez para19:00 America/Mexico_City de la fecha propuesta. Si quedan menos de15min, se detiene para acordar otra fecha; no cambia fechas automáticamente.
5. Recibirás confirmación con ID y fecha solo después de releer Buffer. Programado no significa publicado. buffer-reconciliar.yml consulta19:25y20:25CDMX, cron best effort, sin reenviar. Solo avisa cambios accionables.

## Archivos, música y permisos

70s,1080×1920,30FPS,H.264/AAC, Alex y avatar aprobados. Comparación de dinámicas y acertijos canónicos con historial registrado; no es una consulta en vivo de todo TikTok. QA incluye imágenes, voz, respuestas y descarga por SHA.

Cipher — Kevin MacLeod, CC BY4.0, crédito obligatorio en descripción. -24dB durante voz y -20dB en pausas largas; rampas0.35s y fundidos1/2s. No añadir otra pista nativa encima. metadata.tiktok.isAiGenerated=true obligatorio.

Las revisiones siguen en releases privados y la página estable solo contiene metadatos/enlaces. Después de aprobar se distribuye una copia pública del MP4 final en otro release rv70-publish-SHA, porque Buffer necesita una URL estable sin autenticación. No convertir el borrador de revisión en público.

BUFFER_API_KEY vence1nov2027 y solo tiene account:read/posts:read/posts:write. No poner claves en código, logs o chat. La autorización TikTok más amplia fue concedida por el propietario; nuestra clave no gestiona comentarios ni analíticas.

## Estados y correcciones

READY_FOR_REVIEW → APPROVED_PENDING_TIKTOK → BUFFER_RESERVED → SCHEDULED_VERIFIED_BUFFER. Guardar ID antes de releer. Respuesta ambigua: BUFFER_NEEDS_RECONCILIATION y aviso, sin reintentos de carga. sent con enlace TikTok se registra PUBLISHED_REPORTED_BUFFER: evidencia API, no comprobación visual de TikTok.

Para corregir antes de programar: CORREGIR: [qué cambiar]. Corrígelo y vuelve a notificarme hoy para revisión; no lo programes sin mi aprobación. Invalida aprobación y requiere versión nueva. El corrector automático cambia contenido/dinámica; animación, voz, volumen y encuadre requieren intervención. Una orden CORREGIR no cancela un archivo ya programado: reconciliar/cancelar en Buffer antes de intervenir.

## Evidencia de configuración y límites

35pruebaslocalesPASS. Conexión y pruebas Linux: https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41341309387 . Borrador técnicoMP4/IA/statusdraft: https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41340856575 . Esa prueba no programó ni publicó. Borrador técnico retirado después: https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41357405881 .

Primera programación real comprobada:005v3, SHA de7f410f46eb2088043cc87f1f4fb337545689845abe8fbb933986f30d2a4d55, para2nov2026 a19:00CDMX. Workflow automático SUCCESS https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/41359771979. ID Buffer6ae7c432902c3fb1dec07c14; API y panel confirman una publicación scheduled, archivo/IA/crédito/fecha. Issue5 cerrado. Aún no publicado; comprobar resultado después de la hora. V1/V2superseded. Video004 conserva su programación nativa anterior; no reenviar ninguno.

Fuentes: https://developers.buffer.com/guides/hosting-media · https://developers.buffer.com/guides/posts-and-scheduling.html · https://buffer.com/pricing · https://creativecommons.org/licenses/by/4.0/
