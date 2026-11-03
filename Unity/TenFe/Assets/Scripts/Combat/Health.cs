using System;
using UnityEngine;

namespace TenFe
{
    public sealed class Health : MonoBehaviour
    {
        public float maximum = 100;
        public float Current { get; private set; }
        public bool IsDead => Current <= 0;
        public float Fraction => maximum > 0 ? Current / maximum : 0;
        public event Action Died;
        public event Action<float> Damaged;

        void Awake() => Restore();
        public void Restore() => Current = maximum;
        public void Heal(float amount) { if (!IsDead) Current = Mathf.Min(maximum, Current + Mathf.Max(0, amount)); }
        public void Damage(float amount)
        {
            if (IsDead || amount <= 0) return;
            Current = Mathf.Max(0, Current - amount);
            Damaged?.Invoke(amount);
            if (IsDead) Died?.Invoke();
        }
    }
}
