from BaseModel import DrawModelFromMesh
from mesh import *
from cubeMap import CubeMap
from shaders import *
from framebuffer import Framebuffer
import numpy as np

class EnvironmentShader(BaseShaderProgram):
    """
    Shader program to handle environment mapping using cube maps.
    """

    def __init__(self, name: str = 'environment', map: CubeMap = None):
        """
        Initializes the EnvironmentShader with necessary uniforms for environment mapping.
        
        :param name: Name of the shader program.
        :param map: Optional cube map for environment mapping.
        """

        super().__init__(name=name)
        self.add_uniform('sampler_cube')
        self.add_uniform('PVM')
        self.add_uniform('VM')
        self.add_uniform('VMiT')
        self.add_uniform('VT')
        self.map = map  # Cube map texture for environment reflection

    def bind(self, model, M: np.ndarray):
        """
        Binds the shader program with the provided model and transformation matrix.
        
        :param model: The model being rendered.
        :param M: The model transformation matrix.
        """

        glUseProgram(self.program)

        if self.map is not None:
            # Bind cube map texture for environment reflection
            unit = len(model.mesh.textures)
            glActiveTexture(GL_TEXTURE0)
            self.map.bind()
            self.uniforms['sampler_cube'].bind(0)

        P = model.scene.P  # Projection matrix from the scene
        V = model.scene.camera.V  # View matrix from the camera

        # Bind the perspective-view-model (PVM) matrix
        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))

        # Bind the view-model (VM) matrix
        self.uniforms['VM'].bind(np.matmul(V, M))

        # Bind the inverse-transpose of the VM matrix for normal transformations
        self.uniforms['VMiT'].bind(np.linalg.inv(np.matmul(V, M))[:3, :3].transpose())

        # Bind the transposed view matrix for skybox transformations
        self.uniforms['VT'].bind(V.transpose()[:3, :3])


class EnvironmentMappingTexture(CubeMap):
    """
    A texture class for environment mapping using cube maps, providing a 360-degree
    environment reflection by capturing the scene from six different perspectives.
    """

    def __init__(self, width: int = 200, height: int = 200, center: list = [0, 0, 0], rotation: list = [0, 0, 0]):
        """
        Initializes the cube map with framebuffers for each cube face and sets up view matrices.
        
        :param width: Width of each cube map face.
        :param height: Height of each cube map face.
        :param center: Center of the cube map.
        :param rotation: Rotation for each cube map face.
        """

        super().__init__()

        self.done = False
        self.width = width
        self.height = height

        # Initialize a framebuffer for each cube map face
        self.fbos = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer()
        }

        # Define view matrices for each face of the cube map
        self.views = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: np.matmul(rotationMatrixY(-np.pi/2 - rotation[0]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: np.matmul(rotationMatrixY(np.pi/2 + rotation[0]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: np.matmul(rotationMatrixX(np.pi/2 - rotation[1]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: np.matmul(rotationMatrixX(-np.pi/2 + rotation[1]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: np.matmul(rotationMatrixY(-np.pi - rotation[2]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: np.matmul(rotationMatrixY(rotation[2]), translationMatrix(center)),
        }

        # Bind and initialize textures for each face in the cube map
        self.bind()
        for face, fbo in self.fbos.items():
            glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            fbo.prepare(self, face)
        self.unbind()

    def update(self, scene, exclude: list = []):
        """
        Updates the cube map texture by capturing the scene from each cube face's perspective.
        
        :param scene: The scene to be rendered into the cube map.
        :param exclude: A list of objects to exclude from reflections.
        """

        if self.done:
            return

        self.bind()

        # Save the scene's original projection matrix
        Pscene = scene.P

        # Set the cube map's perspective projection matrix
        scene.P = frustumMatrix(-1.0, 1.0, -1.0, 1.0, 1.0, 20.0)

        # Set viewport to the cube map texture resolution
        glViewport(0, 0, self.width, self.height)

        # Render the scene for each cube map face
        for face, fbo in self.fbos.items():
            fbo.bind()

            # Set view matrix to current face's view perspective
            scene.camera.V = self.views[face]

            # Render reflections excluding specified objects
            scene.draw_reflections(exclude=exclude)

            scene.camera.update()
            fbo.unbind()

        # Reset the viewport to the original scene window size
        glViewport(0, 0, scene.window_size[0], scene.window_size[1])

        # Restore the original projection matrix
        scene.P = Pscene

        self.unbind()


class EnvironmentBox(DrawModelFromMesh):
    """
    A drawable cube used to represent an environment box, typically used to display
    environment reflections.
    """

    def __init__(self, scene, shader: EnvironmentShader = EnvironmentShader(), width: int = 200, height: int = 200):
        """
        Initializes an EnvironmentBox with a cube mesh and an environment mapping texture.
        
        :param scene: The scene in which this environment box will be rendered.
        :param shader: The shader program to use for rendering the environment.
        :param width: Width of the environment mapping texture.
        :param height: Height of the environment mapping texture.
        """
        
        self.done = False
        self.map = EnvironmentMappingTexture(width, height)  # Create an environment map texture

        # Initialize a cube mesh for the environment box, using the provided shader
        super().__init__(scene=scene, M=poseMatrix(), mesh=CubeMesh(shader.map), shader=shader, visible=False)
