# Plan de desarrollo de Ten Fe

## Propósito

Ten Fe será un juego de acción y rol en tercera persona inspirado en el ritmo, la tensión y la exploración de los juegos tipo souls. La primera meta no es crear de inmediato un juego del tamaño de Elden Ring, sino producir un **prototipo vertical corto, jugable y bien terminado** que demuestre combate, exploración, progresión y una batalla contra un jefe.

Este archivo es la fuente principal de planificación del proyecto. Antes de instalar herramientas, crear sistemas o modificar código, se debe leer este documento y actualizar el estado de las tareas afectadas.

## Decisión técnica inicial

- Motor recomendado: Unreal Engine 5.
- Programación inicial: Blueprints para prototipar; C++ solo cuando aporte rendimiento, reutilización o control que Blueprints no resuelva bien.
- Arte 3D: Blender.
- Texturas: Materiales propios, recursos gratuitos con licencia compatible y herramientas del ecosistema de Unreal.
- Audio: Recursos propios o bibliotecas con licencia comercial clara.
- Control de versiones: Git con Git LFS para archivos binarios grandes.
- Plataforma inicial: Windows PC con teclado, mouse y mando.
- Modo inicial: Un jugador y sin conexión.

Estas decisiones son provisionales hasta revisar el hardware disponible y confirmar las preferencias del creador.

## Alcance de la primera versión jugable

El primer prototipo debe contener:

- Un personaje controlable en tercera persona.
- Movimiento, cámara, carrera, salto y fijación de objetivo.
- Ataque ligero, ataque fuerte, esquiva, bloqueo y uso de energía.
- Vida, energía, daño, muerte y reaparición.
- Un punto de descanso que funcione como checkpoint.
- Un enemigo básico con patrulla, detección, persecución, ataque y muerte.
- Un enemigo más resistente o miniboss.
- Un jefe con al menos dos fases o cambios claros de comportamiento.
- Una zona pequeña conectada, con un atajo y un secreto.
- Una moneda o experiencia recuperable después de morir.
- Una mejora sencilla de estadísticas o equipamiento.
- Interfaz mínima para vida, energía, objetivo fijado, moneda y jefe.
- Menú de pausa, opciones básicas, guardado y carga.
- Sonido, música y efectos visuales suficientes para comunicar impactos y peligro.

Quedan fuera del primer prototipo:

- Mundo abierto grande.
- Multijugador.
- Cientos de armas, enemigos o misiones.
- Cinemáticas extensas.
- Creación avanzada de personaje.
- Tienda, monetización o servicios en línea.
- Versiones para consolas o móviles.

## Fases de trabajo

### Fase 0. Definir la visión

- [ ] Escribir una descripción del juego en una frase.
- [ ] Definir el tono visual, el mundo y el conflicto principal.
- [ ] Elegir tres referencias de jugabilidad y tres referencias visuales.
- [ ] Definir qué hará diferente a Ten Fe de otros soulslike.
- [x] Confirmar que se usará Unreal Engine 5.
- [x] Revisar el PC: sistema operativo, procesador, memoria, tarjeta gráfica y espacio libre.
- [x] Definir una meta inicial de 1080p y 60 FPS, ajustable después de medir el prototipo.

Resultado esperado: una visión breve, límites claros y requisitos técnicos confirmados.

### Fase 1. Preparar las herramientas

- [x] Instalar y actualizar Epic Games Launcher.
- [x] Instalar una versión estable de Unreal Engine 5 desde Epic Games Launcher.
- [x] Instalar Visual Studio Community con las herramientas para desarrollo de juegos en C++.
- [x] Instalar Blender.
- [x] Instalar Git y Git LFS.
- [x] Crear el repositorio del proyecto y archivos `.gitignore` y `.gitattributes` apropiados para Unreal y Git LFS.
- [ ] Definir una carpeta externa para cachés y archivos temporales pesados si el disco lo requiere.
- [x] Crear un proyecto de prueba y comprobar que abre, compila y ejecuta.
- [ ] Configurar copia de seguridad del repositorio y de los archivos fuente de arte.

