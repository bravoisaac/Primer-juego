# Primera partida de revisión

Estado: pendiente de realizar con ventana visible y controles físicos. Las 154 comprobaciones automáticas (2026-11-06: 11 de clips, 13 de reglas y 130 de ejecución) y las capturas no sustituyen esta revisión de sensación, legibilidad y dificultad; especialmente falta valorar las animaciones renovadas, recorrer el claustro, comprobar retorno del custodio, los 200 ms de entrada y la cámara de hombro. El aviso intermitente de búfer gráfico D3D11 reapareció durante las capturas; medir FPS y comprobar si también ocurre al jugar.

- [ ] Abrir `Jugar.cmd`; verificar que se ven personaje, escenario, vida, energía y cálices.
- [ ] Revisar cielo del eclipse, detalle de piedra/bronce, estandartes al viento, fuego y brasas desde entrada, patio y templo; comprobar que las sombras permiten distinguir enemigos y bordes.
- [ ] Pausar junto a una llama: partículas, telas y parpadeo deben detenerse y continuar al reanudar. Medir rendimiento a 1080p, incluyendo combate junto a varios braseros.
- [ ] Pulsar H y comprobar que los controles se leen sin recortes.
- [ ] Alternar ventana 4:3 y 16:9: verificar paneles anclados a los bordes, proporciones de símbolos y texto legible. Las capturas automáticas cubren 1024×768, 1280×720 y 1920×1080; falta comprobar el redimensionado con controles físicos.
- [ ] Recibir daño y comprobar el rastro breve de la barra de vida; gastar cálices y revisar sus tres indicadores. Al morir con fe, comprobar el importe del vestigio.
- [ ] Moverse con WASD, girar cámara, correr, saltar y esquivar; acercarse a muros y bordes para revisar la cámara.
- [ ] Pulsar esquiva hacia un lado justo antes de terminar un ataque: debe salir al terminar la recuperación y gastar energía una sola vez. Una pulsación muy temprana debe caducar; varias pulsaciones no deben generar una cadena automática.
- [ ] Pausar después de solicitar una acción pendiente y reanudar: no debe salir sola. Repetir al morir, descansar y recibir un impacto que interrumpe.
- [ ] Acercar la cámara a muros y columnas, luego salir: contracción inmediata y regreso gradual sin atravesar geometría. Fijar/soltar objetivos cerca de paredes laterales y recibir golpes allí para comprobar encuadre y sacudida.
- [ ] Fijar un enemigo; verificar marcador, cambio de objetivo y retirada hasta perder fijación.
- [ ] Comparar alcance y tiempos del ataque ligero y fuerte; comprobar que la señal del enemigo permite anticipar el golpe.
- [ ] Revisar el centinela Meshy en movimiento: pies, hombros, faldones, agarre de espada, anticipación y momento del impacto. Comprobar su caída y recuperación de pose al descansar.
- [ ] Observar los clips renovados: pie apoyado frente al pie que avanza, elevación al correr, preparación que conecta con el golpe, retorno gradual del arma y rodillas que ceden antes de caer. Comparar custodios con paladín, cuya escala modifica el ritmo de reproducción.
- [ ] Dar un golpe ligero durante su desplazamiento: la reacción del torso debe conservar la zancada. Dar dos golpes fuertes sucesivos: la segunda reacción debe comenzar de nuevo. Descansar/reiniciar durante una reacción debe devolver la postura de reposo.
- [ ] Observar su patrulla desde lejos: debe caminar a un punto cercano, frenar y hacer una pausa. Acercarse desde detrás: debe observar y girar progresivamente antes de acelerar.
- [ ] Mantener distancia y luego dejar que se acerque: comprobar carrera → caminar → detenerse → anticipar → golpear → recuperarse. Revisar continuidad de las zancadas y posible deslizamiento de pies.
- [ ] Rodearlo durante la anticipación: debe mantener la dirección comprometida del golpe. Alejarse y descansar: debe regresar sin conservar impulso al reaparecer. Comprobar también paladín y Aster, que comparten la IA.
- [ ] Bloquear de frente, recibir daño por la espalda y agotar energía para probar ruptura de guardia.
- [ ] Usar un cáliz; comprobar animación provisional, retraso de curación y contador.
- [ ] Matar un custodio, morir con fe, recuperarla y comprobar su pérdida tras una segunda muerte sin recuperación.
- [ ] Descansar en ambos altares, comprar vitalidad y comprobar reinicio de enemigos.
- [ ] Confirmar nombre del altar, coste y +25 de vitalidad en su panel; al alcanzar bendición 5 debe mostrar el máximo sin ofrecer otro precio.
- [ ] Desde el primer altar, cruzar el puente oeste y recorrer el patio de ceniza; comprobar ancho del acceso, pretiles y cámara junto a las columnas y fuente.
- [ ] Enfrentarse al custodio del patio, alejarse por ambos puentes y comprobar que regresa sin atascarse en pilares, fuente o portal.
- [ ] Seguir las losas claras hasta la galería, recoger la reliquia frente al retablo y regresar por el puente norte; recorrer el circuito en sentido inverso. Revisar orientación y duración real de la exploración.
- [ ] Morir con fe en el claustro y recuperar el vestigio; cerrar y abrir para verificar que reliquia, fe y checkpoint se conservan.
- [ ] Recorrer el camino este y accionar la palanca; volver por el atajo abierto.
- [ ] Combatir a Aster, observar el cambio de ritmo por debajo de media vida y derrotarlo.
- [ ] Revisar que Aster levante el arma durante toda la anticipación, ejecute un arco visible en el contacto y recupere la postura; comprobar también su golpe fuerte y fase II.
- [ ] Usar Escape; revisar pausa, volumen y sensibilidad. Reanudar y comprobar captura del mouse.
- [ ] Arrastrar ambos deslizadores hasta sus extremos y volver a un valor cómodo; comprobar números, audio/cámara y conservación tras cerrar y abrir el juego. Revisar estados al pasar el mouse y pulsar Continuar.
- [ ] Salir, volver a abrir y verificar altar, vitalidad, fe, reliquia, atajo y victoria; el jefe no debe reaparecer.
- [ ] Registrar duración, FPS, problemas de lectura y dificultad antes de ampliar contenido.

Reportes automáticos: `Validation/core.txt`, `Validation/runtime.txt`, `Validation/build.txt`. Las imágenes `hud_*.png` incluyen la interfaz y documentan escenarios automáticos; no acreditan una partida manual. `santuario.png`, `aster.png` y `atmosfera_*.png` muestran renders de cámara sin HUD.
