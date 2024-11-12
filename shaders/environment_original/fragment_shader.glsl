#version 130

in vec3 normal_view_space;
in vec3 position_view_space;
in vec3 fragment_texCoord;
out vec4 final_color;

uniform samplerCube sampler_cube;
uniform mat3 VT;

void main(void)
{
    vec3 normal_view_space_normalized = normalize(normal_view_space);
    vec3 reflected = reflect(normalize(-position_view_space), normal_view_space_normalized);

    // Sample color from the cubemap
    vec4 reflected_color = texture(sampler_cube, normalize(VT * reflected));

    // Define the gold color tint
    vec3 gold_color = vec3(1.0, 0.843, 0.0);

    // Mix the reflected color with the gold tint, adjust factor for stronger or weaker tint
    final_color = mix(reflected_color, vec4(gold_color, 1.0), 0.3);
}