import pygame
from OpenGL.GL import *
import numpy as np


class ImageWrapper:
    """
    Wrapper for loading and handling image data using Pygame, 
    converting it to a format compatible with OpenGL textures.
    """
    
    def __init__(self, name: str):
        """
        Loads an image from the specified file.
        
        :param name: The filename of the image to load.
        """
        
        print(f'Loading image: texture/{name}')
        self.img = pygame.image.load(f'./textures/{name}')

    def width(self) -> int:
        """
        Returns the width of the loaded image.
        
        :return: Image width in pixels.
        """

        return self.img.get_width()

    def height(self) -> int:
        """
        Returns the height of the loaded image.
        
        :return: Image height in pixels.
        """

        return self.img.get_height()

    def data(self, format: int = GL_RGB) -> bytes:
        """
        Converts the image to a raw byte array for OpenGL texture processing.
        
        :param format: The desired format for OpenGL (GL_RGB or GL_RGBA).
        :return: Byte array representing the image data.
        """

        if format == GL_RGBA:
            return pygame.image.tostring(self.img, "RGBA", 1)
        elif format == GL_RGB:
            return pygame.image.tostring(self.img, "RGB", 1)


class Texture:
    """
    Class to manage texture loading, parameters, and binding within OpenGL.
    """
    
    def __init__(self, name: str, img: np.ndarray = None, wrap: int = GL_REPEAT, 
                 sample: int = GL_NEAREST, format: int = GL_RGBA, type: int = GL_UNSIGNED_BYTE, 
                 target: int = GL_TEXTURE_2D):
        """
        Initializes and loads a texture, either from an image file or data array.
        
        :param name: Name or filename of the texture.
        :param img: Optional image data as a numpy array.
        :param wrap: Wrapping mode for the texture (e.g., GL_REPEAT).
        :param sample: Sampling filter for the texture (e.g., GL_NEAREST).
        :param format: Format of the texture data (e.g., GL_RGBA).
        :param type: Data type of the texture (e.g., GL_UNSIGNED_BYTE).
        :param target: Texture target, default is GL_TEXTURE_2D.
        """

        self.name = name
        self.format = format
        self.type = type
        self.wrap = wrap
        self.sample = sample
        self.target = target
        self.textureid = glGenTextures(1)  # Generate a new texture ID

        print(f'* Loading texture ./textures/{name} at ID {self.textureid}')

        self.bind()

        # Load image or use provided data array
        if img is None:
            img = ImageWrapper(name)
            glTexImage2D(self.target, 0, format, img.width(), img.height(), 0, format, type, img.data(format))
        else:
            glTexImage2D(self.target, 0, format, img.shape[0], img.shape[1], 0, format, type, img)

        # Set texture wrapping and sampling parameters
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, wrap)
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, sample)
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, sample)

        self.unbind()

    def set_shadow_comparison(self):
        """
        Sets the texture to use shadow comparison mode, useful for shadow mapping.
        """

        self.set_parameter(GL_TEXTURE_COMPARE_MODE, GL_COMPARE_REF_TO_TEXTURE)

    def set_parameter(self, param: int, value: int):
        """
        Sets a specific parameter for the texture.
        
        :param param: The parameter to set (e.g., GL_TEXTURE_COMPARE_MODE).
        :param value: The value for the parameter.
        """

        self.bind()
        glTexParameteri(self.target, param, value)
        self.unbind()

    def set_wrap_parameter(self, wrap: int = GL_REPEAT):
        """
        Sets the wrap mode for the texture.
        
        :param wrap: Wrapping mode for the texture (e.g., GL_REPEAT).
        """

        self.wrap = wrap
        self.bind()
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, wrap)
        self.unbind()

    def set_sampling_parameter(self, sample: int = GL_NEAREST):
        """
        Sets the sampling mode for the texture.
        
        :param sample: Sampling filter for the texture (e.g., GL_NEAREST).
        """

        self.sample = sample
        self.bind()
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, sample)
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, sample)
        self.unbind()

    def set_data_from_image(self, data: np.ndarray, width: int = None, height: int = None):
        """
        Loads texture data from a numpy array and sets it as the texture's content.
        
        :param data: The image data as a numpy array.
        :param width: Optional width of the texture (default is data width).
        :param height: Optional height of the texture (default is data height).
        """

        if isinstance(data, np.ndarray):
            width = data.shape[0]
            height = data.shape[1]

        self.bind()
        glTexImage2D(self.target, 0, self.format, width, height, 0, self.format, self.type, data)
        self.unbind()

    def bind(self):
        """
        Binds the texture for use in OpenGL rendering.
        """

        glBindTexture(self.target, self.textureid)

    def unbind(self):
        """
        Unbinds the texture from the current OpenGL context.
        """

        glBindTexture(self.target, 0)
