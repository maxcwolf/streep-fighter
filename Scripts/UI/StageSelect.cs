using Godot;

namespace StreepFighter;

public partial class StageSelect : Control
{
    private int _selection = 0;
    private bool _confirmed;

    private Label _instructionsLabel;
    private HBoxContainer _stagePanels;
    private Panel[] _panels = new Panel[6];
    private Label[] _nameLabels = new Label[6];

    public override void _Ready()
    {
        _instructionsLabel = GetNode<Label>("InstructionsLabel");
        _stagePanels = GetNode<HBoxContainer>("StagePanels");

        for (int i = 0; i < 6; i++)
        {
            _panels[i] = _stagePanels.GetChild<Panel>(i);
            _nameLabels[i] = _panels[i].GetNode<Label>("NameLabel");
            _nameLabels[i].Text = StageData.Stages[i].Name;
        }

        UpdateDisplay();
    }

    public override void _Input(InputEvent @event)
    {
        if (@event is not InputEventKey and not InputEventJoypadButton and not InputEventJoypadMotion) return;
        if (!@event.IsPressed() || _confirmed) return;

        if (Input.IsActionJustPressed("p1_left"))
        {
            _selection = (_selection + 5) % 6;
            AudioManager.Instance?.PlaySFX("menu_select");
            UpdateDisplay();
        }
        else if (Input.IsActionJustPressed("p1_right"))
        {
            _selection = (_selection + 1) % 6;
            AudioManager.Instance?.PlaySFX("menu_select");
            UpdateDisplay();
        }
        else if (Input.IsActionJustPressed("p1_punch"))
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            _confirmed = true;
            GameState.StageIndex = _selection;
            GetTree().ChangeSceneToFile("res://Scenes/Stages/FightStage.tscn");
        }
    }

    private void UpdateDisplay()
    {
        for (int i = 0; i < 6; i++)
        {
            var style = new StyleBoxFlat();
            style.BgColor = new Color(0.12f, 0.08f, 0.16f, 1);
            style.BorderWidthBottom = style.BorderWidthTop = style.BorderWidthLeft = style.BorderWidthRight = 4;
            style.CornerRadiusTopLeft = style.CornerRadiusTopRight = style.CornerRadiusBottomLeft = style.CornerRadiusBottomRight = 2;

            if (i == _selection)
                style.BorderColor = new Color(0.95f, 0.78f, 0.15f, 1);
            else
                style.BorderColor = new Color(0.25f, 0.2f, 0.3f, 1);

            _panels[i].AddThemeStyleboxOverride("panel", style);
        }

        _instructionsLabel.Text = $"A/D to select  |  F to confirm — {StageData.Stages[_selection].Name}";
    }
}
