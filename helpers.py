from loader import load_entities_from_tiled_renderer
from components import *
from exceptions import MapChangeException


def map_transition(world, key, target_x, target_y, entities, player):
    """
    set 'default' key of world dict to next map

    reset Entities list, add in Player, and load objects from map
    """
    if key not in world:
        return

    world['default'] = world[key]

    entities.clear()

    entities.extend(load_entities_from_tiled_renderer(world['default']))

    entities.append(player)

    # todo set the player location according to how he entered the room
    loc = player.components.get(BoundsComponent.name)
    if loc is not None:
        loc.bounds.x = target_x
        loc.bounds.y = target_y

    raise MapChangeException


