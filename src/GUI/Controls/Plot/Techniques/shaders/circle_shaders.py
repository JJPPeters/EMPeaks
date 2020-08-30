vertex_shader = """
#version 150

uniform mat4 projection;
uniform float z_value;

in vec2 circle_centre;

void main()
{
    gl_Position = projection * vec4(circle_centre, -z_value, 1.0);
}
"""

geometry_shader = """
#version 150

layout(points) in;
layout(triangle_strip) out;                                                         
layout(max_vertices = 4) out;

uniform vec2 circle_radii;

uniform float width;
uniform float height;

out vec2 vertex_uv;

void main()                                                                         
{ 
    vec4 vp = gl_in[0].gl_Position;

    float w_o = 1.0 / width;
    float h_o = 1.0 / height;

    vec2 va = vp.xy + vec2(-w_o, -h_o) * circle_radii;
    gl_Position = vec4(va, vp.zw);
    vertex_uv = vec2(0.0, 0.0);
    EmitVertex();

    vec2 vb = vp.xy + vec2(-w_o, h_o) * circle_radii;
    gl_Position = vec4(vb, vp.zw);
    vertex_uv = vec2(0.0, 1.0);
    EmitVertex();

    vec2 vc = vp.xy + vec2(w_o, -h_o) * circle_radii;
    gl_Position = vec4(vc, vp.zw);
    vertex_uv = vec2(1.0, 0.0);
    EmitVertex();

    vec2 vd = vp.xy + vec2(w_o, h_o) * circle_radii;
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
uniform float border_width_x;
uniform float border_width_y;

uniform float ring_frac;

out vec4 output_colour;

void main()
{
    vec2 uv = vertex_uv.xy - vec2(0.5, 0.5);
    float rsq = sqrt(dot(uv, uv));

    float outside = 0.5f; // 0.5^2
    float inside = 0.5f * ring_frac;

    float outer_bw_x = 0.5f - border_width_x;
    float outer_bw_y = 0.5f - border_width_y;
    
    float inner_bw_x = inside + border_width_x;
    float inner_bw_y = inside + border_width_y;
    
    float r_outer_b = (uv.x * uv.x) / (outer_bw_x * outer_bw_x) + (uv.y * uv.y) / (outer_bw_y * outer_bw_y);
    float r_inner_b = 99.9f;

    if (ring_frac != 0.0f)
    {
        r_inner_b = (uv.x * uv.x) / (inner_bw_x * inner_bw_x) + (uv.y * uv.y) / (inner_bw_y * inner_bw_y);
    }

    if (rsq >= outside)
        discard;
    else if (r_outer_b >= 1.0f)
    {
        output_colour = border_colour;
    }
    else if ( rsq < inside)
    {
        discard;
    }
    else if (r_inner_b < 1.0f)
    {
        output_colour = border_colour;
    }
    else
    {
        output_colour = fill_colour;
    }
}
"""