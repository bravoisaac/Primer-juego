# Plan de desarrollo de Ten Fe

## Propósito y fuente de verdad

Ten Fe es un juego de acción en tercera persona tipo soulslike, para un jugador y sin conexión, ambientado entre dioses caídos. La primera meta sigue siendo un prototipo vertical pequeño y comprobable. Este archivo define el alcance, el orden, el estado y las decisiones pendientes. Leerlo completo antes de planificar, instalar herramientas o modificar el proyecto.

## Decisión técnica vigente — 31 de octubre de 2026

- **Motor activo: Unity 6.3, editor instalado 6000.3.26f1.** Cambio y reinicio desde cero solicitados explícitamente por el usuario.
- Proyecto activo: `Unity/TenFe`, C#, renderizador integrado, Direct3D 11 en Windows.
- Entrada inicial: teclado y mouse mediante Input Manager. Mando y reasignación quedan pendientes.
- Blender para arte; Git y Git LFS para fuentes y binarios grandes.
- Sin dependencias externas nuevas, servicios online, compras ni instalaciones pesadas.
- Plataforma inicial: Windows PC. Objetivo provisional: 1080p/60 FPS, pendiente de medición.
- Unreal queda como trabajo histórico conservado: `TenFe.uproject`, `Source`, `Content`, `Config`, `Assets` artísticos y `Tools` no se migran ni se borran.
- El plan anterior completo, con el historial de Unreal y del Paladín, está en `Docs/PLAN_HISTORICO_UNREAL_2026-10-14.md`. Sus casillas completadas no acreditan implementación en Unity.

## Visión inicial

**Frase:** El último peregrino recupera la fe de un santuario abandonado y desafía a los dioses que extinguieron su propia llama.

Tono propuesto: fantasía religiosa oscura, ruinas de basalto y bronce, eclipse y llamas sagradas. Aster, dios del Ocaso, es el jefe del prototipo; Nerea, diosa de la memoria, conserva una reliquia. Estos nombres y detalles narrativos son propuestas editables, no un panteón definitivo aprobado.

La moneda se llama fe. El ciclo combina combate deliberado, uso de energía, descanso, mejora de vitalidad, pérdida y recuperación de fe. El arte actual utiliza primitivas originales para validar escala, lectura de ataques y recorrido.

## Alcance

Una zona corta conectada, personaje en tercera persona, ataque ligero/fuerte, carrera, salto, esquiva, bloqueo, fijación de objetivo, tres enemigos comunes (incluido un paladín resistente), dos altares, un atajo, una reliquia secreta, un jefe con cambio de fase, fe recuperable, mejora de vida, guardado, HUD y pausa.

Quedan fuera sin autorización explícita: mundo abierto, multijugador, contenido masivo, consolas/móviles, monetización, grandes sistemas de equipo o producción artística definitiva antes de validar el combate.

## Fases y casillas de Unity

### Fase 0. Visión y entorno

- [x] Cambiar el motor a Unity por petición del usuario y conservar el trabajo anterior.
- [x] Verificar Unity 6000.3.26f1 instalado y soporte de compilación Windows.
- [x] Escribir una visión inicial que mantenga la temática de dioses.
- [x] Crear proyecto C# separado y exclusiones Git para cachés y compilaciones.
- [ ] Aprobar panteón, tono y mecánica diferenciadora definitiva.
- [ ] Configurar copia de seguridad remota.

### Fase 1. Movimiento y combate base

- [x] Implementar movimiento relativo a cámara, carrera y salto.
- [x] Implementar cámara orbital con colisión y fijación/cambio de objetivo.
- [x] Crear vida, energía, regeneración y muerte.
- [x] Crear ataque ligero y fuerte con alcance, arco frontal y obstrucción por muros.
- [x] Crear esquiva con ventana de invulnerabilidad y gasto de energía.
- [x] Crear bloqueo frontal, ruptura de guardia y reacción de impacto.
- [x] Crear curación limitada y reposición en altares.
- [ ] Validar manualmente sensibilidad, pendientes, bordes y sensación del combate.
- [ ] Añadir animaciones con rig, combos y ventanas de cancelación pulidas.
- [ ] Añadir mando y controles reasignables.

