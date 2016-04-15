from components import *
from entities import *
from constants import *
from pygame.locals import *


def relevant_entities(entities, required_components, optional_components=list(), disallowed_components=list()):
    for item in entities:
        requirements = [comp in item.components for comp in required_components]
        if all(requirements):
            optionalments = [optional[0] in item.components or optional[1] in item.components
                             for optional in optional_components]
            if all(optionalments):
                disallowed = [comp in item.components for comp in disallowed_components]
                if not any(disallowed):
                    yield item


def movement_system(entities, delta_time=0):
    # only want to process entities who have a PositionComponent and either Movement or Acceleration Component

    # for now, we aren't worrying about acceleration. that will come later todo or another system
    requirements = [PositionComponent.name, MovementComponent.name]
    optionals = [(MovementComponent.name, AccelerationComponent.name)]

    for entity in relevant_entities(entities, requirements):
        pos = entity.components[PositionComponent.name]
        mov = entity.components[MovementComponent.name]

        # move according to forever-velocities (aka constant-time)
        pos.move(mov.velx, mov.vely, delta_time)

        # move according to dynamic-velocities (aka will be removed after time runs out)
        # todo how to age dynamic movements?
        for dyn in mov.dynamic:
            pos.move(*dyn)

        # todo purge any stale dynamic movements


def input_system(entities, delta_time=0):
    """
    for each entity that has an input component, take the appropriate action by the component's state

    an input component has a list of keys and their change (True for pressed down, or False or released)

    since the input component is cleared after each run through, this can also be used just as effectively with one-off
     inputs like cast-spell or attack
    """
    for entity in relevant_entities(entities, [InputComponent.name]):
        comp = entity.components[InputComponent.name]

        movement = entity.components.get(MovementComponent.name)

        if movement is not None:
            left = comp.keys.get(K_LEFT)
            if left == True:  # add `left` movement
                movement.add_constant(-PLAYER_MOVE_SPEED, 0)
            elif left == False:  # remove left movement
                movement.add_constant(PLAYER_MOVE_SPEED, 0)

            right = comp.keys.get(K_RIGHT)
            if right == True:  # add `right` movement
                movement.add_constant(PLAYER_MOVE_SPEED, 0)
            elif right == False:  # remove right movement
                movement.add_constant(-PLAYER_MOVE_SPEED, 0)

            up = comp.keys.get(K_UP)
            if up == True:  # add `up` movement
                movement.add_constant(0, PLAYER_MOVE_SPEED)
            elif up == False:  # remove up movement
                movement.add_constant(0, -PLAYER_MOVE_SPEED)

            down = comp.keys.get(K_DOWN)
            if down == True:  # add `down` movement
                movement.add_constant(0, -PLAYER_MOVE_SPEED)
            elif down == False:  # remove down movement
                movement.add_constant(0, PLAYER_MOVE_SPEED)

        attack = entity.components.get(AttackComponent.name)
        direction = entity.components.get(DirectionComponent.name)
        position = entity.components.get(PositionComponent.name)

        # todo implement attacks other than spin attack
        if attack is not None and direction is not None and position is not None:
            space = comp.keys.get(K_SPACE)
            if space == True:
                # attack!
                width, height = attack.ar, attack.ar  # attack radius
                posx, posy = (position.posx - width) / 2, (position.posy - height) / 2
                attack_bounds = Rect(posx, posy, width, height)
                entities.append(Entity([PositionComponent(posx, posy),
                                        BoundsComponent(attack_bounds),
                                        DamageComponent(attack.damage),
                                        TimeToLiveComponent(1.5)]))  # todo change magic number to constant

                animation = entity.components.get(AnimatedSpriteComponent.name)
                if animation is not None:
                    # fixme this is tightly coupled with some magic, think of a different way?
                    # for now states will be enumerated in constants
                    key = STATE_ATTACKING + direction.direction
                    animation.set_state(key)

                print("Player attacked!")

        # after processing, remove all keys
        # todo this may be unnecessary
        comp.keys = {}


def aging_system(entities, delta_time=0):
    to_remove = []
    for entity in relevant_entities(entities, [TimeToLiveComponent.name]):
        ttl_comp = entity.components[TimeToLiveComponent.name]
        if ttl_comp.advance(delta_time):
            to_remove.append(entity)

    [entities.remove(x) for x in to_remove]

mss_rate = 3


def monster_spawn_system(entities, global_timer=1):
    if global_timer % mss_rate == 0:
        # spawn a monster!
        entities.append(
            [
                PositionComponent(),
                MovementComponent(),
                DamageComponent(1)
            ]
        )

        print("Spawned a monster!")

