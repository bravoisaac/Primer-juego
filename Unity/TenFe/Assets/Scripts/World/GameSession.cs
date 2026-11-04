using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TenFe
{
    public sealed class GameSession : MonoBehaviour
    {
        public static GameSession Instance { get; private set; }
        public PlayerController Player;
        public List<EnemyBrain> Enemies = new List<EnemyBrain>();
        public Interactable[] altars;
        public Interactable shortcut, relic, vestige;
        public bool Paused { get; private set; }
        public SaveData Progress { get; private set; } = new SaveData();
        public Interactable Nearby { get; private set; }
        public string Message { get; private set; }
        public int UpgradeCost => 80 + Progress.level * 40;
        public bool TestMode { get; private set; }
        public bool SaveBlocked { get; private set; }
        float messageUntil;
        public bool Ready { get; private set; }

        void Awake()
        {
            Instance = this;
            TestMode = System.Array.Exists(System.Environment.GetCommandLineArgs(), arg => arg == "--smoke-test");
            Time.timeScale = 1;
        }
        void Start()
        {
            if (!TestMode)
            {
                SaveBlocked = !SaveStore.Load(out var loaded);
                if (!SaveBlocked) Progress = loaded;
            }
            Player.Health.maximum = 100 + Progress.level * 25;
            Player.RestoreAt(altars[Progress.checkpoint].respawnPoint.position);
            Player.Health.Died += OnPlayerDeath;
            ApplyWorldState();
            SetPaused(false);
            Notify(SaveBlocked ? "Guardado incompatible: sesión temporal, el archivo original está protegido." : "SANTUARIO DEL OCASO · La fe aún arde", SaveBlocked ? 10 : 5);
            Ready = true;
        }
        void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape)) SetPaused(!Paused);
            if (Paused) return;
            if (Time.time > messageUntil) Message = "";
            Nearby = null;
            if (Player.Health.IsDead) return;
            float closest = 3;
            foreach (var point in altars) Consider(point, ref closest);
            Consider(shortcut, ref closest); Consider(relic, ref closest); Consider(vestige, ref closest);
            if (Nearby != null && Input.GetKeyDown(KeyCode.E)) Nearby.Use();
            if (Nearby != null && Nearby.kind == InteractionKind.Altar && Input.GetKeyDown(KeyCode.V)) Upgrade();
        }
        void Consider(Interactable candidate, ref float closest)
        {
            if (candidate == null || !candidate.gameObject.activeInHierarchy) return;
            float distance = Vector3.Distance(Player.transform.position, candidate.transform.position);
            if (distance < closest && CombatQuery.Clear(Player.transform.position + Vector3.up, candidate.transform.position + Vector3.up))
            { closest = distance; Nearby = candidate; }
        }
        public void SetPaused(bool paused)
        {
            if (paused && Player != null) Player.ClearBufferedInput();
            Paused = paused; Time.timeScale = paused ? 0 : 1;
            Cursor.lockState = paused || TestMode ? CursorLockMode.None : CursorLockMode.Locked;
            Cursor.visible = paused || TestMode;
        }
        public void Notify(string message, float seconds = 3) { Message = message; messageUntil = Time.time + seconds; }
        public void Rest(Interactable altar)
        {
            foreach (var enemy in Enemies)
                if (!enemy.Health.IsDead && enemy.Engaged && Vector3.Distance(Player.transform.position, enemy.transform.position) < 14)
                { Notify("No puedes descansar durante el combate."); return; }
            Progress.checkpoint = altar.checkpointId;
            Player.RestoreAt(altar.respawnPoint.position); ResetEnemies(); Save(); GameAudio.Play(Cue.Rest);
            Notify("La llama te recuerda · Vida y cálices restaurados");
        }
        public bool Upgrade()
        {
            if (Progress.level >= 5) { Notify("Bendición máxima alcanzada"); return false; }
            if (Progress.faith < UpgradeCost) { Notify("Necesitas " + UpgradeCost + " fragmentos de fe"); return false; }
            Progress.faith -= UpgradeCost; Progress.level++;
            Player.Health.maximum = 100 + Progress.level * 25; Player.Health.Heal(25); Save();
            Notify("Bendición de la llama · Vitalidad aumentada"); GameAudio.Play(Cue.Rest); return true;
        }
        void OnPlayerDeath()
        {
            Progress.droppedFaith = Progress.faith; Progress.faith = 0;
            Vector3 position = Player.transform.position;
            if (position.y < -2) position = altars[Progress.checkpoint].respawnPoint.position + Vector3.forward * 3;
            Progress.dropPosition = position + Vector3.up * .25f;
            ApplyVestige(); Save(); GameAudio.Play(Cue.Death);
            StartCoroutine(Respawn());
        }
        IEnumerator Respawn()
        {
            yield return new WaitForSeconds(2.6f);
            Player.RestoreAt(altars[Progress.checkpoint].respawnPoint.position); ResetEnemies();
            Notify(Progress.droppedFaith > 0 ? "Recupera tu vestigio antes de volver a caer" : "Tu juramento continúa");
        }
        void ResetEnemies()
        {
            foreach (var enemy in Enemies)
            {
                if (enemy.boss && Progress.boss) continue;
                enemy.gameObject.SetActive(true); enemy.ResetEnemy();
            }
        }
        public void EnemyDefeated(EnemyBrain enemy)
        {
            if (enemy.boss && Progress.boss) return;
            Progress.faith += enemy.reward;
            if (enemy.boss) { Progress.boss = true; Notify("DIOS DERROTADO · Has recuperado la chispa del Ocaso", 9); GameAudio.Play(Cue.Rest); }
            else Notify("+" + enemy.reward + " fragmentos de fe", 2);
            Save();
        }
        public void RecoverFaith()
        {
            int recovered = Progress.droppedFaith;
            Progress.faith += recovered; Progress.droppedFaith = 0; ApplyVestige(); Save();
            Notify("Fe recuperada · +" + recovered); GameAudio.Play(Cue.Rest);
        }
        public void OpenShortcut()
        {
            Progress.shortcut = true; ApplyWorldState(); Save(); Notify("Atajo abierto · El camino del peregrino"); GameAudio.Play(Cue.Block);
        }
        public void ClaimRelic()
        {
            if (Progress.relic) return;
            Progress.relic = true; Progress.faith += 75; ApplyWorldState(); Save();
            Notify("Reliquia de Nerea, diosa de la memoria · +75 fe", 5); GameAudio.Play(Cue.Rest);
        }
        void ApplyWorldState()
        {
            shortcut.gate.SetActive(!Progress.shortcut); shortcut.gameObject.SetActive(!Progress.shortcut);
            relic.gameObject.SetActive(!Progress.relic);
            foreach (var enemy in Enemies) if (enemy.boss && Progress.boss) enemy.gameObject.SetActive(false);
            ApplyVestige();
        }
        void ApplyVestige() { vestige.transform.position = Progress.dropPosition; vestige.gameObject.SetActive(Progress.droppedFaith > 0); }
        public void Save()
        {
            if (TestMode || SaveBlocked) return;
            if (!SaveStore.Write(Progress)) Notify("No se pudo guardar. Revisa los permisos del disco.", 6);
        }
        void OnApplicationQuit() { if (Ready) Save(); }
        void OnDestroy() { if (Instance == this) { Instance = null; Time.timeScale = 1; Cursor.lockState = CursorLockMode.None; Cursor.visible = true; } }
    }
}
