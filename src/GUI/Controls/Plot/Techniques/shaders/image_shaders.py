vertex_shader = """
#version 150

uniform mat4 projection;
uniform float z_value;

uniform vec2 origin;
uniform float scale;

in vec2 rectangle_position;
in vec2 tex_coords;

out vec2 theCoords;

void main()
{
    vec2 new_pos = (rectangle_position * scale) - origin.yx;
    gl_Position = projection * vec4(new_pos, -z_value, 1.0);
    theCoords = tex_coords;
}
"""

fragment_shader = """
#version 150

uniform sampler2D tex_unit;

uniform float image_min;
uniform float image_max;

uniform float brightness;
uniform float contrast;
uniform float gamma;

uniform vec4 colour_map[256];

in vec2 theCoords;
out vec4 outputColour;

void main()
{
    float r = texture(tex_unit, theCoords).r;
    r = clamp((r - image_min) / image_max, 0.0, 1.0);
    
    r = contrast * (pow(r, gamma) - brightness) + 0.5;
    r = clamp(r, 0.0, 1.0);
    
    float i_f = r * (colour_map.length() - 1);
    
    int i = int(i_f);
    
    vec4 colour = colour_map[i];
    
    if (i != colour_map.length() - 1) {
        float frac = i_f - i;
        colour = (colour_map[i+1] - colour_map[i]) * frac + colour_map[i];
    }
    
    outputColour = colour;
}
"""