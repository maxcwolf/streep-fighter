using Godot;

namespace StreepFighter;

public class StageInfo
{
    public string Name;
    public string DisplayLabel;
    public string ScenePath;
    public Color SkyColor;
    public Color WallColor;
    public Color FloorColor;
}

public static class StageData
{
    public static readonly StageInfo[] Stages =
    {
        new() { Name = "Runway Magazine", DisplayLabel = "RUNWAY MAGAZINE \u2014 NEW YORK CITY",
                ScenePath = "res://Scenes/Stages/Backgrounds/RunwayOffice.tscn",
                SkyColor = new(0.55f, 0.72f, 0.88f, 1), WallColor = new(0.88f, 0.88f, 0.86f, 1), FloorColor = new(0.82f, 0.8f, 0.78f, 1) },
        new() { Name = "Julia's Kitchen", DisplayLabel = "JULIA'S KITCHEN \u2014 PARIS, FRANCE",
                ScenePath = "res://Scenes/Stages/Backgrounds/FrenchKitchen.tscn",
                SkyColor = new(0.92f, 0.85f, 0.72f, 1), WallColor = new(0.72f, 0.45f, 0.28f, 1), FloorColor = new(0.55f, 0.35f, 0.2f, 1) },
        new() { Name = "House of Commons", DisplayLabel = "HOUSE OF COMMONS \u2014 LONDON, ENGLAND",
                ScenePath = "res://Scenes/Stages/Backgrounds/Parliament.tscn",
                SkyColor = new(0.18f, 0.12f, 0.08f, 1), WallColor = new(0.28f, 0.2f, 0.12f, 1), FloorColor = new(0.2f, 0.4f, 0.25f, 1) },
        new() { Name = "Enchanted Woods", DisplayLabel = "THE ENCHANTED WOODS",
                ScenePath = "res://Scenes/Stages/Backgrounds/EnchantedForest.tscn",
                SkyColor = new(0.04f, 0.05f, 0.12f, 1), WallColor = new(0.08f, 0.06f, 0.05f, 1), FloorColor = new(0.08f, 0.12f, 0.06f, 1) },
        new() { Name = "Kalokairi Island", DisplayLabel = "KALOKAIRI ISLAND \u2014 GREECE",
                ScenePath = "res://Scenes/Stages/Backgrounds/GreekVilla.tscn",
                SkyColor = new(0.95f, 0.6f, 0.35f, 1), WallColor = new(0.15f, 0.55f, 0.7f, 1), FloorColor = new(0.88f, 0.82f, 0.72f, 1) },
        new() { Name = "St. Nicholas Church", DisplayLabel = "ST. NICHOLAS CHURCH \u2014 THE BRONX",
                ScenePath = "res://Scenes/Stages/Backgrounds/ChurchInterior.tscn",
                SkyColor = new(0.25f, 0.22f, 0.2f, 1), WallColor = new(0.32f, 0.3f, 0.28f, 1), FloorColor = new(0.35f, 0.3f, 0.25f, 1) },
    };

    public static StageInfo GetByIndex(int index)
    {
        if (index >= 0 && index < Stages.Length)
            return Stages[index];
        return Stages[0];
    }
}
