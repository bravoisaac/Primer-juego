# Paladín élite — base V3

La revisión más reciente está en [`../V4/README.md`](../V4/README.md).
Esta V3 se conserva como fuente de esa nueva pasada y versión anterior.

Revisión local en Blender del 2026-10-13, manteniendo la etapa de formas
grises. Las bases anteriores y el modelo ornamentado se conservan.

## Cambios respecto de V2

- Casco con coronación más marcada, ceja en punta y visor con seis respiraderos
  abiertos en la malla, un interior oscuro separado y pivotes simples.
- Hombreras con borde doblado y cuatro placas por brazo construidas sobre un
  mismo eje y perfil para mejorar los solapamientos.
- Rodilleras de superficie convexa continua, sin la forma abultada de rombo.
- Cuello con pliegues asimétricos, capa menos uniforme y faldones con caída
  curva y largos distintos.
- Hebilla funcional lisa y suelas continuas bajo las botas.

Los respiraderos, pivotes, bordes y hebilla son elementos de construcción.
No se han añadido grabados, bordados, medallones ni texturas decorativas.

## Entrega y comprobaciones

- `PaladinElite_Base.blend`: piezas editables y modificadores; vista inicial
  de tres cuartos con materiales grises.
- `PaladinElite_Base.glb`: exportación estática sin cámaras ni luces.
- `PaladinElite_Base_TresCuartos.png`, `PaladinElite_Base_Frente.png`,
  `PaladinElite_Base_Espalda.png` y `PaladinElite_Base_Detalle.png`: vistas de
  estudio Workbench para examinar la geometría, no el acabado PBR final.
- `validation_base.json`: reimportación real del GLB, 166 mallas,
  366.308 triángulos, tres materiales y altura aproximada de 2,16 m.

Se comprobaron UV y materiales presentes, coordenadas finitas, escala,
correspondencia de mallas y ausencia de luces, cámaras y texturas de imagen.
La inspección de vistas sirve para evaluar esta pose; no certifica ausencia
de todas las intersecciones ni funcionamiento de las articulaciones animadas.

Siguen pendientes la aprobación artística de la silueta, el ajuste completo
en una pose de rig, retopología, skinning, animaciones y validación en Unreal.
Es una interpretación en construcción de la referencia, no una reconstrucción
exacta ni un personaje terminado para el juego.

## Reproducir

Desde la raíz del proyecto:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\refine_paladin_elite_base_v3.py'
```

El generador reutiliza etapas y validación de V2, sustituye explícitamente las
piezas revisadas y escribe únicamente en `Base/V3`.
