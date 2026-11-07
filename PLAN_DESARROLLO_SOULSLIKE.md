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
- [x] Recordar una única pulsación de acción durante 200 ms para encadenar al terminar la recuperación, sin cancelar ataques ni gastar energía antes de ejecutar.
- [x] Suavizar el retorno de cámara tras obstáculos y desplazar el encuadre al fijar objetivo; comprobar colisión lateral y sacudida contra paredes.
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
- [x] Renovar siete clips del centinela con apoyo/avance de pies, tobillos nivelados, anticipación/golpe continuos, recuperación, reacción y caída; sincronizar reproducción, impactos repetidos y reinicio de poses. Animar el arco del ataque de Aster con su progreso real.
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
- [x] Pulir HUD, ayuda y pausa con jerarquía visual de bronce/ceniza, escala proporcional, indicadores de recursos y avisos de combate sin superposición entre enemigos.
- [x] Añadir materiales, poses de combate y audio sintetizado provisionales originales.
- [x] Incorporar texturas PBR del centinela, conversión de metal/rugosidad y reflexión ambiental para leer la armadura; incluir atribución CC BY 4.0 junto al ejecutable.
- [x] Mejorar ambientación del santuario existente: cielo nublado del eclipse, niebla, luz cálida de llamas, piedra/bronce erosionados, fuego y brasas, ceniza suspendida, seis estandartes al viento y brillo suave de cámara.
- [x] Ampliar el mapa con un claustro oeste conectado por dos puentes, patio, galería y nuevo emplazamiento de la reliquia; compilar y validar el recorrido automáticamente.
- [ ] Reemplazar recursos provisionales prioritarios tras aprobar la jugabilidad.
- [ ] Añadir accesibilidad, opciones gráficas y escalado configurable de interfaz.
- [ ] Ampliar y ajustar el recorrido hasta una demo de 15–30 minutos si la base resulta satisfactoria.

### Fase 5. Verificación y entrega

- [x] Compilar el proyecto para Windows con Unity.
- [x] Pasar 13 comprobaciones de atributos, golpes y persistencia en el editor.
- [x] Completar 57 comprobaciones en el ejecutable (37 originales y 20 del centinela), resolver incidencias y revisar vistas renderizadas del nivel y del enemigo.
- [x] Verificar nueve comportamientos adicionales del movimiento gradual y recompilar Windows (66 comprobaciones de ejecución y 13 de reglas aprobadas el 2026-11-02).
- [x] Validar shaders, luces, partículas y tres vistas de ambientación en Windows (74 comprobaciones de ejecución y 13 de reglas; 87 en total).
- [x] Capturar y revisar HUD completo, ayuda, pausa, altar, combate, jefe y muerte; verificar composición a 1280×720, 1024×768 y 1920×1080 (90 comprobaciones de ejecución y 13 de reglas; 103 en total).
- [x] Validar respuesta de acciones y cámara con 17 comprobaciones adicionales: 107 de ejecución y 13 de reglas aprobadas (120 en total).
- [x] Validar la ampliación con recorrido de cápsula en ambos sentidos, suelo continuo, pretiles, reliquia, custodio y tres capturas: 117 comprobaciones de ejecución y 13 de reglas aprobadas (130 en total, 2026-11-06).
- [x] Validar animaciones renovadas: 11 comprobaciones de clips importados, 13 de reglas y 130 de ejecución (154 en total, 2026-11-06); revisar poses renderizadas de marcha, preparación, contacto, recuperación, muerte y Aster.
- [x] Documentar apertura, controles, recursos y validación reproducible.
- [ ] Medir rendimiento y probar en otro equipo.
- [ ] Realizar una partida manual completa y corregir problemas de sensación o equilibrio.

No se considera terminada la demo ni las fases de pulido mientras falte revisión manual.

## Orden de trabajo siguiente

1. Revisar manualmente las nuevas animaciones de guardianes y Aster: apoyo/avance de pies, lectura de golpes, reacciones, muerte y reinicio al descansar; recorrer también el claustro ampliado.
2. Jugar el recorrido con el usuario y ajustar cámara, velocidades, alcance y energía.
3. Aprobar identidad visual y panteón.
4. Refinar el rig del centinela ya integrado y preparar el personaje jugador animado, conservando la arquitectura de combate.
5. Mejorar navegación, accesibilidad y mando.
6. Medir rendimiento, empaquetar y hacer prueba externa.

