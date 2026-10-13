namespace StreepFighter;

public class StageInfo
{
    public string Name;
    public string DisplayLabel;
    /// <summary>Asset key: Assets/Stages/{Key}_far.png, _main.png, _thumb.png.</summary>
    public string Key;

    public string FarPath => $"res://Assets/Stages/{Key}_far.png";
    public string MainPath => $"res://Assets/Stages/{Key}_main.png";
    public string ThumbPath => $"res://Assets/Stages/{Key}_thumb.png";
}

public static class StageData
{
    /// <summary>Width of every stage's main layer; the 384px screen pans across it.</summary>
    public const float Width = 512f;

    public static readonly StageInfo[] Stages =
    {
        new() { Name = "Runway Magazine", DisplayLabel = "RUNWAY MAGAZINE - NEW YORK CITY", Key = "runway" },
        new() { Name = "Julia's Kitchen", DisplayLabel = "JULIA'S KITCHEN - PARIS, FRANCE", Key = "kitchen" },
        new() { Name = "House of Commons", DisplayLabel = "HOUSE OF COMMONS - LONDON, ENGLAND", Key = "parliament" },
        new() { Name = "Enchanted Woods", DisplayLabel = "THE ENCHANTED WOODS", Key = "forest" },
        new() { Name = "Kalokairi Island", DisplayLabel = "KALOKAIRI ISLAND - GREECE", Key = "villa" },
        new() { Name = "St. Nicholas Church", DisplayLabel = "ST. NICHOLAS CHURCH - THE BRONX", Key = "church" },
    };

    public static StageInfo GetByIndex(int index)
    {
        if (index >= 0 && index < Stages.Length)
            return Stages[index];
        return Stages[0];
    }
}
