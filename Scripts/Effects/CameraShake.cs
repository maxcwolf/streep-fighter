using Godot;

namespace StreepFighter;

/// <summary>
/// Trauma-driven screen shake for the fight camera. Reads <see cref="Juice.Trauma"/>
/// and applies a decaying offset each rendered frame; trauma is added on hits
/// elsewhere (Fighter.ReceiveHit) and decays here.
///
/// "Trauma squared" curve: small trauma barely registers, big trauma snaps
/// hard. The offset is whole pixels only and there is no roll - at 384x216 a
/// sub-pixel or rotated camera would smear the art.
/// </summary>
public partial class CameraShake : Camera2D
{
    // How fast trauma bleeds off (per second). Higher = snappier recovery.
    private const float DecayPerSecond = 2.2f;
    // Maximum shake reach at full trauma, in native pixels.
    private const float MaxOffset = 6f;
    // Noise scroll speed - higher = buzzier shake.
    private const float NoiseSpeed = 40f;

    private readonly FastNoiseLite _noiseX = new();
    private readonly FastNoiseLite _noiseY = new();
    private float _noiseTime;

    public override void _Ready()
    {
        _noiseX.Seed = 1;
        _noiseY.Seed = 2;
        foreach (var n in new[] { _noiseX, _noiseY })
        {
            n.NoiseType = FastNoiseLite.NoiseTypeEnum.Perlin;
            n.Frequency = 0.6f;
        }
    }

    public override void _Process(double delta)
    {
        float dt = (float)delta;

        if (Juice.Trauma > 0f)
            Juice.Trauma = Mathf.Max(0f, Juice.Trauma - DecayPerSecond * dt);

        if (Juice.Trauma <= 0.0001f)
        {
            Offset = Vector2.Zero;
            return;
        }

        _noiseTime += dt * NoiseSpeed;
        float shake = Juice.Trauma * Juice.Trauma;
        Offset = new Vector2(
            Mathf.Round(MaxOffset * shake * _noiseX.GetNoise1D(_noiseTime) * 2f),
            Mathf.Round(MaxOffset * shake * _noiseY.GetNoise1D(_noiseTime) * 2f));
    }
}
