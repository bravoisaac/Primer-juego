# Ten Fe · Santuario del Ocaso

Base soulslike original para Windows, creada desde cero en **Unity 6.3 / 6000.3.26f1**. Un peregrino recorre el santuario de un panteón extinguido y recupera la chispa de Aster, dios del Ocaso. Nerea, diosa de la memoria, conserva una reliquia en el camino del regreso. Estos nombres son una propuesta inicial editable.

## Jugar

Abre `Builds/Windows/TenFe.exe` o ejecuta `Jugar.cmd`. Mantén el ejecutable junto a su carpeta `TenFe_Data`, `UnityPlayer.dll` y las demás dependencias de la compilación. La carpeta Builds es local y está excluida de Git.

## Editar en Unity

En Unity Hub elige **Add / Add project from disk** y selecciona esta carpeta (`Unity/TenFe`, no la raíz del proyecto Unreal). Usa el editor **6000.3.26f1** instalado. Abre `Assets/Scenes/Santuario.unity` y pulsa Play. También puedes usar `AbrirUnity.cmd`.

La escena contiene geometría, personajes y referencias editables. `Ten Fe > Crear o reconstruir santuario` reconstruye la escena original: guarda primero tus cambios manuales en otra escena. `Ten Fe > Compilar Windows` compila la escena guardada sin reconstruirla.

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

## Recorrido y reglas

1. Avanza desde las estatuas hasta la llama dorada y descansa.
2. Cruza el primer arco. Los custodios anuncian sus golpes: esquiva y aprovecha su recuperación. Un ataque fuerte interrumpe a los enemigos comunes.
3. El paladín es más resistente. Correr, atacar, bloquear y esquivar consumen energía; una guardia agotada se rompe.
4. A la derecha, antes del templo, encontrarás el segundo altar y el acceso al camino lateral. La palanca abre la reja del regreso; la reliquia de Nerea entrega 75 de fe.
5. Usa fe para aumentar la vida en un altar. Descansar restaura recursos y reinicia enemigos comunes. Los enemigos cercanos en combate impiden descansar.
6. Aster cambia de ritmo al bajar de media vida. Su derrota se conserva al descansar y al cargar.

Al morir dejas tu fe en un vestigio. Recuperarlo devuelve esa cantidad; otra muerte sustituye el vestigio anterior. Reapareces en el último altar. La fe, vitalidad, atajo, reliquia, jefe y último altar se guardan tras acciones importantes y al salir. Al cargar reapareces en el altar con los enemigos comunes reiniciados.

Guardado: `%USERPROFILE%\AppData\LocalLow\TenFe\Ten Fe - Santuario del Ocaso\pilgrim-v1.json`. La escritura conserva una copia `.bak`. Si el archivo está dañado o es incompatible, se inicia una sesión temporal que protege el original y muestra un aviso. Para iniciar de nuevo, cierra el juego y mueve el JSON a una carpeta de respaldo.

## Arquitectura

- `Assets/Scripts/Character`: entrada, movimiento y cámara con colisión.
- `Assets/Scripts/Combat`: vida, energía, ángulos y obstrucción de golpes.
- `Assets/Scripts/AI`: patrulla con pausas, observación, persecución con aceleración y giros graduales, acercamiento lento, frenado, anticipación, ataque, regreso y fases.
- `Assets/Scripts/World`: escena, interacciones y coordinación del ciclo.
- `Assets/Scripts/Save`: datos versionados y guardado con reemplazo de archivo.
- `Assets/Scripts/Presentation`: HUD, opciones, sonido sintético, poses provisionales y `SentinelVisual` para animación esquelética del enemigo.
- `SanctuaryAtmosphere` anima la intensidad de las llamas; `SanctuaryImageEffect` añade brillo suave y viñeta, con retorno al renderizado normal si el shader no está disponible.
- `Assets/Art/GildedSentinel`: modelo del usuario con rig, siete clips de animación, materiales y prefab.
- `Assets/Art/Atmosphere`: cielo con nubes, piedra y bronce erosionados, fuego/brasas, estandartes al viento y acabado de cámara; recursos originales definidos por shaders y una malla editable.
- `Assets/Editor`: generación, validación y compilación.
- `Assets/Scripts/Validation`: comprobaciones dentro del ejecutable con `--smoke-test`.