Resultado esperado: entorno funcional y una escena de prueba que se pueda ejecutar sin errores.

### Fase 2. Crear el prototipo de movimiento

- [x] Crear el proyecto base en tercera persona.
- [ ] Configurar entradas con Enhanced Input.
- [ ] Implementar movimiento, cámara, carrera, salto y esquiva.
- [x] Añadir soporte para teclado, mouse y mando.
- [ ] Probar colisiones, pendientes, escaleras y bordes.
- [ ] Ajustar velocidad, aceleración, giro y consumo de energía.

Resultado esperado: controlar al personaje debe sentirse preciso y consistente en una sala de prueba.

### Fase 3. Construir el combate base

- [x] Crear atributos de vida y energía.
- [ ] Implementar ataques ligeros y fuertes.
- [ ] Implementar detección de golpes y recepción de daño.
- [ ] Añadir bloqueo, esquiva e invulnerabilidad temporal.
- [ ] Añadir fijación y cambio de objetivo.
- [ ] Crear reacciones de impacto, interrupción y muerte.
- [ ] Diseñar ventanas de ataque, recuperación y cancelación.
- [ ] Añadir retroalimentación visual y sonora temporal.

Resultado esperado: un duelo simple debe ser comprensible, justo y divertido aun usando modelos provisionales.

### Fase 4. Crear enemigos y comportamiento

- [x] Crear una base reutilizable para enemigos.
- [ ] Implementar patrulla, percepción, persecución y retorno.
- [ ] Implementar selección de ataques por distancia y estado.
- [ ] Añadir navegación y evitar bloqueos comunes.
- [ ] Crear un enemigo básico y una variante resistente.
- [ ] Crear herramientas de depuración para vida, estados y percepción.
- [ ] Crear e integrar el modelo visual definitivo del Paladín del Ocaso. La malla `RefV2` queda únicamente como prototipo técnico y debe sustituirse por una versión detallada aprobada por el usuario.
- [x] Integrar una base visual detallada y texturizada del Paladín del Ocaso como malla estática con Nanite, conservando `RefV2` como respaldo hasta completar rig y animaciones.
- [ ] Crear el conjunto modular del Paladín del Ocaso: espada, escudo, lanza, maza, arco y ballesta; integrar primero la variante Guardián con espada y escudo.
- [x] Crear una variante 3D local del Paladín de asedio élite a partir de la imagen de cuatro vistas y la base normal proporcionadas: fuente Blender, GLB, FBX, texturas y renders separados.
- [x] Validar el GLB del élite por reimportación limpia en Blender: 3.721.278 triángulos, 17 imágenes incrustadas, materiales y UV presentes, sin referencias externas ni elementos del estudio.
- [x] Crear y validar una base separada del élite sin adornos: materiales grises, casco y soporte corporal reconstruidos, placas ajustadas, tela sin bordado y vistas para revisar la silueta.
- [x] Refinar la base en una segunda versión separada: peto con relieve central, hombreras inclinadas, extremidades ajustadas, rodilleras angulares, botas articuladas y capa con pliegues; GLB reimportado y validado.
- [x] Crear la base V3 con visor perforado, casco revisado, cuatro placas alineadas por brazo, rodilleras convexas, telas asimétricas, hebilla y suelas; conservar V2 y validar la nueva exportación.
- [x] Refinar V3 en una base V4 separada: placa abdominal, coderas envolventes, guanteletes y nudillos ajustados, cuello con pliegues compuestos, tejido más oscuro y taloneras; revisar cinco vistas y reimportar el GLB.
- [x] Crear una copia exacta del GLB original adjuntado y comenzar una edición directa de su propia malla en `PaladinElite/DirectMesh`, conservando UV, conectividad y mapas PBR; guardar Blender, GLB y vistas comparables.
- [x] Dar una pasada amplia a la copia en `DirectMesh/V2`: postura con brazos bajos, proporciones robustas, ocho placas de hombro, capa larga, cuello y faldones; conservar las fuentes anteriores y comprobar la exportación por reimportación.
- [x] Continuar la copia en `DirectMesh/V3` con aberturas reales del visor, respiraderos, guanteletes con placas de dedos, cinturón, ajustes de cuello y acabado; guardar una versión separada y validar su GLB.
- [ ] Aprobar la silueta y las proporciones de `PaladinElite_Base` antes de retomar grabados y acabado.
- [ ] Aprobar visualmente el Paladín élite y preparar retopología, rig, skinning y animaciones antes de integrarlo como enemigo definitivo.

