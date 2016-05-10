import os
import pygame
from pygame.locals import *

from pytmx import *
from pytmx.util_pygame import load_pygame

from components import *
from exceptions import *

"""
copied from https://github.com/bitcraft/PyTMX
thanks to bitcraft!! <3
"""


class TiledRenderer(object):
    """
    Super simple way to render a tiled map
    """

    def __init__(self, filename):
        tm = load_pygame(filename)

        # self.size will be the pixel size of the map
        # this value is used later to render the entire map to a pygame surface
        self.pixel_size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm

    def render_map(self, surface):
        """ Render our map to a pygame surface
        Feel free to use this as a starting point for your pygame app.
        This method expects that the surface passed is the same pixel
        size as the map.
        Scrolling is a often requested feature, but pytmx is a map
        loader, not a renderer!  If you'd like to have a scrolling map
        renderer, please see my pyscroll project.
        """

        # fill the background color of our render surface
        if self.tmx_data.background_color:
            surface.fill(pygame.Color(self.tmx_data.background_color))

        # iterate over all the visible layers, then draw them
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                self.render_tile_layer(surface, layer)

            elif isinstance(layer, TiledObjectGroup):
                # self.render_object_layer(surface, layer)
                pass

            elif isinstance(layer, TiledImageLayer):
                self.render_image_layer(surface, layer)

    def render_tile_layer(self, surface, layer):
        # deref these heavily used references for speed
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        surface_blit = surface.blit

        # iterate over the tiles in the layer
        for x, y, image in layer.tiles():
            surface_blit(image, (x * tw, y * th))

    def render_object_layer(self, surface, layer):
        # deref these heavily used references for speed
        draw_rect = pygame.draw.rect
        draw_lines = pygame.draw.lines
        surface_blit = surface.blit

        # these colors are used to draw vector shapes,
        # like polygon and box shapes
        rect_color = (255, 0, 0)
        poly_color = (0, 255, 0)

        # iterate over all the objects in the layer
        for obj in layer:

            # objects with points are polygons or lines
            if hasattr(obj, 'points'):
                draw_lines(surface, poly_color, obj.closed, obj.points, 3)

            # some objects have an image
            # Tiled calls them "GID Objects"
            elif obj.image:
                surface_blit(obj.image, (obj.x, obj.y))

            # draw a rect for everything else
            # Mostly, I am lazy, but you could check if it is circle/oval
            # and use pygame to draw an oval here...I just do a rect.
            else:
                draw_rect(surface, rect_color,
                          (obj.x, obj.y, obj.width, obj.height), 3)

    def render_image_layer(self, surface, layer):
        if layer.image:
            surface.blit(layer.image, (0, 0))


class UserInterface(object):
    """
    render the user interface in the top left corner.

    currently this only includes the player health bar.

    should be extended to accept events or something, i.e. for the screen to flash red when player takes damage.
    """

    game_over_length = 500

    def __init__(self):
        # load user interface images
        self.full_bar = pygame.image.load(os.path.join('./', "data/ui/full_bar.png")).convert_alpha()

        self.empty_bar = pygame.image.load(os.path.join('./', "data/ui/empty_bar.png")).convert_alpha()

        self.game_over = pygame.image.load(os.path.join('./', "data/ui/game_over.png")).convert_alpha()

        self.invuln = pygame.image.load(os.path.join('./', "data/ui/invuln.png")).convert_alpha()

        self.time_to_show_game_over = 0

    def render(self, surface, player):
        health_comp = player.components[HealthComponent.name]
        # first draw the empty bar fully onto the screen. then draw a percentage of the full bar on top of it
        surface.blit(self.empty_bar, (10, 10))

        h = self.full_bar.get_height()
        w = self.full_bar.get_width()
        w *= health_comp.current_health / health_comp.max_health

        surface.blit(self.full_bar, (10, 10), (0, 0, w, h))

        if health_comp.current_health <= 0:
            surface.blit(self.game_over, (0, 0))
            self.time_to_show_game_over += 1

            if self.time_to_show_game_over > self.game_over_length:
                raise GameOverException

        invuln = player.components.get(InvulnerableComponent.name)
        if invuln is not None:
            surface.blit(self.invuln, (0, 0))
