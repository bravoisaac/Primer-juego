# Ten Fe · Santuario del Ocaso

Base soulslike original para Windows, creada desde cero en **Unity 6.3 / 6000.3.26f1**. Un peregrino recorre el santuario de un panteón extinguido y recupera la chispa de Aster, dios del Ocaso. Nerea, diosa de la memoria, conserva una reliquia en la galería del claustro oeste. Estos nombres son una propuesta inicial editable.

## Jugar

Abre `Builds/Windows/TenFe.exe` o ejecuta `Jugar.cmd`. Mantén el ejecutable junto a su carpeta `TenFe_Data`, `UnityPlayer.dll` y las demás dependencias de la compilación. La carpeta Builds es local y está excluida de Git.

## Editar en Unity

En Unity Hub elige **Add / Add project from disk** y selecciona esta carpeta (`Unity/TenFe`, no la raíz del proyecto Unreal). Usa el editor **6000.3.26f1** instalado. Abre `Assets/Scenes/Santuario.unity` y pulsa Play. También puedes usar `AbrirUnity.cmd`.

La escena contiene geometría, personajes y referencias editables. `Ten Fe > Crear o reconstruir santuario` reconstruye la escena original: guarda primero tus cambios manuales en otra escena. `Ten Fe > Compilar Windows` compila la escena guardada sin reconstruirla.

El mapa incluye el **Claustro de la Memoria**: patio de ceniza con fuente seca, galería con sepulcros y retablo de Nerea, conectados al santuario por dos puentes. Añade 1.800 m² de plataforma a los 2.112 m² originales (aproximadamente +85 %, antes de descontar obstáculos), con un ancho total aproximado de 70 m. `Ten Fe > Ampliar santuario con claustro oeste` actualiza una escena antigua de forma aditiva; si el claustro ya existe, conserva sus cambios manuales. La reconstrucción completa también lo incluye. La superficie no acredita una duración de juego concreta.

`Ten Fe > Aplicar ambientación al santuario guardado` actualiza luz, cielo, materiales y efectos de la escena existente. Conserva la geometría y las colisiones, pero vuelve a aplicar los valores artísticos de `AtmosphereInstaller.cs`. Para ajustes cotidianos, edita los materiales de `Assets/Art/Atmosphere`, las luces o `SanctuaryImageEffect` en la cámara y compila normalmente.

## Controles

| Acción | Control |
|---|---|
| Movimiento / cámara | WASD / mouse |
| Carrera / salto | Shift / F |
| Ataque ligero / fuerte | Clic izquierdo / Q |
| Bloqueo frontal | Mantener clic derecho |
| Esquiva | Espacio + dirección |
| Fijar o cambiar objetivo / soltar si no hay otro | Tab o clic central |
| Curación (3 cálices) | R |
| Descansar, reliquia, palanca, recuperar fe | E |
| Comprar vitalidad junto a un altar | V |
| Ayuda / pausa y opciones | H / Escape |

La interfaz utiliza paneles de bronce y ceniza y mantiene las proporciones en ventanas 4:3 y 16:9. La barra de vida conserva brevemente el daño reciente; los tres indicadores del cáliz muestran sus cargas. Un vestigio pendiente muestra la fe recuperable. Los avisos de ataque priorizan una sola amenaza cercana con línea de visión.

Puedes pulsar la siguiente acción hasta 200 ms antes de terminar la recuperación de la actual. Se conserva solo la última pulsación: no cancela ataques ni acumula una secuencia. La esquiva retiene la dirección elegida al pulsarla. Si al ejecutar faltan energía, suelo o cálices, el intento se descarta. Pausar, morir, reaparecer o recibir un impacto que interrumpe limpia la acción pendiente.

Al fijar un enemigo, la cámara se desplaza ligeramente hacia el hombro para despejar su silueta. Cerca de una pared se acerca de inmediato y recupera su distancia suavemente al salir. La sacudida de impacto también respeta la colisión.

En un altar, el panel muestra el coste de la bendición y sus +25 de vida, o indica que alcanzaste el nivel máximo. H abre los controles agrupados; el mundo continúa activo mientras los consultas. Escape pausa y permite ajustar volumen y sensibilidad con sus valores visibles. Mando, reasignación y tamaño de interfaz configurable siguen pendientes.

## Recorrido y reglas