Resultado esperado: los enemigos reaccionan al jugador de forma predecible y no dependen de eventos colocados manualmente.

### Fase 5. Implementar el ciclo soulslike

- [ ] Crear puntos de descanso y reaparición.
- [ ] Reponer recursos y reiniciar enemigos al descansar.
- [ ] Otorgar moneda o experiencia al derrotar enemigos.
- [ ] Soltar la moneda al morir y permitir recuperarla una vez.
- [ ] Añadir mejoras simples de atributos.
- [x] Implementar inventario y armas equipables.
- [ ] Guardar progreso, opciones y último checkpoint.

Resultado esperado: explorar, combatir, mejorar, morir y recuperar lo perdido forma un ciclo completo.

### Fase 6. Diseñar el nivel vertical

- [ ] Dibujar un mapa sencillo antes de construirlo.
- [ ] Crear el nivel con geometría provisional.
- [ ] Incluir ruta principal, desvío opcional, atajo y secreto.
- [ ] Colocar encuentros con dificultad progresiva.
- [ ] Usar iluminación y puntos de referencia para orientar al jugador.
- [ ] Probar distancias entre checkpoints y tiempos de regreso al jefe.
- [ ] Reemplazar gradualmente la geometría provisional por arte definitivo.

Resultado esperado: una zona de 15 a 30 minutos que invite a explorar y que pueda recorrerse sin perderse injustamente.

### Fase 7. Crear el jefe

- [ ] Definir la fantasía, silueta y mecánica principal del jefe.
- [ ] Diseñar ataques con señales visuales y sonoras claras.
- [ ] Crear una primera fase estable.
- [ ] Añadir una segunda fase o cambio de comportamiento.
- [ ] Ajustar daño, vida, pausas y oportunidades de castigo.
- [ ] Añadir arena, música, barra de vida y recompensa.
- [ ] Probar con personas que no hayan visto el desarrollo.

Resultado esperado: el jefe se puede aprender, superar de forma consistente y explica sus errores al jugador.

### Fase 8. Presentación y accesibilidad

- [ ] Reemplazar recursos temporales prioritarios.
- [x] Sustituir la forma provisional del primer enemigo por un modelo propio.
- [ ] Mejorar animaciones, cámara, impactos, partículas y audio.
- [ ] Crear interfaz y menús coherentes.
- [ ] Añadir controles reasignables y sensibilidad de cámara.
- [ ] Añadir subtítulos, escalado de interfaz y opciones de volumen.
- [ ] Revisar contraste, legibilidad y señales que no dependan solo del color.
- [ ] Añadir opciones gráficas y límite de fotogramas.

Resultado esperado: el prototipo comunica con claridad, tiene identidad y puede ser probado por distintos jugadores.

### Fase 9. Optimización, pruebas y entrega

- [ ] Definir una lista de equipos objetivo.
- [ ] Medir CPU, GPU, memoria y tiempos de carga.
- [ ] Corregir errores que bloquean progreso, pérdidas de guardado y cierres inesperados.
- [ ] Crear una lista de pruebas manuales repetibles.
- [ ] Generar una versión empaquetada para Windows.
- [ ] Probar la versión en un equipo limpio.
- [ ] Preparar capturas, tráiler corto, descripción y notas conocidas.
- [ ] Distribuir una demo privada antes de publicar.

Resultado esperado: una compilación estable, instalable y suficientemente pulida para recibir comentarios reales.

## Orden recomendado de implementación

1. Movimiento y cámara.
2. Vida, energía y daño.
3. Ataques, esquiva y bloqueo.
4. Fijación de objetivo.
5. Primer enemigo.
6. Muerte, reaparición y checkpoint.
7. Moneda recuperable y progresión.
8. Nivel vertical.
9. Jefe.
10. Guardado, opciones, sonido y pulido.

