from time import sleep
import pygame
import sys
import math
import numpy as np
import skfuzzy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
from fuzzy_car_controller import FuzzyCarController

from map import Map
from car import Car, CarController
from keyboard_car_controller import KeyboardCarController

matplotlib.use("Agg")

pygame.init()
pygame.font.init()

FPS = 60
MAX_WIDTH = 1600
MAX_HEIGHT = 900
CHARTS_AREA_WIDTH = 600

map = Map('maps/1.png', MAX_WIDTH - CHARTS_AREA_WIDTH, MAX_HEIGHT) 
map.default_wall_condition = lambda x_y, map : map.surface.get_at(x_y)[1] > 100 # green

screen = pygame.display.set_mode((map.width + CHARTS_AREA_WIDTH, map.height))
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

keyboard_car_controller = KeyboardCarController(car)
fuzzy_car_controller = FuzzyCarController(car)
car_controllers = [ fuzzy_car_controller, keyboard_car_controller ]
car_controller: CarController = car_controllers[1]

all_sprites = pygame.sprite.Group()
all_sprites.add(car)

visualizing = False
paused = False
do_step = False
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
            if event.key == pygame.K_p:
                paused = not paused
            if event.key == pygame.K_s:
                if paused:
                    do_step = True
            if event.key == pygame.K_v:
                visualizing = not visualizing
                sleep(0.100)

    wall_ray_casts = {k: map.cast_ray_to_wall(car.position, car.angle + v) 
                      for k, v in sensors_angles.items()}

    if not paused or do_step:
        try:
            fuzzy_car_controller.update_simulation(sensors=wall_ray_casts)
        except ValueError as error:
            print('Error updating simulation:', error)
            try:
                fuzzy_car_controller.simulation.print_state()
                # Note: requires manual adding str(x) to skfuzzy code in some places to (partially) work
                #   (like when it says about __format__ or something), then still it will error on defuzzification,
                #   but it still provides good explanation of the current state (without zero area consequent terms).
                # TODO: add pull request to skfuzzy to fix this issue?
            except ValueError as error:
                print('Further error printing out state:', error)
            sleep(99)

        car_controller.update(dt=dt)
        all_sprites.update(dt=dt)

        if do_step:
            if not visualizing:
                fuzzy_car_controller.simulation.print_state()
        do_step = False

    screen.blit(map.surface, (0, 0))
    all_sprites.draw(screen)

    for k, v in wall_ray_casts.items():
        v.draw(screen, pygame.Color(99, 20, 20), width=2)

    draw_text(f'FPS: {clock.get_fps():.1f} ' + ('(paused)' if paused else ''), 
              position=(0, 0), color=(255, 255, 255))

    if visualizing:
        fig = fuzzy_car_controller.visualize(width=CHARTS_AREA_WIDTH, height=map.height)
        canvas = agg.FigureCanvasAgg(fig)
        buffer, w_h = canvas.print_to_buffer()
        surf = pygame.image.frombuffer(buffer, w_h, "RGBA")
        screen.blit(surf, (map.width, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), (map.width, 0, CHARTS_AREA_WIDTH, map.height))

    pygame.display.flip()

pygame.quit()
sys.exit()
