from components import *
from entities import *
from constants import *
from helpers import *
from pygame.locals import *
from math import sqrt


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


def movement_system(entities, delta_time=0, world=None, player=None, **kwargs):
    # only want to process entities who have a PositionComponent and either Movement or Acceleration Component

    # for now, we aren't worrying about acceleration. that will come later todo or another system
    requirements = [BoundsComponent.name, MovementComponent.name]

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

        # try:
        if collision_system(new_pos, entity, entities, world=world, player=player):
            # finally, move the entity
            pos.bounds.move_ip(delta_x * delta_time, delta_y * delta_time)
        # except MapChangeException:
        #     raise MapChangeException


def collision_system(new, current, entities, world, player):
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

        # check if this entity is on the current's ignore list
        ignore_list = entity.components.get(CollisionIgnoreComponent.name)
        if ignore_list is not None:
            cont = False
            for ignored in ignore_list.ignore_list:
                if ignored is current:
                    cont = True
            if cont:
                continue

        target_bounds = entity.components[BoundsComponent.name].bounds
        # given the pygame.Rect object 'new' and the pygame.Rect object, check for collision!
        if target_bounds.colliderect(new):
            # does the entity have a collision component?
            # fixme don't allow units to take damage twice or anything
            solid = entity.components.get(CollisionSolidComponent.name)
            knockback = entity.components.get(CollisionKnockbackComponent.name)
            damaging = entity.components.get(CollisionDamagingComponent.name)
            transition = entity.components.get(CollisionTransitionComponent.name)

            if solid is not None:
                can_move = False

            if knockback is not None:
                # add in dynamic movement
                mov = current.components.get(MovementComponent.name)

                # todo fix this
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
                health = current.components.get(HealthComponent.name)
                if health is not None:
                    health.modify(-damaging.damage)
                    # todo set player state to damaged / invulnerable
                    print("someone lost health!!")

            if transition is not None:
                # cause a transition to the next map
                map_transition(world, transition.target, transition.target_x, transition.target_y, entities, player)

    return can_move


def input_system(entities, key_transitions=None, world=None, player=None, **kwargs):
    """
    for each entity that has an input component, take the appropriate action by the component's state

    an input component has a list of keys and their change (True for pressed down, or False or released)

    since the input component is cleared after each run through, this can also be used just as effectively with one-off
     inputs like cast-spell or attack
    """
    if key_transitions is None:
        return

    for entity in relevant_entities(entities, [InputComponent.name]):

        # special testing action: reset position of player to center of screen
        pos = entity.components.get(BoundsComponent.name)

        if pos is not None:
            do_center = key_transitions.get(K_z)
            if do_center:
                pos.bounds.x, pos.bounds.y = 320, 320

        movement = entity.components.get(MovementComponent.name)

        if movement is not None:
            left = key_transitions.get(K_LEFT)
            if left == True:  # add `left` movement
                movement.add_constant(-PLAYER_MOVE_SPEED, 0)
            elif left == False:  # remove left movement
                movement.add_constant(PLAYER_MOVE_SPEED, 0)

            right = key_transitions.get(K_RIGHT)
            if right == True:  # add `right` movement
                movement.add_constant(PLAYER_MOVE_SPEED, 0)
            elif right == False:  # remove right movement
                movement.add_constant(-PLAYER_MOVE_SPEED, 0)

            up = key_transitions.get(K_UP)
            if up == True:  # add `up` movement
                movement.add_constant(0, PLAYER_MOVE_SPEED)
            elif up == False:  # remove up movement
                movement.add_constant(0, -PLAYER_MOVE_SPEED)

            down = key_transitions.get(K_DOWN)
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
            space = key_transitions.get(K_SPACE)
            if space == True:
                # attack!
                entities.append(AttackEntity(entity))

                animation = entity.components.get(AnimatedSpriteComponent.name)
                if animation is not None:
                    animation.set_state(STATE_ATTACKING + direction.direction, False)

                # player cannot move while attacking
                entity.components[RootedComponent.name] = RootedComponent(PLAYER_ATTACK_ANIMATION_DURATION)
                entity.components[UnableToAttackComponent.name] = \
                    UnableToAttackComponent(PLAYER_ATTACK_ANIMATION_DURATION)

                print("Player attacked!")

        # implement world transitions as a number pressed down
        if world is not None:
            key_to_num = {
                K_1: '1',
                K_2: '2',
                K_3: '3'
            }

            for key in key_to_num:
                val = key_transitions.get(key)
                if key_transitions.get(key):
                    try:
                        map_transition(world, key_to_num[key], 'x', entities, player)
                    except Exception:
                        return


