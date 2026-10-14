# Paladín élite — base de formas

La revisión activa está en [`V4/README.md`](V4/README.md). Esta carpeta conserva
la primera base para comparación y recuperación.

Creada localmente en Blender el 2026-10-13. El usuario pidió trabajar primero
el modelo base sin tantos adornos, antes de continuar con el acabado detallado.

## Entrega

- `PaladinElite_Base.blend`: piezas editables, modificadores de grosor y estudio.
- `PaladinElite_Base.glb`: modelo estático de intercambio, sin luces ni cámaras.
- `PaladinElite_Base_TresCuartos.png`, `PaladinElite_Base_Frente.png` y
  `PaladinElite_Base_Espalda.png`: renders reales en Cycles para revisar formas.
- `validation_base.json`: comprobación por reimportación del GLB.

## Cambios de esta base

Se conservan y ajustan las placas principales creadas en el estudio anterior.
Se excluyen por completo los grabados, remaches decorativos, medallones,
bordes dorados, costuras ornamentales y materiales con imágenes. Hay tres
materiales grises uniformes para armadura, articulaciones y tejido.

El casco se reconstruye con una calota redondeada y visor simple; las hombreras
se estrechan y aplanan, los brazos se acercan al cuerpo y la cintura se afina.
El interior texturizado del modelo normal se sustituye por volúmenes limpios
de soporte; las botas se reconstruyen con una cubierta ajustada. Capa, bufanda
y faldones son superficies nuevas, sin bordado ni desgarros.

El modelo detallado original permanece intacto en `../Source/PaladinElite.blend`.
Esta base no se ha integrado en Unreal.

## Validación y límites

GLB reimportado correctamente: 152 mallas, 425.504 triángulos, altura aproximada
de 2,15 m, materiales y UV presentes; sin texturas de imagen ni objetos del
estudio. Se revisaron renders frontal, posterior y tres cuartos, corrigiendo
bordes dentados y el ajuste de las cubiertas de las botas.

Es un estudio estático de formas y piezas separadas, no retopología final,
anatomía de personaje desnudo, rig o modelo listo para animar. Todavía hay que
aprobar proporciones y ajustar articulaciones y solapamientos. No añadir
ornamentos hasta validar esta silueta con el usuario.

## Reproducir

Desde la raíz del proyecto:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\create_paladin_elite_base.py'
```

El script reutiliza funciones geométricas de `create_paladin_elite.py` y lee
únicamente la colección de placas del archivo detallado. Toda la salida se
escribe en esta carpeta `Base`.
