# Paladín Meshy — transformación élite V2

Versión creada localmente en Blender el 2026-10-14 desde la copia editable
`../Work/Paladin_Meshy_Elite_Edit.blend`. No sustituye la fuente de Downloads,
la copia GLB archivada ni la primera edición.

## Cambios

- Postura estática con brazos bajos, derivada de la malla original.
- Mayor volumen del peto, casco y grebas; collar original ajustado bajo la tela.
- Dos hombreras de casquete achatado y seis láminas solapadas.
- Bordes de latón, remaches, relieve vegetal discreto y broches de capa.
- Capa larga con pliegues, borde roto, cuello recogido y faldones frontales.
- Texturas nuevas creadas localmente; los tres mapas PBR originales se conservan.

## Archivos

- `Paladin_Meshy_Elite_V2.blend`: fuente editable, curvas y espesores conservados.
- `Paladin_Meshy_Elite_V2.glb`: geometría evaluada con imágenes incrustadas.
- `TresCuartos.png`, `Frente.png`, `Espalda.png`, `Detalle.png`: renders de Blender.
- `validation_v2.json`: validación de la exportación por reimportación.

## Edición

La malla `Paladin_Meshy_Copia_Editable` conserva sus vértices, caras y UV.
El control `05_Elite_volumen_y_postura` contiene la mezcla de la primera pasada
más las proporciones y postura nuevas. Su valor de trabajo es 1; los controles
01–04 se conservan con valor 0. No activarlos simultáneamente a 1 porque sus
deformaciones se sumarían dos veces. Con todos los controles en 0 se recupera
la malla normalizada de la fuente; las piezas nuevas se ocultan por colección.

Las nuevas piezas están organizadas en `02_Elite_Placas_Adicionales`,
`03_Elite_Bordes_y_Cierres` y `04_Elite_Capa_y_Cuello`. El estudio está aparte.
Las piezas añadidas están ajustadas a la postura de presentación; no siguen
automáticamente el control de postura del cuerpo.

Es una versión de presentación estática. No contiene esqueleto ni animaciones;
requiere revisión artística, ajuste de articulaciones, retopología y skinning
antes de su integración definitiva en el juego. La atribución CC BY 4.0 del
modelo base se mantiene según el registro del proyecto.

## Validación técnica

El GLB se reimporta en una escena vacía y se comprueba el recuento de
triángulos frente a las mallas evaluadas, coordenadas finitas, materiales,
imágenes y ausencia de cámaras, luces o referencias externas. Los hashes
verifican que Downloads, la copia archivada y el Blender de la primera pasada
no se modificaron, y que los tres mapas de la fuente sobreviven a la exportación
sin cambios de bytes. Los hashes de UV y conectividad del cuerpo también se
conservan. Esto no sustituye la revisión de deformaciones en animación.

## Reproducir

Desde la raíz del proyecto, ejecutar Blender con
`--background --python-exit-code 1 --python Tools/Blender/advance_paladin_direct_v2.py`.
El script lee la primera edición y regenera los archivos de esta carpeta.
Para conservar cambios manuales posteriores, trabajar sobre el `.blend` sin
volver a ejecutar el generador encima de esa versión.
