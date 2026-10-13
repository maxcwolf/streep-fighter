using System;
using System.Collections.Generic;
using Godot;

namespace StreepFighter;

/// <summary>
/// A vertical arcade menu: centred bitmap-font entries with a ">" cursor.
/// Up/down with W/S or the arrows, confirm with F / Numpad 1 / Enter, or click.
/// </summary>
public partial class PixelMenu : Control
{
    private const int RowHeight = 14;

    private readonly List<(Label Label, Action Do)> _items = new();
    private Label _cursor;
    private int _index;
    private int _blink;

    /// <summary>Ignore input while false (e.g. during a screen transition).</summary>
    public bool Active { get; set; } = true;

    public PixelMenu()
    {
        MouseFilter = MouseFilterEnum.Ignore;
    }

    public PixelMenu Add(string text, Action action)
    {
        int row = _items.Count;
        var label = PixelUI.Centered(this, text, 0, row * RowHeight);
        label.MouseFilter = MouseFilterEnum.Stop;
        label.MouseEntered += () => Select(row, false);
        label.GuiInput += e =>
        {
            if (Active && e is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
                Activate();
        };
        _items.Add((label, action));
        _cursor ??= PixelUI.Text(this, ">", 0, 0, "bold", PixelUI.Red);
        Select(_index, false);
        return this;
    }

    private void Select(int index, bool sound = true)
    {
        if (_items.Count == 0) return;
        if (sound && index != _index) AudioManager.Instance?.PlaySFX("menu_select");
        _index = (index + _items.Count) % _items.Count;
        for (int i = 0; i < _items.Count; i++)
            PixelUI.Tint(_items[i].Label, i == _index ? PixelUI.Yellow : PixelUI.White);

        var label = _items[_index].Label;
        float textWidth = label.LabelSettings.Font.GetStringSize(label.Text, HorizontalAlignment.Left, -1,
            label.LabelSettings.FontSize).X;
        _cursor.Position = new Vector2(Mathf.Round(-textWidth / 2f) - 12, _index * RowHeight);
    }

    private void Activate()
    {
        if (_items.Count == 0) return;
        AudioManager.Instance?.PlaySFX("menu_confirm");
        _items[_index].Do();
    }

    public override void _Process(double delta)
    {
        if (_cursor != null)
            _cursor.Visible = ++_blink / 16 % 2 == 0;
    }

    public override void _Input(InputEvent @event)
    {
        if (!Active || !IsVisibleInTree() || @event.IsEcho()) return;

        bool up = @event.IsActionPressed("ui_up") || @event.IsActionPressed("p1_jump");
        bool down = @event.IsActionPressed("ui_down") || @event.IsActionPressed("p1_crouch");
        bool accept = @event.IsActionPressed("ui_accept") || @event.IsActionPressed("p1_punch")
                      || @event.IsActionPressed("p2_punch");
        if (!up && !down && !accept) return;

        // Mark handled first: activating an entry may change scene and free this menu.
        GetViewport().SetInputAsHandled();
        if (up) Select(_index - 1);
        else if (down) Select(_index + 1);
        else Activate();
    }
}
