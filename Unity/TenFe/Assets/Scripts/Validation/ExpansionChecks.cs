using System;
using System.Collections;
using UnityEngine;

namespace TenFe
{
    internal static class ExpansionChecks
    {
        internal static IEnumerator Run(GameSession game, Action<bool, string> check,
            Action<Camera, string> capture, Action<Camera> configureCamera)
        {
            var wing = GameObject.Find("Claustro de la Memoria");
            check(wing != null, "Expanded west cloister is present in the saved scene");
            if (wing == null) yield break;
            var player = game.Player;
            var motor = player.GetComponent<CharacterController>();
            foreach (var enemy in game.Enemies)
            {
                enemy.enabled = false;
                // Geometry traversal is isolated from stationary actor occupancy; combat is tested below.
                enemy.GetComponent<CharacterController>().enabled = false;
            }
            player.TestInput = default;
            player.enabled = false;
            bool supported = true, unobstructed = true;
            string groundFailure = "", passageFailure = "";
            // Walk the full loop and the relic spur with the actual capsule, in both directions.
            // Small substeps test bridge seams, portals and decoration instead of teleporting past them.
            Vector3[] route = {
                new Vector3(-7, .1f, -4), new Vector3(-28, .1f, -4), new Vector3(-28, .1f, 10),
                new Vector3(-36, .1f, 10), new Vector3(-36, .1f, 36), new Vector3(-36, .1f, 28),
                new Vector3(-7, .1f, 28)
            };
            try
            {
                player.RestoreAt(route[0]);
                Physics.SyncTransforms();
                for (int pass = 0; pass < 2; pass++)
                {
                    if (pass == 1) Array.Reverse(route);
                    for (int i = 1; i < route.Length; i++)
                    {
                        Vector3 from = route[i - 1], to = route[i];
                        int steps = Mathf.CeilToInt(Vector3.Distance(from, to) / .2f);
                        for (int step = 1; step <= steps; step++)
                        {
                            Vector3 target = Vector3.Lerp(from, to, (float)step / steps);
                            bool hasGround = Physics.Raycast(target + Vector3.up, Vector3.down, out var floor, 2, 1 << 0)
                                && Mathf.Abs(floor.point.y) < .08f;
                            if (!hasGround && supported) groundFailure = " at " + target + " (" + (floor.collider != null ? floor.collider.name : "no ground") + ")";
                            supported &= hasGround;
                            Vector3 move = target - player.transform.position; move.y = -.12f;
                            motor.Move(move);
                            Vector3 error = target - player.transform.position; error.y = 0;
                            bool clear = error.sqrMagnitude < .01f && player.transform.position.y > -.15f;
                            if (!clear && unobstructed) passageFailure = " at " + target + " (capsule " + player.transform.position + ")";
                            unobstructed &= clear;
                            if (step % 16 == 0) yield return null;
                        }
                    }
                }
                check(supported, "Both bridges, cloister loop and relic approach have continuous level ground" + groundFailure);
                check(unobstructed, "Player capsule traverses the full expansion in both directions without obstruction or falling" + passageFailure);
                player.RestoreAt(new Vector3(-36, .1f, 36));
                yield return null;
                check(game.Nearby == game.relic, "Nerea relic is reachable through the gallery interaction radius");
                check(game.shortcut.gate.activeSelf && !game.Progress.shortcut && game.altars.Length == 2,
                    "Expansion preserves the locked east shortcut and both checkpoint references");

                // Verify parapets block the capsule at each exposed edge, including both bridges.
                Vector3[] starts = { new Vector3(-48, .1f, 6), new Vector3(-36, .1f, -14),
                    new Vector3(-24, .1f, 6), new Vector3(-17, .1f, -4), new Vector3(-17, .1f, 28) };
                Vector3[] directions = { Vector3.left, Vector3.back, Vector3.right, Vector3.forward, Vector3.back };
                bool enclosed = true;
                for (int i = 0; i < starts.Length; i++)
                {
                    player.RestoreAt(starts[i]);
                    for (int j = 0; j < 30; j++) motor.Move(directions[i] * .2f + Vector3.down * .1f);
                    enclosed &= Vector3.Distance(starts[i], player.transform.position) < 3;
                }
                check(enclosed, "Courtyard edges and both bridge parapets stop the player capsule");
                player.enabled = true;
                var guard = game.Enemies[1];
                guard.ResetEnemy(); guard.enabled = true;
                player.RestoreAt(new Vector3(-28, .1f, 2));
                float deadline = Time.time + 7;
                bool approached = false;
                while (!guard.Telegraphing && Time.time < deadline)
                {
                    approached |= guard.MotionSpeed > .4f;
                    yield return null;
                }
                check(guard.Home.x < -22 && approached && guard.Telegraphing,
                    "Relocated courtyard guardian perceives, approaches and prepares an attack on the new ground");
                guard.enabled = false; guard.ResetEnemy();

                var obj = new GameObject("Expansion validation camera");
                try
                {
                    var camera = obj.AddComponent<Camera>(); camera.enabled = false;
                    camera.fieldOfView = 65; camera.farClipPlane = 220;
                    configureCamera(camera);
                    Vector3[] views = { new Vector3(-20, 5, -6), new Vector3(-36, 3, 20), new Vector3(-65, 48, -34) };
                    Vector3[] targets = { new Vector3(-39, 3, 6), new Vector3(-36, 4, 42), new Vector3(-17, 0, 15) };
                    string[] files = { "mapa_claustro.png", "mapa_nerea.png", "mapa_general.png" };
                    for (int i = 0; i < views.Length; i++)
                    {
                        camera.transform.position = views[i]; camera.transform.LookAt(targets[i]);
                        capture(camera, files[i]);
                        yield return null;
                    }
                }
                finally { UnityEngine.Object.Destroy(obj); }
            }
            finally
            {
                player.enabled = true; player.RestoreAt(game.altars[0].respawnPoint.position);
                foreach (var enemy in game.Enemies) { enemy.ResetEnemy(); enemy.enabled = true; }
            }
        }
    }
}
