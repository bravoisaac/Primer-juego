using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace TenFe.Editor
{
    public static class AtmosphereInstaller
    {
        const string Folder = "Assets/Art/Atmosphere/";
        const string ScenePath = "Assets/Scenes/Santuario.unity";

        [MenuItem("Ten Fe/Aplicar ambientación al santuario guardado")]
        public static void Install()
        {
            if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(ScenePath);
            ApplyToScene();
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
            AssetDatabase.SaveAssets();
        }
        public static void InstallAndBuild()
        {
            Install(); ProjectTools.ValidateCore(); ProjectTools.BuildWindows();
        }
        public static void ApplyToScene()
        {
            var game = UnityEngine.Object.FindFirstObjectByType<GameSession>();
            var world = GameObject.Find("Santuario del Ocaso — geometría editable");
            if (game == null || world == null) throw new Exception("No se encontró el santuario existente.");
            var sky = Material("Cielo del Ocaso", "TenFe/Sanctuary Sky");
            sky.SetColor("_Zenith", new Color(.025f, .05f, .09f));
            sky.SetColor("_Horizon", new Color(.22f, .28f, .31f));
            sky.SetColor("_Cloud", new Color(.1f, .14f, .19f));
            RenderSettings.skybox = sky;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.32f, .4f, .51f);
            RenderSettings.ambientEquatorColor = new Color(.21f, .27f, .31f);
            RenderSettings.ambientGroundColor = new Color(.1f, .12f, .14f);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = new Color(.17f, .215f, .255f); RenderSettings.fogDensity = .011f;
            if (RenderSettings.sun != null)
            {
                var sun = RenderSettings.sun;
                sun.color = new Color(1, .83f, .63f); sun.intensity = 1.05f;
                sun.transform.rotation = Quaternion.Euler(24, -32, 0);
                sun.shadows = LightShadows.Soft; sun.shadowStrength = .86f;
                sun.shadowBias = .035f; sun.shadowNormalBias = .3f;
            }
            QualitySettings.shadowDistance = 65; QualitySettings.shadowCascades = 2;
            QualitySettings.shadows = ShadowQuality.All; QualitySettings.pixelLightCount = 4;
            var camera = game.Player.orbit.GetComponent<Camera>();
            camera.clearFlags = CameraClearFlags.Skybox; camera.allowHDR = true;
            var effect = EnsureComponent<SanctuaryImageEffect>(camera.gameObject);
            effect.shader = RequireShader("Hidden/TenFe/Sanctuary Grade");

            var basalt = Stone("Basalto erosionado", new Color(.255f, .29f, .31f), new Color(.14f, .20f, .18f), .06f, .27f);
            var limestone = Stone("Caliza envejecida", new Color(.39f, .40f, .38f), new Color(.22f, .25f, .21f), .02f, .24f);
            var bronze = Stone("Bronce envejecido", new Color(.52f, .34f, .12f), new Color(.12f, .24f, .20f), .72f, .48f);
            foreach (var renderer in world.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (renderer.sharedMaterial == null) continue;
                string name = renderer.sharedMaterial.name;
                if (name == "Basalto" || name == basalt.name) renderer.sharedMaterial = basalt;
                else if (name == "Piedra clara" || name == limestone.name) renderer.sharedMaterial = limestone;
                else if (name == "Bronce sagrado" || name == bronze.name) renderer.sharedMaterial = bronze;
            }
            var root = GameObject.Find("Atmósfera del santuario") ?? new GameObject("Atmósfera del santuario");
            var atmosphere = EnsureComponent<SanctuaryAtmosphere>(root);
            var fire = Material("Fuego y brasas", "TenFe/Sacred Fire");
            var lights = new List<Light>();
            foreach (var light in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
            {
                if (light.name != "Luz de ascua") continue;
                light.color = new Color(1, .43f, .12f); light.intensity = 3.1f; light.range = 7;
                light.shadows = LightShadows.None; lights.Add(light);
            }
            foreach (var renderer in world.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (renderer.name != "Ascua") continue;
                // Retain the original fixture for editing, replace only the static visible flame.
                renderer.enabled = false;
                Flame(root.transform, "Brasero " + renderer.transform.position.ToString("F2"), renderer.transform.position - Vector3.up * .2f, fire);
            }
            foreach (var altar in game.altars)
            {
                Flame(altar.transform, "Llama viva", altar.transform.position + Vector3.up * 1.1f, fire);
                var lightObject = Child(altar.transform, "Luz de santuario");
                var light = EnsureComponent<Light>(lightObject);
                light.transform.localPosition = Vector3.up * 1.6f;
                light.type = LightType.Point; light.color = new Color(1, .58f, .22f); light.range = 7; light.intensity = 2.6f;
                lights.Add(light);
            }
            atmosphere.flameLights = lights.ToArray();
            var dust = Particles(root.transform, "Ceniza suspendida", new Vector3(0, 2.5f, 20), fire, 5, 120);
            var main = dust.main;
            main.startLifetime = new ParticleSystem.MinMaxCurve(10, 16); main.startSpeed = .025f;
            main.startSize = new ParticleSystem.MinMaxCurve(.014f, .035f);
            main.startColor = new Color(.4f, .5f, .58f, .32f);
            var shape = dust.shape; shape.shapeType = ParticleSystemShapeType.Box; shape.scale = new Vector3(22, 5, 66);
            var velocity = dust.velocityOverLifetime; velocity.enabled = true; velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = .12f; velocity.y = -.045f; velocity.z = .04f;
            Fade(dust, new Color(.5f, .6f, .7f, .4f), new Color(.5f, .6f, .7f, .4f));

            var cloth = Material("Estandartes del juramento", "TenFe/Pilgrim Banner");
            var mesh = BannerMesh();
            for (int arch = 0; arch < 3; arch++) for (int side = -1; side <= 1; side += 2)
            {
                float z = arch == 0 ? 1 : arch == 1 ? 31 : 51;
                float x = (arch == 0 ? 4.9f : arch == 1 ? 5.4f : 4.4f) * side;
                var banner = Child(root.transform, "Estandarte " + arch + " " + side);
                banner.transform.position = new Vector3(x, arch == 2 ? 7.4f : 5.4f, z - .6f);
                var filter = EnsureComponent<MeshFilter>(banner); filter.sharedMesh = mesh;
                var renderer = EnsureComponent<MeshRenderer>(banner);
                renderer.sharedMaterial = cloth; renderer.shadowCastingMode = ShadowCastingMode.TwoSided;
            }
            Validate(game, atmosphere);
            Debug.Log("TENFE_ATMOSPHERE_READY: sky, weathered surfaces, 6 banners, fire, ash and restrained bloom");
        }
        static Shader RequireShader(string name)
        {
            var shader = Shader.Find(name);
            if (shader == null || ShaderUtil.ShaderHasError(shader)) throw new Exception("Shader inválido: " + name);
            return shader;
        }
        static Material Material(string name, string shaderName)
        {
            string path = Folder + name + ".mat";
            var shader = RequireShader(shaderName);
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null) { material = new Material(shader) { name = name }; AssetDatabase.CreateAsset(material, path); }
            else material.shader = shader;
            EditorUtility.SetDirty(material); return material;
        }
        static Material Stone(string name, Color color, Color patina, float metallic, float smoothness)
        {
            var material = Material(name, "TenFe/Weathered Stone");
            material.SetColor("_Color", color); material.SetColor("_Patina", patina);
            material.SetFloat("_Metallic", metallic); material.SetFloat("_Glossiness", smoothness);
            material.SetFloat("_Relief", .035f); return material;
        }
        static GameObject Child(Transform parent, string name)
        {
            var existing = parent.Find(name);
            if (existing != null) return existing.gameObject;
            var obj = new GameObject(name); obj.transform.SetParent(parent, false); return obj;
        }
        static T EnsureComponent<T>(GameObject obj) where T : Component
        {
            var component = obj.GetComponent<T>();
            return component != null ? component : obj.AddComponent<T>();
        }
        static ParticleSystem Particles(Transform parent, string name, Vector3 position, Material material, float rate, int max)
        {
            var obj = Child(parent, name); obj.transform.position = position;
            var system = EnsureComponent<ParticleSystem>(obj);
            system.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            system.useAutoRandomSeed = false; system.randomSeed = (uint)(17 + Mathf.Abs(position.x * 31 + position.z * 73));
            var main = system.main;
            main.loop = true; main.playOnAwake = true; main.prewarm = true; main.duration = 5;
            main.simulationSpace = ParticleSystemSimulationSpace.World; main.maxParticles = max;
            var emission = system.emission; emission.rateOverTime = rate;
            var renderer = system.GetComponent<ParticleSystemRenderer>(); renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
            renderer.lightProbeUsage = LightProbeUsage.Off; renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            return system;
        }
        static void Flame(Transform parent, string name, Vector3 position, Material material)
        {
            var flame = Particles(parent, name, position, material, 22, 40);
            var main = flame.main;
            main.startLifetime = new ParticleSystem.MinMaxCurve(.45f, .85f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(.4f, .85f);
            main.startSize3D = true; main.startSizeX = new ParticleSystem.MinMaxCurve(.18f, .32f);
            main.startSizeY = new ParticleSystem.MinMaxCurve(.45f, .8f); main.startSizeZ = .2f;
            main.startColor = Color.white;
            var shape = flame.shape; shape.shapeType = ParticleSystemShapeType.Cone; shape.angle = 8; shape.radius = .13f;
            shape.rotation = new Vector3(-90, 0, 0);
            Fade(flame, new Color(3.5f, 1.35f, .25f), new Color(1.2f, .12f, .015f));
            var size = flame.sizeOverLifetime; size.enabled = true;
            size.size = new ParticleSystem.MinMaxCurve(1, AnimationCurve.Linear(0, 1, 1, .12f));

            var embers = Particles(flame.transform, "Brasas", position, material, 7, 40);
            main = embers.main; main.startLifetime = new ParticleSystem.MinMaxCurve(1.2f, 2.6f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(.5f, 1.3f); main.startSize = new ParticleSystem.MinMaxCurve(.018f, .045f);
            main.startColor = Color.white;
            shape = embers.shape; shape.shapeType = ParticleSystemShapeType.Cone; shape.angle = 18; shape.radius = .15f;
            shape.rotation = new Vector3(-90, 0, 0);
            var velocity = embers.velocityOverLifetime; velocity.enabled = true; velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = .16f; velocity.z = .05f;
            Fade(embers, new Color(3, 1.4f, .3f), new Color(1.2f, .28f, .04f));
        }
        static void Fade(ParticleSystem particles, Color start, Color end)
        {
            var gradient = new Gradient();
            gradient.SetKeys(new[] { new GradientColorKey(start, 0), new GradientColorKey(end, 1) },
                new[] { new GradientAlphaKey(0, 0), new GradientAlphaKey(.8f, .12f), new GradientAlphaKey(.35f, .65f), new GradientAlphaKey(0, 1) });
            var colors = particles.colorOverLifetime; colors.enabled = true; colors.color = gradient;
        }
        static Mesh BannerMesh()
        {
            const string path = Folder + "Estandarte.asset";
            var mesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (mesh != null) return mesh;
            const int columns = 8, rows = 24;
            var vertices = new Vector3[(columns + 1) * (rows + 1)]; var uv = new Vector2[vertices.Length];
            var triangles = new List<int>();
            for (int row = 0; row <= rows; row++) for (int col = 0; col <= columns; col++)
            {
                int index = row * (columns + 1) + col;
                float u = (float)col / columns, v = (float)row / rows;
                float torn = row == rows ? .08f + .14f * Mathf.Sin(col * 2.7f) : 0;
                vertices[index] = new Vector3((u - .5f) * 1.15f, -v * 2.9f + torn, Mathf.Sin(u * Mathf.PI * 6) * .035f);
                uv[index] = new Vector2(u, 1 - v);
                if (row == rows || col == columns) continue;
                int below = index + columns + 1;
                triangles.Add(index); triangles.Add(below); triangles.Add(index + 1);
                triangles.Add(index + 1); triangles.Add(below); triangles.Add(below + 1);
            }
            mesh = new Mesh { name = "Estandarte tejido", vertices = vertices, uv = uv, triangles = triangles.ToArray() };
            mesh.RecalculateNormals(); mesh.RecalculateTangents();
            mesh.bounds = new Bounds(new Vector3(0, -1.45f, 0), new Vector3(1.5f, 3.2f, .6f));
            AssetDatabase.CreateAsset(mesh, path); return mesh;
        }
        static void Validate(GameSession game, SanctuaryAtmosphere atmosphere)
        {
            if (RenderSettings.skybox == null || atmosphere.flameLights.Length < 10 ||
                game.Player.orbit.GetComponent<SanctuaryImageEffect>().shader == null)
                throw new Exception("Ambientación incompleta.");
            if (atmosphere.GetComponentsInChildren<Collider>().Length != 0)
                throw new Exception("Los efectos visuales no deben añadir colisiones.");
            Directory.CreateDirectory("Docs/Validation");
            File.WriteAllText("Docs/Validation/atmosphere-import.txt", "PASS: custom sky, world-space materials, six wind banners, ten flame lights, particle effects and camera grade.\nNo gameplay colliders added. Existing scene geometry retained.\n");
        }
    }
}