1. Avanza desde las estatuas hasta la llama dorada y descansa.
2. Cruza el primer arco para enfrentarte al custodio de la nave, o toma el puente a la izquierda después del primer altar para explorar el patio de ceniza y su custodio. Anuncian sus golpes: esquiva y aprovecha su recuperación. Un ataque fuerte interrumpe a los enemigos comunes.
3. El paladín es más resistente. Correr, atacar, bloquear y esquivar consumen energía; una guardia agotada se rompe.
4. Desde el patio oeste, sigue las losas claras hasta el portal de la galería. La reliquia de Nerea está frente al retablo del fondo y entrega 75 de fe. El puente norte devuelve a la nave, cerca del segundo altar. A la derecha del altar continúa el camino este: su palanca abre la reja del regreso al santuario.
5. Usa fe para aumentar la vida en un altar. Descansar restaura recursos y reinicia enemigos comunes. Los enemigos cercanos en combate impiden descansar.
6. Aster cambia de ritmo al bajar de media vida. Su derrota se conserva al descansar y al cargar.

Al morir dejas tu fe en un vestigio. Recuperarlo devuelve esa cantidad; otra muerte sustituye el vestigio anterior. Reapareces en el último altar. La fe, vitalidad, atajo, reliquia, jefe y último altar se guardan tras acciones importantes y al salir. Al cargar reapareces en el altar con los enemigos comunes reiniciados.

Guardado: `%USERPROFILE%\AppData\LocalLow\TenFe\Ten Fe - Santuario del Ocaso\pilgrim-v1.json`. La escritura conserva una copia `.bak`. Si el archivo está dañado o es incompatible, se inicia una sesión temporal que protege el original y muestra un aviso. Para iniciar de nuevo, cierra el juego y mueve el JSON a una carpeta de respaldo.

## Arquitectura

- `Assets/Scripts/Character`: entrada, `PlayerActionBuffer` para retener un único intento, movimiento y cámara con colisión y retorno suave.
- `Assets/Scripts/Combat`: vida, energía, ángulos y obstrucción de golpes.
- `Assets/Scripts/AI`: patrulla con pausas, observación, persecución con aceleración y giros graduales, acercamiento lento, frenado, anticipación, ataque, regreso y fases.
- `Assets/Scripts/World`: escena, interacciones y coordinación del ciclo.
- `Assets/Scripts/Save`: datos versionados y guardado con reemplazo de archivo.
- `Assets/Scripts/Presentation`: `GameHud` conecta estado y opciones a la interfaz; `HudTheme` reúne estilos, símbolos y texturas reutilizables. También incluye sonido sintético, poses provisionales y `SentinelVisual` para animación esquelética del enemigo.
- `SanctuaryAtmosphere` anima la intensidad de las llamas; `SanctuaryImageEffect` añade brillo suave y viñeta, con retorno al renderizado normal si el shader no está disponible.
- `Assets/Art/GildedSentinel`: modelo del usuario con rig, siete clips de animación, materiales y prefab.
- `Assets/Art/Atmosphere`: cielo con nubes, piedra y bronce erosionados, fuego/brasas, estandartes al viento y acabado de cámara; recursos originales definidos por shaders y una malla editable.
- `Assets/Editor`: generación, validación y compilación. `SanctuaryExpansion` añade el claustro a la escena guardada sin reconstruir el santuario; conserva referencias de progreso y reubica un custodio y la reliquia existentes.
- `Assets/Scripts/Validation`: comprobaciones dentro del ejecutable con `--smoke-test`; `ResponsivenessChecks` cubre pulsaciones durante recuperación, pausa, restauración y comportamiento de cámara frente a obstáculos.
- `ExpansionChecks` recorre ambos puentes y la galería con la cápsula real en ambos sentidos, prueba suelo/pretiles, acceso a reliquia y percepción/ataque del custodio reubicado; genera `mapa_claustro.png`, `mapa_nerea.png` y `mapa_general.png`.

Sin paquetes externos, red, cuentas ni servicios dentro del juego. Se utilizan el renderizador integrado y el Input Manager del editor para mantener esta base pequeña. La entrada aún no está abstraída para mando ni reasignación.

## Verificación reproducible

Con el editor cerrado, ejecuta `Validar.ps1` desde PowerShell. Compila **la escena guardada** y ejecuta las comprobaciones del ciclo de juego en una sesión aislada. No usa ni sobrescribe tu partida. Los informes y capturas quedan en `Docs/Validation`; los logs, en `Logs`. Durante las capturas de interfaz la ventana de pruebas puede aparecer y cambiar de resolución; se cierra automáticamente al terminar.

