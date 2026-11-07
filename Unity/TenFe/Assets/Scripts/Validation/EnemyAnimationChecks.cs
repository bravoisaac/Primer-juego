using System;
using System.Collections;
using UnityEngine;

namespace TenFe
{
    internal static class EnemyAnimationChecks
    {
        internal static IEnumerator Run(GameSession game, Action<bool, string> check, Action<EnemyBrain, string> capture)
        {
            foreach (var enemy in game.Enemies) enemy.enabled = false;
            var guard = game.Enemies[0];
            var visual = guard.animatedVisual;
            var player = game.Player;
            guard.ResetEnemy(); guard.enabled = true;
            player.RestoreAt(guard.Home - Vector3.forward * 5);
            float deadline = Time.time + 4;
            while (visual.Playing != "Run" && Time.time < deadline) yield return null;
            guard.ReceiveHit(1, false);
            yield return new WaitForSeconds(.08f);
            check(visual.Playing != "Hit" && guard.MotionSpeed > .1f,
                "A light non-staggering hit preserves skeletal locomotion");
            guard.ReceiveHit(1, true);
            yield return new WaitForSeconds(.3f);
            float before = visual.animator.GetCurrentAnimatorStateInfo(0).normalizedTime;
            guard.ReceiveHit(1, true);
            yield return new WaitForSeconds(.07f);
            var repeated = visual.animator.GetCurrentAnimatorStateInfo(0);
            check(visual.Playing == "Hit" && repeated.IsName("Hit") && repeated.normalizedTime < .3f && repeated.normalizedTime < before,
                "A repeated stagger restarts the recoil instead of holding its old ending");

            game.SetPaused(true);
            yield return new WaitForEndOfFrame();
            Vector3 handBefore = visual.rightHand.position;
            yield return new WaitForSecondsRealtime(.15f);
            check(Vector3.Distance(handBefore, visual.rightHand.position) < .001f, "Pause freezes the skeletal hit pose");
            game.SetPaused(false);
            guard.enabled = false; guard.ResetEnemy();
            yield return new WaitForSeconds(.12f);
            check(visual.Playing == "Idle" && !visual.animator.IsInTransition(0),
                "Rest/reset clears live recoil and returns to the ready pose without requiring death");

            player.RestoreAt(guard.Home - Vector3.forward * 1.8f);
            guard.enabled = true;
            deadline = Time.time + 4;
            while ((!guard.Telegraphing || guard.ActionProgress < .85f) && Time.time < deadline) yield return null;
            yield return new WaitForEndOfFrame();
            capture(guard, "animacion_preparacion.png");
            Vector3 chargedHand = guard.transform.InverseTransformPoint(visual.rightHand.position);
            float healthBefore = player.Health.Current;
            deadline = Time.time + 2;
            while (player.Health.Current >= healthBefore && Time.time < deadline) yield return null;
            yield return new WaitForEndOfFrame();
            var contact = visual.animator.GetCurrentAnimatorStateInfo(0);
            check(contact.IsName("Strike") && Mathf.Abs(contact.normalizedTime - guard.ActionProgress) < .065f &&
                Mathf.Abs(player.Health.Current - (healthBefore - 18)) < .01f,
                "Rendered strike progress agrees with the AI contact frame and applies damage once");
            Vector3 contactHand = guard.transform.InverseTransformPoint(visual.rightHand.position);
            check(Vector3.Distance(chargedHand, contactHand) > .2f, "Sword hand travels from anticipation through the contact arc");
            capture(guard, "animacion_contacto.png");
            deadline = Time.time + 2;
            while (guard.Motion == "Strike" && guard.ActionProgress < .82f && Time.time < deadline) yield return null;
            yield return new WaitForEndOfFrame();
            float recoveryTravel = Vector3.Distance(contactHand, guard.transform.InverseTransformPoint(visual.rightHand.position));
            check(visual.Playing == "Strike" && player.Health.Current == healthBefore - 18 &&
                recoveryTravel > .08f,
                "Strike follows through and recovers without applying a second hit (phase=" + guard.ActionProgress.ToString("F2") +
                ", hand travel=" + recoveryTravel.ToString("F3") + ", health=" + player.Health.Current + ")");
            capture(guard, "animacion_recuperacion.png");
            guard.enabled = false;

            var boss = game.Enemies.Find(e => e.boss);
            boss.gameObject.SetActive(true); boss.ResetEnemy(); boss.enabled = true;
            player.RestoreAt(boss.Home - Vector3.forward * 2.6f);
            deadline = Time.time + 4;
            while ((!boss.Telegraphing || boss.ActionProgress < .2f) && Time.time < deadline) yield return null;
            yield return new WaitForEndOfFrame();
            Quaternion early = boss.visual.swordArm.localRotation;
            deadline = Time.time + 2;
            while (boss.Telegraphing && boss.ActionProgress < .85f && Time.time < deadline) yield return null;
            yield return new WaitForEndOfFrame();
            Quaternion charged = boss.visual.swordArm.localRotation;
            check(boss.Telegraphing && Quaternion.Angle(early, charged) > 35, "Aster visibly raises his weapon throughout anticipation");
            healthBefore = player.Health.Current;
            deadline = Time.time + 2;
            while (player.Health.Current >= healthBefore && Time.time < deadline) yield return null;
            yield return new WaitForEndOfFrame();
            check(boss.Motion == "Strike" && player.Health.Current == healthBefore - 27 &&
                Quaternion.Angle(charged, boss.visual.swordArm.localRotation) > 60,
                "Aster swings through contact instead of holding a fixed attack pose");
            capture(boss, "animacion_aster.png");
            boss.enabled = false;
            foreach (var enemy in game.Enemies) enemy.enabled = false;
            player.RestoreAt(game.altars[0].respawnPoint.position);
        }
    }
}
