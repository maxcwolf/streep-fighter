using Godot;

namespace StreepFighter;

/// <summary>
/// Trauma-driven screen shake for the fight camera. Reads <see cref="Juice.Trauma"/>
/// and applies a decaying offset + rotation each rendered frame. Trauma is
/// added on hits elsewhere (Fighter.TakeDamage) and decays here.
///
/// The math follows the classic "trauma squared" curve (Jan Willem Nijman /
/// GDC talk): shake = trauma^2 so small trauma barely registers and big trauma
/// snaps hard, which reads as campy and punchy.
/// </summary>
public partial class CameraShake : Camera2D
{
    // How fast trauma bleeds off (per second). Higher = snappier recovery.
    private const float DecayPerSecond = 1.6f;

    // Maximum shake reach at full trauma.
    private const float MaxOffset = 26f;       // pixels
    private const float MaxRoll = 0.045f;       // radians (~2.6 deg)

    // Noise scroll speed — higher = buzzier shake.
    private const float NoiseSpeed = 34f;

    private readonly FastNoiseLite _noiseX = new();
    private readonly FastNoiseLite _noiseY = new();
    private readonly FastNoiseLite _noiseR = new();
    private float _noiseTime;
    private Vector2 _restOffset;

    public override void _Ready()
    {
        // Remember the authored offset so shake is applied relative to it.
        _restOffset = Offset;

        _noiseX.Seed = 1;
        _noiseY.Seed = 2;
        _noiseR.Seed = 3;
        foreach (var n in new[] { _noiseX, _noiseY, _noiseR })
        {
            n.NoiseType = FastNoiseLite.NoiseTypeEnum.Perlin;
            n.Frequency = 0.6f;
        }
    }

    public override void _Process(double delta)
    {
        float dt = (float)delta;

        // Decay trauma toward zero.
        if (Juice.Trauma > 0f)
            Juice.Trauma = Mathf.Max(0f, Juice.Trauma - DecayPerSecond * dt);

        if (Juice.Trauma <= 0.0001f)
        {
            Offset = _restOffset;
            Rotation = 0f;
            return;
        }

        _noiseTime += dt * NoiseSpeed;
        float shake = Juice.Trauma * Juice.Trauma; // trauma^2 curve

        float ox = MaxOffset * shake * _noiseX.GetNoise1D(_noiseTime);
        float oy = MaxOffset * shake * _noiseY.GetNoise1D(_noiseTime);
        float roll = MaxRoll * shake * _noiseR.GetNoise1D(_noiseTime);

        Offset = _restOffset + new Vector2(ox, oy);
        Rotation = roll;
    }
}