### Fase 2. Enemigos y jefe

- [x] Crear custodio, paladín resistente y Aster con atributos diferenciados.
- [x] Implementar patrulla, percepción con línea de visión, persecución, anticipación, ataque, recuperación y regreso.
- [x] Añadir evitación local de muros y límite de persecución.
- [x] Cambiar ritmo del jefe al bajar de media vida y variar un golpe cada tres ataques.
- [x] Añadir barra del jefe, recompensa y victoria persistente.
- [x] Integrar el GLB Gilded Sentinel facilitado por el usuario como los tres guardianes, con una copia reducida, rig de 20 huesos y siete animaciones originales.
- [x] Conectar animación esquelética a patrulla, persecución, anticipación, ataque, impacto, muerte y reaparición; verificar deformación real de la malla en ejecución.
- [x] Dar fases más naturales al movimiento: pausas de patrulla y observación, aceleración, giro gradual, acercamiento caminando y frenado antes del ataque; conservar la fase de zancada entre caminar y correr.
- [ ] Pulir pesos en hombros/faldones, agarre de espada, contacto de pies y animaciones del centinela; añadir LOD antes de multiplicar encuentros.
- [ ] Sustituir la evitación local por navegación robusta si aumenta la complejidad del nivel.
- [ ] Ajustar animación, distancias y señales con jugadores reales.
- [ ] Preparar retopología, rig, skinning y LOD de modelos históricos antes de integrarlos.

### Fase 3. Ciclo soulslike

- [x] Crear dos altares con checkpoint, reposición y reinicio de enemigos comunes.
- [x] Evitar descanso con enemigos cercanos en combate.
- [x] Otorgar fe, soltarla al morir y recuperarla en un único vestigio.
- [x] Sustituir el vestigio anterior al morir otra vez.
- [x] Añadir cinco mejoras de vitalidad comprables con fe.
- [x] Guardar checkpoint, fe, mejora, vestigio, atajo, reliquia y jefe en JSON versionado.
- [x] Proteger guardados incompatibles o dañados y usar reemplazo con copia de respaldo.
- [ ] Añadir inventario y equipo cuando el combate base esté validado.

### Fase 4. Zona y presentación

- [x] Construir una escena editable con santuario, patio, templo y eclipse.
- [x] Conectar ruta principal, camino lateral, palanca de atajo y reliquia de Nerea.
- [x] Añadir HUD de vida, energía, cálices, fe, objetivo y jefe.
- [x] Añadir ayuda, pausa, volumen y sensibilidad.
- [x] Añadir materiales, poses de combate y audio sintetizado provisionales originales.
- [x] Incorporar texturas PBR del centinela, conversión de metal/rugosidad y reflexión ambiental para leer la armadura; incluir atribución CC BY 4.0 junto al ejecutable.
- [x] Mejorar ambientación del santuario existente: cielo nublado del eclipse, niebla, luz cálida de llamas, piedra/bronce erosionados, fuego y brasas, ceniza suspendida, seis estandartes al viento y brillo suave de cámara.
- [ ] Reemplazar recursos provisionales prioritarios tras aprobar la jugabilidad.
- [ ] Añadir accesibilidad, opciones gráficas y escalado configurable de interfaz.
- [ ] Ampliar y ajustar el recorrido hasta una demo de 15–30 minutos si la base resulta satisfactoria.

### Fase 5. Verificación y entrega

