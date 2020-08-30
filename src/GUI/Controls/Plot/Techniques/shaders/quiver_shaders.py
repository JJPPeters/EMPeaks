vertex_shader = """
#version 150

uniform mat4 projection;

uniform float z_value;
in vec2 PosBuf;
in float LenBuf;
in float AngBuf;

out float LenPass;
out float AngPass;

void main()                                                                         
{
    gl_Position = projection * vec4(PosBuf.y, PosBuf.x, -z_value, 1.0);
    AngPass = AngBuf;
    LenPass = LenBuf;
} 
"""

geometry_shader = """
#version 150

layout(points) in;
layout(triangle_strip) out;                                                         
layout(max_vertices = 20) out;

uniform int window_width;
uniform int window_height;

uniform float line_width;
uniform float head_width;
uniform float head_length;

uniform float min_length;
uniform float max_length;

uniform float expand;
uniform float scale;

uniform vec4 colour_map[256];

in float LenPass[];
in float AngPass[];

// uniform vec4 fill_colour;
uniform vec4 border_colour;

out vec4 v_col;

void main()                                                                         
{ 
    vec2 win_scale = vec2(window_width, window_height);

    float line_length = scale * LenPass[0] + 2 * expand;
    
    float hl = head_length + 2 * expand;
    
    if (line_length <= hl)
        line_length = hl;
    
    float line_angle = AngPass[0];

    vec4 lm = gl_in[0].gl_Position;

    // get the unit vector for the line
    // -sin as our y starts at the top
    vec2 lu = vec2(cos(line_angle), -sin(line_angle));
    
    // get line endpoints
    float head_pos = line_length / 2.0 - head_length - 2 * expand;
    vec2 e0 = lm.xy + (lu * head_pos) / win_scale; // head side
    vec2 e1 = lm.xy - (lu * line_length / 2.0) / win_scale; // tail side
    
    // get normal vector to line (half so we can expand both sides
    vec2 n0 = vec2(-lu.y, lu.x) * (line_width / 2 + expand);
    vec2 n1 = vec2(-lu.y, lu.x) * (head_width / 2 + 1.5*expand);
    vec2 n2 = lu * (hl + 1.5*expand);
    
    vec2 c0 = e1 + n0 / win_scale;
    vec2 c1 = e1 - n0 / win_scale;
    vec2 c2 = e0 + n0 / win_scale;
    vec2 c3 = e0 - n0 / win_scale;

    vec2 t0 = e0 + n1 / win_scale;
    vec2 t1 = e0 - n1 / win_scale;
    
    vec2 t2 = e0 + n2 / win_scale;

    v_col = border_colour;

    gl_Position = vec4(c1, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c0, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c3, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c2, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(t0, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(t2, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(t1, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c3, lm.zw);
    EmitVertex();
    
    EndPrimitive();
    
    
    // TODO: see what parts of this don't need to be recalculated....
    
    line_length = scale * LenPass[0];
    
    hl = head_length;
    
    if (line_length <= hl)
        line_length = hl;
    
    line_angle = AngPass[0];

    lm = gl_in[0].gl_Position;

    // get the unit vector for the line
    lu = vec2(cos(line_angle), -sin(line_angle));
    
    // get line endpoints
    head_pos = line_length / 2.0 - head_length;
    e0 = lm.xy + (lu * head_pos) / win_scale; // head side
    e1 = lm.xy - (lu * line_length / 2.0) / win_scale; // tail side
    
    // get normal vector to line (half so we can expand both sides
    n0 = vec2(-lu.y, lu.x) * (line_width / 2);
    n1 = vec2(-lu.y, lu.x) * (head_width / 2);
    n2 = lu * (hl);
    
    c0 = e1 + n0 / win_scale;
    c1 = e1 - n0 / win_scale;
    c2 = e0 + n0 / win_scale;
    c3 = e0 - n0 / win_scale;

    t0 = e0 + n1 / win_scale;
    t1 = e0 - n1 / win_scale;
    
    t2 = e0 + n2 / win_scale;
    
    // COLOURMAP
    
    float r = clamp(line_angle / 6.2831853076, 0.0, 1.0);
    
    float i_f = r * (colour_map.length() - 1);
    int i = int(i_f);
    
    vec4 colour = colour_map[i];
    
    if (i != colour_map.length() - 1) {
        float frac = i_f - i;
        colour = (colour_map[i+1] - colour_map[i]) * frac + colour_map[i];
    }
    
    
    // COLOURMAP
    
    v_col = colour;
    v_col.xyz *= clamp((LenPass[0] - min_length) / max_length, 0.0, 1.0);
    
    gl_Position = vec4(c1, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c0, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c3, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c2, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(t0, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(t2, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(t1, lm.zw);
    EmitVertex();
    
    gl_Position = vec4(c3, lm.zw);
    EmitVertex();
    
    EndPrimitive();
}
"""

fragment_shader = """
#version 150

in vec4 v_col;

out vec4 FragColor;

void main()
{
    FragColor = v_col;
}
"""