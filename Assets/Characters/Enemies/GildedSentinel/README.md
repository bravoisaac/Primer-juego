# Gilded Sentinel · enemigo de Unity

Fuente: `Meshy_AI_Gilded_Sentinel_1012232218_texture.glb`, facilitada por el usuario. La copia `Source/GildedSentinel_Original.glb` conserva los bytes del archivo de Downloads. Su SHA256 coincide con la fuente histórica del Paladín:

`b5c989fcf237ea182162e3967ca5462bbaad413947f7cbc09dfefeaf3d87b421`

La fuente tiene 180.540 triángulos, tres texturas de 2048 px, una malla y ningún esqueleto ni animación. La licencia CC BY 4.0 figura en `../Paladin/README.md`, correspondiente al mismo archivo verificado por hash.

## Copia preparada

- `Source/GildedSentinel_Rigged.blend`: archivo editable con rig, pesos, espada y acciones.
- `validation.json`: recuentos, cobertura de pesos, acciones y huella de fuente.
- `Preview/`: renders de poses para revisar deformaciones.
- `Tools/Blender/rig_gilded_sentinel.py`, desde la raíz del repositorio: preparación reproducible.
- `Unity/TenFe/Assets/Art/GildedSentinel`: FBX, texturas, material, Animator y prefab utilizados por el juego.


Animaciones originales de esta adaptación: Idle, Walk, Run, Windup, Strike, Hit y Death. Se exportan dentro del FBX como clips independientes. El movimiento del actor lo controla `EnemyBrain`; Animator solo deforma la presentación. El golpe se aplica al 14 % de Strike, después de la anticipación. Los enemigos comunes y el paladín resistente usan este modelo; Aster conserva su silueta provisional.

## Reproducir la integración

1. Ejecutar Blender 5.2 en segundo plano con `--python Tools/Blender/rig_gilded_sentinel.py`.
2. En Unity, usar `Ten Fe > Integrar centinela animado`: configura materiales y clips y conecta los guardianes de la escena guardada, sin reconstruir el nivel.
3. Usar `Ten Fe > Compilar Windows` y ejecutar `Validar.ps1` con el editor cerrado para repetir las comprobaciones.

El instalador también conserva esta integración si se reconstruye expresamente el santuario mediante el menú del proyecto. Reconstruir la escena sí reemplaza sus cambios manuales, como advierte el diálogo existente.

## Límites

Es un rig funcional de prototipo con pesos anatómicos aproximados y animaciones creadas localmente, sin captura de movimiento ni rig individual de dedos. Hombros, axilas, faldones, agarre de espada y contacto de pies requieren refinamiento artístico. No hay simulación de tela ni LOD. La fuente original y los demás modelos del Paladín permanecen intactos. No se utilizaron compras ni servicios remotos.
