# Instrucción permanente para próximos videos matemáticos

Actualizada por petición del propietario el 2 de noviembre de 2026. Aplica a nuevas generaciones; no reemplaza archivos ya aprobados ni publicaciones programadas.

Genera un video matemático con tres niveles: básico, intermedio y avanzado. Selecciona ejercicios nuevos del catálogo, compáralos individualmente con todo el historial, incluidas las versiones rechazadas, y verifica cada respuesta.

En cada nivel sigue este orden:

1. Presenta el ejercicio y las opciones A, B y C; conserva el tiempo para resolverlo.
2. Muestra la respuesta correcta durante cinco segundos y narra el resultado.
3. Añade una sección separada titulada **«Este es el procedimiento»**. Alex presenta la sección en voz; muestra tres pasos numerados, uno a la vez, con una instrucción breve y su operación matemática. Explica cómo se llega al resultado: no basta repetirlo.
4. Mantén cada paso cuatro segundos, doce segundos de procedimiento por nivel. Después continúa al siguiente nivel.

La versión inicial con procedimiento dura **106 segundos**: los 70 segundos del formato anterior más 36 segundos de explicación. No comprimas la voz ni reduzcas el tiempo para resolver el acertijo. Las explicaciones deben ser correctas, legibles dentro del tablero que abraza el avatar y congruentes con la respuesta marcada. El usuario podrá pedir más tiempo de lectura al revisar.

Conserva la composición del avatar, la voz Alex, la música autorizada y su ajuste de volumen durante el habla. Extiende la pista y coloca el fundido de salida al final real del video. Mantén el aviso de contenido creado por IA y el crédito de la música.

Antes de enviar a revisión, comprueba el archivo completo: duración, tres niveles, tres respuestas y nueve pasos de procedimiento, narración sin superposición, música, legibilidad y descarga. Informa la duración real en el aviso. Si falta alguno de estos elementos, bloquea la entrega y avisa.

Cada archivo nuevo necesita **APROBAR y su SHA-256 completo** antes de programarlo. La instrucción no autoriza publicar ni modifica una aprobación anterior.

## Implementación

`daily/procedure.py` construye y verifica las operaciones por tema y añade la sección al plan. `daily/generate.py` la aplica a todos los planes nuevos del catálogo matemático. El renderer y la narración usan la duración del plan; QA comprueba los nueve pasos en el video y la notificación usa la duración verificada. Los planes históricos sin `procedure_version` conservan su duración original.

## Verificación de esta configuración

46 pruebas locales PASS: los 90 ejercicios cuentan con tres pasos legibles, el cronograma separa respuesta/procedimiento/siguiente nivel y los planes históricos no se modifican. Se produjo una prueba local aislada de 106 segundos, 3180 fotogramas, H.264/AAC 1080 × 1920, con voz y música: decodificación completa, tres respuestas y nueve pasos distintos comprobados en los fotogramas reales; música mezclada sin alterar imágenes y sin saturación detectada. Archivo de prueba SHA-256 `f60af8fda93abeb86734c77c94b725e59ebb5d2bbabd5fbdcb7935a3bf52a883`, marcado `PRUEBA TECNICA. NO PUBLICAR`; no se subió ni reservó una entrega ni se llamó a Buffer. La revisión subjetiva se hará en la siguiente entrega diaria, con su propio archivo y hash.
