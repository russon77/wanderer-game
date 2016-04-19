import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *
from loader import load_player_sprites, load_target_dummy, load_entities_from_tiled_renderer
from graphics import TiledRenderer, UserInterface

pygame.init()

size = width, height = 640, 480
black = 0, 0, 0

screen = pygame.display.set_mode(size)

fps_clock = pygame.time.Clock()

# load our map(s)
renderer = TiledRenderer("data/initial_world.tmx")

# get objects from TiledRenderer, convert them to Entities, and add to entities list
entities = []
entities.extend(load_entities_from_tiled_renderer(renderer))

# load the ui
ui = UserInterface()

# load and initialize entities
sprites = load_player_sprites()

player_input = InputComponent()
player = Entity([BoundsComponent(Rect(width / 2, height / 2, 64, 64)),
                 player_input,
                 MovementComponent(),
                 AttackComponent(),
                 DirectionComponent(),
                 AnimatedSpriteComponent(sprites, STATE_MOVING_EAST, 100),
                 HealthComponent(100)
                 ])

dummy = Entity([
    BoundsComponent(Rect(10, 10, 64, 64)),
    AnimatedSpriteComponent(load_target_dummy()),
    CollisionKnockbackComponent(1, 250),
    CollisionDamagingComponent(10)
])

dummy2 = Entity([
    BoundsComponent(Rect(100, 100, 64, 64)),
    AnimatedSpriteComponent(load_target_dummy())
])

entities.extend([player, dummy, dummy2])
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

    renderer.render_map(screen)

    for system in systems:
        system(entities, delta_time=delta)

    graphics_system(entities, output=screen, delta_time=delta)

    ui.render(screen, player.components[HealthComponent.name])
    pygame.display.flip()
