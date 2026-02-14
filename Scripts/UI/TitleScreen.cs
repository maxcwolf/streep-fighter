using Godot;

namespace StreepFighter;

public partial class TitleScreen : Control
{
    private Button _pvpButton;
    private Button _cpuButton;

    public override void _Ready()
    {
        _pvpButton = GetNode<Button>("VBoxContainer/PvPButton");
        _cpuButton = GetNode<Button>("VBoxContainer/CpuButton");

        AudioManager.Instance?.PlaySFX("title_intro");

        _pvpButton.Pressed += () =>
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            GameState.Mode = GameMode.PvP;
            GameState.Reset();
            GetTree().ChangeSceneToFile("res://Scenes/UI/CharacterSelect.tscn");
        };

        _cpuButton.Pressed += () =>
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            GameState.Mode = GameMode.VsCPU;
            GameState.Reset();
            GetTree().ChangeSceneToFile("res://Scenes/UI/CharacterSelect.tscn");
        };
    }
}
