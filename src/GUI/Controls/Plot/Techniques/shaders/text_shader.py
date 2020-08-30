vertex_shader = """
#version 150

uniform mat4 projection;
uniform float z_value;

in vec2 text_origin;

void main()
{
    gl_Position = projection * vec4(text_origin.y, text_origin.x, -z_value, 1.0);
}
"""

geometry_shader = """
#version 150

layout(points) in;
layout(triangle_strip) out;                                                         
layout(max_vertices = 4) out;

uniform vec4 offsets;
uniform mat4 model;

uniform float width;
uniform float height;

out vec2 vertex_uv;

void main()                                                                         
{ 
    vec4 vp = gl_in[0].gl_Position;
    vec4 wh = vec4(width, height, 1.0, 1.0);


    vec4 oa = model * vec4(offsets.y, offsets.x, 0.0, 0.0) / wh;
    gl_Position = vp + oa;
    vertex_uv = vec2(0.0, 0.0);
    EmitVertex();
    
    vec4 ob = model * vec4(offsets.w, offsets.x, 0.0, 0.0) / wh;
    gl_Position = vp + ob;
    vertex_uv = vec2(1.0, 0.0);
    EmitVertex();
    
    vec4 oc = model * vec4(offsets.y, offsets.z, 0.0, 0.0) / wh;
    gl_Position = vp + oc;
    vertex_uv = vec2(0.0, 1.0);
    EmitVertex();
    
    vec4 od = model * vec4(offsets.w, offsets.z, 0.0, 0.0) / wh;
    gl_Position = vp + od;
    vertex_uv = vec2(1.0, 1.0);
    EmitVertex();
    
    EndPrimitive();
}
"""

fragment_shader = """
#version 150

uniform sampler2D tex_unit;

in vec2 vertex_uv;
out vec4 outputColour;

void main()
{
    float r = texture(tex_unit, vertex_uv).r;

    vec4 my_colour = vec4(1.0, 1.0, 1.0, 1.0*r);

    outputColour = my_colour;
}
"""