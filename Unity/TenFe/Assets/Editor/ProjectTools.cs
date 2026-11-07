using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace TenFe.Editor
{
    public static class ProjectTools
    {
        const string ScenePath = "Assets/Scenes/Santuario.unity";
        [MenuItem("Ten Fe/Crear o reconstruir santuario")]
        public static void CreateScene()
        {
            if (File.Exists(ScenePath) && !Application.isBatchMode && !EditorUtility.DisplayDialog("Reconstruir santuario", "Se sustituirá la escena generada. Guarda tus cambios manuales en otra escena antes de continuar.", "Reconstruir", "Cancelar")) return;
            Directory.CreateDirectory("Assets/Scenes"); Directory.CreateDirectory("Assets/Materials");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var generatedGame = WorldBuilder.Build();
            foreach (var material in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None).SelectMany(r => r.sharedMaterials).Where(m => m != null).Distinct())
            {
                string path = "Assets/Materials/" + material.name + ".mat";
                var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (existing == null) AssetDatabase.CreateAsset(material, path);
                else
                {
                    EditorUtility.CopySerialized(material, existing);
                    foreach (var renderer in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                        if (renderer.sharedMaterial == material) renderer.sharedMaterial = existing;
                    UnityEngine.Object.DestroyImmediate(material);
                }
            }
            PlayerSettings.companyName = "TenFe"; PlayerSettings.productName = "Ten Fe - Santuario del Ocaso";
            SentinelInstaller.AttachToEnemies(generatedGame);
            AtmosphereInstaller.ApplyToScene();
            SanctuaryExpansion.ApplyToScene();
            PlayerSettings.defaultScreenWidth = 1280; PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.runInBackground = true;
            PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            PlayerSettings.colorSpace = ColorSpace.Linear;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.StandaloneWindows64, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.StandaloneWindows64, new[] { UnityEngine.Rendering.GraphicsDeviceType.Direct3D11 });
            QualitySettings.shadows = ShadowQuality.All; QualitySettings.shadowDistance = 60; QualitySettings.antiAliasing = 4;
            QualitySettings.vSyncCount = 1;
            var settings = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            var inputMode = settings.FindProperty("activeInputHandler");
            if (inputMode != null) { inputMode.intValue = 0; settings.ApplyModifiedPropertiesWithoutUndo(); }
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log("TENFE_SCENE_READY " + ScenePath);
        }
        [MenuItem("Ten Fe/Compilar Windows")]
        public static void BuildWindows()
        {
            if (!File.Exists(ScenePath)) CreateScene();
            // Keep the sentinel's dense animated vertices on the GPU instead of uploading CPU skins each frame.
            PlayerSettings.meshDeformation = MeshDeformation.GPU;
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath }, locationPathName = "Builds/Windows/TenFe.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.Development
            });
            if (report.summary.result != BuildResult.Succeeded) throw new Exception("Build failed: " + report.summary.result);
            if (File.Exists("Docs/THIRD_PARTY_NOTICES.txt"))
                File.Copy("Docs/THIRD_PARTY_NOTICES.txt", "Builds/Windows/THIRD_PARTY_NOTICES.txt", true);
            Debug.Log("TENFE_BUILD_OK " + report.summary.totalSize);
        }
        public static void ValidateAndBuild()
        {
            CreateScene();
            ValidateCore();
            BuildWindows();
        }
        public static void ValidateExistingAndBuild()
        {
            if (!File.Exists(ScenePath)) throw new Exception("Missing scene: " + ScenePath);
            ValidateCore();
            BuildWindows();
        }
        [MenuItem("Ten Fe/Validar reglas y guardado")]
        public static void ValidateCore()
        {
            int checks = 0;
            var actor = new GameObject("TestActor");
            try
            {
                var health = actor.AddComponent<Health>(); health.maximum = 100; health.Restore();
                int deaths = 0; health.Died += () => deaths++;
                health.Damage(-1); Require(health.Current == 100, "Negative damage", ref checks);
                health.Damage(25); health.Heal(10); Require(health.Current == 85, "Damage and healing", ref checks);
                health.Damage(200); health.Damage(50); health.Heal(200); Require(health.IsDead && deaths == 1, "Death emitted once, no resurrection by healing", ref checks);
                health.Restore(); Require(health.Current == 100, "Restore", ref checks);
                var stamina = actor.AddComponent<Stamina>(); stamina.Restore();
                Require(stamina.Spend(80) && !stamina.Spend(30) && stamina.Current == 20, "Energy cannot overdraw", ref checks);
                stamina.Restore(); Require(stamina.Current == 100, "Energy restored", ref checks);
                string folder = Path.Combine(Application.dataPath, "../Temp/TenFeTests"); Directory.CreateDirectory(folder);
                string path = Path.Combine(folder, "save.json");
                var data = new SaveData { faith = 210, level = 2, checkpoint = 1, shortcut = true, droppedFaith = 40, dropPosition = new Vector3(2, 0, 5) };
                Require(SaveStore.Write(data, path) && SaveStore.Read(path, out var loaded) && loaded.faith == 210 && loaded.checkpoint == 1 && loaded.dropPosition.z == 5, "Save round trip", ref checks);
                data.boss = true; Require(SaveStore.Write(data, path) && SaveStore.Read(path, out var replaced) && replaced.boss, "Atomic save replacement", ref checks);
                File.WriteAllText(path, "invalid-json"); Require(!SaveStore.Read(path, out _), "Corrupt save rejected", ref checks);
                File.WriteAllText(path, "{\"version\":99}"); Require(!SaveStore.Read(path, out _), "Unknown save version rejected", ref checks);
                File.WriteAllText(path, "{\"version\":1,\"level\":90}"); Require(!SaveStore.Read(path, out _), "Invalid stats rejected", ref checks);
                var target = new GameObject("TestTarget"); target.transform.position = Vector3.forward * 2;
                Require(CombatQuery.InArc(actor.transform, target.transform, 3, 60), "Forward hit", ref checks);
                target.transform.position = Vector3.back * 2;
                Require(!CombatQuery.InArc(actor.transform, target.transform, 3, 60), "Rear target rejected", ref checks);
                UnityEngine.Object.DestroyImmediate(target);
            }
            finally { UnityEngine.Object.DestroyImmediate(actor); }
            Directory.CreateDirectory("Docs/Validation");
            File.WriteAllText("Docs/Validation/core.txt", "PASS: " + checks + " checks. Unity " + Application.unityVersion + ".\nHealth, stamina, forward/rear melee, save roundtrip/replacement/corruption/version/range.\n");
            Debug.Log("TENFE_CORE_TESTS_OK " + checks);
        }
        static void Require(bool condition, string message, ref int checks)
        { if (!condition) throw new Exception("Validation failed: " + message); checks++; }
    }
}
