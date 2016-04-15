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

sprite_list = []
sheet = pygame.image.load("runningcat.png").convert()
for i in range(0, 4):
    src_width = int(1024 / 2)
    src_height = int(1024 / 4)

    src_x = (i % 2) * src_width
    src_y = i * src_height

    surf = pygame.Surface((src_width, src_height))
    surf.blit(sheet, (0, 0), (src_x, src_y, src_width, src_height))

    sprite_list.append(surf)

sprites = {
    'running': sprite_list
}

player_input = InputComponent()
player_pos = PositionComponent((width - ball_rect.width) / 2, (height - ball_rect.height) / 2)
player = Entity([player_pos,
                 player_input,
                 MovementComponent(),
                 BoundsComponent(ball_rect),
                 AttackComponent(),
                 DirectionComponent(),
                 AnimatedSpriteComponent(sprites, 'running')])

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

    graphics_system(entities, output=screen)

    # screen.blit(ball, (player_pos.posx, player_pos.posy))
    pygame.display.flip()
