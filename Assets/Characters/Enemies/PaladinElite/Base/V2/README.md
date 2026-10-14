# Paladín élite — segunda revisión de formas

La revisión más reciente está en [`../V3/README.md`](../V3/README.md).
Esta V2 se conserva como versión anterior.

Modelado local en Blender, 2026-10-13. Se mantiene la etapa de base gris sin
grabados, bordados ni remaches decorativos. La primera base y el modelo
ornamentado permanecen en sus carpetas originales.

## Cambios geométricos

- Peto reconstruido con relieve central, cintura estrecha y recortes superiores.
- Hombreras inclinadas hacia el brazo y tres placas superiores superpuestas.
- Brazales ajustados al antebrazo, coderas y rodilleras con planos angulares.
- Musleras, escarceles con punta y grebas con volumen de pantorrilla y tobillo.
- Casco con planos de mejilla, ceja inclinada y abertura ocular estrecha.
- Botas con tres placas de empeine y capa con pliegues desde los hombros.

## Archivos

- `PaladinElite_Base.blend`: fuente editable con piezas y modificadores.
- `PaladinElite_Base.glb`: exportación estática sin el estudio.
- `PaladinElite_Base_TresCuartos.png`, `PaladinElite_Base_Frente.png` y
  `PaladinElite_Base_Espalda.png`: vistas del modelo renderizadas en Blender.
- `validation_base.json`: resultados de reimportación del GLB.

La validación comprueba correspondencia de mallas, UV, materiales, coordenadas
finitas y escala, además de excluir luces, cámaras y texturas de imagen. No
certifica ausencia de todas las intersecciones ni preparación para animación.

Resultado: 150 mallas, 331.296 triángulos y dimensiones aproximadas de
1,055 × 0,625 × 2,145 m. Tres materiales grises, cero texturas de imagen.

Las vistas de esta revisión usan Workbench con iluminación de estudio y
resaltado de cavidades para revisar contornos; no representan el acabado PBR.

Es un estudio estático para evaluar formas. Quedan pendientes aprobación de
silueta, ajuste de articulaciones en una pose de rig, retopología, skinning,
animaciones y validación en Unreal. No está integrado en el juego.

## Reproducir

Desde la raíz del proyecto:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\refine_paladin_elite_base.py'
```

El script utiliza las funciones de la base anterior y escribe exclusivamente
esta revisión en `Base/V2`.
