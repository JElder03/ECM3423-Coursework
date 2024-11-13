from OpenGL.GL import *

class Framebuffer:
    '''
    Basic class to handle rendering to texture using a framebuffer object.
    '''

    def __init__(self, attachment=GL_COLOR_ATTACHMENT0, texture=None, texture_id=None):
        '''
        Initialise the framebuffer.
        :param attachment: Which output of the rendering process to save (GL_COLOR_ATTACHMENT0, GL_DEPTH_ATTACHMENT, ...)
        :param texture: [optional] if provided, link the framebuffer to the texture object
        :param texture_id: [optional] if provided, link the framebuffer to a texture ID directly
        '''

        self.attachment = attachment
        self.fbo = glGenFramebuffers(1)

        if texture is not None:
            self.prepare(texture)
        elif texture_id is not None:
            self.prepare_texture_id(texture_id)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def prepare(self, texture, target=None, level=0):
        '''
        Link the framebuffer output to a texture object.
        :param texture: The texture object to render to
        :param target: The target of the rendering, if not the default for the texture (use for cube maps)
        :param level: The mipmap level (ignore)
        '''

        target = target if target is not None else texture.target
        self.bind()
        glFramebufferTexture2D(GL_FRAMEBUFFER, self.attachment, target, texture.textureid, level)
        if self.attachment == GL_DEPTH_ATTACHMENT:
            glDrawBuffer(GL_NONE)
            glReadBuffer(GL_NONE)
        self.unbind()

    def prepare_texture_id(self, texture_id, target=GL_TEXTURE_2D, level=0):
        '''
        Link the framebuffer output to a texture ID directly.
        :param texture_id: ID of the texture to render to
        :param target: The target of the rendering
        :param level: The mipmap level (ignore)
        '''

        self.bind()
        glFramebufferTexture2D(GL_FRAMEBUFFER, self.attachment, target, texture_id, level)
        if self.attachment == GL_DEPTH_ATTACHMENT:
            glDrawBuffer(GL_NONE)
            glReadBuffer(GL_NONE)
        self.unbind()
