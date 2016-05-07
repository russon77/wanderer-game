import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *
from loader import *
from graphics import *

pygame.init()

size = width, height = 640, 480
black = 0, 0, 0

screen = pygame.display.set_mode(size)

fps_clock = pygame.time.Clock()

# load our map(s)
world = load_map_files()

# get objects from TiledRenderer, convert them to Entities, and add to entities list
entities = []
entities.extend(load_entities_from_tiled_renderer(world['default']))

# load the ui
ui = UserInterface()

# load and initialize entities
sprites = load_player_sprites()

# initialize the player
player = PlayerEntity((40, 360))

entities.extend([player])
systems = \
    [
        aging_system,
        input_system,
        direction_system,
        direction_movement_animation_system,
        movement_system,
        graphics_system
    ]

while True:
    key_transitions = {}

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type in [KEYDOWN, KEYUP]:
            key_transitions[event.key] = event.type == KEYDOWN  # True for key pressed down, False for released

    delta = fps_clock.tick(60)

    screen.fill(black)

    world['default'].render_map(screen)

    try:
        for system in systems:
            system(entities, delta_time=delta, key_transitions=key_transitions, world=world, player=player)
    except MapChangeException:
        # in case of the map change, we do not want to continue processing -- we can do that after the world has been
        #  changed
        pass

    graphics_system(entities, output=screen, delta_time=delta)

    ui.render(screen, player)
    pygame.display.flip()
