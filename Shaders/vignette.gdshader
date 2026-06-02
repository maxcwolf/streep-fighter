shader_type canvas_item;

// Soft darkened edges for cinematic / theatrical framing.
//   amount   : strength of the darkening at the corners (0 = off, 1 = strong)
//   softness : how far the falloff reaches inward from the edge
//   tint     : the color the edges fade toward (usually near-black Night)
// Designed for a full-screen ColorRect over a stage; samples its own TEXTURE
// so it also works as a tint-overlay on a Polygon2D / TextureRect. Keeps alpha.

uniform float amount : hint_range(0.0, 1.0) = 0.5;
uniform float softness : hint_range(0.05, 1.5) = 0.6;
uniform vec4 tint : source_color = vec4(0.06, 0.04, 0.10, 1.0);

void fragment() {
	vec4 src = texture(TEXTURE, UV);

	// Distance from screen center, normalized so corners ~= 1.
	vec2 d = UV - vec2(0.5);
	float dist = length(d) * 1.41421356; // * sqrt(2) so corners reach ~1.0

	// Smooth falloff: bright center -> dark edges.
	float edge = smoothstep(1.0 - softness, 1.0, dist);
	float darken = edge * amount;

	vec3 col = mix(src.rgb, tint.rgb, darken);
	COLOR = vec4(col, src.a);
}