def aging_system(entities, delta_time=0, **kwargs):
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


def death_system(entities, **kwargs):
    """

    Args:
        entities:
        **kwargs:

    Returns:

    """
    to_remove = []
    for entity in relevant_entities(entities, [HealthComponent.name]):
        health = entity.components[HealthComponent.name].current_health

        if health <= 0:
            # todo if this entity has a death animation, remove all components except for its Bounds and AnimatedSprite,
            # and give it a death timer (TTL component) equal to the length of the animation

            # fixme for now, simply eliminate the entity
            to_remove.append(entity)

    [entities.remove(entity) for entity in to_remove]

mss_rate = 3


def monster_spawn_system(entities, delta_time=0, global_timer=1, **kwargs):
    if global_timer % mss_rate == 0:
        # spawn a monster!
        entities.append(
            [
                MovementComponent()
            ]
        )

        print("Spawned a monster!")


def graphics_system(entities, output=None, delta_time=0, **kwargs):
    # can't do anything if we don't have a screen to draw to!
    if output is None:
        return

    # have to draw the entities in the correct order. any entity positioned 'below' another should be drawn afterward
    # todo move this somewhere else to be more efficient (if it becomes an issue)
    entities_to_draw = [entity for entity in relevant_entities(entities, [BoundsComponent.name], optional_components=[(AnimatedSpriteComponent.name, SpriteComponent.name)])]
    entities_to_draw.sort(
        key=lambda x: x.components[BoundsComponent.name].bounds.y,
        reverse=False
    )

    # process all entries
    for entity in entities_to_draw:
        img = entity.components.get(AnimatedSpriteComponent.name)
        if img is None:
            img = entity.components[SpriteComponent.name]

        img = img.get_image(delta_time=delta_time)
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


# todo implement change to flee personality here thru use of percent max health remaining on Entity
def automation_system(entities, **kwargs):
    for entity in relevant_entities(entities, [AutomatonComponent.name]):
        # get relevant components of our automaton Entity
        personality = entity.components[AutomatonComponent.name].personality
        mov = entity.components.get(MovementComponent.name)
        pos = entity.components.get(BoundsComponent.name)
        attributes = entity.components.get(AttributesComponent.name)

        # get components of the player entity
        # todo find closest enemy -- this isnt a great solution
        player = None
        for ent2 in relevant_entities(entities, [PlayerComponent.name]):
            player = ent2

        # in case something strange happens and there's no player available to act against,
        # we do not need to continue processing the system at all
        if player is None:
            return

        pos_player = player.components.get(BoundsComponent.name)

        # check if player is within aggro range. if not, continue loop
        aggro_range = attributes.vals.get(ATTRIBUTES_AGGRO_RANGE)
        move_speed = attributes.vals.get(ATTRIBUTES_MOVE_SPEED)

        if aggro_range is None:
            continue

        dist = sqrt(
            pow(pos_player.bounds.centerx - pos.bounds.centerx, 2) +
            pow(pos_player.bounds.centery - pos.bounds.centery, 2))

        if dist < aggro_range:

            if personality == PERSONALITY_FLEE:
                # run away from enemy
                delta_x = pos.bounds.centerx - pos_player.bounds.centerx
                delta_y = pos.bounds.centery - pos_player.bounds.centery

                if abs(delta_x) < 0.001:
                    velx = 0.0
                else:
                    velx = (delta_x / abs(delta_x)) * move_speed

                if abs(delta_y) < 0.001:
                    vely = 0.0
                else:
                    vely = -(delta_y / abs(delta_y)) * move_speed

                mov.reset_constant()

                mov.add_constant(velx, vely)

            elif personality == PERSONALITY_AGGRESSIVE:
                # if enemy is within attacking range
                attack_range = attributes.vals.get(ATTRIBUTES_ATTACK_RANGE)
                if attack_range and attack_range < dist:
                    attack = entity.components.get(AttackComponent.name)
                    if attack is not None:
                        pass
                        # if we are on attack cooldown: move away from enemy slowly

                        # else: perform an attack

                # else: move towards enemy
                delta_x = pos.bounds.centerx - pos_player.bounds.centerx
                delta_y = pos.bounds.centery - pos_player.bounds.centery

                if abs(delta_x) < 0.001:
                    velx = 0.0
                else:
                    velx = -(delta_x / abs(delta_x)) * move_speed

                if abs(delta_y) < 0.001:
                    vely = 0.0
                else:
                    vely = (delta_y / abs(delta_y)) * move_speed

                mov.reset_constant()

                mov.add_constant(velx, vely)

        else:
            # for now, just reset movement
            # todo enemies could patrol or pace around rooms
            mov.reset_constant()
