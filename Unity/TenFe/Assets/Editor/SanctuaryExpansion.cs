using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace TenFe.Editor
{
    // Additive, one-time scene upgrade. Existing authored geometry and actor references survive.
    public static class SanctuaryExpansion
    {
        const string RootName = "Claustro de la Memoria";
        static Transform root;
        static Material stone, edge, bronze, dark, cyan;

        [MenuItem("Ten Fe/Ampliar santuario con claustro oeste")]
        public static void Install()
        {
            if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene("Assets/Scenes/Santuario.unity");
            ApplyToScene();
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
            AssetDatabase.SaveAssets();
        }

        public static void InstallAndBuild()
        {
            Install();
            ProjectTools.ValidateCore();
            ProjectTools.BuildWindows();
        }

        public static void ApplyToScene()
        {
            // Running this menu again must preserve manual edits and never duplicate the wing.
            if (GameObject.Find(RootName) != null) return;
            var game = UnityEngine.Object.FindFirstObjectByType<GameSession>();
            var world = GameObject.Find("Santuario del Ocaso — geometría editable");
            if (game == null || world == null || game.Enemies.Count != 4 || game.relic == null)
                throw new InvalidOperationException("Falta la escena base del santuario.");
            stone = RequireMaterial("Art/Atmosphere/Basalto erosionado");
            edge = RequireMaterial("Art/Atmosphere/Caliza envejecida");
            bronze = RequireMaterial("Art/Atmosphere/Bronce envejecido");
            dark = RequireMaterial("Materials/Hierro oscuro");
            cyan = RequireMaterial("Materials/Fe olvidada");

            root = new GameObject(RootName).transform;
            root.SetParent(world.transform, false);
            // Two four-metre openings in the existing parapet, away from its pillars.
            foreach (var collider in world.GetComponentsInChildren<BoxCollider>())
                if (collider.name == "Borde oeste" &&
                    (Mathf.Abs(collider.transform.position.z + 4) < .1f || Mathf.Abs(collider.transform.position.z - 28) < .1f))
                    UnityEngine.Object.DestroyImmediate(collider.gameObject);

            // 28 x 60 m wing plus two 10 x 6 m bridges: 1,800 m² of additional platform.
            Box("Cimientos del claustro", new Vector3(-36, -1.3f, 14), new Vector3(28, 2.4f, 60), dark);
            Box("Patio de ceniza — suelo", new Vector3(-36, -.25f, 0), new Vector3(28, .5f, 32), stone);
            Box("Galería de la memoria — suelo", new Vector3(-36, -.25f, 30), new Vector3(28, .5f, 28), stone);
            Bridge(-4, "Paso de los peregrinos");
            Bridge(28, "Puente del umbral");

            Box("Pretil oeste", new Vector3(-50, .8f, 14), new Vector3(.7f, 1.6f, 60), edge);
            Box("Pretil sur", new Vector3(-36, .8f, -16), new Vector3(28, 1.6f, .7f), edge);
            Box("Ábside de Nerea", new Vector3(-36, 3, 44), new Vector3(28, 6, .8f), stone);
            foreach (var span in new[] { new Vector2(-16, -7), new Vector2(-1, 25), new Vector2(31, 44) })
                Box("Pretil este", new Vector3(-22, .8f, (span.x + span.y) / 2), new Vector3(.7f, 1.6f, span.y - span.x), edge);

            for (int z = -14; z <= 42; z += 4)
                for (int x = -48; x <= -24; x += 4)
                    Box("Losa del claustro", new Vector3(x, .012f, z), new Vector3(3.9f, .024f, 3.9f),
                        (x + z) % 12 == 0 ? edge : stone, false);
            // Continuous pale paving leads from both bridges to the wide central doorway.
            Box("Senda del patio", new Vector3(-28, .03f, 3), new Vector3(3, .025f, 14), edge, false);
            Box("Senda transversal", new Vector3(-32, .03f, 10), new Vector3(11, .025f, 3), edge, false);
            Box("Senda de Nerea", new Vector3(-36, .03f, 25), new Vector3(3, .025f, 30), edge, false);
            Box("Senda del umbral", new Vector3(-29, .03f, 28), new Vector3(14, .025f, 3), edge, false);

            // A fountain and broken portico give the open court a readable centre and silhouette.
            Cylinder("Fuente seca", new Vector3(-39, .2f, -2), new Vector3(7, .2f, 7), dark);
            Cylinder("Brocal de la fuente", new Vector3(-39, .6f, -2), new Vector3(4.8f, .4f, 4.8f), edge);
            Cylinder("Pilar del juramento roto", new Vector3(-39, 2.1f, -2), new Vector3(1.2f, 1.1f, 1.2f), stone);
            for (int z = -12; z <= 12; z += 8)
            {
                Pillar(-46, z, z == 4 ? 3.4f : 6.5f);
                Pillar(-25, z == -4 ? 0 : z, 5.4f);
            }
            Box("Dintel quebrado", new Vector3(-46, 6.7f, -8), new Vector3(1.5f, .6f, 9), edge);
            var fallen = Box("Columna caída", new Vector3(-44, .65f, 9), new Vector3(1.2f, 1.3f, 5), stone);
            fallen.transform.rotation = Quaternion.Euler(0, -24, 0);

            Box("Muro de galería oeste", new Vector3(-45, 2.4f, 16), new Vector3(10, 4.8f, .8f), stone);
            Box("Muro de galería este", new Vector3(-27, 2.4f, 16), new Vector3(10, 4.8f, .8f), stone);
            Pillar(-40, 16, 7); Pillar(-32, 16, 7);
            Box("Portal de la memoria", new Vector3(-36, 7, 16), new Vector3(9.5f, .8f, 1.6f), edge);
            Box("Friso de la memoria", new Vector3(-36, 7.5f, 16), new Vector3(10, .18f, 1.8f), bronze, false);
            for (int z = 20; z <= 40; z += 8)
            {
                Pillar(-46, z, 7.5f);
                // Leave the east-west approach at z=28 clear all the way to the north bridge.
                Pillar(-26, z == 28 ? 32 : z, 7.5f);
                Box("Sepulcro de los fieles", new Vector3(-48, .6f, z), new Vector3(2, 1.2f, 3), dark);
            }
            Box("Cubierta oeste", new Vector3(-46, 7.7f, 30), new Vector3(6, .5f, 28), stone);
            Box("Cubierta este", new Vector3(-26, 7.7f, 30), new Vector3(6, .5f, 28), stone);
            Box("Retablo de Nerea", new Vector3(-36, 4.4f, 43.4f), new Vector3(7, 8.8f, .6f), dark);
            for (int i = 0; i < 40; i++)
            {
                float angle = i * Mathf.PI * 2 / 40;
                var ray = Box("Aureola de la memoria", new Vector3(-36 + Mathf.Cos(angle) * 2.6f, 5 + Mathf.Sin(angle) * 2.6f, 42.9f),
                    new Vector3(.12f, .44f, .12f), bronze, false);
                ray.transform.rotation = Quaternion.Euler(0, 0, angle * Mathf.Rad2Deg);
            }
            Box("Luz de la memoria", new Vector3(-36, 5, 42.8f), new Vector3(.16f, 3, .18f), cyan, false);
            Box("Mesa votiva", new Vector3(-36, .7f, 41), new Vector3(6, 1.4f, 1.6f), edge);
            Banner(-40, 16); Banner(-32, 16);
            Banner(-46, 36); Banner(-26, 36);
            var light = new GameObject("Resplandor de Nerea").AddComponent<Light>();
            light.transform.SetParent(root, false); light.transform.position = new Vector3(-36, 3, 39);
            light.type = LightType.Point; light.color = new Color(.3f, .78f, 1); light.intensity = 2; light.range = 9;
            light.shadows = LightShadows.None;

            game.relic.transform.position = new Vector3(-36, 0, 38);
            game.Enemies[1].transform.position = new Vector3(-28, .1f, 7);
            Debug.Log("TENFE_EXPANSION_READY: connected west cloister, 1800 additional square metres, existing relic and guardian relocated");
        }

        static Material RequireMaterial(string path)
        {
            var material = AssetDatabase.LoadAssetAtPath<Material>("Assets/" + path + ".mat");
            if (material == null) throw new InvalidOperationException("Falta material: " + path);
            return material;
        }
        static GameObject Shape(string name, PrimitiveType type, Vector3 position, Vector3 scale, Material material, bool collision = true)
        {
            var obj = GameObject.CreatePrimitive(type); obj.name = name;
            obj.transform.SetParent(root, false); obj.transform.position = position; obj.transform.localScale = scale;
            obj.GetComponent<Renderer>().sharedMaterial = material;
            if (!collision) UnityEngine.Object.DestroyImmediate(obj.GetComponent<Collider>());
            obj.isStatic = true;
            return obj;
        }
        static GameObject Box(string name, Vector3 position, Vector3 scale, Material material, bool collision = true)
            => Shape(name, PrimitiveType.Cube, position, scale, material, collision);
        static void Cylinder(string name, Vector3 position, Vector3 scale, Material material)
            => Shape(name, PrimitiveType.Cylinder, position, scale, material);
        static void Pillar(float x, float z, float height)
        {
            Cylinder("Basamento", new Vector3(x, .2f, z), new Vector3(1.8f, .2f, 1.8f), edge);
            Cylinder("Columna del claustro", new Vector3(x, height / 2, z), new Vector3(.9f, height / 2, .9f), stone);
            Box("Capitel del claustro", new Vector3(x, height, z), new Vector3(1.6f, .4f, 1.6f), edge);
        }
        static void Bridge(float z, string name)
        {
            Box(name, new Vector3(-17, -.35f, z), new Vector3(10.6f, .7f, 6), stone);
            Box("Pretil del puente", new Vector3(-17, .7f, z - 3), new Vector3(10.6f, 1.4f, .5f), edge);
            Box("Pretil del puente", new Vector3(-17, .7f, z + 3), new Vector3(10.6f, 1.4f, .5f), edge);
            Box("Guía de bronce", new Vector3(-17, .025f, z), new Vector3(10.6f, .025f, .13f), bronze, false);
            for (int side = -1; side <= 1; side += 2)
            {
                Pillar(-23.5f, z + side * 3.5f, 4.5f);
                Box("Sello del paso", new Vector3(-23.5f, 3.5f, z + side * 3.5f), new Vector3(1, .18f, 1), bronze, false);
            }
        }
        static void Banner(float x, float z)
        {
            var template = GameObject.Find("Estandarte 0 -1");
            if (template == null) return;
            var banner = UnityEngine.Object.Instantiate(template, root);
            banner.name = "Estandarte de la memoria";
            banner.transform.position = new Vector3(x, 5.8f, z - .7f);
        }
    }
}
