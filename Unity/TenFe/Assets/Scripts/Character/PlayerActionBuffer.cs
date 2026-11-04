using UnityEngine;

namespace TenFe
{
    internal enum BufferedAction { None, Dodge, Light, Heavy, Heal, Jump }

    // One intent only: repeated presses replace it, never accumulate a combo.
    internal sealed class PlayerActionBuffer
    {
        internal const float Lifetime = .2f;
        BufferedAction pending;
        Vector3 direction;
        float expires;

        internal void Record(PlayerInputFrame frame, Vector3 worldDirection, float now)
        {
            var next = frame.Dodge ? BufferedAction.Dodge : frame.Light ? BufferedAction.Light :
                frame.Heavy ? BufferedAction.Heavy : frame.Heal ? BufferedAction.Heal :
                frame.Jump ? BufferedAction.Jump : BufferedAction.None;
            if (next == BufferedAction.None) return;
            pending = next; direction = worldDirection; expires = now + Lifetime;
        }

        internal bool Take(float now, out BufferedAction action, out Vector3 worldDirection)
        {
            action = now <= expires ? pending : BufferedAction.None;
            worldDirection = direction;
            Clear();
            return action != BufferedAction.None;
        }

        internal void Clear() { pending = BufferedAction.None; direction = Vector3.zero; expires = 0; }
    }
}
