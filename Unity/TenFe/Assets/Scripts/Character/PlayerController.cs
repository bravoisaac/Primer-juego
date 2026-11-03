using UnityEngine;

namespace TenFe
{
    [RequireComponent(typeof(CharacterController), typeof(Health), typeof(Stamina))]
    public sealed class PlayerController : MonoBehaviour
    {
        public OrbitCamera orbit;
        public ActorVisual visual;
        public Health Health { get; private set; }
        public Stamina Energy { get; private set; }
        public EnemyBrain Target { get; private set; }
        public bool Blocking { get; private set; }
        public bool Dodging => action == ActionState.Dodge;
        public bool Invulnerable => Dodging && elapsed >= .04f && elapsed <= .34f;
        public int Flasks { get; private set; } = 3;
        public float MoveSpeed { get; private set; }
        enum ActionState { Free, Light, Heavy, Dodge, Heal, Stagger }
        ActionState action;
        CharacterController controller;
        Vector3 dodgeDirection;
        float vertical, elapsed, duration;
        bool actionApplied;
        internal PlayerInputFrame? TestInput;

        void Awake()
        {
            controller = GetComponent<CharacterController>();
            Health = GetComponent<Health>(); Energy = GetComponent<Stamina>();
        }

        void Update()
        {
            var game = GameSession.Instance;
            if (game == null || game.Paused || Health.IsDead) return;
            var frame = game.TestMode ? TestInput ?? default : PlayerInputFrame.Read();
            if (Target != null && (!Target.gameObject.activeInHierarchy || Target.Health.IsDead || Vector3.Distance(transform.position, Target.transform.position) > 22 ||
                !CombatQuery.Clear(transform.position + Vector3.up, Target.transform.position + Vector3.up))) Target = null;
            if (frame.Target) CycleTarget();

            Vector2 input = Vector2.ClampMagnitude(frame.Move, 1);
            Vector3 forward = Vector3.ProjectOnPlane(orbit.transform.forward, Vector3.up).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, forward);
            Vector3 direction = forward * input.y + right * input.x;
            Blocking = action == ActionState.Free && frame.Block && Energy.Current > 1;

            if (action == ActionState.Free)
            {
                if (frame.Dodge && controller.isGrounded && Energy.Spend(24))
                {
                    Begin(ActionState.Dodge, .56f);
                    dodgeDirection = direction.sqrMagnitude > .01f ? direction : transform.forward;
                    Blocking = false;
                }
                else if (frame.Light && Energy.Spend(22)) Begin(ActionState.Light, .64f);
                else if (frame.Heavy && Energy.Spend(36)) Begin(ActionState.Heavy, 1.08f);
                else if (frame.Heal && Flasks > 0 && Health.Current < Health.maximum) Begin(ActionState.Heal, 1.05f);
                else if (frame.Jump && controller.isGrounded && Energy.Spend(12)) vertical = 6.5f;
            }

            if (action != ActionState.Free)
            {
                elapsed += Time.deltaTime;
                float impact = action == ActionState.Heavy ? .55f : action == ActionState.Heal ? .7f : .25f;
                if (!actionApplied && elapsed >= impact)
                {
                    actionApplied = true;
                    if (action == ActionState.Light || action == ActionState.Heavy) Strike(action == ActionState.Heavy);
                    if (action == ActionState.Heal) { Flasks--; Health.Heal(65); GameAudio.Play(Cue.Rest); }
                }
                if (elapsed >= duration) action = ActionState.Free;
            }

            float speed = Blocking ? 2 : 4.4f;
            if (action == ActionState.Free && !Blocking && input.sqrMagnitude > .01f && frame.Sprint && Energy.Spend(15 * Time.deltaTime)) speed = 7;
            if (action != ActionState.Free) speed = 1.1f;
            Vector3 motion = Dodging ? dodgeDirection * 10 : direction * speed;
            if (controller.isGrounded && vertical < 0) vertical = -2;
            vertical -= 22 * Time.deltaTime;
            controller.Move((motion + Vector3.up * vertical) * Time.deltaTime);
            MoveSpeed = motion.magnitude;
            Vector3 facing = Target != null ? Target.transform.position - transform.position : direction;
            facing.y = 0;
            if (Dodging) facing = dodgeDirection;
            if (facing.sqrMagnitude > .01f && (action == ActionState.Free || Dodging || elapsed < .15f))
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(facing), 14 * Time.deltaTime);
            visual?.Pose(MoveSpeed, Blocking, Dodging, action == ActionState.Light || action == ActionState.Heavy ? elapsed / duration : -1);
            if (transform.position.y < -12) Health.Damage(Health.maximum);
        }

        void Begin(ActionState state, float time)
        { action = state; duration = time; elapsed = 0; actionApplied = false; Blocking = false; }

        void Strike(bool heavy)
        {
            GameAudio.Play(Cue.Swing);
            foreach (var enemy in GameSession.Instance.Enemies)
                if (enemy.gameObject.activeInHierarchy && !enemy.Health.IsDead && CombatQuery.InArc(transform, enemy.transform, heavy ? 3.1f : 2.65f, heavy ? 65 : 55))
                    enemy.ReceiveHit(heavy ? 45 : 24, heavy);
        }

        public void ReceiveHit(float damage, Vector3 origin)
        {
            if (Health.IsDead || Invulnerable) return;
            Vector3 incoming = origin - transform.position; incoming.y = 0;
            if (Blocking && Vector3.Angle(transform.forward, incoming) < 70)
            {
                if (Energy.Spend(damage * 1.15f)) { GameAudio.Play(Cue.Block); return; }
                Begin(ActionState.Stagger, .85f);
                GameSession.Instance.Notify("Guardia rota", 1.5f);
            }
            else Begin(ActionState.Stagger, .32f);
            Health.Damage(damage);
            GameAudio.Play(Cue.Hit);
            orbit.Shake(.13f);
        }

        public void CycleTarget()
        {
            EnemyBrain best = null; float bestScore = float.MaxValue;
            foreach (var enemy in GameSession.Instance.Enemies)
            {
                if (!enemy.gameObject.activeInHierarchy || enemy.Health.IsDead || enemy == Target) continue;
                Vector3 delta = enemy.transform.position - transform.position;
                float distance = delta.magnitude;
                if (distance > 18 || !CombatQuery.Clear(transform.position + Vector3.up, enemy.transform.position + Vector3.up)) continue;
                float angle = Vector3.Angle(orbit.transform.forward, delta);
                if (angle > 75) continue;
                float score = distance + angle * .12f;
                if (score < bestScore) { best = enemy; bestScore = score; }
            }
            Target = best;
        }

        public void RestoreAt(Vector3 position)
        {
            controller.enabled = false; transform.position = position; transform.rotation = Quaternion.identity;
            controller.enabled = true; vertical = 0; action = ActionState.Free; Blocking = false; Target = null;
            Health.Restore(); Energy.Restore(); Flasks = 3;
            if (orbit != null) orbit.ResetView();
        }
    }
}
