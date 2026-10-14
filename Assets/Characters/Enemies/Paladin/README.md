# Paladín del Ocaso

Enemigo original de fantasía medieval oscura creado para el prototipo de **Ten Fe**.
La versión 3 usa como base visual detallada un modelo generado en Meshy 6 Lite a
partir de la vista frontal preparada con las referencias del usuario. Conserva el
yelmo cerrado, el peto curvo, las hombreras, las placas solapadas y los faldones.
Es una interpretación propia y no contiene geometría ni texturas extraídas de otro
juego.

## Archivos

- `Source/PaladinSoldier.blend`: escena fuente editable de Blender.
- `Source/PaladinSoldier_Meshy_Source.glb`: descarga original sin modificar de Meshy.
- `Source/PaladinSoldier_Meshy.blend`: escena normalizada y editable de la versión 3.
- `Exports/SM_PaladinSoldier.fbx`: exportación estática para Unreal Engine.
- `Exports/SM_PaladinSoldier_Meshy.fbx`: exportación detallada de la versión 3.
- `Exports/SM_PaladinGreatsword.fbx`: espada separada para el componente de ataque.
- `Preview/PaladinSoldier.png`: vista previa frontal en tres cuartos.
- `Preview/PaladinSoldier_Back.png`: vista previa posterior de la capa.
- `Preview/PaladinSoldier_Meshy.png`: vista previa renderizada de la base Meshy.
- `Preview/PaladinGuardian_Concept.png`: visualización conceptual de la variante
  Guardián equipada con la espada y el escudo de referencia; no es una captura
  del modelo 3D final ni de Unreal.
- `Textures/Meshy/`: mapas Base Color, ORM y Normal de la versión 3.
- `References/`: copias de las tres referencias entregadas por el usuario; también
  están empaquetadas dentro del archivo `.blend`.
- `References/Weapons/`: láminas de espada, escudo, lanza, maza, arco y ballesta
  que definen el conjunto visual de las variantes del enemigo.
- `WEAPON_SET.md`: especificación de variantes, escala, piezas funcionales,
  requisitos técnicos y orden de producción del conjunto.
- `Archive/v1/`: copia recuperable del modelo anterior.
- `validation.json`: informe reproducible de geometría, materiales y escala.
- `validation_meshy.json`: informe de la geometría y los mapas PBR de la versión 3.
- `Tools/Blender/create_paladin_from_references.py`: generador actual del recurso.
- `Tools/Blender/prepare_meshy_paladin.py`: preparación reproducible del GLB detallado.

## Escala y uso

La versión 3 mide 2,0 metros, está orientada con Z hacia arriba y usa una pose T.
Tiene una malla, 104.517 vértices, 180.540 triángulos, un material PBR y tres mapas
de textura. Unreal la carga como `SM_PaladinSoldier_Meshy`, con Nanite activado y el
material `M_Paladin_Meshy_PBR`; la espada sigue separada como
`SM_PaladinGreatsword`.

Esta integración todavía es estática: no contiene rig ni animaciones. Antes de
considerarla un personaje definitivo se necesita retopología, rig, skinning y una
validación manual de escala, orientación y movimiento dentro del nivel.

## Origen y licencia

- Servicio: Meshy 6 Lite, Image to 3D.
- Fecha de generación: 2026-10-12.
- Licencia elegida al generar: CC BY 4.0.
- Fuente visual: referencias proporcionadas por el usuario y recorte frontal
  preparado en `TripoInput/paladin_front.png`.
