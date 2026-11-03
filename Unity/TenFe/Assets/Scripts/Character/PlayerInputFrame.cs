using UnityEngine;

namespace TenFe
{
    // One snapshot per update. Kept separate so movement/combat can be exercised without OS input.
    internal struct PlayerInputFrame
    {
        public Vector2 Move;
        public bool Sprint, Block, Light, Heavy, Dodge, Jump, Heal, Target;
        public static PlayerInputFrame Read()
        {
            return new PlayerInputFrame
            {
                Move = Vector2.ClampMagnitude(new Vector2(
                    (Input.GetKey(KeyCode.D) ? 1 : 0) - (Input.GetKey(KeyCode.A) ? 1 : 0),
                    (Input.GetKey(KeyCode.W) ? 1 : 0) - (Input.GetKey(KeyCode.S) ? 1 : 0)), 1),
                Sprint = Input.GetKey(KeyCode.LeftShift), Block = Input.GetMouseButton(1),
                Light = Input.GetMouseButtonDown(0), Heavy = Input.GetKeyDown(KeyCode.Q),
                Dodge = Input.GetKeyDown(KeyCode.Space), Jump = Input.GetKeyDown(KeyCode.F),
                Heal = Input.GetKeyDown(KeyCode.R), Target = Input.GetKeyDown(KeyCode.Tab) || Input.GetMouseButtonDown(2)
            };
        }
    }
}
