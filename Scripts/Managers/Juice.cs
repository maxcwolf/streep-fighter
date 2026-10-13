using Godot;

namespace StreepFighter;

/// <summary>
/// Global, lightweight juice state shared between the fighters, the game
/// manager and the camera. Purely static so any node can poke it without a
/// reference. Lives for the duration of the process; reset on round start.
///
/// Hit-stop semantics:
///   - HitStopFrames is counted in PHYSICS ticks (game runs at 60 ticks/s).
///   - GameManager._PhysicsProcess decrements it once per tick and, while it
///     is above zero, skips the fighters' Tick() entirely (their input is
///     still polled, so presses during the freeze are buffered).
///   - Rendering keeps running, so the impact frame stays on screen and the
///     victim's sprite rattles.
///
/// Trauma drives the screen shake; CameraShake decays it each frame.
/// </summary>
public static class Juice
{
    /// <summary>Remaining freeze frames (physics ticks). 0 == not frozen.</summary>
    public static int HitStopFrames;

    /// <summary>Screen-shake trauma, 0..1. Shake intensity ~ trauma^2.</summary>
    public static float Trauma;

    // Suggested trauma amounts (kept small so the camera never goes wild).
    public const float TraumaLight = 0.22f;   // normal punch / projectile
    public const float TraumaMedium = 0.34f;  // kick / heavy
    public const float TraumaHeavy = 0.55f;   // special
    public const float TraumaKO = 0.9f;        // knockout

    // Suggested hit-stop weights (in physics frames @60Hz).
    public const int StopLight = 3;
    public const int StopHeavy = 5;
    public const int StopSpecial = 8;

    /// <summary>Request a freeze. Longest pending request wins (never shortens).</summary>
    public static void HitStop(int frames)
    {
        if (frames > HitStopFrames)
            HitStopFrames = frames;
    }

    /// <summary>Add trauma, clamped to 1.</summary>
    public static void AddTrauma(float amount)
    {
        Trauma = Mathf.Min(1f, Trauma + amount);
    }

    /// <summary>Clear all juice state (call when a round resets).</summary>
    public static void Reset()
    {
        HitStopFrames = 0;
        Trauma = 0f;
    }
}
