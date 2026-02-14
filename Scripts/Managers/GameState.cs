namespace StreepFighter;

public enum GameMode
{
    PvP,
    VsCPU
}

public static class GameState
{
    public static GameMode Mode = GameMode.PvP;
    public static int P1CharacterIndex = 0;
    public static int P2CharacterIndex = 1;
    public static int StageIndex = 0;
    public static int P1RoundWins = 0;
    public static int P2RoundWins = 0;
    public static int RoundsToWin = 2; // best of 3

    public static void Reset()
    {
        P1RoundWins = 0;
        P2RoundWins = 0;
    }
}
