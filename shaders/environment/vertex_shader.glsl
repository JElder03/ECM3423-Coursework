#version 130

in vec3 position;   // The position attribute contains the vertex position
in vec3 normal;     // Store the vertex normal

flat out vec3 position_view_space;   // The position of the vertex in view coordinates (not interpolated)
flat out vec3 normal_view_space;     // The normal of the face in view coordinates (not interpolated)
out vec3 fragment_texCoord;

uniform mat4 PVM;    // The Perspective-View-Model matrix is received as a Uniform
uniform mat4 VM;     // The View-Model matrix is received as a Uniform
uniform mat3 VMiT;   // The inverse-transpose of the view model matrix, used for normals

void main(void)
{
    // Transform the position using the PVM matrix
    gl_Position = PVM * vec4(position, 1.0f);

    // Calculate the position in view space (same for all vertices in the face)
    position_view_space = vec3(VM * vec4(position, 1.0f));

    // Use the face normal (assumes all vertices in the face share the same normal)
    normal_view_space = normalize(VMiT * normal);

    // Calculate texture coordinates (or any additional data)
    fragment_texCoord = reflect(-normalize(position), normal);
}