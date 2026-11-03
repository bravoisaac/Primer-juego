# Primera partida de revisión

Estado: pendiente de realizar con ventana visible y controles físicos. Las 87 comprobaciones automáticas (2026-11-02) no sustituyen esta revisión de sensación, legibilidad y dificultad.

- [ ] Abrir `Jugar.cmd`; verificar que se ven personaje, escenario, vida, energía y cálices.
- [ ] Revisar cielo del eclipse, detalle de piedra/bronce, estandartes al viento, fuego y brasas desde entrada, patio y templo; comprobar que las sombras permiten distinguir enemigos y bordes.
- [ ] Pausar junto a una llama: partículas, telas y parpadeo deben detenerse y continuar al reanudar. Medir rendimiento a 1080p, incluyendo combate junto a varios braseros.
- [ ] Pulsar H y comprobar que los controles se leen sin recortes.
- [ ] Moverse con WASD, girar cámara, correr, saltar y esquivar; acercarse a muros y bordes para revisar la cámara.
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
- [ ] Recorrer el camino lateral, recoger la reliquia y accionar la palanca; volver por el atajo abierto.
- [ ] Combatir a Aster, observar el cambio de ritmo por debajo de media vida y derrotarlo.
- [ ] Usar Escape; revisar pausa, volumen y sensibilidad. Reanudar y comprobar captura del mouse.
- [ ] Salir, volver a abrir y verificar altar, vitalidad, fe, reliquia, atajo y victoria; el jefe no debe reaparecer.
- [ ] Registrar duración, FPS, problemas de lectura y dificultad antes de ampliar contenido.

Reportes automáticos: `Validation/core.txt`, `Validation/runtime.txt`. Las imágenes `santuario.png` y `aster.png` muestran la geometría renderizada por la cámara; excluyen HUD y no documentan una partida manual.
