using UnityEngine;

namespace TenFe
{
    // Generic skeletal animation follows gameplay state; it never moves the actor or applies damage.
    [RequireComponent(typeof(EnemyBrain))]
    public sealed class SentinelVisual : MonoBehaviour
    {
        public Animator animator;
        public SkinnedMeshRenderer body;
        public Transform rightHand;
        public string Playing { get; private set; }
        EnemyBrain brain;
        Health health;
        float hurtUntil;
        bool wasDead;
        void Awake()
        {
            brain = GetComponent<EnemyBrain>(); health = GetComponent<Health>();
            health.Damaged += OnDamage;
            animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
        }
        void OnDamage(float damage) { if (!health.IsDead) hurtUntil = Time.time + .45f; }
        void LateUpdate()
        {
            if (GameSession.Instance != null && GameSession.Instance.Paused) return;
            if (wasDead && !health.IsDead)
            {
                animator.Rebind(); animator.Update(0); Playing = null; hurtUntil = 0;
            }
            wasDead = health.IsDead;
            string next = brain.Motion;
            if (IsLocomotion(next))
            {
                // Separate entry/exit thresholds prevent flicker while braking or touching walls.
                float speed = brain.MotionSpeed;
                next = speed < (Playing == "Idle" ? .16f : .08f) ? "Idle" :
                    speed > (Playing == "Run" ? 1.25f : 1.65f) ? "Run" : "Walk";
            }
            if (health.IsDead) next = "Death";
            else if (Time.time < hurtUntil && (next == "Idle" || next == "Walk" || next == "Run" || next == "Hit")) next = "Hit";
            if (next != Playing)
            {
                if (IsStride(next) && IsStride(Playing))
                {
                    // Walk and run share left/right foot phase; preserve it instead of restarting a step.
                    var current = animator.IsInTransition(0) ? animator.GetNextAnimatorStateInfo(0) : animator.GetCurrentAnimatorStateInfo(0);
                    animator.CrossFade(next, .18f, 0, Mathf.Repeat(current.normalizedTime, 1));
                }
                else animator.CrossFadeInFixedTime(next, next == "Strike" ? .04f : IsLocomotion(next) ? .2f : .12f, 0, 0);
                Playing = next;
            }
            float playback = next == "Run" ? Mathf.Clamp(brain.MotionSpeed / 2.1f, .55f, 1.65f) :
                next == "Walk" ? Mathf.Clamp(brain.MotionSpeed / .9f, .15f, 1.85f) :
                next == "Windup" ? .8f / brain.WindupDuration :
                next == "Strike" ? (35f / 30) / brain.RecoveryDuration : 1;
            animator.speed = IsStride(next) ? Mathf.MoveTowards(animator.speed, playback, 5 * Time.deltaTime) : playback;
        }
        static bool IsStride(string motion) => motion == "Walk" || motion == "Run";
        static bool IsLocomotion(string motion) => motion == "Idle" || IsStride(motion);
        void OnDestroy() { if (health != null) health.Damaged -= OnDamage; }
    }
}
