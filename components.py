from pygame.locals import *
import pygame


class Component(object):
    """
    base class to be inherited by any component
    """
    Forever = 'Forever'

    def __init__(self):
        pass


class MovementComponent(Component):
    """
    represents movement. when combined with a Bounds component, the Entity will move according to its
    dynamic and constant velocities

    constant velocities are for example the velocities set when a player moves his character. they will be also used
    by the ai system for moving those Entities around. constant velocities are constant in the sense that they have to
    be manually managed (i.e. they last forever)

    dynamic velocities, on the other hand, have a finite lifetime. they are used i.e. for applying knockback effects.
    """
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


class DirectionComponent(Component):
    """
    direction component maintains the direction of an Entity. it is implemented in terms of the compass for four
    directions.
    """
    name = 'DirectionComponent'

    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'

    def __init__(self, direction=South):
        Component.__init__(self)
        self.direction = direction

    def set(self, val):
        if val in [self.North, self.South, self.East, self.West]:
            self.direction = val


class InputComponent(Component):
    """
    input component keeps record of the change in keyboard state between frames.

    setting keys[KEY_CONSTANT] = True means that the key was pressed DOWN, while setting it to False means that the key
    was released. the input component should be reset after processing.
    """
    name = 'InputComponent'

    def __init__(self):
        Component.__init__(self)
        self.keys = {}

        self.name = InputComponent.name


class BoundsComponent(Component):
    """
    bounds component keeps position and boundaries of an Entity as a pygame.Rect object.
    """
    name = 'BoundsComponent'

    def __init__(self, bounds):
        Component.__init__(self)
        self.bounds = bounds  # is a pygame.Rect object


class AttackComponent(Component):
    """
    attack component represents the current type of attack that will be executed when an Entity 'attacks'
    """
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
    """
    ttl component implements a death timer for an Entity. the aging system will call advance(delta), and when the
    component has expired, the Entity will be deleted.
    """
    name = 'TimeToLiveComponent'

    def __init__(self, ttl):
        Component.__init__(self)
        self.ttl = ttl

    def advance(self, time):
        self.ttl -= time
        return self.ttl <= 0.0

    def is_alive(self):
        return self.ttl <= 0.0


class StatusComponent(Component):
    """
    status component is the base class for all status effects that have a finite lifetime.
    """
    name = 'StatusComponent'

    def __init__(self, ttl):
        Component.__init__(self)
        self.ttl = ttl

    def advance(self, time):
        self.ttl -= time
        return self.ttl <= 0.0

    def in_effect(self):
        return self.ttl <= 0.0


class RootedComponent(StatusComponent):
    """
    rooted component will stop Entity from moving (i.e. any change in position)
    """
    name = 'RootedComponent'

    def __init__(self, ttl):
        StatusComponent.__init__(self, ttl)


class UnableToAttackComponent(StatusComponent):
    """
    unable to attack component is a debuff in which an Entity cannot execute any attacks
    """
    name = 'UnableToAttackComponent'

    def __init__(self, ttl):
        StatusComponent.__init__(self, ttl)


class SpriteComponent(Component):
    """
    sprite component is the base component for a single, static sprite image
    """
    name = 'SpriteComponent'

    def __init__(self, sprite):
        Component.__init__(self)
        self.sprite = sprite

    def get_image(self, **kwargs):
        return self.sprite


class AnimatedSpriteComponent(SpriteComponent):
    """
    animated sprite component uses the same interface for getting its current image as sprite component

    however, this class implements sprite as a dictionary of lists, where sprites[STATE][INDEX] = surface to draw
    """
    name = 'AnimatedSpriteComponent'

    def __init__(self, sprites, initial_state=None, time_between_frames=100):
        Component.__init__(self)
        # sprites is a dictionary indexed by state and state_index to retrieve an image
        self.sprites = sprites
        self.states = list(sprites.keys())

        if initial_state is None:
            self.state = list(sprites.keys())[0]
        else:
            self.state = initial_state

        self.next_state = self.state

        self.state_index = 0

        self.timer = 0.0
        self.time_between_frames = time_between_frames

    def set_state(self, new_state, repeated=True, reset_index_on_duplicate=True):
        if new_state in self.states:
            if repeated:
                self.next_state = new_state

            if self.state != new_state:
                self.state_index = 0
            elif self.state == new_state and reset_index_on_duplicate:
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


class CollisionImmaterialComponent(Component):
    """
    me thinks that this is unnecessary. simply avoiding to add any other collision component should mean that
    the entity is ignored by the collision system (while keeping movement in-tact)
    """
    name = 'CollisionImmaterialComponent'

    def __init__(self):
        Component.__init__(self)


class CollisionSolidComponent(Component):
    """
    component to represent that this object is not able to be passed through
    """
    name = 'CollisionSolidComponent'

    def __init__(self):
        Component.__init__(self)


class CollisionKnockbackComponent(Component):
    """
    component representing degree of knockback to apply to anything that collides with Entity
    """
    name = 'CollisionKnockbackComponent'

    def __init__(self, knockback, duration):
        Component.__init__(self)

        self.knockback = knockback
        self.duration = duration


class CollisionDamagingComponent(Component):
    """
    any collision involving an entity with this component will hurt the other entity for damage
    """
    name = 'CollisionDamagingComponent'

    def __init__(self, damage):
        Component.__init__(self)

        self.damage = damage
