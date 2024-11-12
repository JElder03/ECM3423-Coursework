# version 130

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment color
in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec2 fragment_texCoord;

//=== 'out' attributes are the output image, usually only one for the color of each pixel
out vec4 final_color;

//=== constants
const int MAX_LIGHTS = 8;  // maximum number of lights

// Uniforms
uniform int has_texture;
uniform sampler2D textureObject; // texture sampler

// Material properties
uniform vec3 Ka; // ambient reflectivity
uniform vec3 Kd; // diffuse reflectivity
uniform vec3 Ks; // specular reflectivity
uniform float Ns; // specular exponent

// Light properties
uniform int num_lights; // number of active lights
uniform vec3 light_positions[MAX_LIGHTS]; // positions of lights in view space
uniform vec3 Ia[MAX_LIGHTS]; // ambient intensity for each light
uniform vec3 Id[MAX_LIGHTS]; // diffuse intensity for each light
uniform vec3 Is[MAX_LIGHTS]; // specular intensity for each light

void main() {
    vec3 camera_direction = -normalize(position_view_space);
    
    // Calculate normal in view space using fragment neighbors
    vec3 xTangent = dFdx(position_view_space);
    vec3 yTangent = dFdy(position_view_space);
    vec3 normal_view_space = normalize(cross(xTangent, yTangent));
    
    // Initialize ambient, diffuse, and specular contributions
    vec4 total_ambient = vec4(0.0f);
    vec4 total_diffuse = vec4(0.0f);
    vec4 total_specular = vec4(0.0f);

    // Accumulate lighting from each light source
    for (int i = 0; i < num_lights; i++) {
        // Calculate light direction and attenuation
        vec3 light_direction = normalize(light_positions[i] - position_view_space);
        float dist = length(light_positions[i] - position_view_space);
        float attenuation = min(1.0 / (dist * dist * 0.005) + 1.0 / (dist * 0.05), 1.0);

        // Calculate ambient component
        total_ambient += vec4(Ia[i] * Ka, 1.0f);

        // Calculate diffuse component
        float diff = max(0.0f, dot(light_direction, normal_view_space));
        total_diffuse += vec4(Id[i] * Kd * diff, 1.0f) * attenuation;

        // Calculate specular component
        vec3 reflected_light = reflect(-light_direction, normal_view_space);
        float spec = pow(max(0.0f, dot(reflected_light, camera_direction)), Ns);
        total_specular += vec4(Is[i] * Ks * spec, 1.0f) * attenuation;
    }

    // Sample from texture if available
    vec4 texval = vec4(1.0f);
    if (has_texture == 1) {
        texval = texture2D(textureObject, fragment_texCoord);
    }

    // Combine shading components with texture and output final color
    final_color = texval * total_ambient + texval * total_diffuse + total_specular;
}
