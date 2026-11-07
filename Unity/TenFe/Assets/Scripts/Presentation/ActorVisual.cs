using UnityEngine;

namespace TenFe
{
    public sealed class ActorVisual : MonoBehaviour
    {
        public Transform body, leftLeg, rightLeg, swordArm, shieldArm;
        public Renderer visor;
        Health health;
        float flash;
        float enemyStride;
        MaterialPropertyBlock block;
        void Awake()
        {
            health = GetComponent<Health>(); block = new MaterialPropertyBlock();
            health.Damaged += amount => flash = .16f;
        }
        void Update()
        {
            flash = Mathf.Max(0, flash - Time.deltaTime);
            if (health.IsDead)
            {
                body.localRotation = Quaternion.Slerp(body.localRotation, Quaternion.Euler(0, 0, 80), Time.deltaTime * 5);
                body.localPosition = Vector3.Lerp(body.localPosition, Vector3.up * .4f, Time.deltaTime * 5);
            }
        }
        public void Pose(float speed, bool blockPose, bool dodge, float attack, bool telegraph = false)
        {
            if (health != null && health.IsDead) return;
            float gait = Mathf.Sin(Time.time * 10) * Mathf.Min(speed / 4, 1);
            body.localPosition = new Vector3(0, dodge ? .45f : 1 + Mathf.Abs(gait) * .035f, 0);
            body.localRotation = Quaternion.Euler(dodge ? 65 : 0, 0, 0);
            leftLeg.localRotation = Quaternion.Euler(gait * 28, 0, 0);
            rightLeg.localRotation = Quaternion.Euler(-gait * 28, 0, 0);
            float swing = attack >= 0 ? Mathf.Sin(attack * Mathf.PI * 2 - 1.2f) * 100 : gait * 12;
            swordArm.localRotation = Quaternion.Euler(attack >= 0 ? -40 : 0, swing, attack >= 0 ? -35 : -8);
            shieldArm.localRotation = Quaternion.Euler(blockPose ? -65 : 0, blockPose ? 45 : 0, 12);
            if (visor != null)
            {
                block.SetColor("_EmissionColor", flash > 0 ? Color.white * 4 : telegraph ? new Color(4, .25f, .04f) : new Color(1.2f, .7f, .2f));
                visor.SetPropertyBlock(block);
            }
        }
        // The prototype boss uses articulated primitives: drive a complete attack arc instead of two frozen poses.
        public void PoseEnemy(float speed, string motion, float progress, bool heavy)
        {
            if (health != null && health.IsDead) return;
            enemyStride += speed * Time.deltaTime * 2.8f;
            float gait = Mathf.Sin(enemyStride) * Mathf.Clamp01(speed / 2.5f);
            float lift = 0, sweep = 0, twist = 0, brace = 0;
            if (motion == "Windup")
            {
                brace = Mathf.SmoothStep(0, 1, progress);
                lift = -100 * brace; sweep = 32 * brace; twist = -22 * brace;
            }
            else if (motion == "Strike")
            {
                if (progress <= EnemyBrain.StrikeContact)
                {
                    float strike = Mathf.SmoothStep(0, 1, progress / EnemyBrain.StrikeContact);
                    lift = Mathf.Lerp(-100, 18, strike); sweep = Mathf.Lerp(32, -65, strike);
                    twist = Mathf.Lerp(-22, 24, strike); brace = 1;
                }
                else
                {
                    float settle = Mathf.SmoothStep(0, 1, (progress - .3f) / .7f);
                    lift = 18 * (1 - settle); sweep = -65 * (1 - settle);
                    twist = 24 * (1 - settle); brace = 1 - settle;
                }
            }
            float blend = 1 - Mathf.Exp(-14 * Time.deltaTime);
            body.localPosition = Vector3.Lerp(body.localPosition, new Vector3(0, 1 - brace * .05f + Mathf.Abs(gait) * .035f, 0), blend);
            body.localRotation = Quaternion.Slerp(body.localRotation, Quaternion.Euler(brace * (heavy ? 12 : 5), twist, -gait * 2), blend);
            leftLeg.localRotation = Quaternion.Slerp(leftLeg.localRotation, Quaternion.Euler(gait * 25 - brace * 8, 0, 0), blend);
            rightLeg.localRotation = Quaternion.Slerp(rightLeg.localRotation, Quaternion.Euler(-gait * 25 + brace * 8, 0, 0), blend);
            // Attack arm follows authored progress directly so damping cannot push contact behind damage.
            swordArm.localRotation = Quaternion.Euler(lift, sweep + gait * 6, -8 - brace * (heavy ? 45 : 27));
            shieldArm.localRotation = Quaternion.Slerp(shieldArm.localRotation, Quaternion.Euler(-30 * brace, 15 * brace, 12), blend);
            if (visor != null)
            {
                block.SetColor("_EmissionColor", flash > 0 ? Color.white * 4 : motion == "Windup" ? new Color(4, .25f, .04f) : new Color(1.2f, .7f, .2f));
                visor.SetPropertyBlock(block);
            }
        }
    }
}
