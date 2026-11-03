using UnityEngine;

namespace TenFe
{
    public static class CombatQuery
    {
        // Actors use layer 8; scenery uses layer 0. Walls must stop melee hits and lock-on.
        public static bool Clear(Vector3 from, Vector3 to)
            => !Physics.Linecast(from, to, 1 << 0, QueryTriggerInteraction.Ignore);

        public static bool InArc(Transform source, Transform target, float range, float angle)
        {
            Vector3 delta = target.position - source.position;
            if (Mathf.Abs(delta.y) > 2.5f) return false;
            delta.y = 0;
            return delta.sqrMagnitude <= range * range &&
                (delta.sqrMagnitude < .01f || Vector3.Angle(source.forward, delta) <= angle) &&
                Clear(source.position + Vector3.up, target.position + Vector3.up);
        }
    }
}
