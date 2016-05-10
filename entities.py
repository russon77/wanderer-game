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
            HealthComponent(100),
            PlayerComponent()
        ]
    )


def DummyEntity(initial_position, damage=False, knockback=False):
    comps = [
        AnimatedSpriteComponent(loader.load_target_dummy()),
        BoundsComponent(Rect(initial_position, (64, 64))),
    ]

    if damage:
        comps.append(CollisionDamagingComponent(damage))

    if knockback:
        comps.append(CollisionKnockbackComponent(*knockback))

    return Entity(comps)


def CobraEntity(initial_position):
    return Entity(
        [
            AnimatedSpriteComponent(loader.load_cobra_sprites(), STATE_STANDING_STILL_SOUTH, 150),
            BoundsComponent(Rect(initial_position, (96, 96))),
            MovementComponent(),
            DirectionComponent(),
            HealthComponent(100),
            AutomatonComponent(PERSONALITY_AGGRESSIVE),
            AttributesComponent({
                ATTRIBUTES_AGGRO_RANGE: 300,
                ATTRIBUTES_ATTACK_RANGE: 50,
                ATTRIBUTES_MOVE_SPEED: 0.09
            }),
            CollisionKnockbackComponent(0.8, 10),
            CollisionDamagingComponent(5)
        ]
    )


def PlayerAttackEntity(attacker):
    direction = attacker.components.get(DirectionComponent.name)
    pos = attacker.components.get(BoundsComponent.name)

    abounds = Rect(0, 0, 0, 0)
    atype = 'horizontal'

    if direction is not None:
        if direction.direction == DirectionComponent.East:
            abounds.width = pos.bounds.width
            abounds.height = abounds.width / 2

            abounds.centery = pos.bounds.centery
            abounds.centerx = pos.bounds.right

        elif direction.direction == DirectionComponent.West:
            abounds.width = pos.bounds.width
            abounds.height = abounds.width / 2

            abounds.centery = pos.bounds.centery
            abounds.centerx = pos.bounds.left

        elif direction.direction == DirectionComponent.North:
            abounds.height = pos.bounds.height
            abounds.width = abounds.height / 2

            abounds.centerx = pos.bounds.x + pos.bounds.width / 2
            abounds.centery = pos.bounds.top

            atype = 'vertical'

        elif direction.direction == DirectionComponent.South:
            abounds.height = pos.bounds.height
            abounds.width = abounds.height / 2

            abounds.centerx = pos.bounds.x + pos.bounds.width / 2
            abounds.centery = pos.bounds.bottom

            atype = 'vertical'

        return Entity(
            [
                BoundsComponent(abounds),
                CollisionDamagingComponent(10),
                CollisionKnockbackComponent(0.5, 100),
                TimeToLiveComponent(100),
                CollisionIgnoreComponent([attacker]),
                SpriteComponent(loader.load_attack_sprite(atype))
            ]
        )
