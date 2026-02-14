using Godot;

namespace StreepFighter;

public partial class PauseMenu : Control
{
    private Button _resumeButton;
    private Button _quitButton;

    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always;
        Visible = false;

        _resumeButton = GetNode<Button>("VBoxContainer/ResumeButton");
        _quitButton = GetNode<Button>("VBoxContainer/QuitButton");

        _resumeButton.Pressed += Resume;
        _quitButton.Pressed += QuitToTitle;
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
        AudioManager.Instance?.PlaySFX("menu_confirm");
        Visible = false;
        GetTree().Paused = false;
    }

    private void QuitToTitle()
    {
        AudioManager.Instance?.PlaySFX("menu_confirm");
        Visible = false;
        GetTree().Paused = false;
        GameState.Reset();
        GetTree().ChangeSceneToFile("res://Scenes/UI/TitleScreen.tscn");
    }
}
