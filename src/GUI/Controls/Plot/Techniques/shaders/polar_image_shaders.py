vertex_shader = """
#version 150

uniform mat4 projection;
uniform float z_value;

in vec2 rectangle_position;
in vec2 tex_coords;

out vec2 theCoords;

void main()
{
    gl_Position = projection * vec4(rectangle_position, -z_value, 1.0);
    theCoords = tex_coords;
}
"""

fragment_shader = """
#version 150

uniform sampler2D tex_unit_magnitude;
uniform sampler2D tex_unit_angle;
uniform sampler2D tex_unit_alpha;

uniform float magnitude_min;
uniform float magnitude_max;

uniform vec4 colour_map[256];

in vec2 theCoords;
out vec4 outputColour;

void main()
{
    float mag = texture(tex_unit_magnitude, theCoords).r;
    mag = clamp((mag - magnitude_min) / magnitude_max, 0.0, 1.0);

    float ang = texture(tex_unit_angle, theCoords).r;
    ang = clamp(ang / 6.2831853076, 0.0, 1.0);

    float alpha = texture(tex_unit_alpha, theCoords).r;

    float i_f = ang * (colour_map.length() - 1);
    int i = int(i_f);

    vec4 colour = colour_map[i];

    if (i != colour_map.length() - 1) {
        float frac = i_f - i;
        colour = (colour_map[i+1] - colour_map[i]) * frac + colour_map[i];
    }

    colour.xyz *= mag;
    colour.w *= alpha;
    
    outputColour = colour;
}
"""