No se debe comenzar con arte definitivo, mundo abierto o una gran cantidad de contenido antes de validar los puntos 1 a 7.

## Arquitectura inicial propuesta

La estructura exacta se decidirá al crear el proyecto, pero debe separar estas responsabilidades:

- `Character`: movimiento, entrada y coordinación del personaje.
- `Combat`: ataques, armas, colisiones, bloqueo y esquiva.
- `Attributes`: vida, energía, estadísticas y estados.
- `AI`: percepción, decisiones, navegación y comportamiento enemigo.
- `Interaction`: checkpoints, objetos, puertas y elementos utilizables.
- `Inventory`: objetos, equipamiento y moneda.
- `Save`: progreso, opciones y restauración de estado.
- `UI`: HUD, menús, indicadores y accesibilidad.
- `World`: niveles, encuentros, iluminación y flujo de exploración.
- `AudioVFX`: sonidos, música, partículas y respuesta de impacto.

Se debe reutilizar una base común para personajes y enemigos cuando sea razonable, evitando un Blueprint gigante que concentre todos los sistemas.

## Reglas de trabajo para Codex

Antes de cada tarea:

1. Leer este archivo.
2. Revisar solo los archivos y sistemas relacionados con la tarea.
3. Explicar el objetivo, el alcance, los archivos candidatos y el riesgo.
4. Pedir confirmación antes de instalar software pesado, cambiar la arquitectura, añadir dependencias grandes, borrar archivos o realizar migraciones.
5. Usar recursos con licencia clara y registrar su origen.

Después de cada tarea:

1. Ejecutar las pruebas disponibles.
2. Indicar qué cambió, qué archivos se modificaron y cómo probarlo.
3. Actualizar las casillas y las secciones Estado actual y Registro de decisiones.
4. Registrar errores conocidos y el siguiente paso recomendado.
5. No declarar una fase terminada si falta validación manual o una compilación necesaria.

## Mapa dinámico del proyecto

