using UnityEngine;

namespace TenFe
{
    public sealed class ActorVisual : MonoBehaviour
    {
        public Transform body, leftLeg, rightLeg, swordArm, shieldArm;
        public Renderer visor;
        Health health;
        float flash;
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
    }
}
