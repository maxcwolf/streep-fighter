using Godot;

namespace StreepFighter;

public partial class StageSelect : Control
{
    private const int Columns = 3;
    private const int GridX = 40, GridY = 36, CellW = 104, CellH = 66;
    private const int ThumbW = 96, ThumbH = 54;
    private const int VsTicks = 120;

    private int _selection = 0;
    private bool _confirmed;
    private int _vsTicks = -1;

    private Control _picker;
    private Control _versusCard;
    private Control _cursor;
    private Label _nameLabel, _locationLabel;

    public override void _Ready()
    {
        _selection = Mathf.Clamp(GameState.StageIndex, 0, StageData.Stages.Length - 1);

        PixelUI.Fill(this);
        PixelUI.Image(this, "res://Assets/UI/select_bg.png", 0, 0);

        _picker = new Control();
        PixelUI.Fill(_picker);
        AddChild(_picker);

        PixelUI.Centered(_picker, "STAGE SELECT", 192, 6, "big");
        for (int i = 0; i < StageData.Stages.Length; i++)
        {
            var (x, y) = Cell(i);
            PixelUI.Box(_picker, x - 2, y - 2, ThumbW + 4, ThumbH + 4, PixelUI.Ink);
            PixelUI.Image(_picker, StageData.Stages[i].ThumbPath, x, y);
        }

        _cursor = new Control { MouseFilter = MouseFilterEnum.Ignore };
        _picker.AddChild(_cursor);
        PixelUI.Frame(_cursor, -4, -4, ThumbW + 8, ThumbH + 8, PixelUI.White, 1);
        PixelUI.Frame(_cursor, -3, -3, ThumbW + 6, ThumbH + 6, PixelUI.Yellow, 2);

        _nameLabel = PixelUI.Centered(_picker, "", 192, 172, "bold", PixelUI.Yellow, 380);
        _locationLabel = PixelUI.Centered(_picker, "", 192, 185, "pixel", PixelUI.White, 380);
        PixelUI.Centered(_picker, "A/D/W/S SELECT   F CONFIRM   ESC BACK", 192, 204, "tiny", PixelUI.Grey, 380);

        UpdateDisplay();
    }

    private static (int X, int Y) Cell(int index) =>
        (GridX + index % Columns * CellW, GridY + index / Columns * CellH);

    public override void _Input(InputEvent @event)
    {
        if (@event is not InputEventKey and not InputEventJoypadButton and not InputEventJoypadMotion) return;
        if (!@event.IsPressed() || @event.IsEcho()) return;

        if (@event.IsActionPressed("ui_cancel"))
        {
            GetViewport().SetInputAsHandled();
            GoBack();
            return;
        }
        if (_confirmed) return;

        int count = StageData.Stages.Length;
        int row = _selection / Columns, col = _selection % Columns;
        int next = _selection;

        if (Input.IsActionJustPressed("p1_left"))
            next = row * Columns + (col + Columns - 1) % Columns;
        else if (Input.IsActionJustPressed("p1_right"))
            next = row * Columns + (col + 1) % Columns;
        else if (Input.IsActionJustPressed("p1_jump") || Input.IsActionJustPressed("p1_crouch"))
            next = (_selection + Columns) % count;
        else if (Input.IsActionJustPressed("p1_punch"))
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            _confirmed = true;
            GameState.StageIndex = _selection;
            ShowVersus();
            return;
        }

        if (next != _selection)
        {
            _selection = next;
            AudioManager.Instance?.PlaySFX("menu_select");
            UpdateDisplay();
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_vsTicks > 0 && --_vsTicks == 0)
            GetTree().ChangeSceneToFile("res://Scenes/Stages/FightStage.tscn");
    }

    /// <summary>Esc: from the VS card back to the stage grid; from the grid back to player select.</summary>
    private void GoBack()
    {
        AudioManager.Instance?.PlaySFX("menu_select");
        if (_confirmed)
        {
            _confirmed = false;
            _vsTicks = -1;
            _versusCard?.QueueFree();
            _versusCard = null;
            _picker.Visible = true;
            return;
        }
        GetTree().ChangeSceneToFile("res://Scenes/UI/CharacterSelect.tscn");
    }

    private void UpdateDisplay()
    {
        var (x, y) = Cell(_selection);
        _cursor.Position = new Vector2(x, y);
        var stage = StageData.Stages[_selection];
        _nameLabel.Text = stage.Name.ToUpper();
        _locationLabel.Text = stage.DisplayLabel;
    }

    /// <summary>The "VS" card shown between stage select and the fight.</summary>
    private void ShowVersus()
    {
        _picker.Visible = false;
        _vsTicks = VsTicks;

        var p1 = FighterData.GetByIndex(GameState.P1CharacterIndex);
        var p2 = FighterData.GetByIndex(GameState.P2CharacterIndex);
        var card = new Control();
        PixelUI.Fill(card);
        AddChild(card);
        _versusCard = card;

        for (int p = 0; p < 2; p++)
        {
            var stats = p == 0 ? p1 : p2;
            int x = p == 0 ? 44 : PixelUI.W - 44 - 80;
            PixelUI.Box(card, x - 3, 39, 86, 106, p == 0 ? PixelUI.P1Blue : PixelUI.P2Red);
            PixelUI.Box(card, x - 1, 41, 82, 102, PixelUI.Ink);
            PixelUI.Image(card, stats.BigPortraitPath, x, 42).FlipH = p == 1;
            PixelUI.Centered(card, stats.ShortName, x + 40, 152, "bold", PixelUI.Yellow, 140);
            PixelUI.Centered(card, stats.Film, x + 40, 164, "tiny", PixelUI.White, 160);
        }

        var vs = PixelUI.Image(card, "res://Assets/UI/announce_vs.png", 0, 0);
        vs.Position = new Vector2(Mathf.Round((PixelUI.W - vs.Size.X) / 2f), 70);
        PixelUI.Centered(card, StageData.GetByIndex(GameState.StageIndex).DisplayLabel, 192, 190, "pixel",
            PixelUI.White, 380);
    }
}
