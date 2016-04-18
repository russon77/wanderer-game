from components import *
from entities import *
from constants import *
from pygame.locals import *


def relevant_entities(entities, required_components, optional_components=list(), disallowed_components=list()):
    # todo optional components should be lists of lists of components such that at least one component from each
    #  sublist is present in the entity
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
    requirements = [BoundsComponent.name, MovementComponent.name]
    optionals = [(MovementComponent.name, AccelerationComponent.name)]

    for entity in relevant_entities(entities, requirements):
        pos = entity.components[BoundsComponent.name]
        mov = entity.components[MovementComponent.name]

        # sums for which to ultimately apply change in position
        delta_x, delta_y = 0, 0

        # disallow self-drive n movement while rooted. dynamic movements can still be applied
        rooted = entity.components.get(RootedComponent.name)
        if rooted is None:
            # move according to forever-velocities (aka constant-time)
            delta_x += mov.velx
            delta_y += mov.vely

        # move according to dynamic-velocities (aka will be removed after time runs out)
        updated_dynamics = []
        for dyn in mov.dynamic:
            delta_x += dyn[0]
            delta_y += dyn[1]

            # purge any stale movements
            if dyn[2] - delta_time > 0.0:
                updated_dynamics.append((dyn[0], dyn[1], dyn[2] - delta_time))

        # it's not great, but it should work
        mov.dynamic = updated_dynamics

        # move will return a new Rect but not mutate the existing one
        new_pos = pos.bounds.move(delta_x * delta_time, delta_y * delta_time)

        if collision_system(new_pos, entity, entities):
            # finally, move the entity
            pos.bounds.move_ip(delta_x * delta_time, delta_y * delta_time)


def collision_system(new, current, entities):
    """
    collision system will be called by the movement system with the new position of one entity to compute against
    the other entities with a position and bounds component

    result of collision will be based on the collision-relevant traits of each entity

    Returns True if player can move
    """
    can_move = True
    for entity in relevant_entities(entities,
                                    [BoundsComponent.name],
                                    disallowed_components=[CollisionImmaterialComponent.name]):
        # do not process an entity's collision with itself
        if entity is current:
            continue

        target_bounds = entity.components[BoundsComponent.name].bounds
        # given the pygame.Rect object 'new' and the pygame.Rect object, check for collision!
        if target_bounds.colliderect(new):
            # does the entity have a collision component?
            # fixme don't allow units to take damage twice or anything
            solid = entity.components.get(CollisionSolidComponent.name)
            knockback = entity.components.get(CollisionKnockbackComponent.name)
            damaging = entity.components.get(CollisionDamagingComponent.name)

            if solid is not None:
                can_move = False

            if knockback is not None:
                # add in dynamic movement
                mov = current.components.get(MovementComponent.name)

                knockback_x, knockback_y = 0, 0

                if target_bounds.x > new.x:
                    knockback_x = -knockback.knockback
                elif target_bounds.x < new.x:
                    knockback_x = knockback.knockback
                elif target_bounds.y > new.y:
                    knockback_y = -knockback.knockback
                elif target_bounds.y < new.y:
                    knockback_y = knockback.knockback

                mov.add_dynamic(knockback_x, knockback_y, knockback.duration)

            if damaging is not None:
                # damage the `current` unit
                # todo this depends on unit health -- not yet implemented
                pass

    return can_move


