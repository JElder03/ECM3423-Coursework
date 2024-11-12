import numpy as np

REFLECT_XY = np.diag([1,1,-1,1])
REFLECT_YZ = np.diag([-1,1,1,1])
REFLECT_XZ = np.diag([1,-1,1,1])

def scaleMatrix(scale):
    if np.isscalar(scale):
        scale = [scale, scale, scale]

    scale.append(1)
    return np.diag(scale)

def translationMatrix(t):
    n = len(t)
    T = np.identity(n+1,dtype='f')
    T[:n,-1] = t
    return T


def rotationMatrixZ(angle):
    c = np.cos(angle)
    s = np.sin(angle)
    R = np.identity(4)
    R[0,0] = c
    R[0,1] = s
    R[1,0] = -s
    R[1,1] = c
    return R


def rotationMatrixX(angle):
    c = np.cos(angle)
    s = np.sin(angle)
    R = np.identity(4)
    R[1,1] = c
    R[1,2] = s
    R[2,1] = -s
    R[2,2] = c
    return R


def rotationMatrixY(angle):
    c = np.cos(angle)
    s = np.sin(angle)
    R = np.identity(4)
    R[0,0] = c
    R[0,2] = s
    R[2,0] = -s
    R[2,2] = c
    return R

def pointRotiationY(angle, position=[0,0,0]):
    R = np.matmul(np.matmul(translationMatrix(position), rotationMatrixY(angle)),translationMatrix([-i for i in position]))
    return R


def poseMatrix(position=[0,0,0], orientation=0, scale=1, reflect=[False, False, False]):
    '''
    Returns a combined TRS matrix for the pose of a model.
    :param position: the position of the model
    :param orientation: the model orientation (for now assuming a rotation around the Z axis)
    :param scale: the model scale, either a scalar for isotropic scaling, or vector of scale factors
    :return: the 4x4 TRS matrix
    '''
    # apply the position and orientation of the object
    m=np.diag([1,1,1,1])

    if reflect[0]:
        m = np.matmul(m, REFLECT_XY)
    if reflect[1]:
        m = np.matmul(m, REFLECT_YZ)
    if reflect[2]:
        m = np.matmul(m, REFLECT_XY)

    if np.isscalar(orientation):
        R = rotationMatrixZ(orientation)
    else:
        R = np.matmul(np.matmul(rotationMatrixX(orientation[0]),rotationMatrixY(orientation[1])), rotationMatrixZ(orientation[2]))
    T = translationMatrix(position)

    # ... and the scale factor
    S = scaleMatrix(scale)

    m = np.matmul(np.matmul(np.matmul(T,m),R),S)

    return m


def orthoMatrix(l,r,t,b,n,f):
    '''
    Returns an orthographic projection matrix
    :param l: left clip plane
    :param r: right clip plane
    :param t: top clip plane
    :param b: bottom clip plane
    :param n: near clip plane
    :param f: far clip plane
    :return: A 4x4 orthographic projection matrix
    '''
    return np.array(
        [
        [2./(r-l),      0.,         0.,         (r+l)/(r-l) ],
        [0.,            -2./(t-b),   0.,         (t+b)/(t-b) ],
        [0.,            0.,         2./(f-n),  (f+n)/(f-n) ],
        [0.,            0.,         0.,         1.          ]
        ]
    )

def frustumMatrix(l,r,t,b,n,f):
    return np.array(
        [
            [ 2*n/(r-l),      0,          (r+l)/(r-l),    0 ],
            [ 0,              -2*n/(t-b),  (t+b)/(t-b),    0 ],
            [ 0,              0,          -(f+n)/(f-n),   -2*f*n/(f-n) ],
            [ 0,              0,          -1,             0 ]
            ]
    )


# Homogeneous coordinates helpers
def homog(v):
    return np.hstack([v,1])

def unhomog(vh):
    return vh[:-1]/vh[-1]

def matmul(L):
    R = L[0]
    for M in L[1:]:
        R = np.matmul(R,M)
    return R