- [x] Compilar el proyecto para Windows con Unity.
- [x] Pasar 13 comprobaciones de atributos, golpes y persistencia en el editor.
- [x] Completar 57 comprobaciones en el ejecutable (37 originales y 20 del centinela), resolver incidencias y revisar vistas renderizadas del nivel y del enemigo.
- [x] Verificar nueve comportamientos adicionales del movimiento gradual y recompilar Windows (66 comprobaciones de ejecución y 13 de reglas aprobadas el 2026-11-02).
- [x] Validar shaders, luces, partículas y tres vistas de ambientación en Windows (74 comprobaciones de ejecución y 13 de reglas; 87 en total).
- [x] Documentar apertura, controles, recursos y validación reproducible.
- [ ] Medir rendimiento y probar en otro equipo.
- [ ] Realizar una partida manual completa y corregir problemas de sensación o equilibrio.

No se considera terminada la demo ni las fases de pulido mientras falte revisión manual.

## Orden de trabajo siguiente

1. Revisar manualmente HUD, menús y controles físicos en la compilación entregada.
2. Jugar el recorrido con el usuario y ajustar cámara, velocidades, alcance y energía.
3. Aprobar identidad visual y panteón.
4. Refinar el rig del centinela ya integrado y preparar el personaje jugador animado, conservando la arquitectura de combate.
5. Mejorar navegación, accesibilidad y mando.
6. Medir rendimiento, empaquetar y hacer prueba externa.

## Mapa dinámico

- Objetivo actual: mejorar gráficos y ambientación del santuario, prioridad elegida por el usuario; conservar recorrido y combate existentes.
- Motor: Unity 6000.3.26f1; C#; renderizador integrado.
- Entrada: `Unity/TenFe/Assets/Scenes/Santuario.unity`; `GameSession.Start` restaura progreso y conecta el ciclo.
- Flujo: aparecer en altar → custodios → paladín → segundo altar → camino lateral/reliquia/atajo → Aster → victoria guardada.
- Personaje: `Character/PlayerController.cs`, `PlayerInputFrame.cs` y `OrbitCamera.cs`. La captura de entrada se separa de las acciones para comprobar controles sin inyectar teclas al sistema operativo.
- Combate: `Combat/Health.cs`, `Stamina.cs`, `CombatQuery.cs`.
- Enemigos: `AI/EnemyBrain.cs`; patrulla con pausas → observación → persecución con aceleración y giro limitado → acercamiento lento → frenado/alineación → anticipación → ataque/recuperación → nueva observación. Comparte Health con el personaje y expone estado/velocidad a `Presentation/SentinelVisual.cs`. Animator genérico controla el skin; CharacterController controla el desplazamiento y la IA aplica el daño al 14 % de Strike. Los siete clips existentes se reutilizan: Walk/Run conservan fase de zancada y emplean umbrales distintos de entrada/salida para evitar alternancias rápidas.
- Estado y mundo: `World/GameSession.cs`, `Interactable.cs`, `WorldBuilder.cs`.
- Guardado: `Save/SaveStore.cs`, JSON local versionado y copia `.bak`.
- Presentación: `Presentation/GameHud.cs`, `ActorVisual.cs` para jugador/jefe, `SentinelVisual.cs` para guardianes y `GameAudio.cs`. `SanctuaryAtmosphere.cs` controla fluctuación de luces; `SanctuaryImageEffect.cs` añade brillo/viñeta a la cámara. Los materiales de `Art/Atmosphere` controlan cielo, erosión, partículas y telas.
- Herramientas: `Assets/Editor/ProjectTools.cs`, `SentinelInstaller.cs`, `AtmosphereInstaller.cs`, `Validar.ps1`; resultados en `Docs/Validation`. El instalador de ambientación actualiza la escena guardada sin reconstruir su geometría; la reconstrucción explícita también incorpora la ambientación. Rig y exportación reproducibles en `Tools/Blender/rig_gilded_sentinel.py`.
- Recursos nuevos: `Assets/Characters/Enemies/GildedSentinel/` conserva GLB, Blender y renders; `Unity/TenFe/Assets/Art/GildedSentinel/` contiene FBX, texturas, material, controlador y prefab. La escena se actualizó sin regenerar su geometría.
- Recursos de ambientación: cinco shaders originales, seis materiales y una malla de estandarte en `Unity/TenFe/Assets/Art/Atmosphere`. Módulo integrado `com.unity.modules.particlesystem` activado; sin dependencias externas. Escena con diez luces de llama y un máximo conjunto de 920 partículas; brillo calculado a un cuarto del ancho/alto de pantalla.
- Estado global: checkpoint, fe, nivel, atajo, reliquia, jefe y vestigio. No hay API ni backend.
- Archivos de esta tarea: `Art/Atmosphere`, `SanctuaryAtmosphere.cs`, `SanctuaryImageEffect.cs`, `AtmosphereInstaller.cs`, `ProjectTools.cs`, `RuntimeSmoke.cs`, `Santuario.unity`, ajustes de proyecto/paquetes, README, procedencia de recursos, pruebas manuales y este plan. Compilación local e informes actualizados. La geometría existente conserva transformaciones y colisiones; se añaden únicamente elementos decorativos sin colisión.
- Archivos preservados: todo el proyecto Unreal y las fuentes artísticas históricas, incluida `Assets/Characters/Enemies/PaladinElite/DirectMesh/V3`.
- Riesgo: medio en coste gráfico y visibilidad; vistas revisadas a 1280×720, pendiente medir 1080p y probar otro equipo. Fuente GLB y modelos históricos preservados. Los pesos del centinela son aproximados y la reducción no sustituye una retopología manual. La escena es editable; reconstruirla sustituye cambios manuales, por eso la compilación cotidiana no la regenera. Reaplicar la ambientación restablece sus parámetros artísticos predeterminados.

