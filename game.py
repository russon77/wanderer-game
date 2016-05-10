import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *
from loader import *
from graphics import *
from exceptions import *


black = 0, 0, 0
initial_position = 40, 360


def play_game(screen, world):

    fps_clock = pygame.time.Clock()

    # get objects from TiledRenderer, convert them to Entities, and add to entities list
    entities = []
    entities.extend(load_entities_from_tiled_renderer(world['default']))

    # load the ui
    ui = UserInterface()

    # initialize the player
    player = PlayerEntity(initial_position)

    entities.append(player)
    systems = \
        [
            death_system,
            aging_system,
            input_system,
            automation_system,
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
            # in case of the map change, we do not want to continue processing --
            # we can do that after the world has been changed
            pass

        graphics_system(entities, output=screen, delta_time=delta)

        try:
            ui.render(screen, player)
        except GameOverException:
            return

        pygame.display.flip()
