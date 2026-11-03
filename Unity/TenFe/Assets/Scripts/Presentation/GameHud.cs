using UnityEngine;

namespace TenFe
{
    public sealed class GameHud : MonoBehaviour
    {
        GUIStyle small, normal, title, center, button;
        readonly Color gold = new Color(.86f, .71f, .42f);
        Texture2D white;
        bool help;
        float volume = .65f;
        void Start()
        {
            volume = PlayerPrefs.GetFloat("volume", .65f); AudioListener.volume = volume;
            GameSession.Instance.Player.orbit.sensitivity = PlayerPrefs.GetFloat("sensitivity", 2.2f);
        }
        void Styles()
        {
            if (white != null) return;
            white = Texture2D.whiteTexture;
            small = new GUIStyle(GUI.skin.label) { fontSize = 14 }; small.normal.textColor = new Color(.73f, .74f, .74f);
            normal = new GUIStyle(small) { fontSize = 18 }; normal.normal.textColor = new Color(.94f, .9f, .8f);
            center = new GUIStyle(normal) { alignment = TextAnchor.MiddleCenter };
            title = new GUIStyle(center) { fontSize = 40 }; title.normal.textColor = gold;
            button = new GUIStyle(GUI.skin.button) { fontSize = 18, fixedHeight = 42 };
        }
        void Rect(float x, float y, float w, float h, Color color)
        { GUI.color = color; GUI.DrawTexture(new Rect(x, y, w, h), white); GUI.color = Color.white; }
        void Bar(float x, float y, float w, float fraction, Color color)
        {
            Rect(x - 2, y - 2, w + 4, 16, new Color(.35f, .3f, .21f));
            Rect(x, y, w, 12, new Color(.08f, .09f, .1f)); Rect(x, y, w * Mathf.Clamp01(fraction), 12, color);
        }
        void OnGUI()
        {
            var game = GameSession.Instance;
            if (game == null || !game.Ready) return;
            Styles();
            GUI.matrix = Matrix4x4.Scale(new Vector3(Screen.width / 1280f, Screen.height / 720f, 1));
            var player = game.Player;
            Rect(24, 23, 332, 119, new Color(.035f, .045f, .055f, .85f));
            GUI.Label(new Rect(40, 31, 300, 25), "EL ÚLTIMO PEREGRINO", normal);
            Bar(40, 69, 296, player.Health.Fraction, new Color(.62f, .19f, .18f));
            Bar(40, 94, 296, player.Energy.Fraction, new Color(.32f, .53f, .43f));
            GUI.Label(new Rect(40, 113, 300, 23), "VIDA " + Mathf.CeilToInt(player.Health.Current) + " / " + player.Health.maximum + "    ·    ENERGÍA " + Mathf.CeilToInt(player.Energy.Current), small);
            GUI.Label(new Rect(950, 28, 300, 26), "✦  " + game.Progress.faith + "  FRAGMENTOS DE FE", normal);
            GUI.Label(new Rect(950, 55, 300, 24), "Bendición " + game.Progress.level + " / 5", small);
            Rect(24, 607, 310, 87, new Color(.035f, .045f, .055f, .85f));
            GUI.Label(new Rect(40, 615, 290, 28), "R   CÁLIZ DE LA LLAMA   " + player.Flasks + " / 3", normal);
            GUI.Label(new Rect(40, 649, 290, 25), "H  Controles    ·    ESC  Pausa", small);
            GUI.Label(new Rect(815, 650, 430, 30), game.Progress.boss ? "JURAMENTO CUMPLIDO · Explora el santuario" : "Busca a Aster en el templo del eclipse", small);

            var camera = player.orbit.GetComponent<Camera>();
            foreach (var enemy in game.Enemies)
            {
                if (!enemy.gameObject.activeInHierarchy || enemy.Health.IsDead) continue;
                if (enemy.boss && enemy.Engaged)
                {
                    GUI.Label(new Rect(340, 566, 600, 30), enemy.title + (enemy.Enraged ? " · FURIA DIVINA" : ""), center);
                    Bar(340, 602, 600, enemy.Health.Fraction, new Color(.64f, .23f, .17f));
                }
                else if (!enemy.boss && Vector3.Distance(player.transform.position, enemy.transform.position) < 13)
                {
                    Vector3 screen = camera.WorldToViewportPoint(enemy.transform.position + Vector3.up * (enemy.elite ? 3 : 2.6f));
                    if (screen.z > 0) Bar(screen.x * 1280 - 36, (1 - screen.y) * 720, 72, enemy.Health.Fraction, new Color(.67f, .29f, .2f));
                }
                if (enemy == player.Target)
                {
                    Vector3 screen = camera.WorldToViewportPoint(enemy.transform.position + Vector3.up * 1.3f);
                    if (screen.z > 0) GUI.Label(new Rect(screen.x * 1280 - 20, (1 - screen.y) * 720 - 20, 40, 40), "◇", title);
                }
                if (enemy.Telegraphing && Vector3.Distance(player.transform.position, enemy.transform.position) < 8)
                    GUI.Label(new Rect(430, 115, 420, 30), "¡" + enemy.title + " prepara un golpe!", center);
            }
            if (!string.IsNullOrEmpty(game.Message))
            {
                Rect(220, 160, 840, 48, new Color(.03f, .035f, .045f, .8f));
                GUI.Label(new Rect(230, 163, 820, 42), game.Message, center);
            }
            if (game.Nearby != null && !player.Health.IsDead)
            {
                Rect(340, 486, 600, 45, new Color(.03f, .035f, .045f, .88f));
                GUI.Label(new Rect(345, 486, 590, 45), game.Nearby.Prompt, center);
            }
            if (player.Health.IsDead)
            {
                Rect(0, 0, 1280, 720, new Color(.02f, .01f, .015f, .7f));
                GUI.Label(new Rect(0, 280, 1280, 90), "TU FE SE APAGA", title);
                GUI.Label(new Rect(0, 370, 1280, 40), "La llama te llamará de nuevo", center);
            }
            if (help && !game.Paused) Controls(360, 230);
            if (game.Paused) Pause(game);
        }
        void Update() { if (Input.GetKeyDown(KeyCode.H)) help = !help; }
        void Controls(float x, float y)
        {
            Rect(x, y, 560, 240, new Color(.025f, .035f, .045f, .96f));
            string[] lines = { "WASD  Moverse     ·     Mouse  Cámara", "Shift  Correr     ·     F  Saltar     ·     Espacio  Esquivar", "Clic izquierdo  Ataque     ·     Q  Ataque fuerte", "Clic derecho  Bloquear     ·     Tab / clic central  Fijar o cambiar", "R  Curarse     ·     E  Interactuar     ·     V  Mejorar en altar", "Los golpes consumen energía. Ataca después de esquivar." };
            for (int i = 0; i < lines.Length; i++) GUI.Label(new Rect(x + 20, y + 18 + i * 34, 530, 30), lines[i], i == 5 ? small : normal);
        }
        void Pause(GameSession game)
        {
            Rect(0, 0, 1280, 720, new Color(.015f, .025f, .035f, .93f));
            GUI.Label(new Rect(0, 35, 1280, 65), "T E N   F E", title);
            GUI.Label(new Rect(0, 95, 1280, 36), "SANTUARIO DEL OCASO · PAUSA", center);
            Controls(360, 145);
            GUI.Label(new Rect(400, 398, 200, 25), "Volumen", normal);
            float nextVolume = GUI.HorizontalSlider(new Rect(620, 411, 240, 20), volume, 0, 1);
            if (!Mathf.Approximately(nextVolume, volume)) { volume = nextVolume; AudioListener.volume = volume; PlayerPrefs.SetFloat("volume", volume); }
            GUI.Label(new Rect(400, 438, 200, 25), "Sensibilidad", normal);
            float sensitivity = GUI.HorizontalSlider(new Rect(620, 451, 240, 20), game.Player.orbit.sensitivity, .5f, 5);
            if (!Mathf.Approximately(sensitivity, game.Player.orbit.sensitivity))
            { game.Player.orbit.sensitivity = sensitivity; PlayerPrefs.SetFloat("sensitivity", sensitivity); }
            if (GUI.Button(new Rect(440, 490, 400, 42), "Continuar el juramento", button)) game.SetPaused(false);
            if (GUI.Button(new Rect(440, 545, 400, 42), "Guardar y salir", button)) { game.Save(); PlayerPrefs.Save(); Application.Quit(); }
            GUI.Label(new Rect(0, 621, 1280, 40), "Base jugable · Modelos y animaciones provisionales", center);
        }
    }
}
