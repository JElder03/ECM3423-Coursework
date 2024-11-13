import pygame
import time

from OpenGL.GL import *
from shaders import *
from camera import Camera

from lightSource import LightSource

class Scene:
    '''
    Main class for drawing an OpenGL scene using the PyGame library
    '''

    def __init__(self, width=800, height=600, shaders=None, cameraCenter=[0,0,0], cameraAngle = [0,0]):
        self.window_size = (width, height)

        # by default, wireframe mode is off
        self.wireframe = False

        # initialise the pygame window
        pygame.init()
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)

        # initialise the window from the OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])

        # enable back face culling to only show faces facing the camera
        glEnable(GL_CULL_FACE)

        # enable the vertex array capability
        glEnableClientState(GL_VERTEX_ARRAY)

        # enable depth test for clean output
        glEnable(GL_DEPTH_TEST)

        # set the default shader program
        self.shaders = 'phong'

        # initialise the projective transform
        near = 1.0
        far = 30.0
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        # cycle through models
        self.show_model = -1

        # use a perspective projection
        self.P = frustumMatrix(left, right, top, bottom, near, far)

        # initialises the camera object
        self.camera = Camera(center=cameraCenter, phi=cameraAngle[0], psi=cameraAngle[1])

        # initialise the light source
        self.light = LightSource(self, position=[0,0,2])

        # a list of models to draw in the scene
        self.models = []

    def add_model(self, model):
        '''
        Adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        '''

        self.models.append(model)

    def add_models_list(self, models_list):
        '''
        Adds a list of models to the scene.
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

        # clear the scene and depth buffer to handle occlusions
        if not framebuffer:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # ensure that the camera view matrix is up to date
            self.camera.update()

        # draw all the models
        for model in self.models:
            model.draw()

        # Switch buffer to display the scene (due to double buffering)
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Method to process keyboard events
        :param event: the event object that was raised
        :return None
        '''

        if event.key == pygame.K_q:
            self.running = False

    def pygameEvents(self):
        '''
        Method to handle PyGame events for user interaction.
        :return None
        '''

        # check whether the window has been closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # keyboard events
            elif event.type == pygame.KEYDOWN:
                self.keyboard(event)

            # mouse event
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mods = pygame.key.get_mods()
                if event.button == 4:
                    self.camera.distance = max(1, self.camera.distance - 1)
                elif event.button == 5:
                     self.camera.distance += 1

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if self.mouse_mvt is not None:
                        # Left mouse button moves left/right and up/down
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.center[0] -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.center[1] -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                elif pygame.mouse.get_pressed()[1]:
                    if self.mouse_mvt is not None:
                        # middle mouse button moves the forward/back
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.center[2] -= 5*(float(self.mouse_mvt[1]) / self.window_size[0])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                elif pygame.mouse.get_pressed()[2]:
                    if self.mouse_mvt is not None:
                        # right mouse button rotates camera about current center
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.phi -= (float(self.mouse_mvt[0]) / self.window_size[0])
                        self.camera.psi -= (float(self.mouse_mvt[1]) / self.window_size[1])
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                else:
                    self.mouse_mvt = None

    def run(self, fps = 30):
        '''
        Draws the scene in a loop until exit.
        :param fps: [optional] The FPS to run any animation at
        :return None
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