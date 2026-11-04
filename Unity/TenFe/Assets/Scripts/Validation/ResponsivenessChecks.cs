using System;
using System.Collections;
using UnityEngine;

namespace TenFe
{
    internal static class ResponsivenessChecks
    {
        internal static IEnumerator Run(GameSession game, Action<bool, string> check)
        {
            var buffer = new PlayerActionBuffer();
            buffer.Record(new PlayerInputFrame { Light = true }, Vector3.forward, 1);
            buffer.Record(new PlayerInputFrame { Dodge = true }, Vector3.left, 1.05f);
            check(buffer.Take(1.1f, out var action, out var direction) && action == BufferedAction.Dodge && direction == Vector3.left,
                "Latest combat intent replaces the previous one and retains its direction");
            check(!buffer.Take(1.11f, out _, out _), "Buffered input is consumed only once");
            buffer.Record(new PlayerInputFrame { Heavy = true }, Vector3.forward, 2);
            check(!buffer.Take(2.21f, out _, out _), "Early combat input expires rather than executing much later");

            foreach (var enemy in game.Enemies) enemy.enabled = false;
            var player = game.Player;
            Vector3 spawn = game.altars[0].respawnPoint.position;
            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.15f);
            yield return Pulse(player, new PlayerInputFrame { Light = true });
            yield return new WaitForSeconds(.49f);
            Vector3 before = player.transform.position;
            yield return Pulse(player, new PlayerInputFrame { Dodge = true, Move = Vector2.left });
            check(!player.Dodging && Mathf.Approximately(player.Energy.Current, 78),
                "Queued dodge neither cancels an attack nor spends stamina early");
            yield return new WaitForSeconds(.18f);
            check(player.Dodging && Mathf.Approximately(player.Energy.Current, 54) && player.transform.position.x < before.x - .1f,
                "Late dodge begins after recovery, moves in the requested direction and pays once");

            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.15f);
            yield return Pulse(player, new PlayerInputFrame { Light = true });
            yield return Pulse(player, new PlayerInputFrame { Heavy = true });
            yield return new WaitForSeconds(.68f);
            check(Mathf.Approximately(player.Energy.Current, 78), "Early heavy input does not start a delayed attack after recovery");

            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.15f);
            yield return Pulse(player, new PlayerInputFrame { Light = true });
            yield return new WaitForSeconds(.49f);
            yield return Pulse(player, new PlayerInputFrame { Dodge = true });
            game.SetPaused(true);
            yield return new WaitForSecondsRealtime(.25f);
            game.SetPaused(false);
            yield return new WaitForSeconds(.19f);
            check(!player.Dodging && Mathf.Approximately(player.Energy.Current, 78), "Pause discards pending combat input before resuming");

            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.15f);
            yield return Pulse(player, new PlayerInputFrame { Light = true });
            yield return new WaitForSeconds(.49f);
            yield return Pulse(player, new PlayerInputFrame { Dodge = true });
            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.1f);
            check(!player.Dodging && player.Energy.Current == 100, "Restoring at an altar clears pending actions");
            player.Energy.Spend(100);
            yield return Pulse(player, new PlayerInputFrame { Dodge = true });
            player.Energy.Restore();
            yield return new WaitForSeconds(.1f);
            check(!player.Dodging && player.Energy.Current == 100, "Rejected action does not fire when stamina becomes available later");

            var orbit = player.orbit;
            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.1f);
            Vector3 pivot = player.transform.position + Vector3.up * 1.65f;
            float originalDistance = Vector3.Distance(pivot, orbit.transform.position);
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = "Temporary camera collision test";
            wall.transform.position = pivot - orbit.transform.forward * 2;
            wall.transform.localScale = new Vector3(4, 4, .3f);
            Physics.SyncTransforms();
            yield return new WaitForSeconds(.05f);
            float contracted = Vector3.Distance(pivot, orbit.transform.position);
            check(contracted < 2 && contracted < originalDistance - 1,
                "Camera immediately contracts in front of an obstructing wall");
            orbit.Shake(.13f);
            yield return new WaitForSeconds(.05f);
            check(!Physics.CheckSphere(orbit.transform.position, .20f, 1 << 0, QueryTriggerInteraction.Ignore),
                "Hit shake keeps the camera sphere outside scenery");
            UnityEngine.Object.Destroy(wall);
            yield return new WaitForSeconds(.08f);
            float recovering = Vector3.Distance(pivot, orbit.transform.position);
            check(recovering > contracted + .1f && recovering < originalDistance - .25f,
                "Camera returns gradually when its obstruction disappears");
            yield return new WaitForSeconds(1);
            check(Mathf.Abs(Vector3.Distance(pivot, orbit.transform.position) - originalDistance) < .08f,
                "Camera recovers its original distance after clearing a wall");

            var guard = game.Enemies[0]; guard.ResetEnemy();
            player.RestoreAt(guard.Home - Vector3.forward * 3);
            yield return new WaitForSeconds(.1f);
            player.CycleTarget();
            yield return new WaitForSeconds(.7f);
            Vector3 relative = orbit.transform.position - (player.transform.position + Vector3.up * 1.65f);
            check(player.Target == guard && Vector3.Dot(relative, orbit.transform.right) > .5f,
                "Lock-on shifts the framing to reveal the enemy beside the player");
            pivot = player.transform.position + Vector3.up * 1.65f;
            var sideWall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            sideWall.name = "Temporary shoulder collision test";
            sideWall.transform.SetPositionAndRotation(pivot + orbit.transform.right * .45f - orbit.transform.forward * 2.5f,
                Quaternion.Euler(0, orbit.transform.eulerAngles.y, 0));
            sideWall.transform.localScale = new Vector3(.1f, 4, 12);
            Physics.SyncTransforms();
            yield return new WaitForSeconds(.1f);
            relative = orbit.transform.position - pivot;
            check(Vector3.Dot(relative, orbit.transform.right) < .2f &&
                !Physics.CheckSphere(orbit.transform.position, .20f, 1 << 0, QueryTriggerInteraction.Ignore),
                "Shoulder framing stays on the player side of a nearby lateral wall");
            UnityEngine.Object.Destroy(sideWall);
            game.SetPaused(true);
            Vector3 pausedPosition = orbit.transform.position;
            Quaternion pausedRotation = orbit.transform.rotation;
            yield return new WaitForSecondsRealtime(.15f);
            check(Vector3.Distance(pausedPosition, orbit.transform.position) < .001f && Quaternion.Angle(pausedRotation, orbit.transform.rotation) < .01f,
                "Camera follow and shake freeze during pause");
            game.SetPaused(false);
            player.RestoreAt(spawn);
            yield return new WaitForSeconds(.1f);
            relative = orbit.transform.position - (player.transform.position + Vector3.up * 1.65f);
            check(Mathf.Abs(Vector3.Dot(relative, orbit.transform.right)) < .01f,
                "Respawn clears shoulder framing and previous camera shake");
        }

        static IEnumerator Pulse(PlayerController player, PlayerInputFrame frame)
        {
            player.TestInput = frame;
            yield return null;
            player.TestInput = default(PlayerInputFrame);
        }
    }
}
