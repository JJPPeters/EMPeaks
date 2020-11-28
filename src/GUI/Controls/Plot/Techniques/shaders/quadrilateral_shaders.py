vertex_shader = """
#version 150

uniform mat4 projection;

uniform float z_value;
uniform float height;
uniform float width;

in vec2 rectangle_position;
in vec2 rectangle_limits;

out vec2 coord_pass;

void main()
{
    gl_Position = projection * vec4(rectangle_position, -z_value, 1.0);
    coord_pass = rectangle_limits * vec2(width, height);
}
"""

fragment_shader = """
#version 150

uniform vec4 fill_colour;
uniform vec4 border_colour;

uniform float height;
uniform float width;

uniform float border_width;

in vec2 coord_pass;
out vec4 outputColour;

void main()
{
    float t = border_width;

    if (coord_pass.x < t || coord_pass.x > width - t || coord_pass.y < t || coord_pass.y > height - t)
        outputColour = border_colour;
    else
        outputColour = fill_colour;
}
"""