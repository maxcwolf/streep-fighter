shader_type canvas_item;

uniform float pixel_size : hint_range(1.0, 16.0) = 4.0;

void fragment() {
	vec2 tex_size = 1.0 / TEXTURE_PIXEL_SIZE;
	vec2 snapped_uv = floor(UV * tex_size / pixel_size) * pixel_size / tex_size;
	COLOR = texture(TEXTURE, snapped_uv);
}
