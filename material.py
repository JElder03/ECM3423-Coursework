class Material:
    '''
    Simple class for storing material information, mainly reflection values
    '''

    def __init__(self, name=None, Ka=[1.,1.,1.], Kd=[1.,1.,1.], Ks=[1.,1.,1.], Ns=10.0, texture=None):
        '''
        :param name: The material name
        :param Ka: The ambient reflection RGB multiplier values
        :param Kd: The diffuse reflection RGB multiplier values
        :param Ks: The specular reflection RGB multiplier values
        :param Ns: The specular reflection power
        '''
        
        self.name = name
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns
        self.texture = texture
        self.alpha = 1.0

class MaterialLibrary:

    def __init__(self):
        self.materials = []
        self.names = {}

    def add_material(self, material):
        self.names[material.name] = len(self.materials)
        self.materials.append(material)

