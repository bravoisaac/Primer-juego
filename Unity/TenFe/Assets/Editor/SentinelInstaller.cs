using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace TenFe.Editor
{
    public sealed class SentinelModelImport : AssetPostprocessor
    {
        void OnPreprocessModel()
        {
            if (assetPath != SentinelInstaller.ModelPath) return;
            var importer = (ModelImporter)assetImporter;
            importer.animationType = ModelImporterAnimationType.Generic;
            importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            importer.importAnimation = true;
            importer.optimizeGameObjects = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.animationCompression = ModelImporterAnimationCompression.Off;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.isReadable = true;
        }
    }

    public static class SentinelInstaller
    {
        public const string ModelPath = "Assets/Art/GildedSentinel/GildedSentinel.fbx";
        public const string PrefabPath = "Assets/Art/GildedSentinel/GildedSentinelVisual.prefab";
        const string Folder = "Assets/Art/GildedSentinel/";
        const string ScenePath = "Assets/Scenes/Santuario.unity";
        static readonly string[] Names = { "Idle", "Walk", "Run", "Windup", "Strike", "Hit", "Death" };

        [MenuItem("Ten Fe/Integrar centinela animado")]
        public static void Install()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var importer = (ModelImporter)AssetImporter.GetAtPath(ModelPath);
            if (importer == null) throw new Exception("Falta el FBX. Ejecuta Tools/Blender/rig_gilded_sentinel.py.");
            var clips = importer.defaultClipAnimations;
            foreach (var clip in clips)
            {
                clip.name = clip.name.Split('|').Last();
                clip.loopTime = clip.name == "Idle" || clip.name == "Walk" || clip.name == "Run";
                clip.loopPose = clip.loopTime;
                clip.lockRootRotation = true; clip.lockRootPositionXZ = true; clip.lockRootHeightY = true;
            }
            importer.clipAnimations = clips; importer.SaveAndReimport();
            var imported = AssetDatabase.LoadAllAssetsAtPath(ModelPath).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__")).ToArray();
            foreach (string name in Names)
                if (!imported.Any(c => c.name == name && c.length > .1f)) throw new Exception("Missing animation: " + name);

            Material surface = SurfaceMaterial();
            Material weapon = AssetDatabase.LoadAssetAtPath<Material>(Folder + "SentinelWeapon.mat");
            if (weapon == null) { weapon = new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(weapon, Folder + "SentinelWeapon.mat"); }
            weapon.color = new Color(.32f, .34f, .36f); weapon.SetFloat("_Metallic", .8f); weapon.SetFloat("_Glossiness", .65f);
            string controllerPath = Folder + "Sentinel.controller";
            var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
            if (controller == null) controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
            var machine = controller.layers[0].stateMachine;
            foreach (string name in Names)
            {
                var state = machine.states.FirstOrDefault(s => s.state.name == name).state ?? machine.AddState(name);
                state.motion = imported.Single(c => c.name == name);
                if (name == "Idle") machine.defaultState = state;
            }
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            var root = (GameObject)PrefabUtility.InstantiatePrefab(model);
            try
            {
                root.name = "Gilded Sentinel — animated visual";
                var animator = root.GetComponent<Animator>() ?? root.AddComponent<Animator>();
                animator.runtimeAnimatorController = controller; animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                foreach (var renderer in root.GetComponentsInChildren<SkinnedMeshRenderer>())
                {
                    renderer.sharedMaterial = renderer.name.Contains("Sword") ? weapon : surface;
                    renderer.quality = SkinQuality.Bone4; renderer.updateWhenOffscreen = true;
                    renderer.localBounds = new Bounds(new Vector3(0, 1, 0), new Vector3(4, 4, 4));
                }
                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(ScenePath);
            var game = UnityEngine.Object.FindFirstObjectByType<GameSession>();
            int installed = AttachToEnemies(game);
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
            Validate(game, imported);
            Debug.Log("TENFE_SENTINEL_INSTALLED " + installed);
        }

        public static int AttachToEnemies(GameSession game)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (prefab == null) return 0;
            ConfigureMetalLighting();
            int count = 0;
            foreach (var enemy in game.Enemies.Where(e => !e.boss))
            {
                if (enemy.animatedVisual != null)
                {
                    enemy.animatedVisual.animator.transform.localPosition = Vector3.down * .08f;
                    count++; continue;
                }
                var legacy = enemy.visual;
                if (legacy != null)
                {
                    if (legacy.body != null) UnityEngine.Object.DestroyImmediate(legacy.body.gameObject);
                    UnityEngine.Object.DestroyImmediate(legacy);
                    enemy.visual = null;
                }
                var model = (GameObject)PrefabUtility.InstantiatePrefab(prefab, enemy.transform);
                model.transform.localPosition = Vector3.down * .08f; model.transform.localRotation = Quaternion.identity;
                var visual = enemy.gameObject.AddComponent<SentinelVisual>();
                visual.animator = model.GetComponent<Animator>();
                visual.body = model.GetComponentsInChildren<SkinnedMeshRenderer>().First(r => r.name == "SentinelBody");
                visual.rightHand = model.GetComponentsInChildren<Transform>().First(t => t.name == "Hand.R");
                enemy.animatedVisual = visual;
                enemy.title = enemy.elite ? "Paladín del Ocaso" : "Centinela dorado";
                enemy.gameObject.name = enemy.title;
                count++;
            }
            return count;
        }

        static Material SurfaceMaterial()
        {
            Texture2D Texture(string name, bool linear, bool normal = false)
            {
                string path = Folder + "Textures/Sentinel_" + name + ".png";
                var importer = (TextureImporter)AssetImporter.GetAtPath(path);
                if (importer == null) throw new Exception("Missing texture " + path);
                importer.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                importer.sRGBTexture = !linear; importer.maxTextureSize = 2048;
                importer.textureCompression = TextureImporterCompression.CompressedHQ;
                importer.SaveAndReimport();
                return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            }
            var material = AssetDatabase.LoadAssetAtPath<Material>(Folder + "SentinelSurface.mat");
            if (material == null) { material = new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(material, Folder + "SentinelSurface.mat"); }
            material.color = Color.white;
            material.mainTexture = Texture("BaseColor", false);
            material.SetTexture("_BumpMap", Texture("Normal", true, true)); material.EnableKeyword("_NORMALMAP");
            material.SetTexture("_MetallicGlossMap", Texture("MetallicSmoothness", true)); material.EnableKeyword("_METALLICGLOSSMAP");
            material.SetFloat("_Metallic", 1); material.SetFloat("_GlossMapScale", .85f);
            // The source GLB declares metallic/roughness only, not an occlusion texture.
            // Standard reads AO from green, which here would incorrectly darken by roughness.
            material.SetTexture("_OcclusionMap", null);
            return material;
        }

        static void ConfigureMetalLighting()
        {
            // The prototype has no skybox. A soft environment reflection lets metal remain legible
            // in shadow, rather than reflecting an entirely black environment.
            string path = Folder + "SanctuaryReflection.asset";
            var cube = AssetDatabase.LoadAssetAtPath<Cubemap>(path);
            if (cube == null)
            {
                const int size = 32;
                cube = new Cubemap(size, TextureFormat.RGBAHalf, true) { name = "SanctuaryReflection" };
                for (int face = 0; face < 6; face++)
                {
                    var pixels = new Color[size * size];
                    for (int y = 0; y < size; y++) for (int x = 0; x < size; x++)
                    {
                        float u = (x + .5f) / size * 2 - 1, v = (y + .5f) / size * 2 - 1;
                        Vector3 direction = face == 0 ? new Vector3(1, -v, -u) : face == 1 ? new Vector3(-1, -v, u) :
                            face == 2 ? new Vector3(u, 1, v) : face == 3 ? new Vector3(u, -1, -v) :
                            face == 4 ? new Vector3(u, -v, 1) : new Vector3(-u, -v, -1);
                        direction.Normalize();
                        Color baseColor = Color.Lerp(new Color(.16f, .18f, .21f), new Color(.5f, .56f, .64f), direction.y * .5f + .5f);
                        float sun = Mathf.Pow(Mathf.Max(0, Vector3.Dot(direction, new Vector3(-.4f, .7f, -.5f).normalized)), 12);
                        pixels[y * size + x] = baseColor + new Color(.35f, .24f, .13f) * sun;
                    }
                    cube.SetPixels(pixels, (CubemapFace)face);
                }
                cube.Apply(true, false); AssetDatabase.CreateAsset(cube, path);
            }
            RenderSettings.defaultReflectionMode = UnityEngine.Rendering.DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = cube; RenderSettings.reflectionIntensity = .85f;
        }

        static void Validate(GameSession game, AnimationClip[] clips)
        {
            var enemies = game.Enemies.Where(e => !e.boss).ToArray();
            foreach (var enemy in enemies)
            {
                var visual = enemy.animatedVisual;
                if (visual == null || visual.body.bones.Length < 15 || visual.animator.avatar == null || !visual.animator.avatar.isValid)
                    throw new Exception("Invalid skeletal enemy: " + enemy.name);
                if (visual.body.sharedMesh.bindposes.Length != visual.body.bones.Length) throw new Exception("Bind pose mismatch");
                if (visual.body.sharedMaterial.mainTexture == null) throw new Exception("Missing PBR surface");
                if (enemy.GetComponent<ActorVisual>() != null) throw new Exception("Duplicate visual driver");
            }
            Directory.CreateDirectory("Docs/Validation");
            File.WriteAllText("Docs/Validation/sentinel-import.txt", "PASS: " + enemies.Length + " skeletal enemies.\n" +
                string.Join("\n", clips.Select(c => c.name + ": " + c.length.ToString("F3") + " seconds")) +
                "\nValidated: avatar, bones/bindposes, textures, single visual driver.\n");
        }
        public static void InstallAndBuild()
        { Install(); ProjectTools.ValidateCore(); ProjectTools.BuildWindows(); }
    }
}
