#version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec3 normal_view_space;     // the normal in view coordinates to this fragment
in vec2 fragment_texCoord;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;

//=== constants
const int MAX_LIGHTS = 8;  // maximum number of lights

//=== uniforms
uniform int has_texture;
uniform sampler2D textureObject;  // texture object

// material uniforms
uniform vec3 Ka;       // ambient reflection properties of the material
uniform vec3 Kd;       // diffuse reflection properties of the material
uniform vec3 Ks;       // specular properties of the material
uniform float Ns;      // specular exponent

// light source arrays for multiple lights
uniform vec3 light_positions[MAX_LIGHTS]; // light positions in view space
uniform vec3 Ia[MAX_LIGHTS];              // ambient light properties for each light
uniform vec3 Id[MAX_LIGHTS];              // diffuse properties of each light source
uniform vec3 Is[MAX_LIGHTS];              // specular properties of each light source
uniform int num_lights;                   // number of active lights
uniform float alpha;

///=== main shader code
void main() {
    vec3 camera_direction = -normalize(position_view_space);
    vec3 normal = normalize(normal_view_space);

    // Initialize the total ambient, diffuse, and specular components
    vec4 total_ambient = vec4(0.0);
    vec4 total_diffuse = vec4(0.0);
    vec4 total_specular = vec4(0.0);

    for (int i = 0; i < num_lights; ++i) {
        vec3 light_direction = normalize(light_positions[i] - position_view_space);

        // Calculate ambient contribution
        vec4 ambient = vec4(Ia[i] * Ka, alpha);
        total_ambient += ambient;

        // Calculate diffuse contribution
        float diff = max(0.0, dot(light_direction, normal));
        vec4 diffuse = vec4(Id[i] * Kd * diff, alpha);
        total_diffuse += diffuse;

        // Calculate specular contribution
        vec3 reflect_dir = reflect(-light_direction, normal);
        float spec = pow(max(0.0, dot(reflect_dir, camera_direction)), Ns);
        vec4 specular = vec4(Is[i] * Ks * spec, alpha);
        total_specular += specular;

        // Calculate attenuation
        float dist = length(light_positions[i] - position_view_space);
        float attenuation = min(1.0 / (dist * dist * 0.005 + dist * 0.05), 1.0);
        
        // Apply attenuation to diffuse and specular components for this light
        total_diffuse *= attenuation;
        total_specular *= attenuation;
    }

    // Sample from the texture map if present
    vec4 texval = vec4(1.0f);
    if (has_texture == 1) {
        texval = texture2D(textureObject, fragment_texCoord);
    }

    // Combine the ambient, diffuse, and specular components
    final_color = texval * total_ambient + texval * total_diffuse + total_specular;
}
