import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *
from loader import load_player_sprites

pygame.init()

size = width, height = 640, 480
black = 0, 0, 0

screen = pygame.display.set_mode(size)

fps_clock = pygame.time.Clock()

ball = pygame.image.load("ball.bmp")
ball_rect = ball.get_rect()


sprites = load_player_sprites()

player_input = InputComponent()
player_pos = PositionComponent((width - ball_rect.width) / 2, (height - ball_rect.height) / 2)
player = Entity([player_pos,
                 player_input,
                 MovementComponent(),
                 BoundsComponent(ball_rect),
                 AttackComponent(),
                 DirectionComponent(),
                 AnimatedSpriteComponent(sprites, STATE_MOVING_EAST, 100)])

entities = [player]
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

    player_input.keys = key_transitions

    screen.fill(black)

    for system in systems:
        system(entities, delta_time=delta)

    graphics_system(entities, output=screen, delta_time=delta)

    # screen.blit(ball, (player_pos.posx, player_pos.posy))
    pygame.display.flip()
