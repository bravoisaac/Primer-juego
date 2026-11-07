using UnityEngine;

namespace TenFe
{
    // Generic skeletal animation follows gameplay state; it never moves the actor or applies damage.
    [DefaultExecutionOrder(50), RequireComponent(typeof(EnemyBrain))]
    public sealed class SentinelVisual : MonoBehaviour
    {
        public Animator animator;
        public SkinnedMeshRenderer body;
        public Transform rightHand;
        public string Playing { get; private set; }
        EnemyBrain brain;
        Health health;
        float recoil;
        int resetVersion, staggerVersion;
        Transform chest;
        readonly System.Collections.Generic.Dictionary<string, float> lengths = new System.Collections.Generic.Dictionary<string, float>();
        void Awake()
        {
            brain = GetComponent<EnemyBrain>(); health = GetComponent<Health>();
            health.Damaged += OnDamage;
            animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            foreach (var clip in animator.runtimeAnimatorController.animationClips) lengths[clip.name] = clip.length;
            foreach (var bone in body.bones) if (bone.name == "Chest") chest = bone;
        }
        void OnDamage(float damage) { if (!health.IsDead) recoil = .18f; }
        // Run after AI and before Animator evaluation, so the contact pose follows the same frame as damage.
        void Update()
        {
            if (GameSession.Instance != null && GameSession.Instance.Paused) return;
            if (resetVersion != brain.AnimationResetVersion)
            {
                animator.Rebind(); animator.Play("Idle", 0, 0); animator.speed = 1; animator.Update(0);
                Playing = "Idle"; recoil = 0;
                resetVersion = brain.AnimationResetVersion;
            }
            string next = brain.Motion;
            if (IsLocomotion(next))
            {
                // Separate entry/exit thresholds prevent flicker while braking or touching walls.
                float speed = brain.MotionSpeed;
                next = speed < (Playing == "Idle" ? .16f : .08f) ? "Idle" :
                    speed > (Playing == "Run" ? 1.25f : 1.65f) ? "Run" : "Walk";
            }
            if (health.IsDead) next = "Death";
            // A full-body recoil belongs only to gameplay stagger; light hits must not freeze walking legs.
            bool repeatHit = next == "Hit" && staggerVersion != brain.StaggerVersion;
            if (next != Playing || repeatHit)
            {
                if (IsStride(next) && IsStride(Playing))
                {
                    // Walk and run share left/right foot phase; preserve it instead of restarting a step.
                    var current = animator.IsInTransition(0) ? animator.GetNextAnimatorStateInfo(0) : animator.GetCurrentAnimatorStateInfo(0);
                    animator.CrossFadeInFixedTime(next, .14f, 0, Mathf.Repeat(current.normalizedTime, 1) * Length(next));
                }
                else
                {
                    float offset = next == "Windup" || next == "Strike" || next == "Hit" ? brain.ActionProgress * Length(next) : 0;
                    if (repeatHit) animator.Play(next, 0, brain.ActionProgress);
                    else animator.CrossFadeInFixedTime(next, next == "Strike" ? .025f : next == "Hit" ? .05f : IsLocomotion(next) ? .18f : .1f, 0, offset);
                }
                Playing = next;
            }
            staggerVersion = brain.StaggerVersion;
            float localSpeed = brain.MotionSpeed / Mathf.Max(.1f, transform.lossyScale.x);
            float playback = next == "Run" ? Mathf.Clamp(localSpeed / 1.75f, .3f, 1.85f) :
                next == "Walk" ? Mathf.Clamp(localSpeed / (.55f / .6f / 1.2f), .12f, 1.85f) :
                next == "Windup" ? Length(next) / brain.WindupDuration :
                next == "Strike" ? Length(next) / brain.RecoveryDuration : next == "Hit" ? Length(next) / .55f : 1;
            animator.speed = IsStride(next) ? Mathf.MoveTowards(animator.speed, playback, 5 * Time.deltaTime) : playback;
        }
        void LateUpdate()
        {
            if (GameSession.Instance != null && GameSession.Instance.Paused) return;
            // Small upper-body response does not replace the current locomotion clip or a committed strike.
            if (chest != null && recoil > 0 && IsLocomotion(Playing))
                chest.localRotation *= Quaternion.Euler(-5 * Mathf.Sin(recoil / .18f * Mathf.PI), 0, 0);
            recoil = Mathf.Max(0, recoil - Time.deltaTime);
        }
        float Length(string motion) => lengths.TryGetValue(motion, out var length) ? length : 1;
        static bool IsStride(string motion) => motion == "Walk" || motion == "Run";
        static bool IsLocomotion(string motion) => motion == "Idle" || IsStride(motion);
        void OnDestroy() { if (health != null) health.Damaged -= OnDamage; }
    }
}
