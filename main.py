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

screen = pygame.display.set_mode((map_image.get_width(), map_image.get_height()))
pygame.display.set_caption("Fuzzy Racing Game")

try:
    my_font = pygame.font.SysFont('consolas', 16)
except:
    my_font = pygame.font.SysFont('dejavusansmono', 16)
    pass

clock = pygame.time.Clock()

car = Car((screen.get_width() // 2, screen.get_height() // 2))
car.angle = math.radians(90)

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

    all_sprites.update(dt=dt)

    screen.blit(map_image, (0, 0))
    all_sprites.draw(screen)

    text_surface = my_font.render(f'velocity: {car.velocity:.2f}', True, (0, 0, 0))
    screen.blit(text_surface, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()
