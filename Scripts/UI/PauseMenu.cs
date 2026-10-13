using Godot;

namespace StreepFighter;

public partial class PauseMenu : Control
{
    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always;
        PixelUI.Fill(this);
        Visible = false;

        PixelUI.Box(this, 0, 0, PixelUI.W, PixelUI.H, new Color(PixelUI.Ink, 0.7f));
        PixelUI.Box(this, 112, 62, 160, 92, PixelUI.White);
        PixelUI.Box(this, 113, 63, 158, 90, PixelUI.Ink);
        PixelUI.Centered(this, "PAUSED", 192, 72, "big");

        var menu = new PixelMenu { Position = new Vector2(PixelUI.W / 2, 108) };
        AddChild(menu);
        menu.Add("RESUME", Resume);
        menu.Add("QUIT TO TITLE", QuitToTitle);
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event.IsActionPressed("ui_cancel"))
        {
            if (Visible)
                Resume();
            else
                Pause();
            GetViewport().SetInputAsHandled();
        }
    }

    private void Pause()
    {
        AudioManager.Instance?.PlaySFX("pause");
        Visible = true;
        GetTree().Paused = true;
    }

    private void Resume()
    {
        Visible = false;
        GetTree().Paused = false;
    }

    private void QuitToTitle()
    {
        Visible = false;
        GetTree().Paused = false;
        GameState.Reset();
        GetTree().ChangeSceneToFile("res://Scenes/UI/TitleScreen.tscn");
    }
}
