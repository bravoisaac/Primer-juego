using UnityEngine;

namespace TenFe
{
    public sealed class GameHud : MonoBehaviour
    {
        HudTheme theme;
        internal bool HelpVisible { get; set; }
        float volume = .65f, healthTrail = 1, trailUntil;
        float previousHealth = -1;
        float width, height;

        void Start()
        {
            volume = Mathf.Clamp01(PlayerPrefs.GetFloat("volume", .65f));
            AudioListener.volume = volume;
            GameSession.Instance.Player.orbit.sensitivity = Mathf.Clamp(PlayerPrefs.GetFloat("sensitivity", 2.2f), .5f, 5);
        }

        void Update()
        {
            var game = GameSession.Instance;
            if (game == null || !game.Ready) return;
            if (Input.GetKeyDown(KeyCode.H) && !game.Paused && !game.Player.Health.IsDead)
                HelpVisible = !HelpVisible;
            float current = game.Player.Health.Fraction;
            if (previousHealth < 0 || current > previousHealth) healthTrail = current;
            else if (current < previousHealth) trailUntil = Time.unscaledTime + .45f;
            if (Time.unscaledTime > trailUntil && !game.Paused)
                healthTrail = Mathf.MoveTowards(healthTrail, current, Time.unscaledDeltaTime * .45f);
            previousHealth = current;
        }

        // A single scale preserves text and symbols at 4:3, 16:9 and ultrawide aspect ratios.
        internal static float CanvasScale(int screenWidth, int screenHeight)
            => Mathf.Max(.01f, Mathf.Min(screenWidth / 1280f, screenHeight / 720f));

