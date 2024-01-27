from dataclasses import dataclass
import math
from typing import Callable, Sequence
import pygame

Coordinate = Sequence[float] # private from pygame._common
MapWallCondition = Callable[[Coordinate, 'Map'], bool]

# Source: https://stackoverflow.com/questions/9018016/how-to-compare-two-colors-for-similarity-difference/9085524#9085524
def color_distance_sq(p: pygame.Color, q: pygame.Color):
    p = pygame.Color(p)
    q = pygame.Color(q)
    r_mean = (p.r + q.r) // 2
    r = p.r - q.r
    g = p.g - q.g
    b = p.b - q.b
    return (((512+r_mean)*r*r)>>8) + 4*g*g + (((767-r_mean)*b*b)>>8)

@dataclass
class RayCastResult:
    start_position: Coordinate
    hit_position: Coordinate | None # none if missed
    angle: float # radians
    distance: int # steps, but works as distance as well; max distance used if missed

    @property
    def hit(self):
        return self.hit_position is not None

    def draw(self, surface, color: pygame.Color, width=1):
        if self.hit:
            pygame.draw.line(surface, color, self.start_position, self.hit_position, width)

class Map:
    def __init__(self, image, max_width, max_height):
        if isinstance(image, str):
            image = pygame.image.load(image) 
        if not isinstance(image, pygame.Surface):
            raise ValueError()

        width = image.get_width()
        height = image.get_height()

        if width > max_width or height > max_height:
            width_scaling_factor = max_width / width
            height_scaling_factor = max_height / height
            scaling_factor = min(width_scaling_factor, height_scaling_factor)
            image = pygame.transform.scale(image, (int(width * scaling_factor),
                                                   int(height * scaling_factor)))

        self.surface = image

        self.starting_position = (width // 2, height // 2)
        self.starting_angle = math.radians(90)
        # TODO: read starting position & angle from file somehow

        self.average_color = pygame.transform.average_color(image, image.get_rect())
        self.default_wall_condition: MapWallCondition = lambda x_y, map : \
            color_distance_sq(map.surface.get_at(x_y), map.average_color) < 33333

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()
    
    def cast_ray_to_wall(self, 
                         position: Sequence[float], 
                         angle: float, 
                         max_distance: int = 200, 
                         condition: MapWallCondition = None):
        if condition is None:
            condition = self.default_wall_condition
        dx, dy = math.sin(angle), math.cos(angle)
        x, y = position
        for distance in range(0, max_distance, 1):
            x += dx
            if x < 0 or self.width <= x:
                break # misses
            y += dy
            if y < 0 or self.height <= y:
                break # misses
            if condition((x, y), self):
                return RayCastResult(position, (x, y), angle, distance) # hit
        return RayCastResult(position, None, angle, max_distance) # missed
