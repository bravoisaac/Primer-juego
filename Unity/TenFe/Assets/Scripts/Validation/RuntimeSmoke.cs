using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TenFe
{
    // Runs only with --smoke-test, against an in-memory save. Never touches a real player's progress.
    public sealed class RuntimeSmoke : MonoBehaviour
    {
        readonly List<string> checks = new List<string>();
        string output;
        bool failed;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Boot()
        {
            if (Array.Exists(Environment.GetCommandLineArgs(), arg => arg == "--smoke-test"))
                new GameObject("Runtime smoke validation").AddComponent<RuntimeSmoke>();
        }
        void Awake()
        {
            // Hidden windows may ignore vSync; cap this automated session rather than flooding the GPU.
            QualitySettings.vSyncCount = 0; Application.targetFrameRate = 60;
            output = Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Docs/Validation"));
            Directory.CreateDirectory(output);
            Application.logMessageReceived += OnLog;
        }
        void OnLog(string message, string trace, LogType type)
        {
            if (type == LogType.Exception || type == LogType.Error || type == LogType.Assert)
            { failed = true; checks.Add("ENGINE ERROR: " + message + "\n" + trace); }
        }
        void Check(bool condition, string label)
        {
            checks.Add((condition ? "PASS " : "FAIL ") + label);
            if (!condition) failed = true;
        }
        IEnumerator Start()
        {
            yield return null;
            var game = GameSession.Instance;
            Check(game != null && game.Ready && game.TestMode, "Scene boot and isolated test session");
            if (game == null || !game.Ready) { Finish(); yield break; }
            var player = game.Player;
            yield return new WaitForSeconds(.5f);
            Check(player.Health.Current == 100 && player.Energy.Current == 100 && player.Flasks == 3, "Player spawn resources");
            var controller = player.GetComponent<CharacterController>();
            Check(controller.isGrounded, "Ground collision at spawn (position=" + player.transform.position + ", flags=" + controller.collisionFlags + ", minimum=" + controller.minMoveDistance + ")");
            Check(game.Enemies.Count == 4 && game.altars.Length == 2, "Four enemies and two checkpoints");
            yield return ValidateAtmosphere(game);
            yield return ExpansionChecks.Run(game, Check, CaptureScene, ConfigureAtmosphereCamera);
            CaptureScene(player.orbit.GetComponent<Camera>(), "santuario.png");
            yield return new WaitForSeconds(.2f);

            // Exercise real perception, windup and damage before freezing AI for deterministic economy checks.
            var guard = game.Enemies[0];
            player.RestoreAt(guard.transform.position + Vector3.forward * 1.7f);
            float detectionTimeout = Time.time + 3;
            while (!guard.Telegraphing && Time.time < detectionTimeout) yield return null;
            Check(guard.Engaged && guard.Telegraphing, "Enemy detects player and announces its strike");
            yield return new WaitForSeconds(1);
            Check(player.Health.Current < 100, "Enemy windup resolves into damage");
            foreach (var enemy in game.Enemies) enemy.enabled = false;
            player.RestoreAt(game.altars[0].respawnPoint.position);
            game.Rest(game.altars[0]);
            Check(!guard.Engaged && player.Health.Current == 100, "Safe rest resets encounters and resources");

            Vector3 start = player.transform.position;
            player.TestInput = new PlayerInputFrame { Move = Vector2.up, Sprint = true };
            yield return new WaitForSeconds(.3f);
            player.TestInput = default(PlayerInputFrame);
            Check(player.transform.position.z > start.z + 1 && player.Energy.Current < 100, "Sprint moves character and consumes stamina");
            yield return new WaitForSeconds(.1f);
            player.TestInput = new PlayerInputFrame { Block = true };
            yield return null;
            float energy = player.Energy.Current;
            player.ReceiveHit(20, player.transform.position + player.transform.forward * 2);
            Check(player.Health.Current == 100 && player.Energy.Current < energy, "Frontal block spends energy and prevents damage");
            player.ReceiveHit(20, player.transform.position - player.transform.forward * 2);
            Check(player.Health.Current == 80, "Rear attacks bypass the shield");
            player.TestInput = default(PlayerInputFrame);
            yield return new WaitForSeconds(.4f);
            player.TestInput = new PlayerInputFrame { Heal = true };
            yield return null;
            player.TestInput = default(PlayerInputFrame);
            yield return new WaitForSeconds(1.1f);
            Check(player.Health.Current == 100 && player.Flasks == 2, "Healing action resolves and consumes one flask");
            player.RestoreAt(start);
            yield return new WaitForSeconds(.3f);
            player.TestInput = new PlayerInputFrame { Dodge = true };
            yield return null;
            player.TestInput = default(PlayerInputFrame);
            yield return new WaitForSeconds(.12f);
            player.ReceiveHit(30, player.transform.position + Vector3.forward);
            Check(player.Invulnerable && player.Health.Current == 100, "Dodge grants invulnerability only during its window");
            yield return new WaitForSeconds(.5f);
            player.ReceiveHit(30, player.transform.position + Vector3.forward);
            Check(!player.Invulnerable && player.Health.Current == 70, "Damage resumes after the dodge window");
            player.RestoreAt(start);
            yield return new WaitForSeconds(.3f);
            player.TestInput = new PlayerInputFrame { Jump = true };
            yield return null;
            player.TestInput = default(PlayerInputFrame);
            yield return new WaitForSeconds(.18f);
            Check(player.transform.position.y > start.y + .4f, "Jump lifts player off the floor");
            yield return new WaitForSeconds(.8f);
            Check(controller.isGrounded, "Player lands after jumping");
            player.RestoreAt(guard.transform.position - Vector3.forward * 2);
            yield return new WaitForSeconds(.3f);
            player.CycleTarget();
            Check(player.Target == guard, "Lock-on selects a visible enemy in front");
            player.TestInput = new PlayerInputFrame { Light = true };
            yield return null;
            player.TestInput = default(PlayerInputFrame);
            yield return new WaitForSeconds(.7f);
            Check(guard.Health.Current == 61, "Light attack damages target exactly once");
            player.TestInput = new PlayerInputFrame { Heavy = true };
            yield return null;
            player.TestInput = default(PlayerInputFrame);
            yield return new WaitForSeconds(1.15f);
            Check(guard.Health.Current == 16, "Heavy attack resolves after windup with higher damage");
            player.RestoreAt(game.altars[0].respawnPoint.position);

            // A scenery collider between two actors must block both melee and targeting.
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.transform.position = new Vector3(0, 1, -13); wall.transform.localScale = new Vector3(4, 3, .3f);
            Physics.SyncTransforms();
            Check(!CombatQuery.Clear(new Vector3(0, 1, -15), new Vector3(0, 1, -11)), "Walls block melee and lock-on");
            Destroy(wall);
            yield return null;

            guard.ReceiveHit(500, true);
            Check(guard.Health.IsDead && game.Progress.faith == 35, "Enemy death grants faith once");
            guard.ReceiveHit(500, true);
            Check(game.Progress.faith == 35, "Dead enemy cannot grant duplicate reward");
            game.ClaimRelic(); game.ClaimRelic();
            Check(game.Progress.faith == 110 && !game.relic.gameObject.activeSelf, "Relic is collected once");
            Check(game.Upgrade() && game.Progress.faith == 30 && player.Health.maximum == 125, "Benediction costs faith and increases vitality");
            Check(!game.Upgrade() && game.Progress.faith == 30, "Insufficient faith cannot buy an upgrade");
            game.OpenShortcut();
            Check(game.Progress.shortcut && !game.shortcut.gate.activeSelf, "Shortcut unlock removes the barrier");
            game.Rest(game.altars[1]);
            Check(game.Progress.checkpoint == 1 && !guard.Health.IsDead && player.Flasks == 3, "Second altar records spawn and revives regular enemies");

            player.Health.Damage(1000);
            Check(game.Progress.faith == 0 && game.Progress.droppedFaith == 30 && game.vestige.gameObject.activeSelf, "Death creates recoverable faith");
            yield return new WaitForSeconds(2.9f);
            Check(!player.Health.IsDead && Vector3.Distance(player.transform.position, game.altars[1].respawnPoint.position) < .4f, "Timed respawn uses last altar");
            game.RecoverFaith();
            Check(game.Progress.faith == 30 && game.Progress.droppedFaith == 0 && !game.vestige.gameObject.activeSelf, "Recovery restores faith and consumes vestige");
            player.Health.Damage(1000); yield return new WaitForSeconds(2.9f);
            player.Health.Damage(1000);
            Check(game.Progress.droppedFaith == 0 && !game.vestige.gameObject.activeSelf, "Second death replaces the old unrecovered vestige");
            yield return new WaitForSeconds(2.9f);

            var boss = game.Enemies.Find(e => e.boss);
            boss.ReceiveHit(300, true); Check(boss.Enraged && !boss.Health.IsDead, "Boss switches phase below half health");
            boss.ResetEnemy();
            player.RestoreAt(new Vector3(0, .1f, 36));
            boss.enabled = true;
            game.Notify("ASTER · DIOS DEL OCASO", 3);
            yield return new WaitForSeconds(.3f);
            CaptureScene(player.orbit.GetComponent<Camera>(), "aster.png");
            yield return new WaitForSeconds(.3f);
            boss.enabled = false;
            boss.ReceiveHit(1000, true);
            Check(game.Progress.boss && game.Progress.faith == 300, "Boss defeat records victory and reward");
            game.Rest(game.altars[0]);
            Check(boss.Health.IsDead && game.Progress.boss, "Rest preserves defeated boss");
            game.SetPaused(true);
            Check(Time.timeScale == 0 && Cursor.lockState == CursorLockMode.None, "Pause freezes world and frees cursor");
            yield return new WaitForSecondsRealtime(.3f);
            game.SetPaused(false);
            Check(Time.timeScale == 1, "Resume restores game time");
            yield return ValidateSentinel(game);
            yield return ValidateNaturalMovement(game);
            yield return ResponsivenessChecks.Run(game, Check);
            yield return ValidateHud(game);
            Finish();
        }
        IEnumerator ValidateHud(GameSession game)
        {
            var hud = FindFirstObjectByType<GameHud>();
            Check(hud != null && hud.enabled, "Presentation HUD is active");
            if (hud == null) yield break;
            // Recreate the initially hidden swapchain before reading its rendered backbuffer.
            // Changing only GUI state does not make a hidden initial window draw a frame.
            Screen.SetResolution(1024, 768, FullScreenMode.Windowed);
            yield return new WaitForSecondsRealtime(.5f);
            Screen.SetResolution(1280, 720, FullScreenMode.Windowed);
            yield return new WaitForSecondsRealtime(.5f);
            foreach (var enemy in game.Enemies) enemy.enabled = false;
            game.Player.RestoreAt(game.altars[0].respawnPoint.position);
            game.Notify("SANTUARIO DEL OCASO · La fe aún arde", 30);
            yield return new WaitForSecondsRealtime(.2f);
            yield return CaptureHud("hud_juego.png");
            hud.HelpVisible = true;
            yield return CaptureHud("hud_ayuda.png");
            hud.HelpVisible = false;
            game.SetPaused(true);
            yield return CaptureHud("hud_pausa.png");
            Screen.SetResolution(1024, 768, FullScreenMode.Windowed);
            yield return new WaitForSecondsRealtime(.5f);
            Check(Screen.width == 1024 && Screen.height == 768, "4:3 presentation resolution applied");
            yield return CaptureHud("hud_pausa_4x3.png");
            game.SetPaused(false);
            yield return CaptureHud("hud_juego_4x3.png");
            Screen.SetResolution(1920, 1080, FullScreenMode.Windowed);
            yield return new WaitForSecondsRealtime(.5f);
            Check(Screen.width == 1920 && Screen.height == 1080, "1080p presentation resolution applied");
            game.SetPaused(true);
            yield return CaptureHud("hud_pausa_1080.png");
            Screen.SetResolution(1280, 720, FullScreenMode.Windowed);
            yield return new WaitForSecondsRealtime(.5f);
            game.SetPaused(false);
            game.Player.RestoreAt(game.altars[0].transform.position - Vector3.forward * 2);
            game.Progress.level = 5;
            game.Player.Health.maximum = 225;
            game.Player.Health.Restore();
            game.Notify("Bendición de la llama · Vitalidad aumentada", 5);
            yield return null;
            Check(game.Nearby == game.altars[0], "Altar interaction is available for presentation capture");
            yield return CaptureHud("hud_altar.png");
            var guard = game.Enemies[0];
            guard.ResetEnemy();
            game.Player.RestoreAt(guard.Home - Vector3.forward * 2);
            game.Player.CycleTarget();
            guard.enabled = true;
            float deadline = Time.time + 4;
            while (!guard.Telegraphing && Time.time < deadline) yield return null;
            Check(game.Player.Target == guard && guard.Telegraphing, "Target and attack warning are visible together");
            yield return CaptureHud("hud_combate.png");
            guard.enabled = false;
            var boss = game.Enemies.Find(e => e.boss);
            game.Progress.boss = false;
            boss.gameObject.SetActive(true); boss.ResetEnemy(); boss.enabled = true;
            game.Player.RestoreAt(boss.Home - Vector3.forward * 2);
            boss.ReceiveHit(300, false);
            deadline = Time.time + 4;
            while (!boss.Telegraphing && Time.time < deadline) yield return null;
            Check(boss.Engaged && boss.Enraged, "Boss phase two HUD is available for presentation capture");
            game.Notify("", 0);
            yield return CaptureHud("hud_jefe.png");
            boss.enabled = false;
            game.Player.Health.Damage(1000);
            yield return CaptureHud("hud_muerte.png", true);
        }
        IEnumerator CaptureHud(string file, bool death = false)
        {
            // Read the rendered backbuffer after IMGUI, including pause while timeScale is zero.
            yield return new WaitForEndOfFrame();
            var pixels = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
            try
            {
                pixels.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0); pixels.Apply();
                File.WriteAllBytes(Path.Combine(output, file), pixels.EncodeToPNG());
                // The top gold panel edge (game) or center ornament (pause) distinguishes UI from a scene-only image.
                float scale = GameHud.CanvasScale(Screen.width, Screen.height);
                bool paused = GameSession.Instance.Paused;
                int x = paused || death ? Screen.width / 2 : Mathf.RoundToInt(44 * scale);
                int y = death ? Mathf.RoundToInt(Screen.height / 2f + 66 * scale) : paused
                    ? Mathf.RoundToInt(Screen.height / 2f + 210 * scale) : Screen.height - Mathf.RoundToInt(28 * scale) - 1;
                Color mark = pixels.GetPixel(x, y);
                Check(mark.r > .08f && mark.r > mark.b * 1.1f, "Rendered HUD ornament present: " + file);
            }
            finally { Destroy(pixels); }
        }
        IEnumerator ValidateSentinel(GameSession game)
        {
            var enemy = game.Enemies[0];
            var visual = enemy.animatedVisual;
            Check(visual != null && visual.body != null && visual.animator != null, "Meshy sentinel replaces the primitive enemy");
            if (visual == null) yield break;
            Check(visual.body.bones.Length >= 15 && visual.animator.avatar.isValid && !visual.animator.applyRootMotion,
                "Sentinel skin and generic avatar are bound; AI owns movement");
            foreach (string name in new[] { "Idle", "Walk", "Run", "Windup", "Strike", "Hit", "Death" })
                Check(visual.animator.HasState(0, Animator.StringToHash(name)), "Sentinel animation present: " + name);
            enemy.ResetEnemy();
            enemy.transform.position = enemy.Home;
            game.Player.RestoreAt(enemy.Home - Vector3.forward * 5);
            enemy.enabled = true;
            Vector3 initial = enemy.transform.position;
            float runTimeout = Time.time + 3;
            while (visual.Playing != "Run" && Time.time < runTimeout) yield return null;
            Check(enemy.transform.position.z < initial.z - .1f && visual.Playing == "Run", "Sentinel turns and accelerates into skeletal locomotion");
            var baked = new Mesh(); visual.body.BakeMesh(baked);
            Vector3[] before = baked.vertices;
            yield return new WaitForSeconds(.18f);
            visual.body.BakeMesh(baked);
            var after = baked.vertices;
            int changed = 0;
            for (int i = 0; i < before.Length; i++) if ((before[i] - after[i]).sqrMagnitude > .000001f) changed++;
            Check(changed > before.Length / 10, "Walking deforms the skinned mesh, not only the root transform");
            Destroy(baked);
            CaptureEnemy(enemy, "centinela_persiguiendo.png");
            float timeout = Time.time + 4;
            while (!enemy.Telegraphing && Time.time < timeout) yield return null;
            yield return new WaitForSeconds(.6f);
            Check(visual.Playing == "Windup", "AI attack windup drives the animation");
            CaptureEnemy(enemy, "centinela_ataque.png");
            float healthBefore = game.Player.Health.Current;
            yield return new WaitForSeconds(.5f);
            Check(visual.Playing == "Strike" && game.Player.Health.Current < healthBefore, "Animated strike applies a timed hit");
            enemy.ReceiveHit(1, true);
            yield return new WaitForSeconds(.15f);
            Check(visual.Playing == "Hit", "Sentinel plays hit reaction when staggered");
            enemy.ReceiveHit(1000, true);
            yield return new WaitForSeconds(1.6f);
            Check(visual.Playing == "Death" && !enemy.GetComponent<CharacterController>().enabled, "Sentinel death holds final pose and disables collision");
            CaptureEnemy(enemy, "centinela_muerto.png");
            enemy.enabled = false;
            enemy.ResetEnemy();
            yield return new WaitForSeconds(.3f);
            Check(visual.Playing == "Idle" && !enemy.Health.IsDead, "Sentinel respawn restores the rig from the death pose");
            CaptureEnemy(enemy, "centinela_integrado.png");
        }
        IEnumerator ValidateNaturalMovement(GameSession game)
        {
            var enemy = game.Enemies[0];
            enemy.ResetEnemy(); enemy.enabled = true;
            game.Player.RestoreAt(enemy.Home - Vector3.forward * 5);
            Vector3 origin = enemy.transform.position;
            yield return new WaitForSeconds(.15f);
            Check(enemy.Engaged && !enemy.Telegraphing && Vector3.Distance(origin, enemy.transform.position) < .15f,
                "Enemy observes before approaching instead of instantly running");
            bool limitedTurns = true, limitedAcceleration = true, ran = false, slowed = false;
            float previousSpeed = enemy.MotionSpeed;
            Quaternion previousRotation = enemy.transform.rotation;
            float deadline = Time.time + 7;
            while (!enemy.Telegraphing && Time.time < deadline)
            {
                yield return null;
                limitedTurns &= Quaternion.Angle(previousRotation, enemy.transform.rotation) <= 240 * Time.deltaTime + .2f;
                limitedAcceleration &= enemy.MotionSpeed - previousSpeed <= 6 * Time.deltaTime + .15f;
                ran |= enemy.animatedVisual.Playing == "Run";
                slowed |= ran && enemy.animatedVisual.Playing == "Walk";
                previousRotation = enemy.transform.rotation; previousSpeed = enemy.MotionSpeed;
            }
            Check(limitedTurns, "Turning and attack preparation never snap toward the player");
            Check(limitedAcceleration && ran, "Pursuit builds speed gradually and reaches a run");
            Check(slowed, "Enemy changes from running to walking near melee range");
            Check(enemy.Telegraphing && enemy.MotionSpeed < .12f, "Enemy plants its feet before announcing a strike");
            Vector3 planted = enemy.transform.position;
            Quaternion committed = enemy.transform.rotation;
            game.Player.RestoreAt(planted - enemy.transform.forward * 1.7f);
            float healthBefore = game.Player.Health.Current;
            yield return new WaitForSeconds(enemy.WindupDuration + .25f);
            Check(Quaternion.Angle(committed, enemy.transform.rotation) < .5f && Vector3.Distance(planted, enemy.transform.position) < .05f,
                "Committed windup and strike keep their heading and planted feet");
            Check(game.Player.Health.Current == healthBefore, "Moving behind a committed strike avoids its damage");

            enemy.ResetEnemy();
            game.Player.RestoreAt(game.altars[1].respawnPoint.position);
            yield return new WaitForSeconds(.4f);
            Check(!enemy.Engaged && enemy.MotionSpeed < .08f && enemy.animatedVisual.Playing == "Idle",
                "Reset clears momentum and starts a quiet patrol pause");
            bool walked = false, pausedAgain = false;
            deadline = Time.time + 9;
            while (Time.time < deadline && !pausedAgain)
            {
                yield return null;
                walked |= enemy.MotionSpeed > .3f;
                pausedAgain = walked && enemy.MotionSpeed < .08f;
            }
            Check(walked && pausedAgain && !enemy.Engaged, "Patrol walks to a nearby point then pauses naturally");
            enemy.enabled = false; enemy.ResetEnemy();
        }
        void CaptureEnemy(EnemyBrain enemy, string file)
        {
            var obj = new GameObject("Validation portrait camera");
            var camera = obj.AddComponent<Camera>(); camera.enabled = false;
            camera.fieldOfView = 40; camera.nearClipPlane = .1f; camera.farClipPlane = 140;
            ConfigureAtmosphereCamera(camera);
            Vector3 focus = enemy.transform.position + Vector3.up * 1.05f;
            camera.transform.position = enemy.transform.position + enemy.transform.forward * 3.4f - enemy.transform.right * 2.8f + Vector3.up * 2.2f;
            if (Physics.Linecast(focus, camera.transform.position, out RaycastHit obstacle, 1 << 0, QueryTriggerInteraction.Ignore))
                camera.transform.position = obstacle.point + (focus - obstacle.point).normalized * .3f;
            camera.transform.LookAt(focus);
            CaptureScene(camera, file); Destroy(obj);
        }
        void ConfigureAtmosphereCamera(Camera camera)
        {
            camera.clearFlags = CameraClearFlags.Skybox; camera.allowHDR = true;
            var source = GameSession.Instance.Player.orbit.GetComponent<SanctuaryImageEffect>();
            if (source == null) return;
            var effect = camera.gameObject.AddComponent<SanctuaryImageEffect>();
            effect.shader = source.shader; effect.bloom = source.bloom; effect.vignette = source.vignette;
        }
        IEnumerator ValidateAtmosphere(GameSession game)
        {
            var atmosphere = FindFirstObjectByType<SanctuaryAtmosphere>();
            Check(atmosphere != null && RenderSettings.skybox != null && RenderSettings.fog,
                "Sanctuary loads the authored sky, fog and atmosphere");
            if (atmosphere == null) yield break;
            var effect = game.Player.orbit.GetComponent<SanctuaryImageEffect>();
            Check(effect != null && effect.Supported, "Camera grade shader is supported in the Windows player");
            Check(atmosphere.flameLights.Length == 10 && atmosphere.GetComponentsInChildren<Collider>().Length == 0,
                "Atmosphere has ten flame lights and no new gameplay collisions");
            bool validShaders = true, hasSurface = false, hasBanner = false;
            foreach (var renderer in FindObjectsByType<Renderer>(FindObjectsSortMode.None))
            {
                var material = renderer.sharedMaterial;
                if (material == null) continue;
                validShaders &= material.shader != null && material.shader.isSupported && material.shader.name != "Hidden/InternalErrorShader";
                hasSurface |= material.shader.name == "TenFe/Weathered Stone";
                hasBanner |= material.shader.name == "TenFe/Pilgrim Banner";
            }
            Check(validShaders && hasSurface && hasBanner, "Weathered materials and wind banners have supported shaders");
            int live = 0, particleBudget = 0;
            foreach (var particles in FindObjectsByType<ParticleSystem>(FindObjectsSortMode.None))
            { if (particles.particleCount > 0) live++; particleBudget += particles.main.maxParticles; }
            Check(live >= 20 && particleBudget <= 1000, "Fire, embers and ash are active within the particle budget");
            var obj = new GameObject("Atmosphere validation camera");
            var camera = obj.AddComponent<Camera>(); camera.enabled = false; camera.fieldOfView = 62;
            camera.nearClipPlane = .1f; camera.farClipPlane = 220;
            ConfigureAtmosphereCamera(camera);
            Vector3[] positions = { new Vector3(0, 4, -15), new Vector3(-8, 3, 4), new Vector3(7, 3, 30) };
            Vector3[] targets = { new Vector3(0, 10, 55), new Vector3(1, 3, 23), new Vector3(0, 12, 80) };
            string[] files = { "atmosfera_entrada.png", "atmosfera_patio.png", "atmosfera_templo.png" };
            for (int i = 0; i < positions.Length; i++)
            {
                camera.transform.position = positions[i]; camera.transform.LookAt(targets[i]);
                CaptureScene(camera, files[i]);
                // Avoid submitting several full scene renders into one graphics frame.
                yield return null;
            }
            Destroy(obj);
        }
        void CaptureScene(Camera camera, string file)
        {
            // Explicit render works in a hidden validation window; desktop screenshots would be black.
            // These are scene previews, without the IMGUI HUD.
            var target = new RenderTexture(1280, 720, 24);
            var pixels = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            var oldTarget = camera.targetTexture;
            var oldActive = RenderTexture.active;
            try
            {
                camera.targetTexture = target; camera.Render(); RenderTexture.active = target;
                pixels.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); pixels.Apply();
                File.WriteAllBytes(Path.Combine(output, file), pixels.EncodeToPNG());
                Color center = pixels.GetPixel(640, 360);
                Check(center.maxColorComponent > .02f, "Camera renders non-black scene: " + file);
            }
            finally
            {
                camera.targetTexture = oldTarget; RenderTexture.active = oldActive;
                target.Release(); Destroy(target); Destroy(pixels);
            }
        }
        void Finish()
        {
            string report = (failed ? "FAILED" : "PASSED") + " runtime smoke checks\nUnity " + Application.unityVersion + "\n" + string.Join("\n", checks);
            File.WriteAllText(Path.Combine(output, "runtime.txt"), report);
            Debug.Log("TENFE_RUNTIME_" + (failed ? "FAIL" : "PASS") + " " + checks.Count);
            Application.Quit(failed ? 1 : 0);
        }
        void OnDestroy() => Application.logMessageReceived -= OnLog;
    }
}
