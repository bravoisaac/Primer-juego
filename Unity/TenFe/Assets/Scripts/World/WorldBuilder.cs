using UnityEngine;
using UnityEngine.Rendering;

namespace TenFe
{
    // Used by the editor to create a real, editable scene. No scene generation is needed at runtime.
    public static class WorldBuilder
    {
        static Material stone, edge, gold, dark, cloth, glow, red, pale, cyan;
        static Transform world;
        public static GameSession Build()
        {
            stone = Mat("Basalto", new Color(.19f, .23f, .27f), .15f);
            edge = Mat("Piedra clara", new Color(.39f, .42f, .43f), .1f);
            gold = Mat("Bronce sagrado", new Color(.56f, .38f, .14f), .7f);
            dark = Mat("Hierro oscuro", new Color(.055f, .075f, .095f), .65f);
            cloth = Mat("Manto del peregrino", new Color(.17f, .3f, .34f), .05f);
            glow = Mat("Llama dorada", new Color(1, .62f, .19f), .3f, new Color(1.7f, .68f, .12f));
            red = Mat("Manto del Ocaso", new Color(.38f, .075f, .065f), .1f);
            pale = Mat("Armadura ceniza", new Color(.57f, .58f, .55f), .65f);
            cyan = Mat("Fe olvidada", new Color(.3f, .8f, .85f), .2f, new Color(.25f, 1.1f, 1.3f));
            world = new GameObject("Santuario del Ocaso — geometría editable").transform;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.37f, .44f, .54f);
            RenderSettings.ambientEquatorColor = new Color(.24f, .28f, .34f);
            RenderSettings.ambientGroundColor = new Color(.12f, .14f, .17f);
            RenderSettings.fog = true; RenderSettings.fogColor = new Color(.12f, .19f, .24f);
            RenderSettings.fogMode = FogMode.ExponentialSquared; RenderSettings.fogDensity = .008f;
            var sun = new GameObject("Luz del eclipse").AddComponent<Light>(); sun.type = LightType.Directional;
            sun.color = new Color(1, .78f, .52f); sun.intensity = 1.25f; sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(32, -35, 0); RenderSettings.sun = sun;

            // Main route and east-side return route.
            Box("Cimientos", new Vector3(0, -1.3f, 18), new Vector3(28, 2.4f, 74), dark);
            Box("Nave principal", new Vector3(0, -.25f, 18), new Vector3(24, .5f, 72), stone);
            Box("Camino del peregrino", new Vector3(16, -.25f, 12), new Vector3(8, .5f, 48), stone);
            for (int z = -16; z <= 52; z += 4)
            {
                for (int x = -10; x <= 10; x += 4) Box("Losa", new Vector3(x, .012f, z), new Vector3(3.92f, .024f, 3.92f), (x / 2 + z / 4) % 3 == 0 ? edge : stone, false);
                Box("Borde oeste", new Vector3(-12, .5f, z), new Vector3(.6f, 1, 4), edge);
                if (z > 34) Box("Borde este", new Vector3(12, .5f, z), new Vector3(.6f, 1, 4), edge);
            }
            Box("Pretil del regreso", new Vector3(20, .55f, 12), new Vector3(.7f, 1.1f, 48), edge);
            Box("Límite sur", new Vector3(4, .6f, -18), new Vector3(32, 1.2f, .7f), edge);
            Box("Límite norte", new Vector3(0, 1.8f, 54), new Vector3(24, 3.6f, 1), stone);
            Box("Final del camino", new Vector3(16, .6f, 36), new Vector3(8, 1.2f, .7f), edge);
            Box("Inicio del camino", new Vector3(16, .6f, -12), new Vector3(8, 1.2f, .7f), edge);
            // Divider has an entrance in the south and an exit near the boss altar.
            Box("Muro del atajo", new Vector3(12, 1.5f, 12), new Vector3(.8f, 3, 34), stone);
            for (int z = -8; z <= 48; z += 8)
            {
                Pillar(new Vector3(-10, 0, z), z % 16 == 0 ? 5.8f : 4.5f);
                if (z != 24 && z != 32) Pillar(new Vector3(10, 0, z), 5.8f);
                if (z % 16 == 0) { Brazier(new Vector3(-7, 0, z)); Brazier(new Vector3(7, 0, z)); }
            }
            Arch(new Vector3(0, 0, 1), 8, 7);
            Arch(new Vector3(0, 0, 31), 9, 8);
            Arch(new Vector3(0, 0, 51), 7, 10);
            Ring("Sello de Aster", new Vector3(0, .06f, 43), 7, .09f, gold, Quaternion.Euler(90, 0, 0));
            Ring("Círculo interior", new Vector3(0, .065f, 43), 5.8f, .045f, gold, Quaternion.Euler(90, 0, 0));
            for (int i = 0; i < 12; i++)
            {
                float a = i * Mathf.PI / 6;
                Box("Marca del juramento", new Vector3(Mathf.Cos(a) * 6.4f, .08f, 43 + Mathf.Sin(a) * 6.4f), new Vector3(.1f, .04f, .7f), gold, false).transform.rotation = Quaternion.Euler(0, -a * Mathf.Rad2Deg, 0);
            }
            // Monumental eclipse and distant silhouettes, all original primitive geometry.
            Ring("Corona del eclipse", new Vector3(0, 24, 85), 8, .22f, glow, Quaternion.identity);
            var eclipse = Shape("Sol extinguido", PrimitiveType.Sphere, new Vector3(0, 24, 85.5f), new Vector3(15.7f, 15.7f, 1), dark, false);
            eclipse.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
            for (int i = 0; i < 16; i++)
            {
                float x = (i - 7.5f) * 9;
                Box("Ruina distante", new Vector3(x, 4 + i % 4 * 2, 78 + i % 3 * 6), new Vector3(4, 20 + i % 4 * 4, 5), dark, false);
            }
            Statue(new Vector3(-7, 0, -12), "Nerea, memoria de los dioses");
            Statue(new Vector3(7, 0, -12), "Aster, guardián del Ocaso");

