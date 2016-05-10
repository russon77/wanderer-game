import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *
from loader import *
from graphics import *

from game import play_game


def intro(screen, world):

    fps_clock = pygame.time.Clock()

    # load the ui
    ui = pygame.image.load(os.path.join('.', 'data', 'ui', 'intro_splash.png'))

    while True:

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type in (KEYDOWN, KEYUP):
                # start the game!
                play_game(screen, world)

        fps_clock.tick(60)

        screen.fill((0, 0, 0))

        screen.blit(ui, (0, 0))

        pygame.display.flip()
