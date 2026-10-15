# Paladín élite — edición directa V3

Continuación local en Blender de `../V2/Paladin_Meshy_Elite_V2.blend`, creada
el 2026-10-14. El modelo original y las versiones anteriores se conservan.

## Cambios de esta pasada

- Dos aberturas reales para los ojos y doce respiraderos en el casco original.
- Interior oscuro del visor, rebordes, pivotes y nervio central.
- Puños acampanados, dos placas dorsales y 22 pequeñas placas sobre los dedos.
- Cinturón ajustado a la superficie del cuerpo, costuras y hebilla con aguja.
- Crestas posteriores del cuello plegadas bajo la tela.
- Acabado menos brillante y más irregular en los metales añadidos; tela algo
  más oscura. Los tres mapas originales del modelo Meshy no se retocan.

## Archivos

- `Paladin_Meshy_Elite_V3.blend`: fuente editable, con controles y modificadores.
- `Paladin_Meshy_Elite_V3.glb`: modelo con geometría evaluada y mapas incrustados.
- `TresCuartos.png`, `Frente.png`, `Espalda.png`, `Casco.png`, `Guantelete.png`:
  renders de la geometría real de Blender.
- `validation_v3.json`: comprobaciones de esta entrega.

## Cómo editar

La malla original conserva sus datos de vértices, conectividad y UV. El control
`06_V3_Cuello_y_ajustes` contiene la forma de la V2 y la corrección del cuello;
su valor es 1 y los controles 01–05 están a cero. Evitar sumarlos a la vez,
porque los controles nuevos ya incluyen las deformaciones anteriores.

El modificador `V3_Aberturas_reales_del_visor` corta el casco mediante el objeto
oculto de la colección `91_V3_Herramientas_Visor`. Se puede desactivar para
recuperar la superficie cerrada. El GLB contiene los cortes evaluados, por lo
que su topología sí incorpora los nuevos bordes; el cortador queda excluido.
Un modificador posterior ajusta las normales para el sombreado.

Los añadidos de esta pasada están en `05_V3_Protecciones` y
`06_V3_Cierres_y_Bordes`. Las piezas se ajustan a la postura de presentación;
no siguen automáticamente los controles de forma ni cuentan con articulación.

## Validación y límites

Se comprueban las ranuras de los ojos con rayos sobre la malla evaluada. El GLB
se reimporta en una escena vacía para comparar triángulos, revisar coordenadas
finitas, materiales, imágenes incrustadas y exclusión del estudio y cortadores.
También se verifican los hashes de UV, conectividad de la malla base, archivo
V2 e imágenes originales.

Continúa siendo una versión artística estática: no tiene rig, skinning ni
animaciones. El ajuste durante movimiento, retopología y acabado final siguen
pendientes. Se mantiene la atribución CC BY 4.0 del recurso Meshy según el
registro del proyecto. Las piezas y superficies añadidas se crean localmente.

## Reproducir

Desde la raíz del proyecto, ejecutar Blender con
`--background --python-exit-code 1 --python Tools/Blender/advance_paladin_direct_v3.py`.
El script lee la V2 y regenera esta carpeta. No ejecutarlo sobre modificaciones
manuales posteriores sin guardar primero otra versión de trabajo.