Sin paquetes externos, red, cuentas ni servicios dentro del juego. Se utilizan el renderizador integrado y el Input Manager del editor para mantener esta base pequeña. La entrada aún no está abstraída para mando ni reasignación.

## Verificación reproducible

Con el editor cerrado, ejecuta `Validar.ps1` desde PowerShell. Compila **la escena guardada** y ejecuta las comprobaciones del ciclo de juego en una sesión aislada. No usa ni sobrescribe tu partida. Los informes y vistas de la cámara (sin HUD) quedan en `Docs/Validation`; los logs, en `Logs`.

Validación del 2026-11-02: **13 comprobaciones de reglas y guardado + 74 de ejecución aprobadas**. Incluye combate, progresión, movimiento gradual, skin del centinela y ocho comprobaciones nuevas de ambientación: carga de cielo/niebla, soporte de shaders, diez luces de fuego, ausencia de nuevas colisiones, partículas activas con presupuesto limitado y tres vistas del santuario. Walk/Run conservan la fase de zancada y ajustan su cadencia a la velocidad. La interfaz IMGUI, los controles físicos, el contacto fino de pies y el equilibrio aún requieren la partida manual de `Docs/PRUEBAS_MANUALES.md`.

Vistas de ambientación: `Docs/Validation/atmosfera_entrada.png`, `atmosfera_patio.png` y `atmosfera_templo.png`. Son capturas del ejecutable sin HUD. Los efectos tienen un máximo conjunto de 920 partículas y el brillo se procesa a un cuarto del ancho/alto de la imagen. Esto limita el coste, pero todavía falta medir FPS a 1080p y probar en otro equipo.

La compilación Windows usa deformación de modelos en GPU (`PlayerSettings.meshDeformation`), según la [API oficial de Unity](https://docs.unity.cn/6000.2/Documentation/ScriptReference/PlayerSettings-meshDeformation.html). En la prueba local final desapareció el aviso de búfer gráfico que aparecía con la deformación en CPU; skin, combate y reaparición pasaron sus comprobaciones.

`ProjectTools.ValidateAndBuild` se reserva para validar la escena original generada y **sí la reconstruye**. Para el trabajo diario usa `ProjectTools.ValidateExistingAndBuild`.

## Estado y límites

Es una base jugable con una zona pequeña, tres guardianes, un jefe de dos ritmos, dos altares, atajo, secreto, progresión y guardado. Los tres guardianes usan el GLB del usuario con rig y animaciones de reposo, caminar, correr, anticipación, ataque, impacto y muerte. El jugador, Aster y el escenario conservan su presentación provisional. No es una demo terminada de 15–30 minutos. Faltan pulido de pesos y animaciones, ajuste manual del combate, mando, reasignación, navegación avanzada, accesibilidad y medición de rendimiento en otros equipos.

El proyecto Unreal y todos los modelos anteriores permanecen en la raíz del repositorio. Una copia del Paladín proporcionada por el usuario se redujo a unos 55.000 triángulos y recibió un rig de 20 huesos para esta integración. Los modelos del élite anteriores no se han modificado ni incorporado.

## Recursos

Geometría del santuario, poses del jugador y tonos sintetizados creados localmente. El cuerpo y las texturas del centinela proceden del GLB Meshy facilitado por el usuario (CC BY 4.0 según el registro histórico del mismo archivo). Rig, animaciones y espada se crearon localmente para esta adaptación. Consulta `Docs/RECURSOS.md`, `Docs/THIRD_PARTY_NOTICES.txt` y el plan principal del repositorio. No se utilizaron recursos de pago.

Editor utilizado: [Unity 6000.3.26f1](https://unity.com/releases/editor/whats-new/6000.3.26f1). Automatización: [referencia oficial de argumentos del editor](https://docs.unity.com/en-us/engine/6000.6/manual/unity-editor/command-line-arguments/editor).
