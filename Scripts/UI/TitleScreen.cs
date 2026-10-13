using Godot;

namespace StreepFighter;

public partial class TitleScreen : Control
{
    private const int LogoY = 12;
    private const int IntroTicks = 58;

    private TextureRect _logo, _kombat;
    private PixelMenu _menu;
    private Label _hint;
    private int _tick;

    public override void _Ready()
    {
        PixelUI.Fill(this);
        PixelUI.Image(this, "res://Assets/UI/title_bg.png", 0, 0);

        _logo = PixelUI.Image(this, "res://Assets/UI/logo.png", 0, 0);
        _logo.Position = new Vector2(Mathf.Round((PixelUI.W - _logo.Size.X) / 2f), -110);
        _kombat = PixelUI.Image(this, "res://Assets/UI/kombat.png", 0, 114);
        _kombat.Position = new Vector2(Mathf.Round((PixelUI.W - _kombat.Size.X) / 2f), 114);
        _kombat.Visible = false;

        _menu = new PixelMenu { Position = new Vector2(PixelUI.W / 2, 156), Visible = false, Active = false };
        AddChild(_menu);
        _menu.Add("VS PLAYER", () => StartGame(GameMode.PvP));
        _menu.Add("VS CPU", () => StartGame(GameMode.VsCPU));
        _menu.AddStars("CPU LEVEL", Settings.MaxCpuLevel, () => Settings.CpuLevel, v => Settings.CpuLevel = v);

        _hint = PixelUI.Centered(this, "W/S SELECT   A/D CPU LEVEL   F OR ENTER START", 192, 204, "tiny",
            PixelUI.Grey, 380);
        _hint.Visible = false;

        AudioManager.Instance?.PlaySFX("title_intro");
    }

    public override void _PhysicsProcess(double delta)
    {
        _tick++;
        // Logo drops in and bounces once; the banner and menu follow.
        if (_tick <= 22)
        {
            float t = _tick / 22f;
            _logo.Position = new Vector2(_logo.Position.X, Mathf.Round(Mathf.Lerp(-110, LogoY, t * t)));
        }
        else if (_tick <= 34)
        {
            float t = (_tick - 22) / 12f;
            _logo.Position = new Vector2(_logo.Position.X, LogoY - Mathf.Round(Mathf.Sin(t * Mathf.Pi) * 5));
        }

        if (_tick == 40) _kombat.Visible = true;
        if (_tick == IntroTicks) ShowMenu();
    }

    private void ShowMenu()
    {
        _tick = Mathf.Max(_tick, IntroTicks);
        _logo.Position = new Vector2(_logo.Position.X, LogoY);
        _kombat.Visible = true;
        _menu.Visible = true;
        _hint.Visible = true;
        _menu.Arm();
    }

    public override void _Input(InputEvent @event)
    {
        // Any press cuts the intro short. The press is NOT swallowed: the menu is
        // live from this frame, so an impatient "down" still moves the cursor (a
        // confirm only skips - the menu waits for it to be released first).
        if (_tick < IntroTicks && @event.IsPressed() && !@event.IsEcho()
            && @event is InputEventKey or InputEventJoypadButton or InputEventMouseButton)
            ShowMenu();
    }

    private void StartGame(GameMode mode)
    {
        _menu.Active = false;
        GameState.Mode = mode;
        GameState.Reset();
        GetTree().ChangeSceneToFile("res://Scenes/UI/CharacterSelect.tscn");
    }
}