        void OnGUI()
        {
            var game = GameSession.Instance;
            if (game == null || !game.Ready) return;
            if (theme == null) theme = new HudTheme();
            Matrix4x4 oldMatrix = GUI.matrix;
            Color oldColor = GUI.color;
            float scale = CanvasScale(Screen.width, Screen.height);
            width = Screen.width / scale; height = Screen.height / scale;
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1));
            GUI.color = Color.white;
            try
            {
                if (game.Paused) { Pause(game); return; }
                Resources(game);
                Encounters(game);
                if (!string.IsNullOrEmpty(game.Message))
                {
                    var notice = new Rect(width / 2 - 230, 28, 460, 84);
                    theme.Panel(notice);
                    theme.Box(new Rect(notice.x, notice.y, 3, notice.height), HudTheme.Gold);
                    theme.Text(new Rect(notice.x + 18, notice.y + 8, notice.width - 36, 68), game.Message, theme.Center);
                }
                if (game.Nearby != null && !game.Player.Health.IsDead) Interaction(game);
                if (game.Player.Health.IsDead) Death(game);
                else if (HelpVisible) Help();
            }
            finally { GUI.matrix = oldMatrix; GUI.color = oldColor; }
        }

        void Resources(GameSession game)
        {
            var player = game.Player;
            theme.Panel(new Rect(28, 28, 350, 134));
            theme.Eclipse(new Rect(44, 43, 42, 42));
            theme.Text(new Rect(98, 40, 260, 22), "EL ÚLTIMO PEREGRINO", theme.Heading);
            theme.Text(new Rect(98, 65, 250, 20), "BENDICIÓN  " + game.Progress.level + " / 5", theme.Small);
            theme.Bar(new Rect(44, 98, 318, 13), player.Health.Fraction, HudTheme.Health, healthTrail);
            theme.Bar(new Rect(44, 123, 318, 7), player.Energy.Fraction, HudTheme.Energy);
            theme.Text(new Rect(44, 136, 170, 20), "VIDA  " + Mathf.CeilToInt(player.Health.Current) + " / " + player.Health.maximum, theme.Small);
            theme.Text(new Rect(216, 136, 146, 20), "ENERGÍA  " + Mathf.CeilToInt(player.Energy.Current), theme.SmallRight);

            theme.Panel(new Rect(width - 264, 28, 236, 84));
            theme.Diamond(width - 239, 55, 5, HudTheme.Gold);
            theme.Text(new Rect(width - 223, 40, 180, 21), "FRAGMENTOS DE FE", theme.Small);
            theme.Text(new Rect(width - 242, 61, 196, 39), game.Progress.faith.ToString("N0"), theme.Number);
            if (game.Progress.droppedFaith > 0)
                theme.Text(new Rect(width - 344, 120, 316, 26), "Vestigio pendiente · " + game.Progress.droppedFaith + " fe", theme.Right);

            float bottom = height - 116;
            theme.Panel(new Rect(28, bottom, 274, 88));
            theme.Key(new Rect(44, bottom + 18, 32, 32), "R");
            theme.Text(new Rect(88, bottom + 13, 198, 24), "CÁLIZ DE LA LLAMA", theme.Heading);
            for (int i = 0; i < 3; i++)
            {
                var pip = new Rect(89 + i * 24, bottom + 46, 16, 19);
                theme.Outline(pip, HudTheme.Border);
                if (i < player.Flasks) theme.Box(new Rect(pip.x + 3, pip.y + 3, 10, 13), HudTheme.Gold);
            }
            theme.Text(new Rect(167, bottom + 42, 115, 25), player.Flasks > 0 ? player.Flasks + " / 3" : "AGOTADOS", theme.Small);
            theme.Text(new Rect(28, height - 24, 340, 22), "H  Controles     /     ESC  Pausa", theme.Small);

            theme.Panel(new Rect(width - 342, height - 106, 314, 78));
            theme.Text(new Rect(width - 326, height - 97, 280, 21), game.Progress.boss ? "JURAMENTO CUMPLIDO" : "EL JURAMENTO", theme.SmallGold);
            theme.Text(new Rect(width - 326, height - 74, 280, 40), game.Progress.boss
                ? "La chispa del Ocaso vuelve a arder."
                : "Busca a Aster en el templo del eclipse.", theme.Body);
        }

        void Encounters(GameSession game)
        {
            var player = game.Player;
            var camera = player.orbit.GetComponent<Camera>();
            EnemyBrain warning = null;
            float nearest = 8;
            foreach (var enemy in game.Enemies)
            {
                if (!enemy.gameObject.activeInHierarchy || enemy.Health.IsDead) continue;
                float distance = Vector3.Distance(player.transform.position, enemy.transform.position);
                if (enemy.boss && enemy.Engaged)
                {
                    float x = width / 2 - 300, y = height - 175;
                    theme.Panel(new Rect(x - 20, y - 8, 640, 72));
                    theme.Text(new Rect(x, y, 600, 28), enemy.title, theme.Center);
                    theme.Bar(new Rect(x, y + 36, 600, 10), enemy.Health.Fraction, HudTheme.Health);
                    if (enemy.Enraged)
                        theme.Text(new Rect(x, y - 35, 600, 25), "FASE II  /  FURIA DIVINA", theme.CenterGold);
                }
                else if (!enemy.boss && distance < 13)
                {
                    Vector3 screen = camera.WorldToViewportPoint(enemy.transform.position + Vector3.up * (enemy.elite ? 3 : 2.6f));
                    if (Visible(screen))
                    {
                        float x = screen.x * width, y = (1 - screen.y) * height;
                        theme.Bar(new Rect(x - 42, y, 84, 5), enemy.Health.Fraction, HudTheme.Health);
                        if (enemy == player.Target)
                            theme.Text(new Rect(x - 150, y - 29, 300, 24), enemy.title, theme.Center);
                    }
                }
                if (enemy == player.Target)
                {
                    Vector3 screen = camera.WorldToViewportPoint(enemy.transform.position + Vector3.up * 1.3f);
                    if (Visible(screen)) theme.Target(screen.x * width, (1 - screen.y) * height);
                }
                // Show the nearest committed threat once, instead of overlapping several labels.
                if (enemy.Telegraphing && distance < nearest &&
                    CombatQuery.Clear(player.transform.position + Vector3.up, enemy.transform.position + Vector3.up))
                { warning = enemy; nearest = distance; }
            }
            if (warning != null && !player.Health.IsDead)
            {
                theme.Panel(new Rect(width / 2 - 230, 124, 460, 48));
                theme.Box(new Rect(width / 2 - 230, 124, 3, 48), HudTheme.Gold);
                theme.Text(new Rect(width / 2 - 214, 126, 428, 44), warning.title + " prepara un golpe", theme.CenterGold);
            }
        }

        static bool Visible(Vector3 viewport) => viewport.z > 0 && viewport.x > .04f && viewport.x < .96f && viewport.y > .06f && viewport.y < .94f;

        void Interaction(GameSession game)
        {
            var nearby = game.Nearby;
            float x = width / 2 - 280, y = height - 274;
            theme.Panel(new Rect(x, y, 560, 78));
            theme.Key(new Rect(x + 18, y + 23, 32, 32), "E");
            bool altar = nearby.kind == InteractionKind.Altar;
            string name = string.IsNullOrWhiteSpace(nearby.title) ? nearby.gameObject.name : nearby.title;
            theme.Text(new Rect(x + 66, y + 12, 474, 25), altar ? "Descansar en " + name : name, theme.Body);
            string detail = altar
                ? (game.Progress.level >= 5 ? "Bendición máxima alcanzada" : "V  Bendición · " + game.UpgradeCost + " fe  /  +25 de vida")
                : nearby.kind == InteractionKind.Vestige ? "Recuperar " + game.Progress.droppedFaith + " fragmentos de fe" : "Interactuar";
            theme.Text(new Rect(x + 66, y + 42, 474, 24), detail, theme.SmallGold);
        }

        void Death(GameSession game)
        {
            theme.Box(new Rect(0, 0, width, height), new Color(.025f, .012f, .016f, .86f));
            float y = height / 2;
            theme.Rule(width / 2 - 240, y - 66, 480);
            theme.Text(new Rect(0, y - 45, width, 70), "TU FE SE APAGA", theme.Title);
            theme.Text(new Rect(0, y + 30, width, 35), game.Progress.droppedFaith > 0
                ? game.Progress.droppedFaith + " fragmentos esperan en tu vestigio"
                : "La llama te llamará de nuevo", theme.Center);
            theme.Rule(width / 2 - 240, y + 92, 480);
        }

        void Help()
        {
            float x = width / 2 - 450, y = height / 2 - 200;
            theme.Panel(new Rect(x, y, 900, 400), true);
            theme.Text(new Rect(x + 28, y + 20, 844, 35), "EL ARTE DE PERSISTIR", theme.Section);
            theme.Text(new Rect(x + 28, y + 59, 844, 26), "Administra tu energía. Observa el golpe y aprovecha la recuperación.", theme.Body);
            theme.Rule(x + 28, y + 104, 844);
            Controls(x + 28, y + 126, 398, false);
            Controls(x + 474, y + 126, 398, true);
            theme.Text(new Rect(x + 28, y + 352, 844, 25), "H  Cerrar ayuda     ·     El mundo sigue activo; usa ESC para pausar.", theme.SmallGold);
        }

        void Controls(float x, float y, float w, bool combat)
        {
            theme.Text(new Rect(x, y, w, 24), combat ? "COMBATE" : "EXPLORACIÓN", theme.SmallGold);
            string[] keys = combat ? CombatKeys : ExploreKeys;
            string[] labels = combat ? CombatLabels : ExploreLabels;
            for (int i = 0; i < keys.Length; i++)
            {
                float row = y + 33 + i * 35;
                theme.Key(new Rect(x, row, 114, 27), keys[i]);
                theme.Text(new Rect(x + 130, row, w - 130, 28), labels[i], theme.Body);
            }
        }

        static readonly string[] ExploreKeys = { "W A S D", "MOUSE", "SHIFT / F", "E / V", "R" };
        static readonly string[] ExploreLabels = { "Moverse", "Girar la cámara", "Correr / saltar", "Interactuar / bendición", "Beber un cáliz" };
        static readonly string[] CombatKeys = { "CLIC IZQ.", "Q", "CLIC DER.", "ESPACIO", "TAB / CENTRAL" };
        static readonly string[] CombatLabels = { "Ataque ligero", "Ataque fuerte", "Mantener el bloqueo", "Esquivar", "Fijar / cambiar objetivo" };

        void Pause(GameSession game)
        {
            theme.Box(new Rect(0, 0, width, height), new Color(.012f, .018f, .025f, .95f));
            float x = width / 2 - 500, y = height / 2 - 316;
            theme.Eclipse(new Rect(x + 4, y + 9, 62, 62));
            theme.Text(new Rect(x + 86, y, 650, 61), "T E N   F E", theme.Logo);
            theme.Text(new Rect(x + 90, y + 61, 650, 26), "SANTUARIO DEL OCASO  /  JURAMENTO EN PAUSA", theme.SmallGold);
            theme.Rule(x, y + 106, 1000);

            theme.Text(new Rect(x, y + 126, 470, 30), "Continúa tu peregrinaje", theme.Section);
            theme.Text(new Rect(x, y + 163, 455, 49), "Cada llama es un refugio. Descansa para recuperar vida, energía y cálices.", theme.Body);
            theme.Panel(new Rect(x, y + 230, 452, 168));
            theme.Text(new Rect(x + 18, y + 241, 416, 25), "AJUSTES", theme.SmallGold);
            theme.Text(new Rect(x + 18, y + 280, 180, 25), "Volumen", theme.Body);
            theme.Text(new Rect(x + 360, y + 280, 74, 25), Mathf.RoundToInt(volume * 100) + "%", theme.SmallRight);
            theme.Box(new Rect(x + 192, y + 295, 151, 3), HudTheme.Border);
            theme.Box(new Rect(x + 192, y + 295, 151 * volume, 3), HudTheme.Gold);
            GUI.SetNextControlName("Volume");
            float nextVolume = GUI.HorizontalSlider(new Rect(x + 192, y + 288, 151, 22), volume, 0, 1, theme.Slider, theme.Thumb);
            if (!Mathf.Approximately(nextVolume, volume))
            { volume = nextVolume; AudioListener.volume = volume; if (!game.TestMode) PlayerPrefs.SetFloat("volume", volume); }
            theme.Text(new Rect(x + 18, y + 337, 170, 25), "Sensibilidad", theme.Body);
            theme.Text(new Rect(x + 360, y + 337, 74, 25), game.Player.orbit.sensitivity.ToString("0.0"), theme.SmallRight);
            theme.Box(new Rect(x + 192, y + 352, 151, 3), HudTheme.Border);
            theme.Box(new Rect(x + 192, y + 352, 151 * Mathf.InverseLerp(.5f, 5, game.Player.orbit.sensitivity), 3), HudTheme.Gold);
            GUI.SetNextControlName("Sensitivity");
            float sensitivity = GUI.HorizontalSlider(new Rect(x + 192, y + 345, 151, 22), game.Player.orbit.sensitivity, .5f, 5, theme.Slider, theme.Thumb);
            if (!Mathf.Approximately(sensitivity, game.Player.orbit.sensitivity))
            { game.Player.orbit.sensitivity = sensitivity; if (!game.TestMode) PlayerPrefs.SetFloat("sensitivity", sensitivity); }

            GUI.SetNextControlName("Resume");
            if (GUI.Button(new Rect(x, y + 426, 452, 52), "Continuar el juramento", theme.PrimaryButton))
            { if (!game.TestMode) PlayerPrefs.Save(); game.SetPaused(false); }
            GUI.SetNextControlName("Quit");
            if (GUI.Button(new Rect(x, y + 492, 452, 46), "Guardar y salir", theme.Button))
            { game.Save(); if (!game.TestMode) PlayerPrefs.Save(); Application.Quit(); }
            theme.Text(new Rect(x, y + 554, 452, 28), "ESC  Volver al santuario", theme.Small);

            theme.Box(new Rect(x + 493, y + 132, 1, 423), HudTheme.Border);
            Controls(x + 534, y + 128, 466, false);
            Controls(x + 534, y + 357, 466, true);
            theme.Rule(x, y + 603, 1000);
            theme.Text(new Rect(x, y + 614, 1000, 26), "La fe que conservas: " + game.Progress.faith + "     /     Bendición " + game.Progress.level + " de 5", theme.SmallGold);
        }

        void OnDestroy() { theme?.Dispose(); }
    }
}
