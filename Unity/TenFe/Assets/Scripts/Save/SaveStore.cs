using System;
using System.IO;
using UnityEngine;

namespace TenFe
{
    [Serializable]
    public sealed class SaveData
    {
        public int version = 1;
        public int faith, level, checkpoint;
        public bool shortcut, relic, boss;
        public int droppedFaith;
        public Vector3 dropPosition;
    }
    public static class SaveStore
    {
        public static string FilePath => Path.Combine(Application.persistentDataPath, "pilgrim-v1.json");
        public static bool Load(out SaveData data) => Read(FilePath, out data);
        public static bool Read(string path, out SaveData data)
        {
            data = new SaveData();
            if (!File.Exists(path)) return true;
            try
            {
                var parsed = JsonUtility.FromJson<SaveData>(File.ReadAllText(path));
                if (parsed == null || parsed.version != 1 || parsed.faith < 0 || parsed.droppedFaith < 0 || parsed.level < 0 || parsed.level > 5 ||
                    parsed.checkpoint < 0 || parsed.checkpoint > 1 || !Finite(parsed.dropPosition)) return false;
                data = parsed; return true;
            }
            catch (Exception e) when (e is IOException || e is ArgumentException || e is UnauthorizedAccessException) { return false; }
        }
        static bool Finite(Vector3 v) => !float.IsNaN(v.x) && !float.IsInfinity(v.x) && !float.IsNaN(v.y) && !float.IsInfinity(v.y) && !float.IsNaN(v.z) && !float.IsInfinity(v.z);
        public static bool Write(SaveData data, string path = null)
        {
            path = path ?? FilePath;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                string temporary = path + ".tmp";
                File.WriteAllText(temporary, JsonUtility.ToJson(data, true));
                if (File.Exists(path)) File.Replace(temporary, path, path + ".bak");
                else File.Move(temporary, path);
                return true;
            }
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
            { Debug.LogWarning("No se pudo guardar el progreso: " + e.Message); return false; }
        }
    }
}
