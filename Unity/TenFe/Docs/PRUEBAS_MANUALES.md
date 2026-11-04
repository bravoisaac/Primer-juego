# Primera partida de revisión

Estado: pendiente de realizar con ventana visible y controles físicos. Las 120 comprobaciones automáticas (2026-11-03) y las capturas de interfaz no sustituyen esta revisión de sensación, legibilidad y dificultad; especialmente falta valorar la nueva ventana de entrada de 200 ms y la cámara de hombro.

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
- [ ] Observar su patrulla desde lejos: debe caminar a un punto cercano, frenar y hacer una pausa. Acercarse desde detrás: debe observar y girar progresivamente antes de acelerar.
- [ ] Mantener distancia y luego dejar que se acerque: comprobar carrera → caminar → detenerse → anticipar → golpear → recuperarse. Revisar continuidad de las zancadas y posible deslizamiento de pies.
- [ ] Rodearlo durante la anticipación: debe mantener la dirección comprometida del golpe. Alejarse y descansar: debe regresar sin conservar impulso al reaparecer. Comprobar también paladín y Aster, que comparten la IA.
- [ ] Bloquear de frente, recibir daño por la espalda y agotar energía para probar ruptura de guardia.
- [ ] Usar un cáliz; comprobar animación provisional, retraso de curación y contador.
- [ ] Matar un custodio, morir con fe, recuperarla y comprobar su pérdida tras una segunda muerte sin recuperación.
- [ ] Descansar en ambos altares, comprar vitalidad y comprobar reinicio de enemigos.
- [ ] Confirmar nombre del altar, coste y +25 de vitalidad en su panel; al alcanzar bendición 5 debe mostrar el máximo sin ofrecer otro precio.
- [ ] Recorrer el camino lateral, recoger la reliquia y accionar la palanca; volver por el atajo abierto.
- [ ] Combatir a Aster, observar el cambio de ritmo por debajo de media vida y derrotarlo.
- [ ] Usar Escape; revisar pausa, volumen y sensibilidad. Reanudar y comprobar captura del mouse.
- [ ] Arrastrar ambos deslizadores hasta sus extremos y volver a un valor cómodo; comprobar números, audio/cámara y conservación tras cerrar y abrir el juego. Revisar estados al pasar el mouse y pulsar Continuar.
- [ ] Salir, volver a abrir y verificar altar, vitalidad, fe, reliquia, atajo y victoria; el jefe no debe reaparecer.
- [ ] Registrar duración, FPS, problemas de lectura y dificultad antes de ampliar contenido.

Reportes automáticos: `Validation/core.txt`, `Validation/runtime.txt`, `Validation/build.txt`. Las imágenes `hud_*.png` incluyen la interfaz y documentan escenarios automáticos; no acreditan una partida manual. `santuario.png`, `aster.png` y `atmosfera_*.png` muestran renders de cámara sin HUD.
