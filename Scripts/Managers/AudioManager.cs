using Godot;

namespace StreepFighter;

public partial class AudioManager : Node
{
    public static AudioManager Instance { get; private set; }

    private const int PoolSize = 8;
    private AudioStreamPlayer[] _players;
    private float _sfxVolumeDb = 0f;

    public override void _Ready()
    {
        Instance = this;
        ProcessMode = ProcessModeEnum.Always;

        _players = new AudioStreamPlayer[PoolSize];
        for (int i = 0; i < PoolSize; i++)
        {
            var player = new AudioStreamPlayer();
            player.Bus = "Master";
            AddChild(player);
            _players[i] = player;
        }
    }

    public void PlaySFX(string name)
    {
        var stream = TryLoad(name);
        if (stream == null) return;

        var player = GetFreePlayer();
        if (player == null) return;

        player.Stream = stream;
        player.VolumeDb = _sfxVolumeDb;
        player.Play();
    }

    public void SetSFXVolume(float db)
    {
        _sfxVolumeDb = db;
    }

    private AudioStream TryLoad(string name)
    {
        string oggPath = $"res://Assets/Audio/SFX/{name}.ogg";
        if (ResourceLoader.Exists(oggPath))
            return GD.Load<AudioStream>(oggPath);

        string wavPath = $"res://Assets/Audio/SFX/{name}.wav";
        if (ResourceLoader.Exists(wavPath))
            return GD.Load<AudioStream>(wavPath);

        string mp3Path = $"res://Assets/Audio/SFX/{name}.mp3";
        if (ResourceLoader.Exists(mp3Path))
            return GD.Load<AudioStream>(mp3Path);

        return null;
    }

    private AudioStreamPlayer GetFreePlayer()
    {
        foreach (var player in _players)
        {
            if (!player.Playing)
                return player;
        }
        // All busy — steal the oldest (first in array)
        return _players[0];
    }
}