- Objetivo actual: transformar la copia real del GLB Meshy en la variante élite mediante pasadas amplias, según la petición de avanzar con cambios más visibles. La versión activa es `PaladinElite/DirectMesh/V3`: continúa la V2 guardada y añade aberturas del casco, guanteletes y cinturón, además de corregir encajes y acabado. Las fuentes originales y las versiones anteriores se conservan.
- Framework o motor detectado: Unreal Engine 5.8.3 instalado.
- Punto de entrada: `TenFe.uproject`, módulo C++ `Source/TenFe` y `ATenFeGameMode`.
- Flujo actual: el mapa del motor carga `ATenFeGameMode`, crea `ATenFeCharacter`, presenta HUD y menú de equipo, genera un muñeco de entrenamiento y crea un enemigo paladín que detecta, persigue, ataca, muere y reaparece.
- Flujo esperado: herramientas, proyecto base, movimiento, combate, enemigos, ciclo de muerte, nivel y jefe.
- Componentes conectados: `ATenFeCharacter`, `UTenFeStatsComponent`, `UTenFeEquipmentComponent`, `UTenFeHUDWidget`, `UTenFeEquipmentMenuWidget`, `ATenFeTrainingDummy` y `ATenFeEnemy`.
- Servicios o sistemas conectados: movimiento, cámara, salto, carrera, vida, energía, daño, defensa, tres armas, tres piezas de armadura, equipo, enemigo básico, malla detallada `SM_PaladinSoldier_Meshy`, material `M_Paladin_Meshy_PBR`, tres texturas PBR, espada provisional `SM_PaladinGreatsword`, especificación modular `WEAPON_SET.md`, referencia visual `PaladinGuardian_Concept.png` y respaldo `SM_PaladinSoldier_RefV2`. El nuevo `PaladinElite` permanece como fuente artística local y todavía no está conectado al juego.
- Estado y navegación: TAB abre/cierra equipo; E cambia de arma; mouse y mando controlan movimiento, cámara, ataque y carrera.
- Patrones que deben respetarse: separación por sistemas, cambios pequeños, pruebas frecuentes y recursos con licencia comprobable.
- Archivos principales: este plan, `TenFe.uproject`, `Source/TenFe/AI/TenFeEnemy.cpp`, `Content/Characters/Enemies/Paladin/`, `Assets/Characters/Enemies/Paladin/`, `Assets/Characters/Enemies/Paladin/WEAPON_SET.md`, `Tools/Blender/prepare_meshy_paladin.py` y `Tools/Unreal/import_meshy_paladin.py`. Para el élite: `Assets/Characters/Enemies/PaladinElite/`, `Tools/Blender/create_paladin_elite.py`, `elite_ornament.py`, `elite_textiles.py` y `validate_paladin_elite.py` en la misma carpeta de herramientas.
- Archivos que no se deben tocar: binarios, cachés, archivos generados y recursos externos sin licencia confirmada.
- Archivos del modelo activo: `Assets/Characters/Enemies/PaladinElite/DirectMesh/V3/Paladin_Meshy_Elite_V3.blend`, `Paladin_Meshy_Elite_V3.glb`, cinco renders, `validation_v3.json`, `README.md` y `Tools/Blender/advance_paladin_direct_v3.py`. La malla base conserva sus vértices, conectividad, UV y tres mapas PBR; el modificador Boolean del visor añade cortes en la geometría evaluada y exportada. El control `06_V3_Cuello_y_ajustes` incluye la forma V2 y la corrección del cuello; 01–05 quedan a cero. Las piezas añadidas y los cortadores no siguen automáticamente esos controles. Colecciones nuevas `05_V3_Protecciones`, `06_V3_Cierres_y_Bordes` y `91_V3_Herramientas_Visor`. Sin rig ni conexión al juego.
- Riesgo actual: la V3 artística está separada del juego. Mide 2,105 m y ronda los 0,8 millones de triángulos, con muchas piezas y sin retopología, rig, animaciones ni LOD; no debe tratarse como personaje animado terminado. El estudio histórico de 3,72 millones de triángulos permanece separado. Siguen pendientes aprobación visual, coherencia de materiales, ajustes finos y revisión de solapamientos en movimiento. El conjunto de armas y el problema previo de Unreal/Zen pertenecen a tareas separadas.

## Estado actual

- Fase activa: Fase 2, crear el prototipo de movimiento, con una primera base de la Fase 4 ya integrada.
- Último avance: V3 creada desde el Blender V2 guardado. Se abrieron dos ranuras oculares y doce respiraderos en el casco mediante un modificador editable, se añadieron interior oscuro y refuerzos del visor, puños, placas dorsales y 22 placas de dedos, además de un cinturón con hebilla. Se corrigieron las crestas del cuello por detrás y se ajustó el acabado de los materiales añadidos; los mapas Meshy originales se conservan.
- Revisión de esta entrega: rayos sobre el cuerpo evaluado confirman las aberturas oculares. GLB reimportado con recuento de triángulos coincidente, coordenadas finitas, materiales y mapas incrustados; sin dependencias externas, estudio ni cortadores. Hashes de V2, UV y conectividad base conservados; tres imágenes originales sin cambios de bytes. Cinco renders revisan conjunto, frontal, espalda, casco y guantelete. Informe en `DirectMesh/V3/validation_v3.json`; la pose sigue siendo estática, sin prueba de animación.
- Bloqueos: no hay bloqueo de servicio externo para la variante élite, creada íntegramente de forma local sobre el GLB facilitado. Sigue pendiente la aprobación artística del usuario y el trabajo de producción: retopología, pose de rig, skinning, animaciones y validación dentro de Unreal. La geometría densa y las piezas superpuestas son de presentación. Las armas y la configuración inválida de Unreal/Zen permanecen pendientes de tareas separadas.
- Siguiente paso recomendado: continuar desde `DirectMesh/V3/Paladin_Meshy_Elite_V3.blend`, priorizando coherencia entre metal original y añadido, caída de faldones, transiciones entre placas y anatomía de manos. Revisar el conjunto con la referencia antes de iniciar retopología o rig. No regenerar encima de cambios manuales posteriores. Animaciones e integración definitiva continúan pendientes.

