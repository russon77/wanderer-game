from components import *
from constants import *

import loader


class Entity(object):
    def __init__(self, components=list()):
        self.components = {}
        for comp in components:
            self.components[comp.name] = comp


def PlayerEntity(initial_position):
    return Entity(
        [
            AnimatedSpriteComponent(loader.load_player_sprites(), STATE_MOVING_EAST, 100),
            InputComponent(),
            BoundsComponent(Rect(initial_position, (64, 64))),
            MovementComponent(),
            AttackComponent(),
            DirectionComponent(),
            HealthComponent(100)
        ]
    )