            var game = new GameObject("Ten Fe — sesión").AddComponent<GameSession>();
            game.gameObject.AddComponent<GameHud>(); game.gameObject.AddComponent<GameAudio>();
            game.Player = CreatePlayer(new Vector3(0, .1f, -12));
            game.Enemies.Add(CreateEnemy(new Vector3(-3, .1f, 8), false, false));
            game.Enemies.Add(CreateEnemy(new Vector3(4, .1f, 18), false, false));
            game.Enemies.Add(CreateEnemy(new Vector3(-4, .1f, 23), false, true));
            game.Enemies.Add(CreateEnemy(new Vector3(0, .1f, 44), true, false));
            game.altars = new[] { Altar(new Vector3(0, 0, -8), 0, "Llama del primer juramento"), Altar(new Vector3(7, 0, 29), 1, "Llama del umbral") };
            var gate = new GameObject("Reja del atajo"); gate.transform.SetParent(world);
            for (int i = 0; i < 9; i++) Box("Barrote", new Vector3(12.4f + i * .85f, 1.5f, -3), new Vector3(.16f, 3, .18f), gold).transform.SetParent(gate.transform);
            Box("Travesaño", new Vector3(16, 2.8f, -3), new Vector3(8, .25f, .3f), gold).transform.SetParent(gate.transform);
            game.shortcut = Interaction("Palanca del regreso", new Vector3(17.8f, 0, 30), InteractionKind.Shortcut, gold);
            game.shortcut.gate = gate; game.shortcut.title = "Abrir el atajo al santuario";
            Box("Refugio secreto", new Vector3(17.8f, 1.2f, 18), new Vector3(3, 2.4f, .6f), stone);
            game.relic = Interaction("Memoria de Nerea", new Vector3(18, 0, 21), InteractionKind.Relic, cyan); game.relic.title = "Recoger la memoria de Nerea";
            game.vestige = Interaction("Vestigio de fe", Vector3.zero, InteractionKind.Vestige, cyan); game.vestige.title = "Recuperar tu fe";
            game.vestige.gameObject.SetActive(false);
            var camera = new GameObject("Cámara del peregrino"); camera.tag = "MainCamera";
            var lens = camera.AddComponent<Camera>(); lens.fieldOfView = 58; lens.nearClipPlane = .1f; lens.farClipPlane = 220;
            lens.clearFlags = CameraClearFlags.SolidColor; lens.backgroundColor = new Color(.09f, .14f, .2f);
            camera.AddComponent<AudioListener>();
            var orbit = camera.AddComponent<OrbitCamera>(); orbit.player = game.Player; game.Player.orbit = orbit;
            camera.transform.SetPositionAndRotation(new Vector3(0, 3.5f, -17), Quaternion.Euler(17, 0, 0));
            return game;
        }
        static Material Mat(string name, Color color, float metallic, Color emission = default)
        {
            var material = new Material(Shader.Find("Standard")) { name = name, color = color };
            material.SetFloat("_Metallic", metallic); material.SetFloat("_Glossiness", .32f);
            if (emission.maxColorComponent > 0) { material.EnableKeyword("_EMISSION"); material.SetColor("_EmissionColor", emission); }
            return material;
        }
        static GameObject Shape(string name, PrimitiveType primitive, Vector3 position, Vector3 scale, Material mat, bool collider = true, Transform parent = null)
        {
            var obj = GameObject.CreatePrimitive(primitive); obj.name = name;
            obj.transform.SetParent(parent != null ? parent : world, false);
            obj.transform.localPosition = position; obj.transform.localScale = scale;
            obj.GetComponent<Renderer>().sharedMaterial = mat;
            if (!collider) Object.DestroyImmediate(obj.GetComponent<Collider>());
            return obj;
        }
        static GameObject Box(string name, Vector3 position, Vector3 scale, Material mat, bool collider = true, Transform parent = null)
            => Shape(name, PrimitiveType.Cube, position, scale, mat, collider, parent);
        static void Pillar(Vector3 point, float height)
        {
            Shape("Base de columna", PrimitiveType.Cylinder, point + Vector3.up * .2f, new Vector3(1.8f, .2f, 1.8f), edge);
            Shape("Columna", PrimitiveType.Cylinder, point + Vector3.up * height / 2, new Vector3(.9f, height / 2, .9f), stone);
            Box("Capitel", point + Vector3.up * height, new Vector3(1.6f, .4f, 1.6f), edge);
            Shape("Anillo de bronce", PrimitiveType.Cylinder, point + Vector3.up * (height - .4f), new Vector3(1.05f, .12f, 1.05f), gold, false);
        }
        static void Arch(Vector3 point, float width, float height)
        {
            Pillar(point + Vector3.left * width / 2, height); Pillar(point + Vector3.right * width / 2, height);
            Box("Dintel sagrado", point + Vector3.up * height, new Vector3(width + 1, .8f, 1.4f), edge);
            Box("Friso de bronce", point + Vector3.up * (height + .5f), new Vector3(width + 1.5f, .18f, 1.6f), gold, false);
        }
        static void Brazier(Vector3 point)
        {
            Shape("Pedestal", PrimitiveType.Cylinder, point + Vector3.up * .65f, new Vector3(.5f, .65f, .5f), dark);
            Shape("Cuenco", PrimitiveType.Cylinder, point + Vector3.up * 1.3f, new Vector3(.9f, .15f, .9f), gold, false);
            Shape("Ascua", PrimitiveType.Sphere, point + Vector3.up * 1.65f, new Vector3(.4f, .7f, .4f), glow, false);
            var lamp = new GameObject("Luz de ascua").AddComponent<Light>(); lamp.transform.SetParent(world);
            lamp.transform.position = point + Vector3.up * 2; lamp.type = LightType.Point; lamp.color = new Color(1, .48f, .16f); lamp.range = 6; lamp.intensity = 2;
        }
        static void Ring(string name, Vector3 point, float radius, float thickness, Material material, Quaternion rotation)
        {
            var root = new GameObject(name).transform; root.SetParent(world); root.position = point; root.rotation = rotation;
            const int segments = 64;
            for (int i = 0; i < segments; i++)
            {
                float a = i * Mathf.PI * 2 / segments;
                var segment = Box("Arco", new Vector3(Mathf.Cos(a) * radius, Mathf.Sin(a) * radius, 0), new Vector3(thickness, radius * Mathf.PI * 2 / segments + .02f, thickness), material, false, root);
                segment.transform.localRotation = Quaternion.Euler(0, 0, a * Mathf.Rad2Deg);
            }
        }
        static void Statue(Vector3 point, string name)
        {
            Box("Pedestal de " + name, point + Vector3.up * .6f, new Vector3(2.8f, 1.2f, 2.8f), edge);
            Shape(name, PrimitiveType.Capsule, point + Vector3.up * 3.3f, new Vector3(1.7f, 2.2f, 1.3f), stone);
            Shape("Rostro velado", PrimitiveType.Sphere, point + Vector3.up * 5.4f, new Vector3(1, 1.2f, 1), edge);
            Ring("Aureola", point + new Vector3(0, 5.4f, .5f), 1.1f, .065f, gold, Quaternion.identity);
        }
        static Interactable Altar(Vector3 point, int id, string name)
        {
            var altar = Interaction(name, point, InteractionKind.Altar, glow); altar.checkpointId = id;
            var spawn = new GameObject("Punto de reaparición").transform; spawn.SetParent(altar.transform); spawn.localPosition = new Vector3(0, .15f, -3);
            altar.respawnPoint = spawn;
            Ring("Círculo de descanso", point + Vector3.up * .05f, 2, .07f, gold, Quaternion.Euler(90, 0, 0));
            return altar;
        }
        static Interactable Interaction(string name, Vector3 point, InteractionKind kind, Material material)
        {
            var root = new GameObject(name); root.transform.SetParent(world); root.transform.position = point;
            var interaction = root.AddComponent<Interactable>(); interaction.kind = kind;
            Shape("Base ritual", PrimitiveType.Cylinder, new Vector3(0, .15f, 0), new Vector3(1.1f, .15f, 1.1f), dark, false, root.transform);
            var crystal = Shape("Chispa divina", PrimitiveType.Cube, new Vector3(0, .9f, 0), new Vector3(.35f, .8f, .35f), material, false, root.transform);
            crystal.transform.localRotation = Quaternion.Euler(0, 45, 18);
            return interaction;
        }
        static GameObject Actor(string name, Vector3 position, float scale, Material armor, Material mantle)
        {
            var root = new GameObject(name); root.layer = 8; root.transform.position = position; root.transform.localScale = Vector3.one * scale;
            var controller = root.AddComponent<CharacterController>(); controller.height = 2; controller.radius = .38f; controller.center = Vector3.up; controller.stepOffset = .3f; controller.minMoveDistance = 0;
            root.AddComponent<Health>();
            var visual = root.AddComponent<ActorVisual>();
            var body = new GameObject("Cuerpo").transform; body.SetParent(root.transform, false); body.localPosition = Vector3.up; visual.body = body;
            Shape("Peto", PrimitiveType.Capsule, new Vector3(0, .25f, 0), new Vector3(.7f, .48f, .45f), armor, false, body);
            Box("Cinturón", new Vector3(0, -.12f, 0), new Vector3(.7f, .13f, .5f), gold, false, body);
            Shape("Casco", PrimitiveType.Sphere, new Vector3(0, .85f, 0), new Vector3(.55f, .65f, .52f), armor, false, body);
            visual.visor = Box("Ranura luminosa", new Vector3(0, .88f, .26f), new Vector3(.39f, .055f, .04f), glow, false, body).GetComponent<Renderer>();
            Box("Cresta", new Vector3(0, 1.17f, 0), new Vector3(.08f, .22f, .55f), gold, false, body);
            Box("Manto", new Vector3(0, .08f, -.28f), new Vector3(.8f, 1.05f, .08f), mantle, false, body).transform.localRotation = Quaternion.Euler(-12, 0, 0);
            visual.leftLeg = Limb("Pierna izquierda", body, new Vector3(-.22f, -.2f, 0), armor, new Vector3(.24f, .72f, .3f));
            visual.rightLeg = Limb("Pierna derecha", body, new Vector3(.22f, -.2f, 0), armor, new Vector3(.24f, .72f, .3f));
            visual.swordArm = Limb("Brazo espada", body, new Vector3(.47f, .5f, 0), armor, new Vector3(.24f, .6f, .28f));
            visual.shieldArm = Limb("Brazo escudo", body, new Vector3(-.47f, .5f, 0), armor, new Vector3(.24f, .6f, .28f));
            Box("Hoja", new Vector3(0, -.45f, .68f), new Vector3(.12f, .065f, 1.25f), pale, false, visual.swordArm);
            Box("Guarda", new Vector3(0, -.45f, .1f), new Vector3(.42f, .09f, .08f), gold, false, visual.swordArm);
            Box("Escudo", new Vector3(-.12f, -.35f, .18f), new Vector3(.08f, .75f, .55f), dark, false, visual.shieldArm);
            Box("Emblema del escudo", new Vector3(-.17f, -.35f, .18f), new Vector3(.02f, .5f, .06f), gold, false, visual.shieldArm);
            return root;
        }
        static Transform Limb(string name, Transform body, Vector3 position, Material material, Vector3 size)
        {
            var joint = new GameObject(name).transform; joint.SetParent(body, false); joint.localPosition = position;
            Box("Placa", new Vector3(0, -size.y / 2, 0), size, material, false, joint); return joint;
        }
        static PlayerController CreatePlayer(Vector3 position)
        {
            var root = Actor("El último peregrino", position, 1, pale, cloth);
            root.AddComponent<Stamina>(); var player = root.AddComponent<PlayerController>(); player.visual = root.GetComponent<ActorVisual>(); return player;
        }
        static EnemyBrain CreateEnemy(Vector3 position, bool boss, bool elite)
        {
            var root = Actor(boss ? "Aster, dios del Ocaso" : elite ? "Paladín del Ocaso" : "Custodio sin fe", position, boss ? 1.65f : elite ? 1.18f : 1, boss ? gold : dark, red);
            root.GetComponent<Health>().maximum = boss ? 560 : elite ? 150 : 85;
            var enemy = root.AddComponent<EnemyBrain>(); enemy.boss = boss; enemy.elite = elite; enemy.title = root.name;
            enemy.reward = boss ? 300 : elite ? 65 : 35; enemy.visual = root.GetComponent<ActorVisual>(); return enemy;
        }
    }
}
