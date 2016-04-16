from pygame.locals import *


class Component(object):
    Forever = 'Forever'

    def __init__(self):
        pass


class PositionComponent(Component):
    name = 'PositionComponent'

    def __init__(self, posx=0, posy=0):
        Component.__init__(self)
        self.posx = posx
        self.posy = posy

        self.name = PositionComponent.name

    def move(self, x, y, delta):
        self.posx += x * delta
        self.posy += y * delta


class MovementComponent(Component):
    name = 'MovementComponent'

    def __init__(self, velx=0, vely=0, dynamic=list()):
        Component.__init__(self)
        self.velx = velx
        self.vely = vely

        self.dynamic = dynamic

        self.name = MovementComponent.name

    def add_constant(self, velx, vely):
        self.velx += velx
        self.vely -= vely

    def add_dynamic(self, velx, vely, ttl):
        self.dynamic.append((velx, vely, ttl))


class AccelerationComponent(Component):
    name = 'AccelerationComponent'

    def __init__(self, accx=0, accy=0):
        Component.__init__(self)
        self.accx = accx
        self.accy = accy

        self.name = AccelerationComponent.name


class DirectionComponent(Component):
    name = 'DirectionComponent'

    North = 0
    South = 1
    East = 2
    West = 3

    def __init__(self, direction=South):
        Component.__init__(self)
        self.direction = direction


class InputComponent(Component):
    name = 'InputComponent'

    def __init__(self):
        Component.__init__(self)
        self.keys = {}

        self.name = InputComponent.name


class BoundsComponent(Component):
    name = 'BoundsComponent'

    def __init__(self, bounds):
        Component.__init__(self)
        self.bounds = bounds  # ideally is a pygame Rect object


class DamageComponent(Component):
    name = 'DamageComponent'

    def __init__(self, damage):
        Component.__init__(self)
        self.damage = damage


class AttackComponent(Component):
    Slash = 0
    Stab = 1
    Spin = 2

    name = 'AttackComponent'

    def __init__(self, damage=0, atype=Spin, ar=0):
        Component.__init__(self)
        self.atype = atype
        self.ar = ar
        self.damage = damage

        self.name = AttackComponent.name


class TimeToLiveComponent(Component):
    name = 'TimeToLiveComponent'

    def __init__(self, ttl):
        Component.__init__(self)
        self.ttl = ttl

    def advance(self, time):
        self.ttl -= time
        return self.ttl <= 0.0

    def is_alive(self):
        return self.ttl <= 0.0


class SpriteComponent(Component):
    name = 'SpriteComponent'

    def __init__(self, sprite):
        # todo change to a dictionary/state like object
        Component.__init__(self)
        self.sprite = sprite

    def get_image(self):
        return self.sprite


class AnimatedSpriteComponent(SpriteComponent):
    name = 'AnimatedSpriteComponent'

    def __init__(self, sprites, initial_state, time_between_frames):
        Component.__init__(self)
        # sprites is a dictionary indexed by state and state_index to retrieve an image
        # todo add direction i.e. sprites[state][direction][index] = surface to draw
        self.sprites = sprites
        self.states = list(sprites.keys())

        self.state = initial_state
        self.state_index = 0

        self.next_state = initial_state

        self.timer = 0.0
        self.time_between_frames = time_between_frames

    def set_state(self, new_state, repeated=True):
        if new_state in self.states:
            if repeated:
                self.next_state = new_state

            self.state_index = 0
            self.state = new_state

    def get_image(self, delta_time=0):
        # advance timer
        self.timer += delta_time
        if self.timer >= self.time_between_frames:
            self.timer = 0

            # now advance the frame
            self.state_index += 1
            if self.state_index >= len(self.sprites[self.state]):
                self.state = self.next_state
                self.state_index = 0

        return self.sprites[self.state][self.state_index]

