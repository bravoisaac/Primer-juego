# Paladín de asedio élite — estudio 3D local

Variante de presentación creada el **2026-10-13** en Blender 5.2.2, mediante
modelado paramétrico y materiales propios. No se utilizó un servicio remoto
para generar esta variante. La imagen de cuatro vistas del usuario guía su
armadura, acabado metálico, bufanda marrón y capa desgarrada.

## Qué se ha construido

- Casco facetado nuevo, cresta, visor cerrado, ranura ocular, respiraderos
  representados como detalles oscuros y costillas de latón.
- Peto con nervaduras, cintura articulada, cinturón y hebilla independientes.
- Hombreras de doble borde, remaches y cuatro placas solapadas por brazo.
- Coderas, brazales y guanteletes con dedos y pulgar divididos en piezas.
- Escarcelas, musleras, rodilleras, grebas y escarpes articulados.
- Relieves de acanto y venas modelados como curvas con volumen, además de
  grabado pequeño, desgaste y rayas en los mapas PBR originales.
- Capa con pliegues y desgarros geométricos, patrón de damasco original,
  fibras, costuras, bufanda oscura y faldones asimétricos.

Se reaprovecha la malla texturizada del paladín normal como capa interior
anatómica. Se ensancha el tronco y se bajan los brazos mediante deformación
estática. Se sustituyen el casco y las manos originales. Esta variante es una
interpretación modelada de la referencia, no una reconstrucción exacta ni una
malla creada íntegramente desde cero.

## Archivos de entrega

- `Source/PaladinElite.blend`: fuente editable por colecciones; curvas y
  modificadores conservados, materiales y texturas empaquetados, estudio de luz.
- `Exports/PaladinElite.glb`: modelo con materiales y mapas incrustados,
  sin suelo, luces ni cámaras del estudio.
- `Exports/PaladinElite.fbx`: intercambio de mallas con texturas incrustadas.
- `Textures/`: mapas propios de color, rugosidad y normales, calculados
  localmente. Los mapas del interior heredado se conservan incrustados en
  BLEND y GLB y en la carpeta del paladín normal; no hubo nuevas descargas.
- `Preview/PaladinElite_Front.png`: render frontal en tres cuartos.
- `Preview/PaladinElite_Back.png`: render posterior en tres cuartos.
- `Preview/PaladinElite_Detail.png`: render de casco, cuello y armadura superior.
- `References/PaladinElite_FourViews.png`: copia de la imagen del usuario.
- `validation_elite.json`: recuento y dimensiones del ensamblaje exportado.
- `validation_export.json`: comprobación independiente del contenedor GLB y
  de su reimportación en Blender.

## Edición y reproducción

Abrir `Source/PaladinElite.blend`. Las colecciones separan la base normal,
armadura nueva, grabados y herrajes, tejidos y estudio. El escenario de
iluminación se excluye de las exportaciones del personaje.

Desde la raíz del proyecto en PowerShell:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\create_paladin_elite.py'
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\validate_paladin_elite.py'
```

Añadir `-- --draft` al primer comando produce solo la fuente y una vista
frontal de menor resolución. El generador se apoya en `elite_ornament.py` y
`elite_textiles.py`, ambos dentro de `Tools/Blender/`.

## Estado y límites

Validación final: **correcta**, sin errores ni advertencias. La reimportación
limpia del GLB conserva 3.721.278 triángulos, 923 objetos de malla, 10 materiales
y 17 imágenes incrustadas, sin dependencias externas. Altura: 2,182 m. Se
revisaron los tres renders y se corrigieron la unión de la bufanda y las
extrusiones anómalas que producía el grosor en los desgarros. El archivo Blender
se abre encuadrado, en previsualización de materiales y con piezas editables.

Modelo estático de presentación, con geometría densa y piezas superpuestas.
No tiene esqueleto, pesos, animaciones, colisión ni LOD de juego. No está
preparado como sólido estanco para impresión 3D. El FBX requiere configurar
los materiales en el motor; GLB y BLEND conservan la presentación PBR.

No sustituye al enemigo actual de Unreal. Antes de integrarlo como personaje
animado se debe aprobar el diseño, corregir los ajustes de las piezas en una
pose de rig, retopologizar, crear UV de producción, hornear detalle y hacer rig,
skinning y pruebas de deformación. Las zonas ocultas bajo la capa y los
solapamientos necesitan revisión de producción. El detalle del relieve y del
tejido se aprecia mejor en el render cercano y en la fuente Blender.

## Procedencia

Base: `../Paladin/Source/PaladinSoldier_Meshy_Source.glb`, idéntico por SHA256
al `Meshy_AI_Gilded_Sentinel_1012232218_texture.glb` suministrado. El registro
previo del proyecto identifica esa base como Meshy 6 Lite, 2026-10-12, CC BY 4.0;
se conserva esa procedencia y el requisito de atribución. La variante élite
se ha construido localmente sobre ella sin una nueva generación en Meshy.

Referencia visual: imagen entregada por el usuario. La referencia y la licencia
de la base se conservan por separado; el documento no certifica derechos que
el proyecto aún no haya comprobado.
