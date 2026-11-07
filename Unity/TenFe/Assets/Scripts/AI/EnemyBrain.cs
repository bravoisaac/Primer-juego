using UnityEngine;

namespace TenFe
{
    [RequireComponent(typeof(CharacterController), typeof(Health))]
    public sealed class EnemyBrain : MonoBehaviour
    {
        public string title = "Custodio sin fe";
        public bool boss;
        public bool elite;
        public int reward = 35;
        public ActorVisual visual;
        public SentinelVisual animatedVisual;
        public Health Health { get; private set; }
        public bool Enraged => boss && Health.Fraction <= .5f;
        public bool Telegraphing => state == State.Windup;
        public bool Engaged { get; private set; }
        enum State { Idle, Alert, Chase, Settle, Windup, Recover, Stagger, Return, Dead }
        State state;
        CharacterController motor;
        Vector3 home, attackDirection, patrolTarget, velocity;
        float timer, gravity, patrolPhase, patrolPause;
        bool heavy, phaseAnnounced;
        int attackCount;
        bool pendingStrike;
        public float MotionSpeed { get; private set; }
        public float WindupDuration { get; private set; } = .8f;
        public float RecoveryDuration { get; private set; } = 1.15f;
        public const float StrikeContact = .14f;
        public int AnimationResetVersion { get; private set; }
        public int StaggerVersion { get; private set; }
        public bool HeavyAttack => heavy;
        public float ActionProgress => Mathf.Clamp01(1 - timer / (state == State.Windup ? WindupDuration :
            state == State.Recover ? RecoveryDuration : state == State.Stagger ? .55f : 1));
        public string Motion => state == State.Dead ? "Death" : state == State.Windup ? "Windup" :
            state == State.Recover ? "Strike" : state == State.Stagger ? "Hit" :
            MotionSpeed > 1.4f ? "Run" : MotionSpeed > .1f ? "Walk" : "Idle";
        public Vector3 Home => home;

