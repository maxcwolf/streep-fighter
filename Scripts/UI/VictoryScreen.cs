using Godot;

namespace StreepFighter;

public partial class VictoryScreen : Control
{
    private Label _winnerLabel;
    private Label _characterLabel;
    private Button _playAgainButton;
    private Button _menuButton;

    public override void _Ready()
    {
        _winnerLabel = GetNode<Label>("VBoxContainer/WinnerLabel");
        _characterLabel = GetNode<Label>("VBoxContainer/CharacterLabel");
        _playAgainButton = GetNode<Button>("VBoxContainer/PlayAgainButton");
        _menuButton = GetNode<Button>("VBoxContainer/MenuButton");

        _playAgainButton.Pressed += () =>
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            GameState.Reset();
            GetTree().ChangeSceneToFile("res://Scenes/UI/CharacterSelect.tscn");
        };

        _menuButton.Pressed += () =>
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            GameState.Reset();
            GetTree().ChangeSceneToFile("res://Scenes/UI/TitleScreen.tscn");
        };
    }

    public void ShowWinner(int playerIndex, string characterName)
    {
        string playerStr = playerIndex == 0 ? "PLAYER 1" : "PLAYER 2";
        if (GameState.Mode == GameMode.VsCPU && playerIndex == 1)
            playerStr = "CPU";
        _winnerLabel.Text = $"{playerStr} WINS!";
        _characterLabel.Text = characterName;
        Visible = true;
    }
}