Validación más reciente, **2026-11-06: 13 comprobaciones de reglas + 117 de ejecución aprobadas (130 en total)**. Añade diez comprobaciones del mapa ampliado y tres vistas revisadas: `mapa_claustro.png`, `mapa_nerea.png` y `mapa_general.png`. Se recorrieron ambos accesos y la galería con la cápsula real en ambos sentidos, se probaron pretiles, reliquia y custodio. Se corrigieron dos columnas que obstruían los pasos. Reaplicar la ampliación no duplicó geometría. El aviso intermitente de búfer gráfico D3D11 reapareció durante las capturas de la ejecución final; no hubo errores del motor ni fallos de comprobaciones. Siguen pendientes la partida manual, el retorno del custodio por recorridos complejos y la medición de FPS.

Validación del 2026-11-03: **13 comprobaciones de reglas y guardado + 107 de ejecución aprobadas (120 en total)**. Incluye combate, progresión, movimiento gradual, skin del centinela, ambientación, presentación y 17 comprobaciones nuevas de respuesta de acciones y cámara. Se verifican caducidad y ejecución única de intentos, pausa, gasto de energía, retorno tras obstáculos y colisión al desplazar el encuadre junto a paredes laterales. Se mantienen diez capturas completas de interfaz: juego, ayuda, pausa, altar con bendición máxima, objetivo preparando un golpe, jefe en fase II y muerte. Hay vistas a 1280×720, 1024×768 y 1920×1080. Los archivos `hud_*.png` incluyen IMGUI; las vistas de cámara anteriores lo excluyen. Los clics y teclas físicos, la comodidad del encuadre, el contacto fino de pies y el equilibrio aún requieren la partida manual de `Docs/PRUEBAS_MANUALES.md`.

Vistas de ambientación: `Docs/Validation/atmosfera_entrada.png`, `atmosfera_patio.png` y `atmosfera_templo.png`. Son capturas del ejecutable sin HUD. Los efectos tienen un máximo conjunto de 920 partículas y el brillo se procesa a un cuarto del ancho/alto de la imagen. Esto limita el coste, pero todavía falta medir FPS a 1080p y probar en otro equipo.

La compilación Windows usa deformación de modelos en GPU (`PlayerSettings.meshDeformation`), según la [API oficial de Unity](https://docs.unity.cn/6000.2/Documentation/ScriptReference/PlayerSettings-meshDeformation.html). Esta medida redujo el aviso de búfer gráfico, pero ha reaparecido de forma intermitente; no se considera resuelto. Skin, combate y reaparición pasaron sus comprobaciones.

`ProjectTools.ValidateAndBuild` se reserva para validar la escena original generada y **sí la reconstruye**. Para el trabajo diario usa `ProjectTools.ValidateExistingAndBuild`.

## Estado y límites

Es una base jugable con una zona pequeña, tres guardianes, un jefe de dos ritmos, dos altares, atajo, secreto, progresión y guardado. Los tres guardianes usan el GLB del usuario con rig y animaciones de reposo, caminar, correr, anticipación, ataque, impacto y muerte. El jugador, Aster y el escenario conservan su presentación provisional. No es una demo terminada de 15–30 minutos. Faltan pulido de pesos y animaciones, ajuste manual del combate, mando, reasignación, navegación avanzada, accesibilidad y medición de rendimiento en otros equipos.

El proyecto Unreal y todos los modelos anteriores permanecen en la raíz del repositorio. Una copia del Paladín proporcionada por el usuario se redujo a unos 55.000 triángulos y recibió un rig de 20 huesos para esta integración. Los modelos del élite anteriores no se han modificado ni incorporado.

## Recursos

Geometría del santuario, poses del jugador y tonos sintetizados creados localmente. El cuerpo y las texturas del centinela proceden del GLB Meshy facilitado por el usuario (CC BY 4.0 según el registro histórico del mismo archivo). Rig, animaciones y espada se crearon localmente para esta adaptación. Consulta `Docs/RECURSOS.md`, `Docs/THIRD_PARTY_NOTICES.txt` y el plan principal del repositorio. No se utilizaron recursos de pago.

Editor utilizado: [Unity 6000.3.26f1](https://unity.com/releases/editor/whats-new/6000.3.26f1). Automatización: [referencia oficial de argumentos del editor](https://docs.unity.com/en-us/engine/6000.6/manual/unity-editor/command-line-arguments/editor).
