# Paladín élite — base V4

Revisión local en Blender del 2026-10-13. Parte del archivo guardado de V3 y
escribe sus resultados aquí, conservando todas las versiones anteriores.

## Cambios

- Placa abdominal superpuesta al peto, con curvatura compartida y borde
  superior; cinturón y hebilla ajustados a esa placa.
- Coderas envolventes con expansión lateral y bordes de grosor definido,
  sustituyendo las piezas abultadas en rombo.
- Puños abiertos de guantelete, dos placas de dorso por mano y protección de
  nudillos; articulaciones interiores de los dedos reducidas para mejorar
  el encaje bajo las placas existentes.
- Cuello con pliegues grandes y pequeñas arrugas, leve ajuste de la caída
  superior de la capa y un gris más oscuro para el tejido.
- Correas laterales del peto y taloneras simples.

Se mantienen materiales grises sin texturas de imagen, grabados, medallones
ni bordados. Los elementos añadidos corresponden a la construcción de las
placas y su ajuste. El tejido usa un material PBR mate; Workbench solo muestra
la geometría y los colores de estudio, no reproduce ese acabado físico.

## Archivos

- `PaladinElite_Base.blend`: fuente editable con modificadores y estudio.
- `PaladinElite_Base.glb`: modelo estático sin luces ni cámaras.
- `PaladinElite_Base_TresCuartos.png`, `PaladinElite_Base_Frente.png`,
  `PaladinElite_Base_Espalda.png`, `PaladinElite_Base_Detalle.png` y
  `PaladinElite_Base_Guantelete.png`: cinco vistas reales de Blender Workbench.
- `validation_base.json`: reimportación del GLB y comprobaciones.

## Verificación y estado

180 mallas, 429.324 triángulos, tres materiales y dimensiones aproximadas de
1,108 × 0,625 × 2,163 m. La exportación se reimportó correctamente, comprobando
UV y materiales presentes, coordenadas finitas, escala y ausencia del estudio
y de texturas de imagen. Se revisaron las cinco vistas y se corrigieron cruces
visibles entre puño, brazal y nudillos detectados en la primera pasada.

Sigue siendo una interpretación estática en construcción. Quedan pendientes
aprobación de proporciones, revisión completa de solapamientos en una pose de
rig, retopología, skinning, animaciones e integración en Unreal. La validación
de archivo no certifica funcionamiento mecánico de las articulaciones.

## Reproducir

Desde la raíz del proyecto:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python 'Tools\Blender\refine_paladin_elite_base_v4.py'
```

Requiere el archivo `Base/V3/PaladinElite_Base.blend`. No sobrescribe esa fuente.