## Mapa dinámico

- Objetivo actual: mejorar las animaciones de los enemigos por petición del usuario: zancadas con fases de apoyo/avance, golpes con preparación y recuperación continuas, reacciones y caída; mantener sincronía con el daño y animar el ataque de Aster. Mapa ampliado conservado: 1.800 m² de plataforma adicional (+85 % nominal).
- Motor: Unity 6000.3.26f1; C#; renderizador integrado.
- Entrada: `Unity/TenFe/Assets/Scenes/Santuario.unity`; `GameSession.Start` restaura progreso y conecta el ciclo.
- Flujo: primer altar → patio principal o puente oeste → patio de ceniza/custodio → galería/reliquia de Nerea → puente de regreso → paladín/segundo altar → palanca/atajo este → Aster. Ambos puentes del claustro permiten regreso; la reja del atajo este conserva su palanca.
- Personaje: `PlayerInputFrame` captura entrada → `PlayerActionBuffer` conserva la última acción hasta 200 ms → `PlayerController` la consume cuando queda libre, comprobando energía, suelo y cálices. Se conserva la dirección solicitada para la esquiva. Impacto que interrumpe, pausa, muerte y restauración limpian la cola. `OrbitCamera` contrae distancia ante paredes, suaviza el retorno y desplaza el hombro al fijar objetivo; comprueba también el desplazamiento lateral y la sacudida. La entrada de pruebas sigue separada de las teclas físicas.
- Combate: `Combat/Health.cs`, `Stamina.cs`, `CombatQuery.cs`.
- Enemigos: `AI/EnemyBrain.cs`; patrulla → observación → persecución gradual → acercamiento/frenado → anticipación → ataque/recuperación. Expone `ActionProgress`, `AnimationResetVersion` y `StaggerVersion`; la IA conserva daño al 14 % de Strike. `SentinelVisual.Update` se ejecuta después de IA y antes del Animator: conserva fase Walk/Run, ajusta ritmo a velocidad/escala y duración real de clips, reinicia Hit ante otro stagger y vuelve directamente a Idle al restaurar. Un golpe sin stagger añade una reacción breve al torso en LateUpdate sin reemplazar la locomoción. `ActorVisual.PoseEnemy` mueve cuerpo/arma/guardia de Aster a partir del progreso real de su ataque; el jugador conserva su controlador visual.
- Clips: `Tools/Blender/sentinel_motion.py` comparte las siete poses entre el generador completo y `polish_gilded_animations.py`. Solución de dos segmentos para rodilla/tobillo, fases de apoyo/avance y elevación del pie, preparación/Strike continuos, recuperación suavizada, reacción rápida y caída iniciada en las rodillas. `GildedSentinel.fbx` conserva nombres y duraciones; `GildedSentinel_Animated.blend` es la nueva fuente editable. No hay IK de terreno en ejecución ni cambios de malla/pesos.
- Estado y mundo: `World/GameSession.cs`, `Interactable.cs`, `WorldBuilder.cs`.
- Guardado: `Save/SaveStore.cs`, JSON local versionado y copia `.bak`.
- Presentación: `Presentation/GameHud.cs` lee recursos, progreso e interacciones de `GameSession` y estados de `PlayerController`/`EnemyBrain`; `HudTheme.cs` concentra estilos, paneles, símbolos y texturas reutilizables. Escala uniforme y anclajes a bordes; ayuda, pausa y muerte tienen composiciones separadas. `ActorVisual.cs` representa jugador/jefe, `SentinelVisual.cs` los guardianes y `GameAudio.cs` el sonido. `SanctuaryAtmosphere.cs` controla fluctuación de luces; `SanctuaryImageEffect.cs` añade brillo/viñeta a la cámara. Los materiales de `Art/Atmosphere` controlan cielo, erosión, partículas y telas.
- Herramientas: `ProjectTools.cs`, `SentinelInstaller.cs`, `SentinelAnimationTools.cs`, `AtmosphereInstaller.cs`, `Validar.ps1`; resultados en `Docs/Validation`. La validación cotidiana comprueba ahora también clips importados antes de compilar la escena guardada. `polish_gilded_animations.py` rehace solo animaciones sobre el rig existente; `rig_gilded_sentinel.py` permite reconstrucción completa. Ambos usan `sentinel_motion.py`.
- Recursos nuevos: `Assets/Characters/Enemies/GildedSentinel/` conserva GLB, Blender y renders; `Unity/TenFe/Assets/Art/GildedSentinel/` contiene FBX, texturas, material, controlador y prefab. La escena se actualizó sin regenerar su geometría.
- Recursos de ambientación: cinco shaders originales, seis materiales y una malla de estandarte en `Unity/TenFe/Assets/Art/Atmosphere`. Módulo integrado `com.unity.modules.particlesystem` activado; sin dependencias externas. Escena con diez luces de llama y un máximo conjunto de 920 partículas; brillo calculado a un cuarto del ancho/alto de pantalla.
- Estado global: checkpoint, fe, nivel, atajo, reliquia, jefe y vestigio. No hay API ni backend.
- Archivos de esta tarea: `EnemyBrain.cs`, `SentinelVisual.cs`, `ActorVisual.cs`, nuevo `Editor/SentinelAnimationTools.cs`, nuevo `Validation/EnemyAnimationChecks.cs`, `RuntimeSmoke.cs`, `ProjectTools.cs`, `Validar.ps1`, tres scripts Blender, FBX, nueva fuente `.blend` e informe artístico. Documentación, atribución, informes y capturas actualizados. Escena ampliada, malla, pesos, texturas, controles del jugador y formato de guardado preservados.
- Patrón de edición: instalador aditivo, ejecutado una vez sobre la escena guardada. Si ya existe `Claustro de la Memoria`, vuelve sin duplicar ni reemplazar ajustes manuales. Reutiliza materiales y telas de ambientación; conserva referencias de altares, jefe y palanca. Una reconstrucción completa continúa siendo una acción explícita que reemplaza la escena.
- Archivos preservados: todo el proyecto Unreal y las fuentes artísticas históricas, incluida `Assets/Characters/Enemies/PaladinElite/DirectMesh/V3`.
- Riesgo: medio en lectura de animación, deformación de hombros/faldones, contacto fino de pies y rendimiento. Los clips pasan comprobaciones geométricas de huesos, pero los pesos siguen siendo aproximados; falta revisión artística/manual, IK de terreno y LOD. Aviso gráfico D3D11 intermitente y retorno de IA por obstáculos complejos siguen pendientes. Fuente GLB y rig inicial preservados. La compilación cotidiana conserva la escena guardada.

