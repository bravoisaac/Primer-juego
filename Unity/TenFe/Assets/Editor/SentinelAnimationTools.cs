using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace TenFe.Editor
{
    public static class SentinelAnimationTools
    {
        [MenuItem("Ten Fe/Validar animaciones del centinela")]
        public static void Validate()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var clips = AssetDatabase.LoadAllAssetsAtPath(SentinelInstaller.ModelPath).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__")).ToDictionary(c => c.name);
            var report = new List<string>();
            bool passed = true;
            void Check(bool ok, string label) { report.Add((ok ? "PASS " : "FAIL ") + label); passed &= ok; }
            var model = UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(SentinelInstaller.PrefabPath));
            try
            {
                model.GetComponent<Animator>().enabled = false;
                var bones = model.GetComponentsInChildren<Transform>().Where(t => t.name == "Root" || t.name == "Hips" || t.name == "Chest" ||
                    t.name == "Head" || t.name.StartsWith("Thigh.") || t.name.StartsWith("Shin.") || t.name.StartsWith("Foot.") ||
                    t.name.StartsWith("UpperArm.") || t.name.StartsWith("Forearm.") || t.name.StartsWith("Hand.")).ToArray();
                var leftFoot = bones.Single(t => t.name == "Foot.L");
                var rightFoot = bones.Single(t => t.name == "Foot.R");
                var root = bones.Single(t => t.name == "Root");
                foreach (string name in new[] { "Idle", "Walk", "Run" })
                {
                    var clip = clips[name];
                    clip.SampleAnimation(model, 0);
                    var positions = bones.Select(t => t.localPosition).ToArray();
                    var rotations = bones.Select(t => t.localRotation).ToArray();
                    clip.SampleAnimation(model, clip.length);
                    Check(bones.Select((t, i) => Vector3.Distance(t.localPosition, positions[i]) < .002f && Quaternion.Angle(t.localRotation, rotations[i]) < .1f).All(v => v),
                        name + " loop closes without a pose jump");
                }
                clips["Windup"].SampleAnimation(model, clips["Windup"].length);
                var windupRotations = bones.Select(t => t.localRotation).ToArray();
                var windupPositions = bones.Select(t => t.localPosition).ToArray();
                clips["Strike"].SampleAnimation(model, 0);
                Check(bones.Select((t, i) => Quaternion.Angle(t.localRotation, windupRotations[i]) < .1f &&
                    Vector3.Distance(t.localPosition, windupPositions[i]) < .002f).All(v => v), "Windup ends at the exact opening pose of Strike");

                foreach (string name in new[] { "Walk", "Run" })
                {
                    var clip = clips[name];
                    float stance = name == "Walk" ? .6f : .5f;
                    float min = float.PositiveInfinity, max = float.NegativeInfinity, lift = 0;
                    Vector3 first = Vector3.zero, last = Vector3.zero, rootStart = Vector3.zero;
                    bool stationaryRoot = true;
                    for (int frame = 0; frame <= 60; frame++)
                    {
                        float phase = frame / 60f;
                        clip.SampleAnimation(model, phase * clip.length);
                        Vector3 foot = model.transform.InverseTransformPoint(leftFoot.position);
                        if (frame == 0) { first = foot; rootStart = root.localPosition; }
                        if (phase <= stance) { min = Mathf.Min(min, foot.y); max = Mathf.Max(max, foot.y); last = foot; }
                        else lift = Mathf.Max(lift, foot.y);
                        stationaryRoot &= Vector3.Distance(root.localPosition, rootStart) < .001f;
                    }
                    Check(max - min < .02f, name + " support ankle stays level (variation " + (max - min).ToString("F4") + " m)");
                    Check(lift - max > .035f, name + " swing foot clears the ground (lift " + (lift - max).ToString("F4") + " m)");
                    Check(Mathf.Abs(Mathf.Abs(last.z - first.z) - (name == "Walk" ? .55f : .70f)) < .035f && stationaryRoot,
                        name + " support stride matches playback calibration with no root translation");
                }
                clips["Strike"].SampleAnimation(model, 0);
                Vector3 leftStart = leftFoot.position, rightStart = rightFoot.position;
                clips["Strike"].SampleAnimation(model, clips["Strike"].length * EnemyBrain.StrikeContact);
                Check(Vector3.Distance(leftFoot.position, leftStart) < .005f && Vector3.Distance(rightFoot.position, rightStart) < .005f,
                    "Both attack feet remain planted through damage contact");
            }
            finally { UnityEngine.Object.DestroyImmediate(model); }
            Directory.CreateDirectory("Docs/Validation");
            File.WriteAllText("Docs/Validation/animation-clips.txt", (passed ? "PASSED" : "FAILED") + " imported clip checks\n" + string.Join("\n", report) + "\n");
            if (!passed) throw new Exception("Animation validation failed. See Docs/Validation/animation-clips.txt.");
            Debug.Log("TENFE_ANIMATION_CLIPS_PASS " + report.Count);
        }
        public static void ValidateAndBuild()
        {
            Validate(); ProjectTools.ValidateCore(); ProjectTools.BuildWindows();
        }
    }
}
