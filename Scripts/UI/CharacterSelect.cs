using Godot;

namespace StreepFighter;

public partial class CharacterSelect : Control
{
    private const int Columns = 3;
    private const int GridX = 126, GridY = 104, CellW = 44, CellH = 54;
    private const int PortraitW = 40, PortraitH = 50;
    private const int BigW = 80, BigH = 100, BigY = 38;

    private int _p1Selection = 0;
    private int _p2Selection = 1;
    private bool _p1Confirmed;
    private bool _p2Confirmed;
    private int _leaveTicks = -1;
    private int _clock;

    // Character select voice clip keys (matches Assets/Audio/SFX/select_*.mp3)
    private static readonly string[] SelectClipKeys = {
        "select_miranda", "select_julia", "select_thatcher",
        "select_witch", "select_donna", "select_aloysius"
    };

    private readonly Control[] _cursor = new Control[2];
    private readonly Label[] _cursorTag = new Label[2];
    private readonly TextureRect[] _big = new TextureRect[2];
    private readonly Label[] _name = new Label[2];
    private readonly Label[] _film = new Label[2];
    private readonly Label[] _special = new Label[2];
    private readonly Label[] _ready = new Label[2];
    private Label _cpuLabel;

    public override void _Ready()
    {
        PixelUI.Fill(this);
        PixelUI.Image(this, "res://Assets/UI/select_bg.png", 0, 0);
        PixelUI.Centered(this, "PLAYER SELECT", 192, 6, "big");

        string hint = GameState.Mode == GameMode.PvP
            ? "1P: A/D/W/S + F        2P: ARROWS + NUM 1"
            : "1P: A/D/W/S + F";
        PixelUI.Centered(this, hint, 192, 28, "tiny", PixelUI.Grey, 380);

        for (int i = 0; i < FighterData.Count; i++)
        {
            var (x, y) = Cell(i);
            PixelUI.Box(this, x - 2, y - 2, PortraitW + 4, PortraitH + 4, PixelUI.Ink);
            PixelUI.Image(this, FighterData.GetByIndex(i).PortraitPath, x, y);
        }

        for (int p = 0; p < 2; p++)
        {
            Color col = p == 0 ? PixelUI.P1Blue : PixelUI.P2Red;
            int bx = p == 0 ? 10 : PixelUI.W - 10 - BigW;
            PixelUI.Box(this, bx - 2, BigY - 2, BigW + 4, BigH + 4, PixelUI.White);
            PixelUI.Box(this, bx - 1, BigY - 1, BigW + 2, BigH + 2, PixelUI.Ink);
            _big[p] = PixelUI.Image(this, FighterData.GetByIndex(p).BigPortraitPath, bx, BigY);
            _big[p].FlipH = p == 1;
            int cx = bx + BigW / 2;
            _name[p] = PixelUI.Centered(this, "", cx, BigY + BigH + 6, "bold", PixelUI.Yellow, 110);
            _film[p] = PixelUI.Centered(this, "", cx, BigY + BigH + 18, "tiny", PixelUI.White, 110);
            _special[p] = PixelUI.Centered(this, "", cx, BigY + BigH + 26, "tiny", PixelUI.Cyan, 110);
            _ready[p] = PixelUI.Centered(this, "READY!", cx, BigY + BigH + 38, "bold", PixelUI.Red, 110);

            // Cursor: a 2px frame in the player's colour with a tag riding on top.
            _cursor[p] = new Control { MouseFilter = MouseFilterEnum.Ignore };
            AddChild(_cursor[p]);
            PixelUI.Frame(_cursor[p], -4, -4, PortraitW + 8, PortraitH + 8, PixelUI.White, 1);
            PixelUI.Frame(_cursor[p], -3, -3, PortraitW + 6, PortraitH + 6, col, 2);
            int tagX = p == 0 ? -4 : PortraitW - 13;
            PixelUI.Box(_cursor[p], tagX, -13, 17, 10, col);
            _cursorTag[p] = PixelUI.Text(_cursor[p], p == 0 ? "1P" : "2P", tagX + 1, -12);
        }

        _cpuLabel = PixelUI.Centered(this, "CPU", PixelUI.W - 10 - BigW / 2, BigY + BigH / 2 - 8, "big");

        UpdateDisplay();

        AudioManager.Instance?.PlaySFX("select_welcome");
    }

    private static (int X, int Y) Cell(int index) =>
        (GridX + index % Columns * CellW, GridY + index / Columns * CellH);

    public override void _Input(InputEvent @event)
    {
        if (@event is not InputEventKey and not InputEventJoypadButton and not InputEventJoypadMotion) return;
        if (!@event.IsPressed() || @event.IsEcho() || _leaveTicks >= 0) return;

        if (!_p1Confirmed)
            HandlePlayer("p1", ref _p1Selection, ref _p1Confirmed);

        if (!_p2Confirmed && GameState.Mode == GameMode.PvP)
            HandlePlayer("p2", ref _p2Selection, ref _p2Confirmed);
    }

    private void HandlePlayer(string prefix, ref int selection, ref bool confirmed)
    {
        int count = FighterData.Count;
        int row = selection / Columns, col = selection % Columns;
        int next = selection;

        if (Input.IsActionJustPressed(prefix + "_left"))
            next = row * Columns + (col + Columns - 1) % Columns;
        else if (Input.IsActionJustPressed(prefix + "_right"))
            next = row * Columns + (col + 1) % Columns;
        else if (Input.IsActionJustPressed(prefix + "_jump") || Input.IsActionJustPressed(prefix + "_crouch"))
            next = (selection + Columns) % count;
        else if (Input.IsActionJustPressed(prefix + "_punch"))
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            PlaySelectClip(selection);
            confirmed = true;
            UpdateDisplay();
            CheckBothConfirmed();
            return;
        }

        if (next != selection)
        {
            selection = next;
            AudioManager.Instance?.PlaySFX("menu_select");
            UpdateDisplay();
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
            _leaveTicks = 50; // let "READY!" land before moving on
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        _clock++;
        bool blink = _clock / 6 % 2 == 0;
        _cursor[0].Visible = _p1Confirmed || blink;
        _cursor[1].Visible = GameState.Mode == GameMode.PvP ? (_p2Confirmed || !blink) : _p2Confirmed;
        _ready[0].Visible = _p1Confirmed && _clock / 8 % 2 == 0;
        _ready[1].Visible = _p2Confirmed && _clock / 8 % 2 == 0;

        if (_leaveTicks > 0 && --_leaveTicks == 0)
            GetTree().ChangeSceneToFile("res://Scenes/UI/StageSelect.tscn");
    }

    private void PlaySelectClip(int characterIndex)
    {
        if (characterIndex >= 0 && characterIndex < SelectClipKeys.Length)
            AudioManager.Instance?.PlaySFX(SelectClipKeys[characterIndex]);
    }

    private void UpdateDisplay()
    {
        ShowPick(0, _p1Selection, true);
        bool showP2 = GameState.Mode == GameMode.PvP || _p2Confirmed;
        ShowPick(1, _p2Selection, showP2);
        _cpuLabel.Visible = !showP2;
    }

    private void ShowPick(int p, int selection, bool visible)
    {
        var stats = FighterData.GetByIndex(selection);
        var (x, y) = Cell(selection);
        _cursor[p].Position = new Vector2(x, y);
        _big[p].Visible = visible;
        _big[p].Texture = PixelUI.Tex(stats.BigPortraitPath);
        _name[p].Text = visible ? stats.ShortName : "";
        _film[p].Text = visible ? stats.Film : "";
        _special[p].Text = visible ? stats.SpecialName : "";
    }
}
