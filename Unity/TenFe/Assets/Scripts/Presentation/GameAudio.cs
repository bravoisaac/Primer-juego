using System;
using UnityEngine;

namespace TenFe
{
    public enum Cue { Swing, Hit, Block, Rest, Death, Warn, Boss }
    public sealed class GameAudio : MonoBehaviour
    {
        static GameAudio instance;
        AudioSource effects, drone;
        AudioClip[] clips;
        void Awake()
        {
            instance = this;
            effects = gameObject.AddComponent<AudioSource>(); effects.volume = .3f;
            clips = new AudioClip[7];
            float[] frequencies = { 160, 65, 740, 440, 52, 260, 90 };
            for (int i = 0; i < clips.Length; i++) clips[i] = Tone("TenFe_" + (Cue)i, frequencies[i], i == 3 ? 1.4f : .28f, i < 3);
            drone = gameObject.AddComponent<AudioSource>(); drone.clip = Tone("TenFe_Ambient", 55, 8, false, true);
            drone.loop = true; drone.volume = .07f; drone.Play();
        }
        static AudioClip Tone(string name, float frequency, float duration, bool noise, bool ambient = false)
        {
            const int rate = 22050;
            var samples = new float[(int)(rate * duration)]; var random = new System.Random(42);
            for (int i = 0; i < samples.Length; i++)
            {
                float t = (float)i / rate;
                float envelope = ambient ? 1 : Mathf.Sin(Mathf.PI * i / samples.Length) * Mathf.Exp(-3 * t / duration);
                float signal = Mathf.Sin(2 * Mathf.PI * frequency * t) * .4f + Mathf.Sin(2 * Mathf.PI * frequency * 1.5f * t) * .15f;
                if (noise) signal = signal * .4f + ((float)random.NextDouble() * 2 - 1) * .4f;
                samples[i] = signal * envelope;
            }
            var clip = AudioClip.Create(name, samples.Length, 1, rate, false); clip.SetData(samples, 0); return clip;
        }
        public static void Play(Cue cue) { if (instance != null) instance.effects.PlayOneShot(instance.clips[(int)cue]); }
        void OnDestroy()
        {
            if (clips != null) foreach (var clip in clips) Destroy(clip);
            if (drone != null) Destroy(drone.clip);
            if (instance == this) instance = null;
        }
    }
}
