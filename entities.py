

class Entity(object):
    def __init__(self, components=list()):
        self.components = {}
        for comp in components:
            self.components[comp.name] = comp
