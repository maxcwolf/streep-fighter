using Godot;

namespace StreepFighter;

public partial class CharacterSelect : Control
{
    private int _p1Selection = 0;
    private int _p2Selection = 1;
    private bool _p1Confirmed;
    private bool _p2Confirmed;

    private Label _p1Label;
    private Label _p2Label;
    private Label _instructionsLabel;
    private HBoxContainer _characterPanels;

    // Character select voice clip keys (matches Assets/Audio/SFX/select_*.mp3)
    private static readonly string[] SelectClipKeys = {
        "select_miranda", "select_julia", "select_thatcher",
        "select_witch", "select_donna", "select_aloysius"
    };

    // Visual panels for each character
    private Panel[] _panels = new Panel[6];
    private Label[] _nameLabels = new Label[6];

    public override void _Ready()
    {
        _p1Label = GetNode<Label>("P1Label");
        _p2Label = GetNode<Label>("P2Label");
        _instructionsLabel = GetNode<Label>("InstructionsLabel");
        _characterPanels = GetNode<HBoxContainer>("CharacterPanels");

        for (int i = 0; i < 6; i++)
        {
            _panels[i] = _characterPanels.GetChild<Panel>(i);
            _nameLabels[i] = _panels[i].GetNode<Label>("NameLabel");
            _nameLabels[i].Text = FighterData.CharacterNames[i];
        }

        UpdateDisplay();

        AudioManager.Instance?.PlaySFX("select_welcome");
    }

    public override void _Input(InputEvent @event)
    {
        if (@event is not InputEventKey and not InputEventJoypadButton and not InputEventJoypadMotion) return;
        if (!@event.IsPressed()) return;

        // P1 controls: A/D to move, F to confirm
        if (!_p1Confirmed)
        {
            if (Input.IsActionJustPressed("p1_left"))
            {
                _p1Selection = (_p1Selection + 5) % 6;
                AudioManager.Instance?.PlaySFX("menu_select");
                UpdateDisplay();
            }
            else if (Input.IsActionJustPressed("p1_right"))
            {
                _p1Selection = (_p1Selection + 1) % 6;
                AudioManager.Instance?.PlaySFX("menu_select");
                UpdateDisplay();
            }
            else if (Input.IsActionJustPressed("p1_punch"))
            {
                AudioManager.Instance?.PlaySFX("menu_confirm");
                PlaySelectClip(_p1Selection);
                _p1Confirmed = true;
                UpdateDisplay();
                CheckBothConfirmed();
            }
        }

        // P2 controls (if PvP): arrows to move, Num1 to confirm
        if (!_p2Confirmed && GameState.Mode == GameMode.PvP)
        {
            if (Input.IsActionJustPressed("p2_left"))
            {
                _p2Selection = (_p2Selection + 5) % 6;
                AudioManager.Instance?.PlaySFX("menu_select");
                UpdateDisplay();
            }
            else if (Input.IsActionJustPressed("p2_right"))
            {
                _p2Selection = (_p2Selection + 1) % 6;
                AudioManager.Instance?.PlaySFX("menu_select");
                UpdateDisplay();
            }
            else if (Input.IsActionJustPressed("p2_punch"))
            {
                AudioManager.Instance?.PlaySFX("menu_confirm");
                PlaySelectClip(_p2Selection);
                _p2Confirmed = true;
                UpdateDisplay();
                CheckBothConfirmed();
            }
        }
        else if (!_p2Confirmed && GameState.Mode == GameMode.VsCPU)
        {
            // CPU auto-picks randomly on P1 confirm
        }
    }

    private void CheckBothConfirmed()
    {
        if (GameState.Mode == GameMode.VsCPU && _p1Confirmed)
        {
            // CPU picks a random different character
            _p2Selection = ((int)(GD.Randi() % 5) + _p1Selection + 1) % 6;
            _p2Confirmed = true;
            UpdateDisplay();
        }

        if (_p1Confirmed && _p2Confirmed)
        {
            GameState.P1CharacterIndex = _p1Selection;
            GameState.P2CharacterIndex = _p2Selection;
            GetTree().ChangeSceneToFile("res://Scenes/UI/StageSelect.tscn");
        }
    }

    private void PlaySelectClip(int characterIndex)
    {
        if (characterIndex >= 0 && characterIndex < SelectClipKeys.Length)
            AudioManager.Instance?.PlaySFX(SelectClipKeys[characterIndex]);
    }

    private void UpdateDisplay()
    {
        _p1Label.Text = $"1P: {FighterData.CharacterNames[_p1Selection]}" + (_p1Confirmed ? " [READY]" : "");

        if (GameState.Mode == GameMode.PvP)
            _p2Label.Text = $"2P: {FighterData.CharacterNames[_p2Selection]}" + (_p2Confirmed ? " [READY]" : "");
        else
            _p2Label.Text = "2P: CPU (auto-pick)";

        string instructions = GameState.Mode == GameMode.PvP
            ? "P1: A/D + F to confirm  |  P2: ←/→ + Num1 to confirm"
            : "P1: A/D + F to confirm";
        _instructionsLabel.Text = instructions;

        // Highlight selected panels with SF2-style colors
        for (int i = 0; i < 6; i++)
        {
            var style = new StyleBoxFlat();
            style.BgColor = new Color(0.12f, 0.08f, 0.16f, 1);
            style.BorderWidthBottom = style.BorderWidthTop = style.BorderWidthLeft = style.BorderWidthRight = 4;
            style.CornerRadiusTopLeft = style.CornerRadiusTopRight = style.CornerRadiusBottomLeft = style.CornerRadiusBottomRight = 2;

            if (i == _p1Selection && i == _p2Selection)
                style.BorderColor = new Color(0.95f, 0.78f, 0.15f, 1); // Gold = both
            else if (i == _p1Selection)
                style.BorderColor = new Color(0.15f, 0.45f, 0.95f, 1); // P1 Blue
            else if (i == _p2Selection && GameState.Mode == GameMode.PvP)
                style.BorderColor = new Color(0.95f, 0.2f, 0.15f, 1); // P2 Red
            else
                style.BorderColor = new Color(0.25f, 0.2f, 0.3f, 1); // Muted purple-gray

            _panels[i].AddThemeStyleboxOverride("panel", style);
        }
    }
}