def input_system(entities, **kwargs):
    """
    for each entity that has an input component, take the appropriate action by the component's state

    an input component has a list of keys and their change (True for pressed down, or False or released)

    since the input component is cleared after each run through, this can also be used just as effectively with one-off
     inputs like cast-spell or attack
    """
    for entity in relevant_entities(entities, [InputComponent.name]):
        comp = entity.components[InputComponent.name]

        # special testing action: reset position of player to center of screen
        pos = entity.components.get(BoundsComponent.name)

        if pos is not None:
            do_center = comp.keys.get(K_z)
            if do_center:
                pos.bounds.x, pos.bounds.y = 320, 320

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
        position = entity.components.get(BoundsComponent.name)
        debuff_cant_attack = entity.components.get(UnableToAttackComponent.name)

        # todo implement attacks other than spin attack
        if attack is not None and direction is not None and position is not None and debuff_cant_attack is None:
            space = comp.keys.get(K_SPACE)
            if space == True:
                # attack!
                width, height = attack.ar, attack.ar  # attack radius
                posx, posy = (position.bounds.x - width) / 2, (position.bounds.y - height) / 2
                attack_bounds = Rect(posx, posy, width, height)
                # todo make attacks a real thing

                animation = entity.components.get(AnimatedSpriteComponent.name)
                if animation is not None:
                    animation.set_state(STATE_ATTACKING + direction.direction, False)

                # player cannot move while attacking
                entity.components[RootedComponent.name] = RootedComponent(PLAYER_ATTACK_ANIMATION_DURATION)
                entity.components[UnableToAttackComponent.name] = \
                    UnableToAttackComponent(PLAYER_ATTACK_ANIMATION_DURATION)

                print("Player attacked!")

        # after processing, remove all keys
        # todo this may be unnecessary
        comp.keys = {}


def aging_system(entities, delta_time=0):
    # remove stale entities
    to_remove = []
    for entity in relevant_entities(entities, [TimeToLiveComponent.name]):
        ttl_comp = entity.components[TimeToLiveComponent.name]
        if ttl_comp.advance(delta_time):
            to_remove.append(entity)

    [entities.remove(x) for x in to_remove]

    # remove stale components from entities
    for entity in entities:
        to_remove = []
        for key in entity.components.keys():
            if isinstance(entity.components[key], StatusComponent):
                if entity.components[key].advance(delta_time):
                    to_remove.append(key)

        for key in to_remove:
            del entity.components[key]


mss_rate = 3


def monster_spawn_system(entities, delta_time=0, global_timer=1):
    if global_timer % mss_rate == 0:
        # spawn a monster!
        entities.append(
            [
                MovementComponent()
            ]
        )

        print("Spawned a monster!")


def graphics_system(entities, output=None, delta_time=0):
    # can't do anything if we don't have a screen to draw to!
    if output is None:
        return

    # todo combine both static and dynamic through use of their shared "get_image()" interface

    # process animated entities
    for entity in relevant_entities(entities, [AnimatedSpriteComponent.name, BoundsComponent.name]):
        img = entity.components[AnimatedSpriteComponent.name].get_image(delta_time)
        pos = entity.components[BoundsComponent.name].bounds.x, entity.components[BoundsComponent.name].bounds.y

        output.blit(img, pos)

    # todo process static entries
    for entity in relevant_entities(entities, [SpriteComponent.name, BoundsComponent.name]):
        img = entity.components[SpriteComponent.name].get_image()
        pos = entity.components[BoundsComponent.name].bounds.x, entity.components[BoundsComponent.name].bounds.y

        output.blit(img, pos)


def direction_system(entities, **kwargs):
    for entity in relevant_entities(entities,
                                    [MovementComponent.name, DirectionComponent.name],
                                    disallowed_components=[RootedComponent.name]):  # if you're stuck, you're stuck!
        mov = entity.components[MovementComponent.name]
        dire = entity.components[DirectionComponent.name]

        if mov.velx < 0.0:
            dire.set(DirectionComponent.West)
        elif mov.velx > 0.0:
            dire.set(DirectionComponent.East)
        elif mov.vely < 0.0:
            dire.set(DirectionComponent.North)
        elif mov.vely > 0.0:
            dire.set(DirectionComponent.South)


def direction_movement_animation_system(entities, **kwargs):
    for entity in relevant_entities(entities,
                                    [MovementComponent.name, DirectionComponent.name, AnimatedSpriteComponent.name],
                                    disallowed_components=[RootedComponent.name]):  # if you're stuck, you're stuck!
        # seems to be working. will keep this here until a better way is found
        ani = entity.components[AnimatedSpriteComponent.name]
        mov = entity.components[MovementComponent.name]
        dire = entity.components[DirectionComponent.name]

        if mov.velx > 0.0 or mov.velx < 0.0 or mov.vely > 0.0 or mov.vely < 0.0:
            ani.set_state(STATE_MOVING + dire.direction, reset_index_on_duplicate=False)
        else:
            ani.set_state(STATE_STANDING_STILL + dire.direction, reset_index_on_duplicate=False)
