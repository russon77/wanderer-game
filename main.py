import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *

pygame.init()

size = width, height = 640, 480
black = 0, 0, 0

screen = pygame.display.set_mode(size)

fps_clock = pygame.time.Clock()

ball = pygame.image.load("ball.bmp")
ball_rect = ball.get_rect()


sprites = {
    STATE_MOVING: [],
    STATE_ATTACKING: [],
    STATE_STANDING_STILL: []
}

sheet = pygame.image.load("standing.png").convert()
for i in range(0, 3):
    src_width = int(160 / 3)
    src_height = 80

    src_x = i * src_width
    src_y = 0

    surf = pygame.Surface((src_width, src_height))
    surf.blit(sheet, (0, 0), (src_x, src_y, src_width, src_height))

    sprites[STATE_STANDING_STILL].append(surf)


sheet = pygame.image.load("walking.png").convert()
for i in range(0, 4):
    src_width = int(220 / 4)
    src_height = 80

    src_x = i * src_width
    src_y = 0

    surf = pygame.Surface((src_width, src_height))
    surf.blit(sheet, (0, 0), (src_x, src_y, src_width, src_height))

    sprites[STATE_MOVING].append(surf)

sheet = pygame.image.load("attacking.png").convert()
for i in range(0, 3):
    src_width = int(220 / 3)
    src_height = 80
    src_x = i * src_width
    src_y = 0

    surf = pygame.Surface((src_width, src_height))
    surf.blit(sheet, (0, 0), (src_x, src_y, src_width, src_height))

    sprites[STATE_ATTACKING].append(surf)

player_input = InputComponent()
player_pos = PositionComponent((width - ball_rect.width) / 2, (height - ball_rect.height) / 2)
player = Entity([player_pos,
                 player_input,
                 MovementComponent(),
                 BoundsComponent(ball_rect),
                 AttackComponent(),
                 DirectionComponent(),
                 AnimatedSpriteComponent(sprites, STATE_STANDING_STILL, 200)])

entities = [player]
systems = [movement_system, input_system, aging_system, graphics_system]

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
