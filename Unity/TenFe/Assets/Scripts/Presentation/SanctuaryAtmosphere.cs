using UnityEngine;

namespace TenFe
{
    // Presentation only: fixtures remain editable in the scene and never affect collision or combat.
    public sealed class SanctuaryAtmosphere : MonoBehaviour
    {
        public Light[] flameLights;
        float[] intensities;
        void Awake()
        {
            intensities = new float[flameLights.Length];
            for (int i = 0; i < flameLights.Length; i++)
                if (flameLights[i] != null) intensities[i] = flameLights[i].intensity;
        }
        void Update()
        {
            for (int i = 0; i < flameLights.Length; i++)
            {
                if (flameLights[i] == null) continue;
                float flutter = Mathf.PerlinNoise(i * 3.71f, Time.time * 2.4f);
                flameLights[i].intensity = intensities[i] * (.88f + flutter * .24f);
            }
        }
    }
}
