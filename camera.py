from matutils import *

class Camera:
    '''
    Base class for handling the camera.
    '''

    def __init__(self, center=[0,0,0], phi=0, psi=0):
        self.V = np.identity(4)
        self.phi = phi               # azimuth angle
        self.psi = psi              # zenith angle
        self.distance = 5.         # distance of the camera to the centre point
        self.center = center  # position of the centre
        self.update()               # calculate the view matrix

    def update(self):
        '''
        Function to update the camera view matrix from parameters.
        '''

        # calculate the translation matrix for the view center
        T0 = translationMatrix(self.center)

        # calculate the rotation matrix from the angles phi (azimuth) and psi (zenith) angles
        R = np.matmul(rotationMatrixX(self.psi), rotationMatrixY(self.phi))

        # calculate translation for the camera distance to the center point
        T = translationMatrix([0., 0., -self.distance])

        # finally calculate the view matrix by combining the three matrices
        self.V = np.matmul(np.matmul(T, R), T0)