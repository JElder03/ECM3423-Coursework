import pygame

from scene import Scene

from lightSource import LightSource

from blender import load_obj_file

from BaseModel import DrawModelFromMesh

from shaders import *

from ShadowMapping import *

from sphereModel import Sphere
from torusModel import Torus

from skyBox import *

from environmentMapping import *

class ParisOlympicsScene(Scene):

    def __init__(self):
        Scene.__init__(self,width=1000, height=1000, cameraCenter=[-0,7,-7], cameraAngle=[np.pi, 0])
        
        cauldron_light = LightSource(self, position=[0,-6.5,7], Ia=[0.1,0.1,0.05], Id=[0.9,0.9,0.4], Is=[1.0,1.0,0.4])
        self.statue_light = LightSource(self, position=[0,-4.95,-8], Ia=[0.05,0.05,0.05], Id=[0.8,0.8,0.8], Is=[0.8,0.8,0.8])
        self.lights = [cauldron_light,self.statue_light]

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.statue_light)

        self.environment1 = EnvironmentMappingTexture(width=1000, height=1000, center=[-2.5,4,7.5], rotation=[0,np.pi/15,0])
        self.environment2 = EnvironmentMappingTexture(width=1000, height=1000, center=[0,-5,-8], rotation=[0,-np.pi/15,0])

        self.skybox = SkyBox(scene=self)

        tree = load_obj_file('models/tree.obj')

        self.tree = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[3.5*j,-10,-3+i*2], scale=12.5, orientation=[0,np.pi/4*i*j,0]), mesh=tree[0], shader=FlatShader()) for i in range(4) for j in (-1,1)]

        chariot = load_obj_file('models/chariot.obj')
        chariotMesh = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-5.15,-5.75], scale=0.5, orientation=[0,np.pi/2,-np.pi/9]), mesh=mesh, shader=FlatShader()) for mesh in chariot]

        horse = load_obj_file('models/horse.obj')
        rhorse = load_obj_file('models/horse.obj', reflect=True)
        horseMesh1 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0.35,-5.65,-7.5], scale=3, orientation=[0,np.pi-np.pi/20,0]), mesh=horse[0], shader=FlatShader())
        horseMesh2 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[-0.35,-5.65,-7.5], scale=3, orientation=[0,np.pi+np.pi/20,0]), mesh=horse[0], shader=FlatShader())
        horseMesh3 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0.85,-5.65,-7.5], scale=3, orientation=[0,np.pi-np.pi/17.5,0]), mesh=rhorse[0], shader=FlatShader())
        horseMesh4 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[-0.85,-5.65,-7.5], scale=3, orientation=[0,np.pi+np.pi/17.5,0]), mesh=rhorse[0], shader=FlatShader())
        
        athena = load_obj_file('models/athena.obj', reflect=True)
        athenaMesh = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-4.95,-6], scale=0.15, orientation=[0,np.pi,0]), mesh=athena[0], shader=FlatShader())

        self.statue = [horseMesh1] + [horseMesh2] + [horseMesh3] + [horseMesh4] + chariotMesh + [athenaMesh]

        venus = load_obj_file('models/venus.obj')
        rvenus = load_obj_file('models/venus.obj', reflect=True)
        venusMesh1 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[1.5,-5.50,-7.5], scale=0.013, orientation=[0,np.pi/15,0]), mesh=venus[0], shader=EnvironmentShader(map=self.environment1))
        venusMesh2 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[-1.5,-5.50,-7.5], scale=0.013, orientation=[0,-np.pi/15,0]), mesh=rvenus[0], shader=EnvironmentShader(map=self.environment2))
        
        spotlight = load_obj_file('models/spotlight.obj')
        self.spotlight = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-5.5,-8], scale=0.01, orientation=[0,np.pi/2,0]), mesh=mesh, shader=FlatShader()) for mesh in spotlight]

        self.mirrorStatue = [venusMesh1, venusMesh2]

        fountain = load_obj_file('models/fountain.obj')
        self.fountain = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-10,7], scale=[0.4,0.2,0.4]), mesh=mesh, shader=FlatShader()) for mesh in fountain]
        
        arch = load_obj_file('models/arch.obj')
        self.arch = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-10,-7], scale=0.2, orientation=[np.pi/2,0,0]), mesh=arch[0], shader=FlatShader())

        self.torus = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-7,7], scale=1, orientation=[np.pi/2,0,0]), mesh=Torus(nvert=4), shader=FlatShader())
        self.sphere = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0,-2.5,7], scale=2), mesh=Sphere(nhoriz=40, nvert=20), shader=FlatShader())
        
        

        rope = load_obj_file('models/rope.obj')

        self.ropes = [[DrawModelFromMesh(scene=self, M=np.matmul(pointRotiationY(i * np.pi/10, position=[0,-5.5,7]), poseMatrix(position=[1.3,-5.2,7], scale=0.28, orientation=[0,0,np.pi/15])), mesh=mesh, shader=FlatShader()) for mesh in rope] for i in range(20)]

        '''
        meshes = load_obj_file('models/scene2.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]),scaleMatrix([0.5,0.5,0.5])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]
        )
        '''
        

    def draw_shadow_map(self):
        
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    def draw_reflections(self, exclude=[]):
        glClear(GL_DEPTH_BUFFER_BIT)
        self.skybox.draw()

        for mesh in self.spotlight:
            if mesh not in exclude:
                mesh.draw()

        for mesh in self.tree:
            if mesh not in exclude:
                mesh.draw()

        for mesh in self.fountain:
            if mesh not in exclude:
                mesh.draw()

        self.arch.draw()
        for mesh in self.statue:
            if mesh not in exclude:
                mesh.draw()

        for mesh in self.mirrorStatue:
            if mesh not in exclude:
                mesh.draw()


    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # when using a framebuffer, we do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()
        
        self.skybox.draw()
        self.shadows.render(self)

        if not framebuffer:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            self.environment1.update(self, exclude=[self.mirrorStatue[0]])
            self.environment2.update(self, exclude=[self.mirrorStatue[1]])

            for mesh in self.mirrorStatue:
                mesh.draw()  
            glDisable(GL_BLEND)

        for mesh in self.tree:
            mesh.draw()

        for mesh in self.fountain:
            mesh.draw()

        self.arch.draw()
        for mesh in self.statue:
            mesh.draw()

        for mesh in self.spotlight:
            mesh.draw()

        for mesh in self.mirrorStatue:
            mesh.draw()      
        
        self.torus.draw()
        self.sphere.draw()

        for rope in self.ropes:
            for mesh in rope:
                mesh.draw()   

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.

        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''
        Scene.keyboard(self, event)

        if event.key == pygame.K_s:
            print("Starting animation")
        elif event.key == pygame.K_f:
            print("Stopping animation")


if __name__ == '__main__':
    # initialises the scene object
    # scene = Scene(shaders='gouraud')
    scene = ParisOlympicsScene()

    # starts drawing the scene
    scene.run()
