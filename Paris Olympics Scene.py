import pygame
import time

# Import necessary classes and functions from various modules
from scene import Scene
from lightSource import LightSource
from blender import load_obj_file
from BaseModel import DrawModelFromMesh
from sphereModel import Sphere
from torusModel import Torus
from skyBox import *
from environmentMapping import *

class ParisOlympicsScene(Scene):
    '''
    Specific class for drawing the Paris Olympics OpenGL scene using the PyGame library
    '''

    def __init__(self):
        # Initialize the base scene with specified width, height, and camera settings
        Scene.__init__(self, width=1000, height=1000, cameraCenter=[-0, 4, 6], cameraAngle=[np.pi, 0])
        
        # Define light sources in the scene
        self.cauldron_light = LightSource(self, position=[0, -6.5, 7], Ia=[0.06, 0.035, 0.03], Id=[0.9, 0.5, 0], Is=[1.0, 0.5, 0])
        statue_light = LightSource(self, position=[0, -4.95, -8], Ia=[0.02, 0.02, 0.02], Id=[0.8, 0.8, 0.8], Is=[0.8, 0.8, 0.8])
        self.lights = [self.cauldron_light, statue_light]

        # Initialize environment textures and skybox
        self.environment1 = EnvironmentMappingTexture(width=1000, height=1000, center=[-2.5, 4, 7.5], rotation=[0, np.pi/15, 0])
        self.environment2 = EnvironmentMappingTexture(width=1000, height=1000, center=[0, -5, -8], rotation=[0, -np.pi/15, 0])
        self.skybox = SkyBox(scene=self)
        
        # Load and initialize objects in the scene
        self.initialise_objects()

        # Store initial positions for animated objects and ropes
        self.animated_init_positions = [obj.M for obj in self.animated_objects]
        self.ropes_init_positions = [obj.M for obj in self.rope_objects]

    def initialise_objects(self):
        '''
        Load and initialize each model with specific transformations and shaders
        :return: None
        '''
    
        tree = load_obj_file('models/tree.obj')
        treeMeshes = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[3.5*j, -10, -3+i*2], scale=12.5, orientation=[0, np.pi/4*i*j, 0]), mesh=tree[0], shader=FlatShader()) for i in range(4) for j in (-1, 1)]
        
        # Load chariot model
        chariot = load_obj_file('models/chariot.obj')
        chariotMeshes = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -5.15, -5.75], scale=0.5, orientation=[0, np.pi/2, -np.pi/9]), mesh=mesh, shader=FlatShader()) for mesh in chariot]

        # Load horse models with different transformations
        horse = load_obj_file('models/horse.obj')
        rhorse = load_obj_file('models/horse.obj', reflect=True)
        horseMesh1 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0.35, -5.65, -7.5], scale=3, orientation=[0, np.pi - np.pi/20, 0]), mesh=horse[0], shader=FlatShader())
        horseMesh2 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[-0.35, -5.65, -7.5], scale=3, orientation=[0, np.pi + np.pi/20, 0]), mesh=horse[0], shader=FlatShader())
        horseMesh3 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0.85, -5.65, -7.5], scale=3, orientation=[0, np.pi - np.pi/17.5, 0]), mesh=rhorse[0], shader=FlatShader())
        horseMesh4 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[-0.85, -5.65, -7.5], scale=3, orientation=[0, np.pi + np.pi/17.5, 0]), mesh=rhorse[0], shader=FlatShader())
        
        # Load Athena statue with reflection
        athena = load_obj_file('models/athena.obj', reflect=True)
        athenaMesh = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -4.95, -6], scale=0.15, orientation=[0, np.pi, 0]), mesh=athena[0], shader=FlatShader())

        # Load and setup Venus statues with environment mapping
        venus = load_obj_file('models/venus.obj')
        rvenus = load_obj_file('models/venus.obj', reflect=True)
        venusMesh1 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[1.5, -5.50, -7.5], scale=0.013, orientation=[0, np.pi/15, 0]), mesh=venus[0], shader=EnvironmentShader(map=self.environment1))
        venusMesh2 = DrawModelFromMesh(scene=self, M=poseMatrix(position=[-1.5, -5.50, -7.5], scale=0.013, orientation=[0, -np.pi/15, 0]), mesh=rvenus[0], shader=EnvironmentShader(map=self.environment2))
        
        # Load and configure spotlight and fountain objects
        spotlight = load_obj_file('models/spotlight.obj')
        spotlightMeshes = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -5.5, -8], scale=0.01, orientation=[0, np.pi/2, 0]), mesh=mesh, shader=FlatShader()) for mesh in spotlight]
        fountain = load_obj_file('models/fountain.obj')
        fountainMeshes = [DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -10, 7], scale=[0.4, 0.2, 0.4]), mesh=mesh, shader=FlatShader()) for mesh in fountain]
        
        # Load and initialize other objects in the scene
        arch = load_obj_file('models/arch.obj')
        archMesh = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -10, -7], scale=0.2, orientation=[np.pi/2, 0, 0]), mesh=arch[0], shader=FlatShader())
        torusMesh = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -7, 7], scale=1, orientation=[np.pi/2, 0, 0]), mesh=Torus(nvert=4), shader=FlatShader())
        sphereMesh = DrawModelFromMesh(scene=self, M=poseMatrix(position=[0, -2.5, 7], scale=2), mesh=Sphere(nhoriz=40, nvert=20), shader=FlatShader())

        # Initialize ropes with transformations
        rope = load_obj_file('models/rope.obj')
        self.rope_objects = []
        self.ropes_center = np.array([0, -5.5, 7])
        for i in range(10):
            for mesh in rope:
                self.rope_objects.append(DrawModelFromMesh(scene=self, M=np.matmul(pointRotiationY(i * np.pi/5, position=self.ropes_center), poseMatrix(position=[1.3, -5.2, 7], scale=0.28, orientation=[0, 0, np.pi/15])), mesh=mesh, shader=FlatShader()))
        
        # Define different types of objects for easy handling in animations and rendering
        self.objects = chariotMeshes + [horseMesh1, horseMesh2, horseMesh3, horseMesh4] + treeMeshes + [athenaMesh] + spotlightMeshes + fountainMeshes + [archMesh]
        self.reflective_objects = [venusMesh1, venusMesh2]                                                                                                                                                                                        
        self.animated_objects = [torusMesh, sphereMesh]

    def draw_reflections(self, exclude=[]):
        '''
        Draws the scene to generate a reflection texture for environment mapped objects
        :param exclude: [optional] A list of models not to draw in the reflection
        :return: None
        '''

        # Clear depth buffer and draw skybox
        glClear(GL_DEPTH_BUFFER_BIT)
        self.skybox.draw()

        # Draw each object with reflections, excluding specified ones if any
        for mesh in self.objects + self.reflective_objects + self.animated_objects + self.rope_objects:
            if mesh not in exclude:
                if isinstance(mesh, list):
                    print(len(mesh))
                mesh.draw()

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :param framebuffer: [optional] Indicates the use of a framebuffer
        :return: None
        '''
        
        # Clear the color and depth buffers to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Update camera unless using framebuffer
        if not framebuffer:
            self.camera.update()
        
        # Draw skybox and enable blending for reflections
        self.skybox.draw()
        if not framebuffer:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Update environment maps for reflections
            self.environment1.update(self, exclude=[self.reflective_objects[0]])
            self.environment2.update(self, exclude=[self.reflective_objects[1]])

            glDisable(GL_BLEND)

        # Draw all objects in the scene
        for mesh in self.objects + self.reflective_objects + self.animated_objects + self.rope_objects:
            mesh.draw()

        # Swap buffers to display the rendered scene
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        :param event: the Pygame event containing the keyboard info
        :return None
        '''
        
        # Call base class keyboard event handler
        Scene.keyboard(self, event)

        # Handle custom keyboard events
        if event.key == pygame.K_s:
            print("Starting animation")
            self.animating = True
        elif event.key == pygame.K_f:
            print("Stopping animation")
            self.animating = False
        elif event.key == pygame.K_p:
            print("Updating Shaders")
            for obj in self.objects + self.animated_objects + self.rope_objects:
                obj.bind_shader('phong')
            for obj in self.reflective_objects:
                obj.bind_shader(EnvironmentShader(map=obj.shader.map, name='environment_phong'))
        elif event.key == pygame.K_o:
            print("Updating Shaders")
            for obj in self.objects + self.animated_objects + self.rope_objects:
                obj.bind_shader('flat')
            for obj in self.reflective_objects:
                obj.bind_shader(EnvironmentShader(map=obj.shader.map, name='environment'))

    def animate(self):
        '''
        Animate scene objects, ropes, and light positions if the specified frame time has passed
        :return None
        '''

        if time.time() - self.last_frame >= self.FPS / 1000:
            translation = np.array([0.01, 0.02, -0.02])  # Define movement vector
            rotation = np.pi / self.FPS  # Define rotation angle
            self.last_frame = time.time()
            
            # Update rope center and light position
            self.ropes_center += translation
            self.cauldron_light.position += translation

            # Animate ropes with transformations
            for object in self.animated_objects + self.rope_objects:
                object.M = np.matmul(translationMatrix(translation), object.M)
                object.M = np.matmul(pointRotiationY(rotation, position=self.ropes_center), object.M)

if __name__ == '__main__':
    # Create and run the scene
    scene = ParisOlympicsScene()
    scene.run(fps=60)