## Estado actual

- Fase activa: pulido de animaciones solicitado el 2026-11-06; sensación manual, pesos y rendimiento externo pendientes.
- Último avance (2026-11-06): siete clips regenerados sobre el rig existente. Caminar/correr tienen fases de apoyo y avance, elevación de pies y rodillas orientadas hacia delante; preparación/golpe comparten pose de enlace, con continuación del arco y retorno gradual. Reacciones rápidas, respiración sutil y rodillas que ceden antes de caer. Reproducción adaptada a escala/velocidad, impactos leves limitados al torso, stagger repetido reiniciado y restauración directa de Idle. Aster ejecuta su preparación y arco de ataque según el progreso real. Windows recompilado y listo en `Unity/TenFe/Jugar.cmd`.
- Verificación de animaciones (2026-11-06): `Validar.ps1` terminó con 11 comprobaciones de clips importados, 13 de reglas y 130 de ejecución: **154 aprobadas**. Se verificaron cierre de ciclos, continuidad Windup/Strike, altura de apoyo del tobillo (variación 0,9 mm al caminar y 3,7 mm al correr), elevación del pie y ausencia de desplazamiento de raíz. En ejecución: impactos leves/repetidos, pausa, reinicio, coincidencia del progreso visual con daño único, recuperación y movimiento del arma de Aster. Cuatro nuevas capturas `animacion_*.png` y retratos de marcha/muerte revisados. Se corrigió una transición residual al descansar durante Hit. El aviso gráfico intermitente reapareció; no hubo errores de motor ni fallos finales.
- Avance previo del mapa (2026-11-06): instalador aditivo del claustro oeste, con dos pasos de seis metros de ancho y entradas de cuatro metros en el pretil original. Patio con fuente seca/columnas rotas, galería cubierta a ambos lados, sepulcros y retablo de Nerea; un custodio y la reliquia existentes reubicados. Geometría original local, sin recursos externos ni dependencias.
- Verificación del mapa (2026-11-06): `Validar.ps1` terminó correctamente con 13 comprobaciones de reglas y 117 de ejecución (130 en total). Diez nuevas verifican presencia de la ampliación, suelo, recorrido bidireccional con cápsula real, pretiles, interacción de la reliquia, referencias de progreso, encuentro reubicado y tres renders. Revisadas `mapa_claustro.png`, `mapa_nerea.png` y `mapa_general.png`. Reaplicar el instalador conservó una sola copia del claustro. Se desplazaron dos columnas que cortaban los accesos; la prueba de geometría aísla colisiones de enemigos y comprueba el combate por separado.
- Incidencia gráfica (2026-11-06): el aviso intermitente `Ran out of Graphics Ring Buffer space` apareció durante capturas, incluida la última ejecución, sin errores del motor ni fallos de las 130 comprobaciones. No se considera resuelto ni se acredita rendimiento; medir FPS y revisar una partida con controles físicos. El mapa conserva 920 partículas máximas y tres guardianes animados, con cuatro estandartes y una luz sin sombras adicionales.
- Avance previo de combate (2026-11-03): cola de una acción con vigencia de 200 ms para recibir pulsaciones al final de la recuperación. La energía se cobra al ejecutar y los intentos rechazados se descartan; no se acumulan combos ni se acortan ataques. La cámara recupera gradualmente su distancia tras una pared, aplica un encuadre lateral al fijar enemigo y limita también la sacudida por colisiones. Conservados HUD renovado, ambientación, daño y costes anteriores.
- Verificación (2026-11-03): Windows recompilado; 13 comprobaciones de reglas/guardado y 107 de ejecución aprobadas (120 en total). Las 17 nuevas cubren reemplazo/caducidad de intentos, ejecución única tras recuperación, dirección de esquiva, coste diferido, limpieza al pausar/restaurar, rechazo por energía, contracción/retorno de cámara, colisión durante sacudida y encuadre contra pared lateral. Se mantienen las diez capturas del HUD y todas las comprobaciones previas. Informes en `Unity/TenFe/Docs/Validation/core.txt`, `runtime.txt` y `build.txt`.
- Validación: contacto con suelo, carrera, salto/aterrizaje, energía, bloqueo frontal, daño por espalda, curación, ventana de invulnerabilidad, fijación, ataques ligero/fuerte, obstrucción por muros, IA, recompensas, descanso, checkpoints, muerte, recuperación, segunda muerte, mejora, atajo, fase del jefe, victoria y pausa. La prueba usa estado aislado y no sobrescribe partidas reales.
- Incidencias corregidas: el umbral mínimo de movimiento descartaba desplazamientos pequeños e interrumpía la detección del suelo; se fijó en cero. Los objetivos desactivados se excluyen del combate/fijación y la recompensa del jefe se protege frente a duplicados. Se usa renderizado directo a textura para revisar escenas con la ventana de pruebas oculta.
- Movimiento corregido (2026-11-02): arranques a velocidad completa, giro instantáneo antes del golpe y reinicio de zancada al cambiar Walk/Run. Se actualiza gravedad incluso durante observación, preparación y recuperación; la velocidad retenida se ajusta al desplazamiento real para evitar impulso acumulado contra muros. La evitación sigue siendo local; no se añadió navegación avanzada ni contacto de pies por IK.
- Ajuste gráfico (2026-11-02): durante la validación apareció `Ran out of Graphics Ring Buffer space` en D3D11. Separar capturas por fotograma no lo eliminó; activar `PlayerSettings.meshDeformation = MeshDeformation.GPU` eliminó el aviso en la ejecución final, con pruebas de skin, ataque y reaparición aprobadas. Se conservan partículas limitadas y brillo reducido; no equivale a una medición de rendimiento.
- Revisión visual: las capturas `Docs/Validation/hud_*.png` sí incluyen IMGUI; se revisan composición y textos a 1280×720, 1024×768 y 1920×1080. Las vistas previas `atmosfera_*.png`, `santuario.png` y retratos de enemigos siguen siendo renders sin HUD. La partida manual completa, los clics/teclas físicos, el contacto fino de pies y el equilibrio siguen pendientes.
- Incidencias de interfaz corregidas (2026-11-03): estiramiento independiente de ejes, adornos desplazados al escalar, solapamiento de avisos de enemigos y título vacío del altar en la escena (se usa su nombre como respaldo). La prueba recrea la superficie de ventana antes de leer el fotograma completo; la ventana oculta inicial no disponía de un búfer dibujado. Ajustes en `--smoke-test` no escriben preferencias del jugador.
- Registro gráfico (2026-11-03): el aviso de búfer D3D11 reapareció en el primer intento de validación, pero estuvo ausente en las dos últimas ejecuciones, incluida la final de 103 comprobaciones. Sin cambios adicionales al renderizador; rendimiento y posible recurrencia pendientes de la partida manual.
- Validación de cámara/entrada (2026-11-03): suite final de 120 comprobaciones aprobada, sin errores del motor ni aviso de búfer gráfico. Vista de combate revisada con encuadre de hombro. Falta validar sensación de los 200 ms y comodidad de cámara con jugadores; no equivale a una medición de FPS.
- Recursos: cuerpo/texturas Meshy facilitados por el usuario; su SHA256 coincide con el Paladín histórico cuya licencia CC BY 4.0 consta en el repositorio. Rig, clips y espada creados localmente. Procedencia en `Unity/TenFe/Docs/RECURSOS.md`; atribución distribuida en `THIRD_PARTY_NOTICES.txt`.
- Bloqueos externos: ninguno. Unity requirió acceso al contexto local de licencia/cachés y compiló correctamente; no se instalaron herramientas ni se hicieron compras.
- Siguiente paso: abrir `Unity/TenFe/Jugar.cmd`, observar patrulla/carrera y combatir con custodios, paladín y Aster; revisar apoyo de pies, mano/espada, lectura de preparación/contacto/recuperación, reacción repetida y caída. Completar la partida por el claustro y medir FPS a 1080p según `Docs/PRUEBAS_MANUALES.md`. Pesos, agarre de dedos, IK de terreno, LOD, accesibilidad y mando continúan pendientes.

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
| 2026-11-03 | Continuar la mejora visual con HUD, ayuda y pausa; separar estilos de datos y usar escala uniforme | Petición general de mejora; el siguiente paso del plan era revisar HUD, menús y controles | Implementado en IMGUI, sin dependencias ni cambios de alcance; controles físicos pendientes |
| 2026-11-03 | Añadir capturas reales del HUD después del renderizado, en tres resoluciones | Las vistas de cámara existentes no permitían detectar recortes, adornos desplazados ni textos vacíos de la interfaz | Windows recompilado; 103 comprobaciones aprobadas y diez capturas de interfaz revisadas; partida manual pendiente |
| 2026-11-03 | Retener la última pulsación durante 200 ms y mejorar cámara de combate | Nueva petición general de mejora; continuar el pulido de controles previsto sin cambiar daño, costes ni duración de ataques | Windows recompilado; 120 comprobaciones aprobadas, incluyendo pared lateral y sacudida; sensación manual pendiente |
| 2026-11-06 | Ampliar la zona con 1.800 m² de claustro oeste, dos puentes, patio y galería; redistribuir un custodio y la reliquia | Petición explícita de mejorar y agrandar el mapa; mantener una zona conectada sin mundo abierto, multijugador ni multiplicación de enemigos densos | Windows recompilado; 130 comprobaciones aprobadas y tres vistas revisadas. Dos columnas desplazadas para despejar los pasos. Aviso gráfico intermitente, duración de 15–30 minutos y revisión manual pendientes |
| 2026-11-06 | Renovar los siete clips del centinela sobre el rig actual y animar el arco del ataque de Aster | Petición explícita de mejorar animaciones; fuentes locales compartidas, sin paquetes ni cambios de daño/duración. Conservar GLB, rig inicial, malla, pesos y mapa ampliado | Windows recompilado; 154 comprobaciones aprobadas y poses revisadas. Reinicio de Hit corregido. Contacto fino de pies, pesos, agarre, revisión manual y aviso gráfico intermitente pendientes |

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
