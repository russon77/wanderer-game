import pygame
import sys
from pygame.locals import *

from entities import *
from components import *
from systems import *
from loader import *
from graphics import *

from intro import intro

pygame.init()

size = width, height = 640, 480
black = 0, 0, 0

screen = pygame.display.set_mode(size)

fps_clock = pygame.time.Clock()

# load our map(s)
world = load_map_files()

intro(screen, world)
