shader_type canvas_item;

// Ben-Day dot / halftone overlay. Designed for a ColorRect or Polygon2D.
// Produces classic comic dots that stay screen-stable and crisp regardless of
// the node's size, because the dot grid is anchored to screen pixels.
//   dot_size : grid cell size in screen pixels (~8 reads like print halftone)
//   angle    : rotation of the dot grid in radians (~0.4 = the classic tilt)
//   tint     : color of the dots
//   bg       : color behind the dots
//   softness : edge feather of each dot (0 = hard ink, higher = airbrushed)
//   density  : dot fill amount (0 = no dots, 1 = dots touch). 0.5 = even ink.

uniform float dot_size : hint_range(2.0, 64.0) = 8.0;
uniform float angle = 0.4;
uniform vec4 tint : source_color = vec4(0.09, 0.07, 0.12, 1.0);
uniform vec4 bg : source_color = vec4(0.97, 0.93, 0.82, 1.0);
uniform float softness : hint_range(0.0, 1.0) = 0.35;
uniform float density : hint_range(0.0, 1.0) = 0.5;

void fragment() {
	// Screen-pixel coordinates so the dot grid never stretches with the node.
	// SCREEN_PIXEL_SIZE = 1.0 / viewport_size, so this recovers pixels.
	vec2 screen_px = SCREEN_UV / SCREEN_PIXEL_SIZE;

	// Rotate the sampling space so the dot lattice sits at `angle`.
	float ca = cos(angle);
	float sa = sin(angle);
	vec2 rotated = vec2(
		screen_px.x * ca - screen_px.y * sa,
		screen_px.x * sa + screen_px.y * ca
	);

	// Position within the current dot cell, centered on the cell.
	float cell = max(dot_size, 1.0);
	vec2 cell_uv = fract(rotated / cell) - 0.5;
	float dist = length(cell_uv);

	// Dot radius driven by density; softness feathers the rim.
	float radius = clamp(density, 0.0, 1.0) * 0.7071; // 0.7071 = half-diagonal
	float feather = max(softness * 0.5, 0.001);
	float dot = 1.0 - smoothstep(radius - feather, radius + feather, dist);

	COLOR = mix(bg, tint, dot);
}
