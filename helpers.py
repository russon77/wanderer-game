from loader import load_entities_from_tiled_renderer
from components import *


def map_transition(world, key, ttype, entities, player):
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
        if ttype == 'x':
            loc.bounds.x = world['default'].pixel_size[0] - loc.bounds.x - loc.bounds.width
        elif ttype == 'y':
            loc.bounds.y = world['default'].pixel_size[1] - loc.bounds.y - loc.bounds.height

    raise Exception


