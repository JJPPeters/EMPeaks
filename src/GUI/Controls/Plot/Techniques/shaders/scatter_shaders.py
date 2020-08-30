vertex_shader = """
#version 150

uniform mat4 projection;
uniform float z_value;

in vec2 PosBuf;
in int SelBuf;

out int SelPass;

void main()                                                                         
{
    // Notw swapped x and y as we use columns major in the program
    gl_Position = projection * vec4(PosBuf.y, PosBuf.x, -z_value, 1.0);
    SelPass = SelBuf;
} 
"""

geometry_shader = """
#version 150

layout(points) in;
layout(triangle_strip) out;                                                         
layout(max_vertices = 4) out;

uniform vec2 radii;

uniform float width;
uniform float height;

in int SelPass[];

out vec2 vertex_uv;
flat out int selected;

void main()                                                                         
{ 
    selected = SelPass[0];

    vec4 vp = gl_in[0].gl_Position;

    float w_o = 1.0 / width;
    float h_o = 1.0 / height;

    vec2 va = vp.xy + vec2(-w_o, -h_o) * radii;
    gl_Position = vec4(va, vp.zw);
    vertex_uv = vec2(0.0, 0.0);
    EmitVertex();

    vec2 vb = vp.xy + vec2(-w_o, h_o) * radii;
    gl_Position = vec4(vb, vp.zw);
    vertex_uv = vec2(0.0, 1.0);
    EmitVertex();

    vec2 vc = vp.xy + vec2(w_o, -h_o) * radii;
    gl_Position = vec4(vc, vp.zw);
    vertex_uv = vec2(1.0, 0.0);
    EmitVertex();

    vec2 vd = vp.xy + vec2(w_o, h_o) * radii;
    gl_Position = vec4(vd, vp.zw);
    vertex_uv = vec2(1.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
"""

fragment_shader = """
#version 150

in vec2 vertex_uv;

uniform vec4 fill_colour;
uniform vec4 border_colour;
uniform float border_width;

uniform vec4 selected_fill_colour;
uniform vec4 selected_border_colour;

out vec4 FragColor;
flat in int selected;

void main()
{
    vec2 uv = vertex_uv.xy - vec2(0.5, 0.5);
    float rsq = dot(uv, uv);

    float outside = 0.25f; // 0.5^2

    float b_w = border_width;

    if(rsq >= outside)
        discard;
    else if (rsq >= outside - b_w)
    {
        if (selected == 0)
            FragColor = border_colour;
        else
            FragColor = selected_border_colour;
    }
    else
    {
        if (selected == 0)
            FragColor = fill_colour;
        else
            FragColor = selected_fill_colour;
    }
}
"""