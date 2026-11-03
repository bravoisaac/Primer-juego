using UnityEngine;

namespace TenFe
{
    public enum InteractionKind { Altar, Shortcut, Relic, Vestige }
    public sealed class Interactable : MonoBehaviour
    {
        public InteractionKind kind;
        public string title;
        public Transform respawnPoint;
        public GameObject gate;
        public int checkpointId;
        public string Prompt => kind == InteractionKind.Altar ? "E  Descansar   ·   V  Bendición (" + GameSession.Instance.UpgradeCost + " fe)" : "E  " + title;
        public void Use()
        {
            var game = GameSession.Instance;
            switch (kind)
            {
                case InteractionKind.Altar: game.Rest(this); break;
                case InteractionKind.Shortcut: game.OpenShortcut(); break;
                case InteractionKind.Relic: game.ClaimRelic(); break;
                case InteractionKind.Vestige: game.RecoverFaith(); break;
            }
        }
    }
}
