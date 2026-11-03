using UnityEngine;

namespace TenFe
{
    [ExecuteAlways, RequireComponent(typeof(Camera))]
    public sealed class SanctuaryImageEffect : MonoBehaviour
    {
        public Shader shader;
        [Range(0, 1)] public float bloom = .32f;
        [Range(0, .4f)] public float vignette = .15f;
        Material material;
        public bool Supported => shader != null && shader.isSupported;

        void OnRenderImage(RenderTexture source, RenderTexture destination)
        {
            if (!Supported) { Graphics.Blit(source, destination); return; }
            if (material == null) material = new Material(shader) { hideFlags = HideFlags.HideAndDontSave };
            var a = RenderTexture.GetTemporary(Mathf.Max(1, source.width / 4), Mathf.Max(1, source.height / 4), 0, source.format);
            var b = RenderTexture.GetTemporary(a.width, a.height, 0, source.format);
            a.filterMode = b.filterMode = FilterMode.Bilinear;
            try
            {
                Graphics.Blit(source, a, material, 0);
                for (int i = 0; i < 2; i++)
                {
                    material.SetVector("_BlurDirection", new Vector4(1 + i, 0, 0, 0)); Graphics.Blit(a, b, material, 1);
                    material.SetVector("_BlurDirection", new Vector4(0, 1 + i, 0, 0)); Graphics.Blit(b, a, material, 1);
                }
                material.SetTexture("_BloomTex", a);
                material.SetFloat("_BloomStrength", bloom); material.SetFloat("_Vignette", vignette);
                Graphics.Blit(source, destination, material, 2);
            }
            finally { RenderTexture.ReleaseTemporary(a); RenderTexture.ReleaseTemporary(b); }
        }
        void OnDisable()
        {
            if (material == null) return;
            if (Application.isPlaying) Destroy(material); else DestroyImmediate(material);
            material = null;
        }
    }
}
