# Edición directa de la copia del paladín Meshy

**Versión activa: [V3](V3/README.md)**. Continúa la V2 con aberturas del visor,
respiraderos, guanteletes, cinturón y correcciones de encaje y materiales.
Los archivos descritos abajo corresponden a la primera pasada conservada.

Creada el 2026-10-14 por petición del usuario. Esta línea de trabajo parte
directamente del GLB adjuntado y modifica sus vértices conservando su diseño,
UV, conectividad y materiales. Las bases grises anteriores quedan separadas.

## Archivos

- `Source/Paladin_Meshy_Original_Copy.glb`: copia exacta, byte por byte, del
  archivo de Downloads. Se conserva como fuente intacta.
- `Work/Paladin_Meshy_Elite_Edit.blend`: copia de trabajo en Blender, con los
  primeros ajustes activos y los tres mapas PBR incrustados.
- `Exports/Paladin_Meshy_Elite_Edit.glb`: exportación de la forma modificada,
  sin luces, cámaras ni dependencias de archivos externos.
- `Preview/`: tres vistas de la edición y una vista del original normalizado
  con la misma cámara e iluminación para comparar proporciones.
- `validation_direct_edit.json`: hashes y comprobaciones de la entrega.

## Primera pasada de modificación

Se normalizó la copia de trabajo a 2,08 m y se apoyó en el suelo. El diseño
permanece en la pose T de la fuente. Las modificaciones son proporcionales y
graduales; no se cortaron piezas ni se reconstruyó la armadura con primitivas.

En las propiedades de datos de la malla hay cuatro controles de forma
(shape keys), con valor inicial 1 y máximo 1,5:

1. `01_Peto_y_cintura`: peto un poco más ancho y profundo, cintura afinada.
2. `02_Hombros_y_brazales`: volumen y posición de hombros; sección de brazos.
3. `03_Volumen_grebas`: más volumen en las pantorrillas, manteniendo los pies.
4. `04_Ancho_casco`: casco ligeramente más ancho, con transición al cuello.

Al poner los cuatro valores en 0 se recupera la forma original normalizada.
La base `00_Original_normalizado` permanece intacta. Esta es una primera pasada
conservadora de proporciones; el diseño todavía corresponde al paladín normal.

## Comprobaciones

- Original de Downloads y copia archivada: mismo SHA256
  `b5c989fcf237ea182162e3967ca5462bbaad413947f7cbc09dfefeaf3d87b421`.
- 104.517 vértices editables y 180.540 triángulos conservados.
- Hashes de UV y conectividad idénticos antes y después.
- 72.708 vértices desplazados; desplazamiento máximo aproximado de 24 mm.
- GLB reimportado: una malla, geometría coincidente y tres mapas PBR cuyos
  archivos incrustados mantienen los mismos hashes de la fuente.
- Vistas frontal, posterior y tres cuartos revisadas. Los cambios de volumen
  son sutiles; no se observaron nuevas roturas ni estiramientos evidentes.

La malla sigue estática y sin rig. El trabajo posterior debe revisar también
las articulaciones en movimiento y preparar retopología, skinning y animación
antes de integrarla como personaje definitivo. La licencia CC BY 4.0 se
conserva según el registro del recurso original en el proyecto.

## Reproducir

Desde la raíz del proyecto:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\edit_paladin_meshy_copy.py'
```

El script lee la copia archivada y escribe los archivos de trabajo y exportación
en esta carpeta. Para continuar una edición manual, abrir el `.blend` guardado;
volver a ejecutar el generador reproduce la primera pasada.