## Estado actual

- Fase activa: pulido gráfico y de ambientación implementado; sensación, skin y rendimiento externo pendientes.
- Último avance (2026-11-02): ambientación renovada con cielo de eclipse y nubes, niebla, luces cálidas, superficies erosionadas, telas al viento, fuego y ceniza. Conservados recorrido, colisiones, combate y movimientos graduales del enemigo. Compilación Windows actualizada en `Unity/TenFe/Builds/Windows/TenFe.exe`; los modelos de jugador y jefe siguen siendo provisionales.
- Verificación: 13 comprobaciones de reglas/guardado y 74 comprobaciones en ejecución aprobadas (87 en total). Las ocho nuevas comprueban carga de ambiente, shaders de cámara/materiales, luces sin nuevas colisiones, partículas activas con presupuesto limitado y tres vistas renderizadas. Informes en `Unity/TenFe/Docs/Validation/core.txt`, `runtime.txt` y `atmosphere-import.txt`; importación del centinela documentada en `sentinel-import.txt`.
- Validación: contacto con suelo, carrera, salto/aterrizaje, energía, bloqueo frontal, daño por espalda, curación, ventana de invulnerabilidad, fijación, ataques ligero/fuerte, obstrucción por muros, IA, recompensas, descanso, checkpoints, muerte, recuperación, segunda muerte, mejora, atajo, fase del jefe, victoria y pausa. La prueba usa estado aislado y no sobrescribe partidas reales.
- Incidencias corregidas: el umbral mínimo de movimiento descartaba desplazamientos pequeños e interrumpía la detección del suelo; se fijó en cero. Los objetivos desactivados se excluyen del combate/fijación y la recompensa del jefe se protege frente a duplicados. Se usa renderizado directo a textura para revisar escenas con la ventana de pruebas oculta.
- Movimiento corregido (2026-11-02): arranques a velocidad completa, giro instantáneo antes del golpe y reinicio de zancada al cambiar Walk/Run. Se actualiza gravedad incluso durante observación, preparación y recuperación; la velocidad retenida se ajusta al desplazamiento real para evitar impulso acumulado contra muros. La evitación sigue siendo local; no se añadió navegación avanzada ni contacto de pies por IK.
- Ajuste gráfico (2026-11-02): durante la validación apareció `Ran out of Graphics Ring Buffer space` en D3D11. Separar capturas por fotograma no lo eliminó; activar `PlayerSettings.meshDeformation = MeshDeformation.GPU` eliminó el aviso en la ejecución final, con pruebas de skin, ataque y reaparición aprobadas. Se conservan partículas limitadas y brillo reducido; no equivale a una medición de rendimiento.
- Revisión visual: capturas del ejecutable de entrada, patio, templo, cámara jugable y centinela; comprobados materiales, iluminación, telas por ambas caras y siluetas. Vistas nuevas en `Docs/Validation/atmosfera_*.png`; comparación anterior en `BeforeAtmosphere`. Estas vistas no incluyen HUD IMGUI. La partida manual completa, el contacto fino de pies y el equilibrio siguen pendientes.
- Recursos: cuerpo/texturas Meshy facilitados por el usuario; su SHA256 coincide con el Paladín histórico cuya licencia CC BY 4.0 consta en el repositorio. Rig, clips y espada creados localmente. Procedencia en `Unity/TenFe/Docs/RECURSOS.md`; atribución distribuida en `THIRD_PARTY_NOTICES.txt`.
- Bloqueos externos: ninguno. Unity requirió acceso al contexto local de licencia/cachés y compiló correctamente; no se instalaron herramientas ni se hicieron compras.
- Siguiente paso: abrir `Unity/TenFe/Jugar.cmd`, recorrer entrada/patio/templo y comprobar claridad de enemigos y bordes bajo la nueva iluminación. Medir FPS a 1080p y completar `Unity/TenFe/Docs/PRUEBAS_MANUALES.md`, incluyendo movimiento del enemigo y pausa de los efectos, antes de dar por terminado el pulido.

