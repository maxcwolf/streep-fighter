namespace StreepFighter;

public class FighterStats
{
    public string Name;
    public int MaxHealth;
    public float WalkSpeed;
    public int PunchDmg;
    public int KickDmg;
    public int SpecialDmg;
    public float SpecialCooldown;
    public float BlockReduction;
    public string ScenePath;
}

public static class FighterData
{
    public static readonly FighterStats MirandaPriestly = new()
    {
        Name = "Miranda Priestly",
        MaxHealth = 1000,
        WalkSpeed = 250f,
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
        MaxHealth = 1000,
        WalkSpeed = 200f,
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
        MaxHealth = 1200,
        WalkSpeed = 180f,
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
        MaxHealth = 900,
        WalkSpeed = 220f,
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
        MaxHealth = 950,
        WalkSpeed = 280f,
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
        MaxHealth = 1100,
        WalkSpeed = 200f,
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

    public static readonly string[] CharacterNames = { "Miranda Priestly", "Julia Child", "Margaret Thatcher", "The Witch", "Donna Sheridan", "Sister Aloysius" };
}
