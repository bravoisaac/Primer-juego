using UnityEngine;

namespace TenFe
{
    public sealed class OrbitCamera : MonoBehaviour
    {
        public PlayerController player;
        public float sensitivity = 2.2f;
        const float FollowDistance = 5.3f, CollisionRadius = .22f;
        float yaw, pitch = 17, shake, distance = FollowDistance, shoulder;
        public void ResetView()
        {
            yaw = player.transform.eulerAngles.y; pitch = 17;
            distance = FollowDistance; shoulder = 0; shake = 0;
        }
        public void Shake(float strength) => shake = Mathf.Max(shake, strength);
        void LateUpdate()
        {
            if (player == null || GameSession.Instance == null || GameSession.Instance.Paused) return;
            Vector3 pivot = player.transform.position + Vector3.up * 1.65f;
            float follow = 1 - Mathf.Exp(-7 * Time.deltaTime);
            if (player.Target != null)
            {
                Vector3 delta = player.Target.transform.position + Vector3.up - pivot;
                yaw = Mathf.LerpAngle(yaw, Mathf.Atan2(delta.x, delta.z) * Mathf.Rad2Deg, follow);
                pitch = Mathf.Lerp(pitch, 14, follow);
            }
            else if (!GameSession.Instance.TestMode)
            {
                yaw += Input.GetAxisRaw("Mouse X") * sensitivity;
                pitch = Mathf.Clamp(pitch - Input.GetAxisRaw("Mouse Y") * sensitivity, -25, 65);
            }
            shoulder = Mathf.Lerp(shoulder, player.Target != null ? .65f : 0, follow);
            Quaternion rotation = Quaternion.Euler(pitch, yaw, 0);
            Vector3 focus = pivot + rotation * Vector3.right * shoulder;
            // Check the shoulder offset too, so shifting the framing cannot cross a side wall.
            focus = Constrain(pivot, focus);
            Vector3 back = rotation * Vector3.back;
            float available = Vector3.Distance(focus, Constrain(focus, focus + back * FollowDistance));
            // Obstacles pull the camera inward immediately; only the outward recovery is smoothed.
            distance = available < distance ? available : Mathf.Lerp(distance, available, 1 - Mathf.Exp(-5 * Time.deltaTime));
            shake = Mathf.MoveTowards(shake, 0, Time.deltaTime);
            Vector3 position = focus + back * distance + Random.insideUnitSphere * shake;
            position = Constrain(focus, position);
            transform.SetPositionAndRotation(position, rotation);
        }

        static Vector3 Constrain(Vector3 origin, Vector3 desired)
        {
            Vector3 delta = desired - origin;
            float length = delta.magnitude;
            if (length < .001f) return origin;
            if (Physics.SphereCast(origin, CollisionRadius, delta / length, out RaycastHit hit, length, 1 << 0, QueryTriggerInteraction.Ignore))
                return origin + delta / length * Mathf.Max(0, hit.distance - .06f);
            return desired;
        }
    }
}
