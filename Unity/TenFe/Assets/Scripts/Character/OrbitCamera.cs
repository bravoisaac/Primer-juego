using UnityEngine;

namespace TenFe
{
    public sealed class OrbitCamera : MonoBehaviour
    {
        public PlayerController player;
        public float sensitivity = 2.2f;
        float yaw, pitch = 17, shake;
        public void ResetView() { yaw = player.transform.eulerAngles.y; pitch = 17; }
        public void Shake(float strength) => shake = strength;
        void LateUpdate()
        {
            if (player == null || GameSession.Instance == null || GameSession.Instance.Paused) return;
            Vector3 focus = player.transform.position + Vector3.up * 1.65f;
            if (player.Target != null)
            {
                Vector3 delta = player.Target.transform.position + Vector3.up - focus;
                yaw = Mathf.LerpAngle(yaw, Mathf.Atan2(delta.x, delta.z) * Mathf.Rad2Deg, 7 * Time.deltaTime);
                pitch = Mathf.Lerp(pitch, 14, 5 * Time.deltaTime);
            }
            else if (!GameSession.Instance.TestMode)
            {
                yaw += Input.GetAxisRaw("Mouse X") * sensitivity;
                pitch = Mathf.Clamp(pitch - Input.GetAxisRaw("Mouse Y") * sensitivity, -25, 65);
            }
            Quaternion rotation = Quaternion.Euler(pitch, yaw, 0);
            Vector3 back = rotation * Vector3.back;
            float distance = 5.3f;
            if (Physics.SphereCast(focus, .22f, back, out RaycastHit hit, distance, 1 << 0, QueryTriggerInteraction.Ignore))
                distance = Mathf.Max(.3f, hit.distance - .15f);
            shake = Mathf.MoveTowards(shake, 0, Time.deltaTime);
            transform.SetPositionAndRotation(focus + back * distance + Random.insideUnitSphere * shake, rotation);
        }
    }
}
