using Godot;

namespace StreepFighter;

/// <summary>
/// Player preferences that outlive the session (stored in user://settings.cfg).
/// </summary>
public static class Settings
{
    public const int MinCpuLevel = 1;
    public const int MaxCpuLevel = 8;
    public const int DefaultCpuLevel = 4;

    private const string Path = "user://settings.cfg";
    private static bool _loaded;
    private static int _cpuLevel = DefaultCpuLevel;

    /// <summary>CPU difficulty, 1 (pushover) to 8 (hardest), like SF2's star levels.</summary>
    public static int CpuLevel
    {
        get
        {
            Load();
            return _cpuLevel;
        }
        set
        {
            Load();
            int level = Mathf.Clamp(value, MinCpuLevel, MaxCpuLevel);
            if (level == _cpuLevel) return;
            _cpuLevel = level;
            Save();
        }
    }

    private static void Load()
    {
        if (_loaded) return;
        _loaded = true;
        var file = new ConfigFile();
        if (file.Load(Path) == Error.Ok)
            _cpuLevel = Mathf.Clamp((int)file.GetValue("game", "cpu_level", DefaultCpuLevel), MinCpuLevel, MaxCpuLevel);
    }

    private static void Save()
    {
        var file = new ConfigFile();
        file.SetValue("game", "cpu_level", _cpuLevel);
        file.Save(Path);
    }
}
