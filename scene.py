# pygame is just used to create a window with the operating system on which to draw.
import pygame

import time

# imports all openGL functions
from OpenGL.GL import *

# import the shader class
from shaders import *

# import the camera class
from camera import Camera

# and we import a bunch of helper functions
from matutils import *

from lightSource import LightSource

class Scene:
    '''
    This is the main class for adrawing an OpenGL scene using the PyGame library
    '''
    def __init__(self, width=800, height=600, shaders=None, cameraCenter=[0,0,0], cameraAngle = [0,0]):
        '''
        Initialises the scene
        '''

        self.window_size = (width, height)

        # by default, wireframe mode is off
        self.wireframe = False

        # the first two lines initialise the pygame window. You could use another library for this,
        # for example GLut or Qt
        pygame.init()
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)

        # Here we start initialising the window from the OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])

        # enable back face culling (see lecture on clipping and visibility
        glEnable(GL_CULL_FACE)
        # depending on your model, or your projection matrix, the winding order may be inverted,
        # Typically, you see the far side of the model instead of the front one
        # uncommenting the following line should provide an easy fix.
        #glCullFace(GL_FRONT)

        # enable the vertex array capability
        glEnableClientState(GL_VERTEX_ARRAY)

        # enable depth test for clean output (see lecture on clipping & visibility for an explanation
        glEnable(GL_DEPTH_TEST)

        # set the default shader program (can be set on a per-mesh basis)
        self.shaders = 'phong'

        # initialise the projective transform
        near = 1.0
        far = 20.0
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        # cycle through models
        self.show_model = -1

        # to start with, we use an orthographic projection; change this.
        self.P = frustumMatrix(left, right, top, bottom, near, far)

        # initialises the camera object
        self.camera = Camera(center=cameraCenter, phi=cameraAngle[0], psi=cameraAngle[1])

        # initialise the light source
        self.light = LightSource(self, position=[0,0,2])


        # This class will maintain a list of models to draw in the scene,
        self.models = []

    def add_model(self, model):
        '''
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        '''

        # bind the default shader to the mesh
        #model.bind_shader(self.shaders)

        # and add to the list
        self.models.append(model)

    def add_models_list(self, models_list):
        '''
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        '''
        for model in models_list:
            self.add_model(model)

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        if not framebuffer:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # ensure that the camera view matrix is up to date
            self.camera.update()

        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Method to process keyboard events. Check Pygame documentation for a list of key events
        :param event: the event object that was raised
        '''
        if event.key == pygame.K_q:
            self.running = False

        # flag to switch wireframe rendering
        elif event.key == pygame.K_0:
            if self.wireframe:
                print('--> Rendering using colour fill')
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                self.wireframe = False
            else:
                print('--> Rendering using colour wireframe')
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                self.wireframe = True

    def pygameEvents(self):
        '''
        Method to handle PyGame events for user interaction.
        '''
        # check whether the window has been closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # keyboard events
            elif event.type == pygame.KEYDOWN:
                self.keyboard(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mods = pygame.key.get_mods()
                if event.button == 4:
                    #pass
                    #TODO: WS2
                    if mods & pygame.KMOD_CTRL:
                        self.light.position *= 1.1
                        self.light.update()
                    else:
                        self.camera.distance = max(1, self.camera.distance - 1)

                elif event.button == 5:
                    #pass
                    #TODO: WS2
                    if mods & pygame.KMOD_CTRL:
                        self.light.position *= 0.9
                        self.light.update()
                    else:
                        self.camera.distance += 1

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        #TODO: WS2
                        self.camera.center[0] -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.center[1] -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()

                elif pygame.mouse.get_pressed()[1]:
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()

                        # middle mouse button moves the forward/back
                        self.camera.center[2] -= 5*(float(self.mouse_mvt[1]) / self.window_size[0])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()

                elif pygame.mouse.get_pressed()[2]:
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        #TODO: WS2
                        self.camera.phi -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.psi -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                else:
                    self.mouse_mvt = None

    def run(self, fps = 30):
        '''
        Draws the scene in a loop until exit.
        '''

        self.running = True
        self.animating = False
        self.FPS = fps
        self.last_frame = time.time()

        while self.running:
            self.pygameEvents()
            if self.animating:
                self.animate()
            self.draw()
        
        '''
        FRAMES_PER_SECOND = 10
        SKIP_TICKS = 1.0 / FRAMES_PER_SECOND  # time in seconds

        next_game_tick = time.time()  # start with wall-clock time
        sleep_time = 0

        self.running = True
        while self.running:
            self.pygameEvents()

            # continue drawing the scene
            self.draw()

            # calculate the next frame time
            next_game_tick += SKIP_TICKS
            sleep_time = next_game_tick - time.time()

            # pause execution if there is remaining time in the frame
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print("missed frame")
        '''