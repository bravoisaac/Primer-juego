# Procedencia de recursos

| Recurso | Origen | Uso |
|---|---|---|
| Santuario, pilares, arcos, eclipse, estatuas y suelo | Geometría original mediante primitivas de Unity, `WorldBuilder.cs` | Prototipo editable |
| Peregrino y Aster | Primitivas y materiales originales, `WorldBuilder.cs` | Siluetas provisionales sin rig |
| Centinelas y paladín | GLB Meshy proporcionado por el usuario; coincide por SHA256 con la fuente histórica CC BY 4.0 | Cuerpo reducido a 54.999 triángulos y texturas originales |
| Rig y animaciones del centinela | Creación local original en `rig_gilded_sentinel.py`: 20 huesos, siete acciones y espada | Skin y animación genérica Unity; pesos de prototipo |
| Poses y movimiento de armas | Código original, `ActorVisual.cs` | Lectura básica de acciones |
| Audio de ambiente y combate | Síntesis matemática local, `GameAudio.cs` | Audio provisional |
| Cielo nublado, desgaste de piedra/bronce, fuego, brasas y ceniza | Shaders y sistemas de partículas originales creados localmente en `Assets/Art/Atmosphere` y `AtmosphereInstaller.cs` | Ambientación del santuario; sin texturas ni paquetes descargados |
| Estandartes del juramento | Malla y motivo geométrico originales creados por `AtmosphereInstaller.cs`; movimiento por shader | Seis telas decorativas sin colisión |
| Brillo y viñeta | Shader y componente originales `SanctuaryGrade.shader` / `SanctuaryImageEffect.cs` | Acabado suave de cámara; sin paquete de posprocesado externo |
| UI | IMGUI y fuente integrada en Unity | HUD provisional |
| Motor y módulos integrados | Instalación local de Unity 6000.3.26f1 | Sujetos a los términos de Unity |

No se compraron ni descargaron paquetes externos. El usuario proporcionó el GLB del centinela para esta integración. Su fuente y todos los modelos históricos se conservan; una copia reducida, con rig y animaciones nuevos, sí forma parte de la compilación Unity. La atribución y los cambios están registrados en `THIRD_PARTY_NOTICES.txt`, que también se copia junto al ejecutable. El panteón propuesto es original y puede renombrarse cuando se defina la historia.
