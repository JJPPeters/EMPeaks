vertex_shader = """
#version 150

uniform mat4 projection;

uniform float z_value;
in vec2 PosBuf;

void main()                                                                         
{
    gl_Position = projection * vec4(PosBuf.y, PosBuf.x, -z_value, 1.0);
} 
"""

geometry_shader = """
#version 150

layout(lines) in;
layout(triangle_strip) out;                                                         
layout(max_vertices = 4) out;

uniform float thickness;
uniform float window_height;
uniform float window_width;

out vec2 vertex_uv;
out float l0;

void main()                                                                         
{ 
    vec2 win_scale = vec2(window_width, window_height);

    vec2 pz = gl_in[0].gl_Position.zw;
    vec2 p0 = gl_in[0].gl_Position.xy * win_scale;
    vec2 p1 = gl_in[1].gl_Position.xy * win_scale;

    l0 = length(p1-p0);
    vec2 v0 = normalize(p1-p0);

    vec2 n0 = vec2(-v0.y, v0.x);

    vec2 nw = (thickness * n0);
    vec2 nc = vec2(nw.y, -nw.x);

    // start at negative normal
    gl_Position = vec4( (p0 - nw - nc) / win_scale, pz);
    vertex_uv = vec2(-thickness, -thickness);
    EmitVertex();
    // proceed to positive normal
    gl_Position = vec4( (p0 + nw - nc) / win_scale, pz);
    vertex_uv = vec2(thickness, -thickness);
    EmitVertex();


    // proceed other end negative normal
    gl_Position = vec4( (p1 - nw + nc) / win_scale, pz);
    vertex_uv = vec2(-thickness, l0 + thickness);
    EmitVertex();
    // proceed other end positive normal
    gl_Position = vec4( (p1 + nw + nc) / win_scale, pz);
    vertex_uv = vec2(thickness, l0 + thickness);
    EmitVertex();

    EndPrimitive();
}
"""

fragment_shader = """
#version 150

in vec2 vertex_uv;
in float l0;

uniform float thickness;
uniform vec4 colour;

out vec4 FragColor;

void main()
{

    if (vertex_uv.y < 0)
    {
        float r = thickness*thickness;
        float rsq = dot(vertex_uv, vertex_uv);
        if (rsq > r)
            discard;
        else
            FragColor = colour;
    }
    else if (vertex_uv.y > l0)
    {
        float r = thickness*thickness;
        vec2 ofst = vec2(0.0, l0);
        float rsq = dot(vertex_uv-ofst, vertex_uv-ofst);
        if (rsq > r)
            discard;
        else
            FragColor = colour;
        
    }
    else
        FragColor = colour;
}
"""

# geometry_shader = """
# #version 150
#
# layout(lines_adjacency) in;
# layout(triangle_strip) out;
# layout(max_vertices = 5) out;
#
# uniform float thickness;
# uniform float window_height;
# uniform float window_width;
#
#
# out vec2 vertex_uv;
#
# void main()
# {
#     float miter_limit = 0.8;
#     vec2 win_scale = vec2(window_width, window_height);
#
#     vec2 pz = gl_in[0].gl_Position.zw;
#     vec2 p0 = gl_in[0].gl_Position.xy * win_scale;
#     vec2 p1 = gl_in[1].gl_Position.xy * win_scale;
#     vec2 p2 = gl_in[2].gl_Position.xy * win_scale;
#     vec2 p3 = gl_in[3].gl_Position.xy * win_scale;
#
#     vec2 v0 = normalize(p1-p0);
#     vec2 v1 = normalize(p2-p1);
#     vec2 v2 = normalize(p3-p2);
#
#     vec2 n0 = vec2(-v0.y, v0.x);
#     vec2 n1 = vec2(-v1.y, v1.x);
#     vec2 n2 = vec2(-v2.y, v2.x);
#
#     vec2 miter_a = normalize(n0 + n1);
#     vec2 miter_b = normalize(n1 + n2);
#
#     float length_a = thickness / dot(miter_a, n1);
#     float length_b = thickness / dot(miter_b, n1);
#
#     // prevent excessively long miters at sharp corners
#     if( dot(v0,v1) < -miter_limit ) {
#         miter_a = n1;
#         length_a = thickness;
#     }
#
#     if( dot(v0,n1) > 0 ) {
#         // start at negative miter
#         gl_Position = vec4( (p1 - length_a * miter_a) / win_scale, pz);
#         EmitVertex();
#         // proceed to positive normal
#         gl_Position = vec4( (p1 + thickness * n1) / win_scale, pz);
#         EmitVertex();
#     }
#     else {
#         // start at negative normal
#         gl_Position = vec4( (p1 - thickness * n1) / win_scale, pz);
#         EmitVertex();
#         // proceed to positive miter
#         gl_Position = vec4( (p1 + length_a * miter_a) / win_scale, pz);
#         EmitVertex();
#     }
#
#     if( dot(v1,v2) < -miter_limit )
#     {
#         miter_b = n1;
#         length_b = thickness;
#     }
#
#     if( dot(v2,n1) < 0 ) {
#         // proceed to negative miter
#         gl_Position = vec4( (p2 - length_b * miter_b) / win_scale, pz);
#         EmitVertex();
#         // proceed to positive normal
#         gl_Position = vec4( (p2 + thickness * n1) / win_scale, pz);
#         EmitVertex();
#         // end at positive normal
#         gl_Position = vec4( (p2 + thickness * n2) / win_scale, pz);
#         EmitVertex();
#     }
#     else {
#         // proceed to negative normal
#         gl_Position = vec4( (p2 - thickness * n1) / win_scale, pz);
#         EmitVertex();
#         // proceed to positive miter
#         gl_Position = vec4( (p2 + length_b * miter_b) / win_scale, pz);
#         EmitVertex();
#         // end at negative normal
#         gl_Position = vec4( (p2 - thickness * n2) / win_scale, pz);
#         EmitVertex();
#     }
#     EndPrimitive();
# }
# """
#
# fragment_shader = """
# #version 150
#
# uniform vec4 colour;
#
# out vec4 FragColor;
#
# void main()
# {
#     FragColor = colour;
# }
# """