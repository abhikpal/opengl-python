from ctypes import *

import pyglet
from pyglet.gl import *

# Initialize the window
window = pyglet.window.Window(
    width=800,
    height=600,
    caption="OpenGL",
    resizable=False,
    visible=True,
    config=Config(
        double_buffer=True,
        sample_buffers=1,
        samples=4
    )
)

# Create Vertex Array Object
vao = GLuint()
glGenVertexArrays(1, pointer(vao))
glBindVertexArray(vao)

# Create a list of vertices and convert this list to a GLFLoat arary
# so that OpenGL can use it.

vertices = [
#    Position      Color             Texture
    -0.5,  0.5,    1.0, 0.0, 0.0,    0.0, 0.0, # Top-left
     0.5,  0.5,    0.0, 1.0, 0.0,    1.0, 0.0, # Top-right
     0.5, -0.5,    0.0, 0.0, 1.0,    1.0, 1.0, # Bottom-right
    -0.5, -0.5,    1.0, 1.0, 1.0,    0.0, 1.0  # Bottom-left
]
vertices_typed = (GLfloat * len(vertices))(*vertices)

# Create a Vertex Buffer Object and copy vertex data to it.
vbo = GLuint()
glGenBuffers(1, pointer(vbo))

glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices_typed), vertices_typed, GL_STATIC_DRAW)

# Create an element array
ebo = GLuint()
glGenBuffers(1, pointer(ebo))

elements = [
    0, 1, 2,
    2, 3, 0
]
elements_typed = (GLuint * len(elements))(*elements)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(elements_typed), elements_typed, GL_STATIC_DRAW)

# Create and compile the shaders
# 
# NOTE: In Python 3, byte strings are different from string objects.
# The shader program expects us to send in bytes and NOT strings.
# Hence, we add a `b` right before the shader sources.

vertex_source = b"""
    #version 130

    in vec2 position;
    in vec3 color;
    in vec2 texcoord;

    out vec3 Color;
    out vec2 Texcoord;

    void main()
    {
        Color = color;
        Texcoord = texcoord;
        gl_Position = vec4(position, 0.0, 1.0);
    }
"""
vertex_shader = glCreateShader(GL_VERTEX_SHADER)
glShaderSource(
    vertex_shader,
    1,
    cast(pointer(c_char_p(vertex_source)), POINTER(POINTER(c_char))),
    None
)
glCompileShader(vertex_shader)

fragment_source = b"""
    #version 130

    in vec3 Color;
    in vec2 Texcoord;

    out vec4 outColor;

    uniform sampler2D tex;

    void main()
    {
        outColor = texture(tex, Texcoord) * vec4(Color, 1.0);
    }
"""
fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(
    fragment_shader,
    1,
    cast(pointer(c_char_p(fragment_source)), POINTER(POINTER(c_char))),
    None
)
glCompileShader(fragment_shader)

# Link the shaders into a shader program
shader_program = glCreateProgram()
glAttachShader(shader_program, vertex_shader)
glAttachShader(shader_program, fragment_shader)
glBindFragDataLocation(shader_program, 0, b"outColor")
glLinkProgram(shader_program)
glUseProgram(shader_program)

# specify the layout of the vertex data
pos_attrib = glGetAttribLocation(shader_program, b"position")
glEnableVertexAttribArray(pos_attrib)
glVertexAttribPointer(pos_attrib, 2, GL_FLOAT, GL_FALSE, 7 * sizeof(GLfloat(1)), 0)

col_attrib = glGetAttribLocation(shader_program, b"color")
glEnableVertexAttribArray(col_attrib)
glVertexAttribPointer(col_attrib, 3, GL_FLOAT, GL_FALSE, 7 * sizeof(GLfloat(1)), 2 * sizeof(GLfloat(1)))

tex_attrib = glGetAttribLocation(shader_program, b"texcoord")
glEnableVertexAttribArray(tex_attrib)
glVertexAttribPointer(tex_attrib, 2, GL_FLOAT, GL_FALSE, 7 * sizeof(GLfloat(1)), 5 * sizeof(GLfloat(1)))

tex = GLuint()
glGenTextures(1, pointer(tex))
glBindTexture(GL_TEXTURE_2D, tex)

image = pyglet.image.load("sample.png")
width, height = image.width, image.height
image_data = image.get_data('RGB', - width * 3)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

def update(dt):
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0)
    
@window.event
def on_exit():
    glDeleteTextures(1, pointer(tex))
    
    glDeleteProgram(shader_program)
    glDeleteShader(fragment_shader)
    glDeleteShader(vertex_shader)

    glDeleteBuffers(1, pointer(ebo))
    glDeleteBuffers(1, pointer(vbo))

    glDeleteVertexArrays(1, pointer(vao))

    window.close()
    exit()
    
if __name__ == '__main__':
    pyglet.clock.schedule(update)
    pyglet.app.run()