## Decisiones pendientes

- ¿Unreal Engine 5 será el motor definitivo?
- ¿La cámara y el combate serán similares a Elden Ring, Sekiro o una mezcla propia?
- ¿Cuál será la ambientación: medieval, religiosa, oscura, fantástica, futurista u otra?
- ¿Qué habilidad o mecánica hará único a Ten Fe?
- ¿Se usará arte realista, estilizado o una combinación?
- ¿Qué especificaciones tiene el PC de desarrollo?
- ¿El primer objetivo será una demo para portafolio, una publicación comercial o aprendizaje?

## Registro de decisiones

| Fecha | Decisión | Motivo | Estado |
|---|---|---|---|
| 2026-10-11 | Limitar la primera meta a un prototipo vertical | Un juego del tamaño de Elden Ring requiere un equipo grande, varios años y un presupuesto elevado | Provisional |
| 2026-10-11 | Usar Unreal Engine 5, Blender, Visual Studio, Git y Git LFS | Es una base adecuada para acción 3D, creación de recursos y control de versiones | Confirmado |
| 2026-10-11 | Objetivo inicial de 1080p a 60 FPS | El equipo tiene un i7-11800H, 16 GB de RAM, una RTX 3060 Laptop y espacio suficiente; se medirán Nanite, Lumen y calidad de texturas antes de fijar ajustes definitivos | Provisional |
| 2026-10-11 | Usar Unreal Engine 5.8.3 y un proyecto Blueprint de tercera persona | La versión instalada ofrece la plantilla oficial con movimiento, cámara y Enhanced Input adecuados como punto de partida | Confirmado |
| 2026-10-12 | Crear la base jugable como módulo C++ modular y mantener Blueprints para contenido futuro | Permite compilar y probar sistemas sin depender de recursos binarios, manteniendo vida, equipo y UI separados | Confirmado |
| 2026-10-12 | Incluir tres armas y tres piezas de armadura provisionales | Permite validar daño, defensa, peso y selección de equipo antes de producir modelos definitivos | Confirmado |
| 2026-10-12 | Diseñar el Paladín del Ocaso como enemigo medieval oscuro original, sin copiar personajes ni emblemas de Elden Ring | Conserva la referencia general soulslike y evita depender de recursos externos o identidades visuales ajenas | Confirmado |
| 2026-10-12 | Integrar primero el paladín como malla estática y conservar el generador de Blender | Permite validar silueta, escala y combate antes de invertir en rig, skinning y animaciones | Confirmado |
| 2026-10-12 | Rehacer el paladín usando las tres vistas ortográficas proporcionadas por el usuario y separar la espada del cuerpo | Acerca la silueta a la referencia y permite mover el arma con el componente de ataque sin modificar la IA | Confirmado |
| 2026-10-12 | Considerar `SM_PaladinSoldier_RefV2` solo un prototipo y generar una nueva base HD mediante cuatro vistas coherentes en Tripo | El usuario requiere una armadura realista y detallada; las primitivas de Blender no alcanzan la fidelidad visual solicitada | En curso |
| 2026-10-12 | No contratar automáticamente el plan de Tripo al encontrar el bloqueo de multivista/exportación | El plan exige un cargo anual de €108 y toda compra requiere una decisión expresa del usuario | Confirmado |
| 2026-10-12 | Probar Meshy con las cuatro referencias y los créditos gratuitos antes de contratar un servicio | Meshy permite activar visión múltiple y concede 100 créditos al registrarse, aunque la exportación gratuita puede depender del modelo generado | Confirmado; se usó Meshy 6 Lite con una vista |
| 2026-10-12 | Adoptar el modelo Meshy descargado bajo CC BY 4.0 como nueva base visual estática del enemigo | Supera claramente la apariencia geométrica de `RefV2`, incluye mapas PBR y puede validarse en Unreal antes de invertir en retopología y rig | Confirmado como base, pendiente como personaje animado definitivo |
| 2026-10-12 | Crear seis armas coherentes y reutilizar un solo Paladín del Ocaso en cinco variantes: Guardián, Lancero, Macero, Arquero y Ballestero | Aumenta la variedad de combate sin duplicar el personaje, el rig ni toda la IA; la producción se hará por etapas para proteger el alcance del prototipo | Confirmado; referencias y especificación registradas |
| 2026-10-13 | Crear el Paladín de asedio élite localmente en Blender, sin servicios remotos de generación | El usuario pidió evaluar el nivel de modelado propio usando su imagen y GLB normal como referencia; Blender ya estaba instalado y no fueron necesarias herramientas adicionales | Modelo de presentación creado; aprobación visual pendiente |
| 2026-10-13 | Conservar el élite como recurso separado con fuente editable, exportaciones y validación independiente | Permite revisar geometría y detalle sin sustituir el enemigo normal ni confundir una pose estática de alta densidad con un personaje listo para animarse | Confirmado; integración en Unreal pendiente |
| 2026-10-13 | Priorizar una base limpia del élite y posponer adornos | El usuario pidió crear primero el modelo base; los materiales grises y la ausencia de grabados permiten evaluar la silueta y el ajuste de las placas | Base creada y validada técnicamente; aprobación de proporciones pendiente |
| 2026-10-13 | Refinar las formas de la base en `Base/V2` y conservar la primera versión | El usuario pidió seguir mejorando el modelo; se reconstruyeron las placas principales y sus proporciones con superficies editables locales, sin volver todavía al acabado ornamental | Segunda base validada por reimportación; aprobación artística pendiente |
| 2026-10-13 | Continuar en `Base/V3` con construcción del casco, solapamientos y caída de telas | El usuario pidió seguir mejorando; los respiraderos, pivotes, hebilla y bordes son elementos funcionales de la base, manteniendo pendientes los grabados y acabados | Tercera base creada localmente y validada; V2 conservada |
| 2026-10-13 | Crear V4 a partir del archivo V3 guardado y priorizar peto, coderas, manos y tela | El usuario pidió más mejoras; se afinó la construcción y el encaje de las piezas sin retomar todavía adornos ni reemplazar versiones anteriores | V4 validada por reimportación y cinco vistas; aprobación artística pendiente |
| 2026-10-14 | Adoptar una copia exacta del GLB original como nueva línea de edición directa | El usuario indicó crear una copia y modificar ese modelo; se mantienen sus vértices, UV, conectividad y materiales mediante shape keys independientes, conservando las bases grises anteriores | Copia verificada por SHA256 y primera edición validada; aprobación artística pendiente |
| 2026-10-14 | Avanzar por pasadas amplias sobre la copia y guardar una V2 separada | El usuario pidió cambios mayores; se modifica la silueta completa con postura, volumen, ocho placas de hombro y telas, conservando la malla original y su PBR | Versión de presentación local; aprobación artística y preparación para animación pendientes |
| 2026-10-14 | Continuar desde V2 en una V3 separada con cortes editables del casco y protecciones de manos | El usuario pidió seguir; se conservan datos y mapas de la malla base, mientras los modificadores generan las nuevas aberturas en la exportación | Validación técnica local; acabado artístico y animación pendientes |

## Riesgos principales

- Alcance excesivo: reducir cada idea a una versión comprobable en pocos días o semanas.
- Combate sin buena sensación: validar con recursos provisionales antes de crear arte definitivo.
- Archivos demasiado grandes: configurar Git LFS y exclusiones antes de producir contenido.
- Recursos sin licencia: conservar enlaces, autor, licencia y comprobante de descarga.
- Pérdida de trabajo: usar control de versiones y copias de seguridad desde el inicio.
- Rendimiento: medir desde el prototipo y no esperar al final.
- Dependencia de tutoriales: comprender y adaptar cada sistema en vez de copiar proyectos completos.

## Criterio de éxito del primer prototipo

El prototipo estará completo cuando una persona pueda instalarlo, aprender los controles, recorrer una zona, abrir un atajo, derrotar enemigos, morir, recuperar su moneda, mejorar al personaje y vencer al jefe sin ayuda del desarrollador, manteniendo estabilidad y rendimiento aceptables en el equipo objetivo.
