# Reto Visual 70

Retos visuales originales para @retovisual70. Repositorio independiente del proyecto YouTube.

El Piloto 001 «¿Qué objeto desapareció?» tiene tres rondas de 4/6/8 objetos, soluciones completas y duración de 70 segundos, 1080 × 1920, 30 FPS, MP4/H.264. Sin avatar, voz ni música. No hay código de publicación ni programación automática.

## Generar localmente

Requisitos: Python 3.12, FFmpeg y FFprobe en PATH, con libx264. El render usa CPU, dos hilos de codificación y fotogramas secuenciales enviados por pipe; no guarda miles de imágenes.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/pilot.py --previews
.\.venv\Scripts\python.exe scripts/pilot.py --seconds 10
.\.venv\Scripts\python.exe scripts/pilot.py --seconds 70
```

En Linux usar `.venv/bin/python`. Las fuentes Barlow y su licencia están incluidas. No se necesitan credenciales, API de pago ni conexión para renderizar después de instalar dependencias.

Las salidas quedan en `output/piloto-001-v1/`, excluidas de Git. Cada video tiene un JSON con SHA-256, versiones, métricas y validación con FFprobe. Se comprueba duración, cantidad de fotogramas, resolución, FPS, H.264, formato de píxeles, ausencia de audio y decodificación completa. No se sobrescriben videos existentes; para una revisión utilizar otra carpeta con `--output output/piloto-001-v2`.

## Estado y límites

- Prueba A de infraestructura GitHub: aprobada en https://github.com/estebansanchezoficial/reto-visual-70/actions/runs/40980086865.
- El workflow A permanece exclusivamente manual y no genera contenido. Este cambio no lo modifica ni ejecuta otra A.
- Las pruebas de video son locales. Sus mediciones no equivalen a mediciones de GitHub Actions.
- Ver `docs/PLAN-PILOTO-001.md` para guion, controles, texto propuesto, revisión y próximos temas.
- Ver `assets/PROVENANCE.md` y `assets/fonts/OFL.txt` para recursos y licencia.
- Un video generado queda pendiente de revisión del usuario. Solo la aprobación del MP4 concreto autoriza su publicación.
- Creator Rewards y la elegibilidad de este formato/cuenta siguen pendientes de comprobación; no se prometen ingresos.