        void Awake()
        {
            Health = GetComponent<Health>(); motor = GetComponent<CharacterController>();
            home = transform.position; patrolPhase = home.x; patrolTarget = home; patrolPause = .8f;
            Health.Died += OnDeath;
        }
        void Update()
        {
            var game = GameSession.Instance;
            if (game == null || game.Paused || Health.IsDead || game.Player.Health.IsDead) return;
            var player = game.Player;
            float distance = Vector3.Distance(transform.position, player.transform.position);
            timer -= Time.deltaTime;
            if (Enraged && !phaseAnnounced)
            { phaseAnnounced = true; game.Notify("ASTER DESPIERTA · Sus golpes son más rápidos", 3); GameAudio.Play(Cue.Boss); }
            if (state == State.Windup)
            {
                Move(Vector3.zero, 0, attackDirection);
                if (timer <= 0)
                {
                    state = State.Recover; RecoveryDuration = Enraged ? .65f : boss ? 1.05f : 1.15f;
                    timer = RecoveryDuration; pendingStrike = true;
                }
                return;
            }
            if (state == State.Recover || state == State.Stagger)
            {
                Move(Vector3.zero, 0, Vector3.zero);
                // The blade reaches its target 14% into the strike clip, after the readable windup.
                if (state == State.Recover && pendingStrike && timer <= RecoveryDuration * (1 - StrikeContact))
                {
                    pendingStrike = false;
                    if (CombatQuery.InArc(transform, player.transform, AttackRange + .55f, heavy ? 85 : 55))
                        player.ReceiveHit(boss ? (heavy ? 38 : 27) : elite ? 25 : 18, transform.position);
                    GameAudio.Play(Cue.Swing);
                }
                if (timer <= 0) { timer = state == State.Stagger ? .12f : .22f; state = State.Alert; }
                return;
            }
            if (distance < (boss ? 15 : 10) && state == State.Idle && CombatQuery.Clear(transform.position + Vector3.up, player.transform.position + Vector3.up))
            { state = State.Alert; timer = elite ? .22f : .32f; Engaged = true; }
            if (Engaged && (distance > 23 || Vector3.Distance(transform.position, home) > (boss ? 14 : 17)))
            { state = State.Return; Engaged = false; }
            Vector3 destination = home;
            float speed = 2;
            Vector3 toPlayer = player.transform.position - transform.position; toPlayer.y = 0;
            if (state == State.Alert)
            {
                Move(Vector3.zero, 0, toPlayer);
                if (timer <= 0) state = State.Chase;
                return;
            }
            if (state == State.Settle)
            {
                // Plant the feet and face the target before committing to a readable strike.
                Move(Vector3.zero, 0, toPlayer);
                if (distance > AttackRange + .35f || !CombatQuery.Clear(transform.position + Vector3.up, player.transform.position + Vector3.up))
                { state = State.Chase; return; }
                if (timer <= 0 && MotionSpeed < .12f && Vector3.Angle(transform.forward, toPlayer) < 8)
                {
                    attackDirection = transform.forward;
                    heavy = boss && ++attackCount % 3 == 0;
                    state = State.Windup; WindupDuration = (heavy ? 1.15f : .8f) * (Enraged ? .72f : 1);
                    timer = WindupDuration;
                    GameAudio.Play(Cue.Warn);
                }
                return;
            }
            if (state == State.Chase)
            {
                destination = player.transform.position;
                float approach = Mathf.InverseLerp(AttackRange, AttackRange + 2.2f, distance);
                speed = Mathf.Lerp(.85f, Enraged ? 3.5f : boss ? 2.5f : 2.8f, approach);
                if (distance <= AttackRange && CombatQuery.Clear(transform.position + Vector3.up, player.transform.position + Vector3.up))
                {
                    state = State.Settle; timer = .18f;
                    Move(Vector3.zero, 0, toPlayer);
                    return;
                }
            }
            else if (state == State.Return)
            {
                speed *= Mathf.Clamp01(Vector3.Distance(transform.position, home) / 1.2f);
                if (Vector3.Distance(transform.position, home) < .25f)
                { state = State.Idle; Health.Restore(); phaseAnnounced = false; patrolTarget = home; patrolPause = .8f; }
            }
            else
            {
                if (boss) { Move(Vector3.zero, 0, Vector3.zero); return; }
                Vector3 toPatrol = patrolTarget - transform.position; toPatrol.y = 0;
                if (toPatrol.magnitude < .25f)
                {
                    patrolPause -= Time.deltaTime;
                    if (patrolPause <= 0)
                    {
                        patrolPhase += 2.1f;
                        patrolTarget = home + new Vector3(Mathf.Sin(patrolPhase) * 1.6f, 0, Mathf.Cos(patrolPhase) * 1.2f);
                        patrolPause = .8f + .4f * (1 + Mathf.Sin(patrolPhase));
                    }
                }
                destination = patrolTarget;
                speed = .85f * Mathf.Clamp01((toPatrol.magnitude - .18f) / .7f);
            }
            Vector3 movement = destination - transform.position; movement.y = 0;
            movement = movement.magnitude > .2f ? movement.normalized : Vector3.zero;
            Move(movement, speed, movement);
            if (transform.position.y < -10) ResetEnemy();
        }
        void LateUpdate()
        {
            if (GameSession.Instance != null && GameSession.Instance.Paused) return;
            visual?.PoseEnemy(MotionSpeed, Motion, ActionProgress, heavy);
        }
        void Move(Vector3 direction, float speed, Vector3 facing)
        {
            // Steering and momentum are separate: turn first, then build speed along the new heading.
            if (direction.sqrMagnitude > .01f && Physics.SphereCast(transform.position + Vector3.up * .7f, .35f, direction, out RaycastHit wall, 1.2f, 1 << 0, QueryTriggerInteraction.Ignore))
            {
                direction = Vector3.ProjectOnPlane(direction, wall.normal); direction.y = 0;
                direction = direction.sqrMagnitude > .01f ? direction.normalized : Vector3.zero;
                facing = direction;
            }
            if (facing.sqrMagnitude > .001f)
                transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(facing), (elite ? 190 : 240) * Time.deltaTime);
            float alignment = direction.sqrMagnitude > .01f ? Mathf.Clamp01(Vector3.Dot(transform.forward, direction)) : 0;
            Vector3 desired = direction * speed * alignment * alignment;
            velocity = Vector3.MoveTowards(velocity, desired, (desired.sqrMagnitude < velocity.sqrMagnitude ? 9 : 6) * Time.deltaTime);
            if (motor.isGrounded && gravity < 0) gravity = -2;
            gravity -= 22 * Time.deltaTime;
            Vector3 before = transform.position;
            motor.Move((velocity + Vector3.up * gravity) * Time.deltaTime);
            MotionSpeed = Vector3.ProjectOnPlane(motor.velocity, Vector3.up).magnitude;
            // Do not store speed into a wall and release it as a burst when steering clears it.
            if (Time.deltaTime > 0)
                velocity = Vector3.ProjectOnPlane(transform.position - before, Vector3.up) / Time.deltaTime;
        }
        float AttackRange => boss ? 3.2f : elite ? 2.5f : 2.1f;
        public void ReceiveHit(float damage, bool stagger)
        {
            if (Health.IsDead) return;
            Health.Damage(damage); GameAudio.Play(Cue.Hit);
            if (Health.IsDead) return;
            Engaged = true;
            if (stagger && !boss) { state = State.Stagger; timer = .55f; pendingStrike = false; velocity = Vector3.zero; StaggerVersion++; }
            else if (state == State.Idle || state == State.Return) state = State.Chase;
        }
        void OnDeath()
        {
            state = State.Dead; Engaged = false; motor.enabled = false; pendingStrike = false; MotionSpeed = 0; velocity = Vector3.zero;
            GameSession.Instance?.EnemyDefeated(this);
        }
        public void ResetEnemy()
        {
            AnimationResetVersion++;
            motor.enabled = false; transform.position = home; transform.rotation = Quaternion.identity;
            motor.enabled = true; Health.Restore(); state = State.Idle; Engaged = false;
            phaseAnnounced = false; attackCount = 0; gravity = 0; pendingStrike = false; MotionSpeed = 0;
            velocity = Vector3.zero; patrolPhase = home.x; patrolTarget = home; patrolPause = .8f; timer = 0;
        }
    }
}
