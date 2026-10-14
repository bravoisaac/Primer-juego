# Conjunto de armas del Paladín del Ocaso

## Objetivo

Crear seis armas que compartan el lenguaje visual del Paladín del Ocaso y
permitan producir varias versiones del mismo enemigo sin duplicar su cuerpo,
materiales base, rig ni lógica común.

## Variantes de combate

| Variante | Equipo | Función inicial |
|---|---|---|
| Guardián | Espada y escudo | Enemigo base defensivo, alcance corto |
| Lancero | Lanza | Control de distancia y ataques lineales |
| Macero | Maza | Golpes lentos, ruptura de guardia y mayor impacto |
| Arquero | Arco | Hostigamiento a distancia y reposicionamiento |
| Ballestero | Ballesta | Disparo más lento, preciso y potente |

Todas las variantes reutilizarán la misma malla del paladín. Las diferencias
de atributos, equipo y selección de ataques deberán configurarse con datos o
propiedades editables, no con copias independientes de toda la clase enemiga.

## Dirección artística común

- Fantasía medieval oscura y religiosa, original de `Ten Fe`.
- Acero envejecido y ligeramente ennegrecido, latón u oro viejo y cuero marrón.
- Alas, plumas estilizadas y figura alada como motivos recurrentes.
- Grabados finos en zonas de lectura cercana; el relieve grande debe conservar
  una silueta clara durante el combate.
- Desgaste concentrado en filos, remaches, empuñaduras y superficies de impacto.
- No copiar emblemas, geometría ni texturas de otras propiedades intelectuales.

## Escala propuesta para el paladín de 2 metros

| Recurso | Medida de referencia | Piezas funcionales |
|---|---:|---|
| Espada | 120 cm de largo total | Hoja, guarda, empuñadura y pomo |
| Escudo cometa | 95 x 62 cm | Cuerpo, borde, asa y correa posterior |
| Lanza | 245 cm de largo total | Asta, punta y regatón |
| Maza | 88 cm de largo total | Cabeza, mango, empuñadura y pomo |
| Arco | 170 cm sin tensar | Cuerpo flexible y cuerda separada |
| Ballesta | 92 x 76 cm | Cuerpo, arco, cuerda, mecanismo y virote |

Estas medidas son una base de producción. Deben verificarse en Unreal junto a
la mano, el cuerpo y las animaciones antes de cerrar los pivotes definitivos.

## Requisitos técnicos

- Fuente editable en Blender y exportación compatible con Unreal Engine 5.
- Z hacia arriba, escala real en metros y transformaciones aplicadas.
- Pivote en el punto de agarre de espada, lanza, maza, arco y ballesta; pivote
  del escudo centrado en su asa interior.
- High poly para biseles, grabados y daño; versión de juego con UV limpias.
- Mapas PBR de 2K por arma o atlas compartido cuando conserve la calidad:
  Base Color, Normal y ORM.
- Colisión sencilla para inventario y mundo; las trazas de combate deben usar
  volúmenes o sockets específicos y no la colisión compleja del render.
- Arco y ballesta deben conservar cuerda y partes móviles separadas para su
  posterior rig y animación.
- Presupuesto orientativo de 10.000 a 35.000 triángulos por arma en LOD0. La
  lectura visual dependerá principalmente de silueta, biseles y mapas horneados.

## Nombres de producción propuestos

- `SM_Paladin_Sword`
- `SM_Paladin_Shield`
- `SM_Paladin_Spear`
- `SM_Paladin_Mace`
- `SKM_Paladin_Bow`
- `SKM_Paladin_Crossbow`

El prefijo es provisional para arco y ballesta hasta decidir si se deformarán
con malla esquelética o con componentes y animaciones dentro de Unreal.

## Orden de producción

1. Espada y escudo: validan agarre, bloqueo, escala y el lenguaje visual.
2. Lanza y maza: validan alcances y ritmos cuerpo a cuerpo alternativos.
3. Arco y ballesta: requieren proyectiles, cuerda y animaciones adicionales.

El prototipo vertical debe integrar primero al Guardián. Las demás variantes se
incorporarán gradualmente para no retrasar la validación del combate base.

La apariencia objetivo del primer conjunto puede consultarse en
`Preview/PaladinGuardian_Concept.png`. Es una referencia conceptual para escala,
paleta y lectura de silueta, no geometría final ni una captura del juego.

## Referencias recibidas

Las seis láminas entregadas por el usuario se conservan en
`References/Weapons/`:

- `paladin_sword.png`
- `paladin_shield.png`
- `paladin_spear.png`
- `paladin_mace.png`
- `paladin_bow.png`
- `paladin_crossbow.png`

Origen registrado: referencias aportadas por el usuario el 2026-10-12. Antes de
una distribución comercial se debe confirmar que el usuario posee o puede usar
los diseños de origen.
