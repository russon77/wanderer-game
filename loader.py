import pygame
import os
from glob import glob
from functools import lru_cache
from pytmx import *
from ast import literal_eval

from constants import *
from components import *
import entities as entities_mod
from graphics import *


@lru_cache()
def load_sprite_file(name, num):
    sheet = pygame.image.load(os.path.join('./', name)).convert_alpha()

    bounds = sheet.get_rect()

    sprites = []

    for i in range(0, num):
        src_width = int(bounds.width / num)
        src_height = bounds.height

        src_x = i * src_width
        src_y = 0

        surf = pygame.Surface((src_width, src_height), pygame.SRCALPHA, 32)
        surf.blit(sheet, (0, 0), (src_x, src_y, src_width, src_height))

        sprites.append(surf)

    return sprites


def load_multi_row_sprite_file(name, sprite_size, indices, sprites_per_row=None):
    """
    this will take a sprite sheet with m by n sprites, where number of sprites per row is the same for every row
    Args:
        name: name of file to access
        sprite_size: tuple of (width, height) representing size of individual sprite
        indices: array of hashable values to index the result sprite rows (in order)

    Returns:

    """
    sheet = pygame.image.load(os.path.join('./', name)).convert_alpha()

    bounds = sheet.get_rect()

    sprite_width, sprite_height = sprite_size

    if sprites_per_row is None:
        sprites_per_row = int(bounds.width / sprite_width)

    num_rows = len(indices)

    sprite_dict = {}

    for row in range(0, num_rows):
        sprites = []

        for i in range(0, sprites_per_row):

            src_x = i * sprite_width
            src_y = row * sprite_height

            surf = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA, 32)
            surf.blit(sheet, (0, 0), (src_x, src_y, sprite_width, sprite_height))

            sprites.append(surf)

        sprite_dict[ indices[row] ] = sprites

    return sprite_dict


def load_cobra_sprites():
    keys = [
        STATE_MOVING_NORTH,
        STATE_MOVING_EAST,
        STATE_MOVING_SOUTH,
        STATE_MOVING_WEST
    ]

    sprites = load_multi_row_sprite_file("data/cobra/king_cobra.png", (96, 96), keys)

    more_keys = [
        STATE_STANDING_STILL_NORTH,
        STATE_STANDING_STILL_EAST,
        STATE_STANDING_STILL_SOUTH,
        STATE_STANDING_STILL_WEST
    ]

    more_sprites = load_multi_row_sprite_file("data/cobra/king_cobra.png", (96, 96), more_keys, 1)

    return {**sprites, **more_sprites}


def load_target_dummy():
    return {
        STATE_STANDING_STILL: load_sprite_file("data/target_dummy/combat_dummy.png", 8)
    }


def load_player_sprites():
    sprites = {
        STATE_ATTACKING_NORTH: load_sprite_file("data/human/attacking_north.png", 8),
        STATE_ATTACKING_SOUTH: load_sprite_file("data/human/attacking_south.png", 8),
        STATE_ATTACKING_EAST: load_sprite_file("data/human/attacking_east.png", 8),
        STATE_ATTACKING_WEST: load_sprite_file("data/human/attacking_west.png", 8),

        STATE_STANDING_STILL_NORTH: load_sprite_file("data/human/standing_still_north.png", 1),
        STATE_STANDING_STILL_SOUTH: load_sprite_file("data/human/standing_still_south.png", 1),
        STATE_STANDING_STILL_EAST: load_sprite_file("data/human/standing_still_east.png", 1),
        STATE_STANDING_STILL_WEST: load_sprite_file("data/human/standing_still_west.png", 1),

        STATE_MOVING_NORTH: load_sprite_file("data/human/walking_north.png", 9),
        STATE_MOVING_SOUTH: load_sprite_file("data/human/walking_south.png", 9),
        STATE_MOVING_EAST: load_sprite_file("data/human/walking_east.png", 9),
        STATE_MOVING_WEST: load_sprite_file("data/human/walking_west.png", 9)

    }

    return sprites


def load_entities_from_tiled_renderer(tr):
    entities = []

    for layer in tr.tmx_data.visible_layers:
        if isinstance(layer, TiledObjectGroup):
            for obj in layer:

                # check if object is a pre-defined type
                obj_type = obj.properties.get('obj_type')
                if obj_type is not None:
                    if obj_type == 'dummy':
                        # check for dummy options: damage, knockback
                        # this fancy auto-loader only works for components that require a single value
                        extra = {
                            'damage': False,
                            'knockback': False
                        }

                        for key in extra:
                            val = obj.properties.get(key)
                            if val is not None:
                                extra[key] = literal_eval(val)

                        entities.append(entities_mod.DummyEntity((obj.x, obj.y), **extra))
                    elif obj_type == 'cobra':
                        entities.append(entities_mod.CobraEntity((obj.x, obj.y)))

                    continue

                # otherwise, create the custom Entity according to its properties
                comps = []

                comps.append(BoundsComponent(Rect(obj.x, obj.y, obj.width, obj.height)))

                for key in obj.properties.keys():
                    # pseudo switch statement
                    if key == 'damage':
                        comps.append(CollisionDamagingComponent(int(obj.properties[key])))
                    elif key == 'solid' and obj.properties[key]:
                        comps.append(CollisionSolidComponent())
                    elif key == 'input' and obj.properties[key]:
                        comps.append(InputComponent())
                    elif key == 'transition':
                        target_x = obj.properties.get('target_x')
                        target_y = obj.properties.get('target_y')
                        if target_x is not None and target_y is not None:
                            comps.append(CollisionTransitionComponent(obj.properties[key], int(target_x), int(target_y)))

                entities.append(entities_mod.Entity(comps))

    return entities


def load_map_files():
    res = {}

    for file in glob(os.path.join('./', 'data/places/*')):
        tr = TiledRenderer(file)
        res[tr.tmx_data.properties['id']] = tr

        if tr.tmx_data.properties.get('default'):
            res['default'] = tr

    return res
