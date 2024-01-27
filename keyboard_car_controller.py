import pygame

from car import Car, CarController

class KeyboardCarController(CarController):
    def __init__(self, car: Car):
        super().__init__(car)

    def update(self, dt: float, *args, **kwargs):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and keys[pygame.K_DOWN]:
            self.gas = 0.5
        elif keys[pygame.K_UP]:
            self.gas = 1
        elif keys[pygame.K_DOWN]:
            self.gas = -1
        else:
            self.gas = 0

        steer = 0
        if keys[pygame.K_LEFT]:
            steer += 1
        if keys[pygame.K_RIGHT]:
            steer -= 1
        self.steer = steer

        if keys[pygame.K_SPACE]:
            self.brake = 1
        else:
            self.brake = 0

        super().update(dt, *args, **kwargs)
