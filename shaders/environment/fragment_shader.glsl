#version 130

flat in vec3 normal_view_space;
flat in vec3 position_view_space;
in vec3 fragment_texCoord;
out vec4 final_color;

uniform samplerCube sampler_cube;
uniform mat3 VT;

void main(void)
{
    vec3 reflected = reflect(normalize(-position_view_space), normalize(normal_view_space));

    // Sample color from the cubemap and apply a gold tint
    vec4 reflected_color = texture(sampler_cube, normalize(VT * reflected));
    vec3 gold_color = vec3(1.0, 0.843, 0.0);
    final_color = mix(reflected_color, vec4(gold_color, 1.0), 0.3);
}