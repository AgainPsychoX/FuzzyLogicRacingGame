import pygame
import sys
import math

from car import Car

pygame.init()
pygame.font.init()

FPS = 60
MAX_WIDTH = 1600
MAX_HEIGHT = 900

map_image = pygame.image.load('maps/1.png') 
if map_image.get_width() > MAX_WIDTH or map_image.get_height() > MAX_HEIGHT:
    width_scaling_factor = MAX_WIDTH / map_image.get_width()
    height_scaling_factor = MAX_HEIGHT / map_image.get_height()
    scaling_factor = min(width_scaling_factor, height_scaling_factor)
    map_image = pygame.transform.scale(map_image, (int(map_image.get_width() * scaling_factor),
                                                   int(map_image.get_height() * scaling_factor)))

starting_position = (map_image.get_width() // 2, map_image.get_height() // 2)

screen = pygame.display.set_mode((map_image.get_width(), map_image.get_height()))
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

car = Car(starting_position)
car.angle = math.radians(90)

def cast_ray_to_wall(position, a):
    MAX_DISTANCE = 300
    dx, dy = math.sin(a), math.cos(a)
    for d in range(0, MAX_DISTANCE, 1):
        x = int(position[0] + d * dx)
        if x < 0 or map_image.get_width() <= x:
            return None
        y = int(position[1] + d * dy)
        if y < 0 or map_image.get_height() <= y:
            return None
        c = map_image.get_at((x, y))
        if c[1] > 100: # if green-ish
            return (d, a, x, y, c)
    return None

all_sprites = pygame.sprite.Group()
all_sprites.add(car)

running = True
while running:
    dt = clock.tick(FPS) / 1000 # s

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                car.position = list(starting_position)
                car.angle = math.radians(90)
                car.velocity = 0

    all_sprites.update(dt=dt)

    wall_sensors_angles = {
        'head': 0,
        'left': math.radians(30),
        'right': math.radians(-30),
    }

    screen.blit(map_image, (0, 0))
    all_sprites.draw(screen)

    wall_ray_casts = {k: cast_ray_to_wall(car.position, car.angle + v) 
                      for k, v in wall_sensors_angles.items()}

    for k, v in wall_ray_casts.items():
        if v is not None:
            pygame.draw.line(screen, (99, 20, 20), 
                             car.rect.center, (v[2], v[3]), 
                             width=2)

    draw_text(f'velocity={car.velocity:.1f}\n' +
              'walls distances:\n' + 
              '\n'.join([f'  {k}={v[0] if v is not None else "too far"}' 
                         for k, v in wall_ray_casts.items()]), 
              (0, 0), color=(255, 255, 255))

    pygame.display.flip()

pygame.quit()
sys.exit()
