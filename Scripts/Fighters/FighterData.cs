namespace StreepFighter;

public class FighterStats
{
    public string Name;
    /// <summary>Asset key: Assets/Sprites/Fighters/{Key}.png, Assets/UI/portrait_{Key}.png.</summary>
    public string Key;
    public string ShortName;
    public string Film;
    public string SpecialName;
    public string WinQuote;
    public int MaxHealth;
    /// <summary>Pixels per second at the game's native 384x216.</summary>
    public float WalkSpeed;
    public int PunchDmg;
    public int KickDmg;
    public int SpecialDmg;
    public float SpecialCooldown;
    public float BlockReduction;
    public string ScenePath;

    public string SheetPath => $"res://Assets/Sprites/Fighters/{Key}.png";
    /// <summary>Second-player colours, used when both players pick the same fighter.</summary>
    public string AltSheetPath => $"res://Assets/Sprites/Fighters/{Key}_alt.png";
    public string PortraitPath => $"res://Assets/UI/portrait_{Key}.png";
    public string BigPortraitPath => $"res://Assets/UI/portrait_{Key}_big.png";
}

public static class FighterData
{
    public static readonly FighterStats MirandaPriestly = new()
    {
        Name = "Miranda Priestly",
        Key = "miranda",
        ShortName = "MIRANDA",
        Film = "THE DEVIL WEARS PRADA",
        SpecialName = "THAT'S ALL",
        WinQuote = "THAT'S ALL.",
        MaxHealth = 1000,
        WalkSpeed = 105f,
        PunchDmg = 80,
        KickDmg = 100,
        SpecialDmg = 150,
        SpecialCooldown = 3.0f,
        BlockReduction = 0.8f,
        ScenePath = "res://Scenes/Fighters/MirandaPriestly.tscn"
    };

    public static readonly FighterStats JuliaChild = new()
    {
        Name = "Julia Child",
        Key = "julia",
        ShortName = "JULIA",
        Film = "JULIE & JULIA",
        SpecialName = "BON APPETIT",
        WinQuote = "BON APPETIT!",
        MaxHealth = 1000,
        WalkSpeed = 84f,
        PunchDmg = 70,
        KickDmg = 90,
        SpecialDmg = 180,
        SpecialCooldown = 4.0f,
        BlockReduction = 0.8f,
        ScenePath = "res://Scenes/Fighters/JuliaChild.tscn"
    };

    public static readonly FighterStats MargaretThatcher = new()
    {
        Name = "Margaret Thatcher",
        Key = "thatcher",
        ShortName = "THATCHER",
        Film = "THE IRON LADY",
        SpecialName = "IRON FIST",
        WinQuote = "THE LADY'S NOT FOR TURNING.",
        MaxHealth = 1200,
        WalkSpeed = 76f,
        PunchDmg = 90,
        KickDmg = 110,
        SpecialDmg = 250,
        SpecialCooldown = 5.0f,
        BlockReduction = 0.9f,
        ScenePath = "res://Scenes/Fighters/MargaretThatcher.tscn"
    };

    public static readonly FighterStats TheWitch = new()
    {
        Name = "The Witch",
        Key = "witch",
        ShortName = "THE WITCH",
        Film = "INTO THE WOODS",
        SpecialName = "CURSE OF THE WOODS",
        WinQuote = "CAREFUL THE THINGS YOU SAY.",
        MaxHealth = 900,
        WalkSpeed = 92f,
        PunchDmg = 65,
        KickDmg = 85,
        SpecialDmg = 200,
        SpecialCooldown = 3.5f,
        BlockReduction = 0.75f,
        ScenePath = "res://Scenes/Fighters/TheWitch.tscn"
    };

    public static readonly FighterStats DonnaSheridan = new()
    {
        Name = "Donna Sheridan",
        Key = "donna",
        ShortName = "DONNA",
        Film = "MAMMA MIA!",
        SpecialName = "DANCING QUEEN",
        WinQuote = "MAMMA MIA, HERE I GO AGAIN!",
        MaxHealth = 950,
        WalkSpeed = 118f,
        PunchDmg = 70,
        KickDmg = 85,
        SpecialDmg = 130,
        SpecialCooldown = 3.0f,
        BlockReduction = 0.7f,
        ScenePath = "res://Scenes/Fighters/DonnaSheridan.tscn"
    };

    public static readonly FighterStats SisterAloysius = new()
    {
        Name = "Sister Aloysius",
        Key = "aloysius",
        ShortName = "ALOYSIUS",
        Film = "DOUBT",
        SpecialName = "DIVINE DISCIPLINE",
        WinQuote = "I HAVE SUCH DOUBTS... ABOUT YOU.",
        MaxHealth = 1100,
        WalkSpeed = 84f,
        PunchDmg = 85,
        KickDmg = 95,
        SpecialDmg = 180,
        SpecialCooldown = 4.0f,
        BlockReduction = 0.92f,
        ScenePath = "res://Scenes/Fighters/SisterAloysius.tscn"
    };

    public static FighterStats GetByIndex(int index)
    {
        return index switch
        {
            0 => MirandaPriestly,
            1 => JuliaChild,
            2 => MargaretThatcher,
            3 => TheWitch,
            4 => DonnaSheridan,
            5 => SisterAloysius,
            _ => MirandaPriestly
        };
    }

    public const int Count = 6;

    public static readonly string[] CharacterNames = { "Miranda Priestly", "Julia Child", "Margaret Thatcher", "The Witch", "Donna Sheridan", "Sister Aloysius" };
}
