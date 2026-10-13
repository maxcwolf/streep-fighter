using Godot;

namespace StreepFighter;

public partial class VictoryScreen : Control
{
    private TextureRect _portrait;
    private Label _winnerLabel, _characterLabel, _quoteLabel;
    private PixelMenu _menu;

    public override void _Ready()
    {
        PixelUI.Fill(this);
        Visible = false;

        PixelUI.Box(this, 0, 0, PixelUI.W, PixelUI.H, new Color(PixelUI.Ink, 0.78f));
        PixelUI.Box(this, 38, 44, 84, 104, PixelUI.White);
        PixelUI.Box(this, 39, 45, 82, 102, PixelUI.Ink);
        _portrait = PixelUI.Image(this, FighterData.MirandaPriestly.BigPortraitPath, 40, 46);

        _winnerLabel = PixelUI.Text(this, "", 136, 46, "big");
        _characterLabel = PixelUI.Text(this, "", 136, 68, "bold", PixelUI.Yellow);
        _quoteLabel = PixelUI.Text(this, "", 136, 84, "pixel", PixelUI.White, HorizontalAlignment.Left, 232);
        _quoteLabel.AutowrapMode = TextServer.AutowrapMode.Word;
        _quoteLabel.Size = new Vector2(232, 40);

        _menu = new PixelMenu { Position = new Vector2(252, 158), Active = false };
        AddChild(_menu);
        _menu.Add("PLAY AGAIN", () => Leave("res://Scenes/UI/CharacterSelect.tscn"));
        _menu.Add("MAIN MENU", () => Leave("res://Scenes/UI/TitleScreen.tscn"));
    }

    private void Leave(string scene)
    {
        _menu.Active = false;
        GameState.Reset();
        GetTree().ChangeSceneToFile(scene);
    }

    public void ShowWinner(int playerIndex, FighterStats stats)
    {
        string playerStr = playerIndex == 0 ? "1P" : "2P";
        if (GameState.Mode == GameMode.VsCPU && playerIndex == 1)
            playerStr = "CPU";
        _winnerLabel.Text = $"{playerStr} WINS!";
        _characterLabel.Text = stats.Name.ToUpper();
        _quoteLabel.Text = $"\"{stats.WinQuote}\"";
        _portrait.Texture = PixelUI.Tex(stats.BigPortraitPath);
        Visible = true;
        _menu.Arm(40); // don't let a button still being mashed from the fight pick an option
    }
}
