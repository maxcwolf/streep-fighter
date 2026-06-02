shader_type canvas_item;

// Posterize a sampled texture into 2-3 luminance bands and remap them onto a
// dark -> (mid) -> light color ramp. Warhol / Lichtenstein pop-art portraits.
// Sample TEXTURE at UV and preserve the source alpha.
//   dark     : color for the darkest band (shadows)
//   light    : color for the brightest band (highlights)
//   mid      : optional middle band color (used when levels >= 3)
//   use_mid  : if false, ramp is a straight dark<->light two-tone
//   levels   : number of posterization bands (2 or 3 typical, default 3)
//   contrast : pushes luminance toward its extremes before banding

uniform vec4 dark : source_color = vec4(0.45, 0.05, 0.08, 1.0);
uniform vec4 light : source_color = vec4(0.96, 0.79, 0.18, 1.0);
uniform vec4 mid : source_color = vec4(0.80, 0.10, 0.13, 1.0);
uniform bool use_mid = true;
uniform float levels : hint_range(2.0, 5.0) = 3.0;
uniform float contrast : hint_range(0.0, 2.0) = 1.0;

void fragment() {
	vec4 src = texture(TEXTURE, UV);

	// Perceptual luminance of the source pixel.
	float lum = dot(src.rgb, vec3(0.299, 0.587, 0.114));

	// Optional contrast curve around mid-gray, then posterize to N bands.
	lum = clamp((lum - 0.5) * contrast + 0.5, 0.0, 1.0);
	float bands = max(floor(levels), 2.0);
	float quant = floor(lum * bands) / (bands - 1.0);
	quant = clamp(quant, 0.0, 1.0);

	// Remap the quantized value onto the color ramp.
	vec3 ramp;
	if (use_mid) {
		// dark (t<=0.5) -> mid (t=0.5) -> light (t>=1.0)
		if (quant < 0.5) {
			ramp = mix(dark.rgb, mid.rgb, quant * 2.0);
		} else {
			ramp = mix(mid.rgb, light.rgb, (quant - 0.5) * 2.0);
		}
	} else {
		ramp = mix(dark.rgb, light.rgb, quant);
	}

	COLOR = vec4(ramp, src.a);
}
