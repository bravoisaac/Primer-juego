# Base Unity — mapa de implementación

## Tarea activa: centinela animado

- Objetivo: integrar `Meshy_AI_Gilded_Sentinel_1012232218_texture.glb` como enemigo con rig y movimientos.
- Fuente inspeccionada: SHA256 coincide con `Assets/Characters/Enemies/Paladin/Source/PaladinSoldier_Meshy_Source.glb`; 180.540 triángulos, tres texturas, sin skin ni animaciones. Licencia histórica CC BY 4.0.
- Flujo: fuente GLB preservada → copia Blender con rig/pesos/animaciones → FBX y texturas Unity → prefab → EnemyBrain → compilación y validación.
- Archivos candidatos: EnemyBrain, ActorVisual, WorldBuilder, ProjectTools, RuntimeSmoke, recursos PBR históricos.
- Archivos a modificar: carpeta nueva del centinela, herramienta Blender nueva, importador Unity, presentación animada, conexiones puntuales de IA y documentación.
- Preservar: GLB de Downloads, fuentes del Paladín/élite, Unreal, geometría y encuentros de la escena actual.
- Riesgo medio: deformación de armadura, conversión de ejes/escala y sincronización de golpes; revisar poses en Blender y Unity. No se añaden servicios ni paquetes de pago.
- Implementación: FBX genérico con 20 huesos y siete clips; cuerpo reducido a 54.999 triángulos. SentinelInstaller conecta el prefab a los tres enemigos comunes sin reconstruir el nivel. SentinelVisual sigue el estado de EnemyBrain; este aplica el golpe al 14 % de Strike.
- Validación de esta entrega: 13 comprobaciones base y 57 de ejecución aprobadas, incluidas deformación real del skin, anticipación/golpe, impacto, muerte y recuperación de pose; importación de avatares, huesos y clips validada. Artefactos en `Docs/Validation`.
- Archivos artísticos: fuente/copia Blender en `Assets/Characters/Enemies/GildedSentinel` desde la raíz del repositorio; recursos de juego en `Unity/TenFe/Assets/Art/GildedSentinel`.

- Objetivo: reiniciar Ten Fe en Unity conservando la temática de dioses, en una zona pequeña para un jugador.
- Motor: Unity 6.3 (6000.3.26f1), C#, renderizador integrado; módulos incluidos con el editor, sin recursos ni paquetes externos.
- Entrada: `Assets/Scenes/Santuario.unity`, generada por `TenFe.Editor.ProjectTools.CreateScene`.
- Flujo: santuario → guardianes → atajo y reliquia → Aster, dios del Ocaso → victoria.
- Componentes: PlayerController, OrbitCamera, Health, Stamina, EnemyBrain, SentinelVisual, Interactable, GameSession, GameHud, GameAudio.
- Estado: checkpoint, fe, vestigio de muerte, bendiciones, atajo, reliquia y jefe; guardado local JSON versionado.
- Patrones: separar movimiento, combate/atributos, mundo, persistencia y presentación. Arte provisional original.
- Archivos candidatos revisados: plan principal, AGENTS.md, exclusiones Git y herramientas instaladas.
- Archivos a modificar: carpeta nueva `Unity/TenFe`, exclusiones Git y plan principal.
- Archivos preservados: proyecto Unreal, Source, Content, Assets artísticos y Tools existentes.
- Riesgo: medio en jugabilidad nueva; bajo sobre trabajo anterior. Se requieren compilación, prueba del ciclo de juego y revisión visual.
- Mando, reasignación, arte/rig definitivos, navegación avanzada y pulido quedan pendientes.
- Estado al 2026-11-01: escena y compilación Windows con centinela animado; 13 comprobaciones de reglas/guardado y 57 en ejecución aprobadas. Vistas del nivel/enemigo sin HUD. La prueba manual de interfaz, controles físicos, pesos y equilibrio queda en `PRUEBAS_MANUALES.md`.
- Entrada: `PlayerInputFrame` captura teclado/mouse; `PlayerController` ejecuta acciones. Las pruebas suministran entradas al mismo controlador únicamente en `--smoke-test`.
- Corrección validada: `CharacterController.minMoveDistance = 0` mantiene contacto con el suelo en fotogramas con desplazamiento pequeño. Fijación/ataques excluyen actores desactivados.
