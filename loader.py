import pygame
import os

from constants import *
from components import *


def load_sprite_file(name, num):
    sheet = pygame.image.load(os.path.join('./', name)).convert()

    bounds = sheet.get_rect()

    sprites = []

    for i in range(0, num):
        src_width = int(bounds.width / num)
        src_height = bounds.height

        src_x = i * src_width
        src_y = 0

        surf = pygame.Surface((src_width, src_height))
        surf.blit(sheet, (0, 0), (src_x, src_y, src_width, src_height))

        sprites.append(surf)

    return sprites


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