## Decisiones pendientes

- ¿Conservar Aster y Nerea como nombres del panteón?
- ¿Combate pausado o agresivo, y qué mecánica divina propia lo distinguirá?
- ¿Arte realista, estilizado o intermedio?
- ¿El primer objetivo final es aprendizaje, portafolio o demo comercial?
- ¿Qué modelos históricos conviene adaptar después de retopología y rig?

## Registro de decisiones

| Fecha | Decisión | Motivo | Estado |
|---|---|---|---|
| 2026-10-11 a 2026-10-14 | Trabajo previo en Unreal y modelos de paladines | Desarrollo histórico | Conservado; detalle completo en el plan histórico |
| 2026-10-31 | Cambiar a Unity y comenzar una base nueva | Petición explícita del usuario, manteniendo temática de dioses | Confirmado |
| 2026-10-31 | Usar Unity 6000.3.26f1 instalado y carpeta `Unity/TenFe` | Evitar instalaciones y conservar el trabajo anterior | Implementado |
| 2026-10-31 | C#, renderizador integrado, Input Manager y módulos integrados | Base pequeña compilable sin paquetes externos | Implementado; mando y reasignación pendientes |
| 2026-10-31 | Proponer Santuario del Ocaso, Aster y Nerea | Concretar la temática divina en un recorrido pequeño | Implementado como propuesta narrativa editable |
| 2026-10-31 | Usar geometría, poses y audio provisionales originales | Validar primero sistemas y ciclo de juego | Implementado; arte final pendiente |
| 2026-10-31 | Mantener modelos densos del Paladín fuera de la nueva compilación | Requieren retopología, rig y animaciones | Conservados sin modificación |
| 2026-10-31 | Usar Direct3D 11 en esta base | La prueba con Direct3D 12 emitió avisos de agotamiento del búfer gráfico | Compilado y vistas revisadas |
| 2026-10-31 | Aislar validaciones del guardado del jugador | Probar muerte y progresión sin modificar una partida real | Implementado con `--smoke-test` |
| 2026-11-01 | Completar validación automática y entregar ejecutable, escena y fuentes | El usuario pidió continuar; se corrigió el contacto con suelo y se verificó el ciclo completo por escenarios automáticos | 50 comprobaciones aprobadas; prueba manual y pulido pendientes |
| 2026-11-01 | Integrar el GLB Meshy adjuntado como enemigo con movimientos | Petición explícita del usuario; archivo idéntico por hash a la fuente del Paladín histórico | Copia independiente, original preservado |
| 2026-11-01 | Crear rig genérico, pesos y siete clips localmente; reducir el cuerpo a 54.999 triángulos | La fuente no tenía esqueleto; permite cumplir el movimiento sin compras, servicios externos ni paquetes de terceros | Funcional; refinamiento artístico y LOD pendientes |
| 2026-11-01 | Mantener el daño bajo control de IA y sincronizarlo con Strike; reponer el rig al reaparecer | Evita golpes duplicados por animación y cadáveres que reaparecen deformados | Comprobado en ejecución; 70 comprobaciones totales aprobadas |
| 2026-11-01 | Conservar texturas, documentar adaptación y distribuir atribución CC BY 4.0 | La licencia histórica corresponde exactamente al archivo suministrado | Registrado y copiado junto al ejecutable |
| 2026-11-02 | Introducir pausas de observación/patrulla, aceleración y frenado, giros limitados y preparación del golpe; mantener fase de zancada Walk/Run | Petición de movimiento más humano; reutiliza los siete clips y mantiene el daño sincronizado sin ampliar contenido ni instalar dependencias | Windows recompilado; 79 comprobaciones aprobadas; sensación y contacto fino de pies pendientes de revisión manual |
| 2026-11-02 | Priorizar gráficos y ambientación: recursos procedurales originales, fuego/brasas, telas, niebla y acabado suave de cámara sobre la escena existente | El usuario eligió explícitamente gráficos y ambientación al pedir mejorar el juego | Implementado; vistas revisadas y 87 comprobaciones aprobadas; rendimiento externo pendiente |
| 2026-11-02 | Activar únicamente el módulo de partículas incluido en Unity y mantener instalador separado del combate | Añadir movimiento ambiental sin paquetes externos, nuevas colisiones ni reconstrucción de la zona | Reproducible mediante `AtmosphereInstaller`; fuentes y materiales editables |
| 2026-11-02 | Deformar los modelos animados en GPU en la compilación Windows | Reducir las transferencias de los skins densos y corregir el aviso de búfer gráfico observado en las pruebas | Aviso ausente en la ejecución final; 87 comprobaciones aprobadas; FPS externos pendientes |

