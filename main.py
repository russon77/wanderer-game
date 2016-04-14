import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *

pygame.init()

fps_clock = pygame.time.Clock()

size = width, height = 640, 480
black = 0, 0, 0

ball = pygame.image.load("ball.bmp")
ball_rect = ball.get_rect()

player_input = InputComponent()
player_pos = PositionComponent((width - ball_rect.width) / 2, (height - ball_rect.height) / 2)
player = Entity([player_pos,
                 player_input,
                 MovementComponent(),
                 BoundsComponent(ball_rect),
                 AttackComponent(),
                 DirectionComponent()])

entities = [player]
systems = [movement_system, input_system, aging_system]

screen = pygame.display.set_mode(size)

while True:
    key_transitions = {}

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type in [KEYDOWN, KEYUP]:
            key_transitions[event.key] = event.type == KEYDOWN  # True for key pressed down, False for released

    delta = fps_clock.tick(60)

    player_input.keys = key_transitions
    for system in systems:
        system(entities, delta_time=delta)

    screen.fill(black)
    screen.blit(ball, (player_pos.posx, player_pos.posy))
    pygame.display.flip()
