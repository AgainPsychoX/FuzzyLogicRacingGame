from time import sleep
import pygame
import sys
import math
import numpy as np
import skfuzzy
import matplotlib
import matplotlib.pyplot as plt
from fuzzy_car_controller import FuzzyCarController

from map import Map
from car import Car, CarController
from keyboard_car_controller import KeyboardCarController

matplotlib.use('module://pygame_matplotlib.backend_pygame')

pygame.init()
pygame.font.init()

FPS = 60
MAX_WIDTH = 1600
MAX_HEIGHT = 900

map = Map('maps/1.png', MAX_WIDTH, MAX_HEIGHT) 
map.default_wall_condition = lambda x_y, map : map.surface.get_at(x_y)[1] > 100 # green

screen = pygame.display.set_mode((map.width, map.height))
pygame.display.set_caption("Fuzzy Racing Game")

try:
    my_font = pygame.font.SysFont('consolas', 16)
except:
    my_font = pygame.font.SysFont('dejavusansmono', 16)
    pass

def draw_text(
        text: str, 
        position, 
        font: pygame.font.Font = my_font, 
        surface: pygame.Surface = screen, 
        color: pygame.Color = (0, 0, 0)):
    position = list(position)
    for line in text.splitlines():
        text_surface = my_font.render(line, True, color)
        surface.blit(text_surface, position)
        position[1] += font.get_height()

clock = pygame.time.Clock()

car = Car(map.starting_position, map.starting_angle)

sensors_angles = {
    'head': math.radians(0),
    'left': math.radians(30),
    'right': math.radians(-30),
}

car_controllers = [
    FuzzyCarController(car),
    KeyboardCarController(car)
]
car_controller: CarController = car_controllers[0]

all_sprites = pygame.sprite.Group()
all_sprites.add(car)

running = True
while running:
    dt = clock.tick(FPS) / 1000 # s

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_r:
                car.position = list(map.starting_position)
                car.angle = map.starting_angle
                car.velocity = 0
            if event.key == pygame.K_c:
                car_controller = car_controllers[(car_controllers.index(car_controller) + 1) % len(car_controllers)]
                print(f'Switching to {type(car_controller).__name__}')
                sleep(0.100)

    wall_ray_casts = {k: map.cast_ray_to_wall(car.position, car.angle + v) 
                      for k, v in sensors_angles.items()}

    car_controller.update(dt=dt, sensors=wall_ray_casts)
    all_sprites.update(dt=dt)

    screen.blit(map.surface, (0, 0))
    all_sprites.draw(screen)

    for k, v in wall_ray_casts.items():
        v.draw(screen, pygame.Color(99, 20, 20), width=2)

    draw_text(f'velocity={car.velocity:.1f}\n' +
              'walls distances:\n' + 
              '\n'.join([f'  {k}={v.distance if v.hit else "too far"}' 
                         for k, v in wall_ray_casts.items()]), 
              (0, 0), color=(255, 255, 255))

    # TODO: draw fuzzy controller graphs for variables activation

    pygame.display.flip()

pygame.quit()
sys.exit()