## Reglas de trabajo

1. Leer este plan completo y revisar solo sistemas relacionados.
2. Explicar objetivo, alcance, archivos y riesgos antes de modificar.
3. Pedir confirmación antes de instalaciones pesadas, compras, borrados o migraciones que no estén ya autorizadas por el usuario.
4. Mantener sistemas separados; no concentrar combate, IA, HUD y guardado en un único componente.
5. Registrar origen y licencia de cualquier recurso externo.
6. Ejecutar verificaciones pertinentes y distinguir pruebas automáticas de revisión manual.
7. Actualizar casillas, mapa, estado, errores conocidos y decisiones al completar una tarea importante.
8. No declarar una fase terminada si falta compilación o validación manual necesaria.

## Riesgos y criterio de éxito

Riesgos actuales: sensación del combate sin pulir, pesos/animaciones básicos del centinela, jugador/jefe sin rig, evitación local limitada y rendimiento no medido en otros equipos. Los demás modelos históricos siguen sin preparación de juego. Evitar ampliar contenido antes de validar controles y ciclo.

El prototipo final se considerará completo cuando otra persona pueda abrirlo, aprender los controles, recorrer la zona, abrir el atajo, derrotar enemigos, morir, recuperar fe, mejorar al personaje y vencer al jefe sin ayuda, con estabilidad y rendimiento aceptables. La base actual es el punto de partida de esa validación.
