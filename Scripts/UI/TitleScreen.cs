using Godot;

namespace StreepFighter;

public partial class TitleScreen : Control
{
    private const int LogoY = 12;

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

        _menu = new PixelMenu { Position = new Vector2(PixelUI.W / 2, 158), Visible = false, Active = false };
        AddChild(_menu);
        _menu.Add("VS PLAYER", () => StartGame(GameMode.PvP));
        _menu.Add("VS CPU", () => StartGame(GameMode.VsCPU));

        _hint = PixelUI.Centered(this, "W/S SELECT   F OR ENTER START", 192, 202, "tiny", PixelUI.Grey, 380);
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
        if (_tick == 58)
        {
            _menu.Visible = true;
            _menu.Active = true;
            _hint.Visible = true;
        }
    }

    public override void _Input(InputEvent @event)
    {
        // Any confirm skips the intro animation.
        if (_tick < 58 && @event.IsPressed() && !@event.IsEcho() && @event is InputEventKey or InputEventJoypadButton)
        {
            _tick = 57;
            _logo.Position = new Vector2(_logo.Position.X, LogoY);
            _kombat.Visible = true;
            GetViewport().SetInputAsHandled();
        }
    }

    private void StartGame(GameMode mode)
    {
        _menu.Active = false;
        GameState.Mode = mode;
        GameState.Reset();
        GetTree().ChangeSceneToFile("res://Scenes/UI/CharacterSelect.tscn");
    }
}
