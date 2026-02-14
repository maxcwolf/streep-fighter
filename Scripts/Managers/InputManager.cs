namespace StreepFighter;

public static class InputManager
{
    public static string Action(int playerIndex, string action)
    {
        string prefix = playerIndex == 0 ? "p1_" : "p2_";
        return prefix + action;
    }
}
