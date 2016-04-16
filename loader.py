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


def load_player_sprites():
    sprites = {
        STATE_MOVING: load_sprite_file("walking.png", 4),
        STATE_ATTACKING: load_sprite_file("attacking.png", 3),
        STATE_STANDING_STILL: load_sprite_file("standing.png", 3),

        STATE_STANDING_STILL_NORTH: load_sprite_file("images/standing_still_north.png", 1),
        STATE_STANDING_STILL_SOUTH: load_sprite_file("images/standing_still_south.png", 1),
        STATE_STANDING_STILL_EAST: load_sprite_file("images/standing_still_east.png", 1),
        STATE_STANDING_STILL_WEST: load_sprite_file("images/standing_still_west.png", 1),

        STATE_MOVING_NORTH: load_sprite_file("images/walking_north.png", 4),
        STATE_MOVING_SOUTH: load_sprite_file("images/walking_south.png", 4),
        STATE_MOVING_EAST: load_sprite_file("images/walking_east.png", 4),
        STATE_MOVING_WEST: load_sprite_file("images/walking_west.png", 4)

    }

    return sprites
