from BaseModel import BaseModel,DrawModelFromMesh
from mesh import *

from OpenGL.GL.framebufferobjects import *

from cubeMap import CubeMap

from shaders import *

from framebuffer import Framebuffer


class EnvironmentShader(BaseShaderProgram):
    def __init__(self, name='environment', map=None):
        BaseShaderProgram.__init__(self, name=name)
        self.add_uniform('sampler_cube')
        self.add_uniform('PVM')
        self.add_uniform('VM')
        self.add_uniform('VMiT')
        self.add_uniform('VT')

        self.map = map

    def bind(self, model, M):
        glUseProgram(self.program)

        if self.map is not None:
            #self.map.update(model.scene)
            unit = len(model.mesh.textures)
            glActiveTexture(GL_TEXTURE0)
            self.map.bind()
            self.uniforms['sampler_cube'].bind(0)

        P = model.scene.P  # get projection matrix from the scene
        V = model.scene.camera.V  # get view matrix from the camera

        # set the PVM matrix uniform
        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))

        # set the PVM matrix uniform
        self.uniforms['VM'].bind(np.matmul(V, M))

        # set the PVM matrix uniform
        self.uniforms['VMiT'].bind(np.linalg.inv(np.matmul(V, M))[:3, :3].transpose())

        self.uniforms['VT'].bind(V.transpose()[:3, :3])


class EnvironmentMappingTexture(CubeMap):
    def __init__(self, width=200, height=200, center=[0,0,0], rotation=[0,0,0]):
        CubeMap.__init__(self)

        self.done = False

        self.width = width
        self.height = height

        self.fbos = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer()
        }

        t = 0.0
        self.views = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: np.matmul(rotationMatrixY(-np.pi/2-rotation[0]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: np.matmul( rotationMatrixY(+np.pi/2+rotation[0]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: np.matmul(rotationMatrixX(+np.pi/2-rotation[1]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: np.matmul(rotationMatrixX(-np.pi/2+rotation[1]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: np.matmul(rotationMatrixY(-np.pi-rotation[2]), translationMatrix(center)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: np.matmul(rotationMatrixY(rotation[2]), translationMatrix(center)),
        }

        self.bind()
        for (face, fbo) in self.fbos.items():
            glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            fbo.prepare(self, face)
        self.unbind()

    def update(self, scene, exclude=[]):
        if self.done:
            return

        self.bind()

        Pscene = scene.P

        scene.P = frustumMatrix(-1.0, +1.0, -1.0, +1.0, 1.0, 20.0)

        glViewport(0, 0, self.width, self.height)

        for (face, fbo) in self.fbos.items():
            fbo.bind()
            #scene.camera.V = np.identity(4)
            scene.camera.V = self.views[face]

            scene.draw_reflections(exclude=exclude)

            scene.camera.update()
            fbo.unbind()

        # reset the viewport
        glViewport(0, 0, scene.window_size[0], scene.window_size[1])

        scene.P = Pscene

        self.unbind()


class EnvironmentBox(DrawModelFromMesh):
    def __init__(self, scene, shader=EnvironmentShader(), width=200, height=200):
        self.done = False

        self.map = EnvironmentMappingTexture(width, height)

        DrawModelFromMesh.__init__(self, scene=scene, M=poseMatrix(), mesh=CubeMesh(shader.map), shader=shader, visible=False)
