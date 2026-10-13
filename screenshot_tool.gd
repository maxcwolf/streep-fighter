extends Node

# Dev tool: plays through the real menus with synthetic key presses and saves
# native-resolution (384x216) screenshots of each screen and of a fight.
#
#   Godot --path . res://screenshot_tool.tscn -- <out_dir> [p1 0-5] [stage 0-5] [cpu|pvp]
#
# Must run with a window (not --headless) or nothing is rendered.

const KEY := {"left": KEY_A, "right": KEY_D, "up": KEY_W, "down": KEY_S,
	"punch": KEY_F, "kick": KEY_G, "block": KEY_H, "special": KEY_T,
	"p2_punch": KEY_KP_1, "p2_right": KEY_RIGHT}

var out := "user://shots"
var pick := 0
var stage := 0
var cpu := true


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0: out = args[0]
	if args.size() > 1: pick = int(args[1])
	if args.size() > 2: stage = int(args[2])
	if args.size() > 3: cpu = args[3] != "pvp"
	DirAccess.make_dir_recursive_absolute(out)
	await get_tree().process_frame
	# Detach from "current scene" so scene changes made by the game don't free us.
	var root := get_tree().root
	get_tree().current_scene = null
	root.remove_child(self)
	root.add_child(self)
	get_tree().change_scene_to_file("res://Scenes/UI/TitleScreen.tscn")
	await run()
	get_tree().quit()


func frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func key(code: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = code
	ev.keycode = code
	ev.pressed = pressed
	Input.parse_input_event(ev)


func tap(action: String, hold := 3) -> void:
	key(KEY[action], true)
	await frames(hold)
	key(KEY[action], false)
	await frames(2)


func shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, name])
	print("shot ", name)


func run() -> void:
	await frames(90)
	await shot("01_title")
	if cpu:
		await tap("down")
	await tap("punch")
	await frames(30)
	for i in pick % 3:
		await tap("right")
	if pick >= 3:
		await tap("down")
	await frames(8)
	await shot("02_select")
	await tap("punch")
	if not cpu:
		await tap("p2_right")
		await tap("p2_punch")
	await frames(20)
	await shot("03_select_ready")
	await frames(60)
	for i in stage % 3:
		await tap("right")
	if stage >= 3:
		await tap("down")
	await frames(8)
	await shot("04_stage")
	await tap("punch")
	await frames(40)
	await shot("05_versus")
	await frames(120)
	await shot("06_round")
	await frames(80)
	await shot("07_fight")
	await frames(40)
	# --- a scripted flurry from player 1
	key(KEY["right"], true)
	await frames(26)
	await shot("08_walk")
	await frames(14)
	key(KEY["right"], false)
	key(KEY["punch"], true)
	await frames(7)
	await shot("09_punch")
	key(KEY["punch"], false)
	await frames(20)
	key(KEY["kick"], true)
	await frames(9)
	await shot("10_kick")
	key(KEY["kick"], false)
	await frames(26)
	key(KEY["down"], true)
	await frames(6)
	key(KEY["kick"], true)
	await frames(8)
	await shot("11_sweep")
	key(KEY["kick"], false)
	key(KEY["down"], false)
	await frames(40)
	key(KEY["up"], true)
	key(KEY["right"], true)
	await frames(8)
	key(KEY["up"], false)
	await frames(12)
	await shot("12_jump")
	key(KEY["kick"], true)
	await frames(8)
	await shot("13_jumpkick")
	key(KEY["kick"], false)
	key(KEY["right"], false)
	await frames(40)
	key(KEY["special"], true)
	await frames(3)
	key(KEY["special"], false)
	for i in 5:
		await frames(6)
		await shot("14_special_%d" % i)
	await frames(30)
	key(KEY["block"], true)
	await frames(30)
	await shot("15_block")
	key(KEY["block"], false)
	key(KEY_ESCAPE, true)
	await frames(3)
	key(KEY_ESCAPE, false)
	await frames(6)
	await shot("15_pause")
	key(KEY_ESCAPE, true)
	await frames(3)
	key(KEY_ESCAPE, false)
	await frames(6)
	if cpu:
		# let the CPU beat on an idle player 1 to see reactions and a K.O.
		for i in 14:
			await frames(45)
			await shot("16_free_%02d" % i)
		return
	# two-player: player 2 stands still while player 1 runs through everything
	var moves := ["punch", "kick", "special", "kick", "punch", "special"]
	for i in 62:
		key(KEY["right"], true)
		await frames(24)
		key(KEY["right"], false)
		key(KEY[moves[i % moves.size()]], true)
		await frames(3)
		key(KEY[moves[i % moves.size()]], false)
		await frames(9)
		await shot("17_spam_%02d" % i)
		await frames(40)
		if i % 3 == 2:
			await shot("18_after_%02d" % i)
