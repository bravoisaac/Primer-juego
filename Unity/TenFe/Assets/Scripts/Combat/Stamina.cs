using UnityEngine;

namespace TenFe
{
    public sealed class Stamina : MonoBehaviour
    {
        public float maximum = 100;
        public float regeneration = 26;
        public float Current { get; private set; }
        public float Fraction => Current / maximum;
        float recoveryAt;
        void Awake() => Restore();
        void Update()
        {
            if (Time.time >= recoveryAt) Current = Mathf.Min(maximum, Current + regeneration * Time.deltaTime);
        }
        public bool Spend(float amount)
        {
            if (amount < 0 || Current + .001f < amount) return false;
            Current = Mathf.Max(0, Current - amount);
            recoveryAt = Time.time + .75f;
            return true;
        }
        public void Restore() { Current = maximum; recoveryAt = 0; }
    }
}
