from OpenGL.GL import *
import numpy as np
from mesh import Mesh
from material import Material


class Torus(Mesh):
    '''
    Create a torus mesh
    '''
    
    def __init__(self, inner_radius=0.5, outer_radius=1.0, nvert=30, nhoriz=30, material=Material()):
        # Calculate the number of vertices and initialize arrays
        n = nvert * nhoriz
        vertices = np.zeros((n, 3), 'f')
        colors = np.zeros((n, 3), 'f')
        textureCoords = np.zeros((n, 2), 'f')

        vslice = 2.0 * np.pi / nvert
        hslice = 2.0 * np.pi / nhoriz

        # Create vertices
        for i in range(nvert):
            theta = i * vslice
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            for j in range(nhoriz):
                phi = j * hslice
                cos_phi = np.cos(phi)
                sin_phi = np.sin(phi)

                x = (outer_radius + inner_radius * cos_theta) * cos_phi
                y = (outer_radius + inner_radius * cos_theta) * sin_phi
                z = inner_radius * sin_theta

                v_index = i * nhoriz + j
                vertices[v_index] = [x, y, z]
                colors[v_index] = [float(i) / float(nvert), float(j) / float(nhoriz), 1.0]
                textureCoords[v_index] = [float(i) / float(nvert), float(j) / float(nhoriz)]

        # Calculate the number of faces and initialize the indices array
        nfaces = nvert * nhoriz * 2
        indices = np.zeros((nfaces, 3), dtype=np.uint32)
        k = 0

        # Create indices for triangles
        for i in range(nvert):
            for j in range(nhoriz):
                next_i = (i + 1) % nvert
                next_j = (j + 1) % nhoriz

                # First triangle
                indices[k, 0] = i * nhoriz + j
                indices[k, 2] = next_i * nhoriz + j
                indices[k, 1] = i * nhoriz + next_j
                k += 1

                # Second triangle
                indices[k, 0] = next_i * nhoriz + j
                indices[k, 2] = next_i * nhoriz + next_j
                indices[k, 1] = i * nhoriz + next_j
                k += 1

        # Initialize Mesh with computed data
        Mesh.__init__(self,
                      vertices=vertices,
                      faces=indices,
                      textureCoords=textureCoords,
                      material=material
                      )
