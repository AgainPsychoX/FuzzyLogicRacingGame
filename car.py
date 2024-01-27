import pygame
import math

from map import Coordinate

car_image = pygame.transform.scale(pygame.image.load('car.png'), (33, 22))

class Car(pygame.sprite.Sprite):
    MAX_VELOCITY_FORWARD = 200
    MAX_VELOCITY_BACKWARD = 20
    ACCELERATION_FACTOR_FORWARD = 100
    ACCELERATION_FACTOR_BACKWARD = 100
    BRAKING_FACTOR = 100
    IDLE_DECAY_FACTOR = 5
    STEER_DECAY_FACTOR = 5

    def __init__(self, position: Coordinate, angle: float = 0):
        super().__init__()
        self.base_image = car_image
        self.position = list(position)
        self.velocity: float = 0
        self.angle = angle # radians

    def update(self, dt: float):
        # speed decay
        self.brake(dt * Car.IDLE_DECAY_FACTOR)

        self.position[0] += self.velocity * math.sin(self.angle) * dt
        self.position[1] += self.velocity * math.cos(self.angle) * dt

        self.image = pygame.transform.rotate(self.base_image, math.degrees(self.angle) - 90)
        self.rect = self.image.get_rect(center=self.position)

    def accelerate(self, value: float):
        self.velocity += value

    def brake(self, value: float):
        s = math.copysign(1.0, self.velocity)
        self.velocity = s * max(0, abs(self.velocity) - value)

    def rotate(self, angle_delta: float):
        self.angle += angle_delta

class CarController():
    def __init__(self, car: Car):
        self.car = car
        self.brake: float = 0
        self.gas: float = 0
        self.steer: float = 0

    def update(self, dt: float, *args, **kwargs):
        self.brake = max(0, min(1, self.brake))
        self.gas   = max(-1, min(1, self.gas))
        self.steer = max(-1, min(1, self.steer))

        # TODO: smooth gas
        if self.gas > 0:
            if self.car.velocity < 0:
                self.car.brake(dt * Car.BRAKING_FACTOR)
            else:
                self.car.accelerate(dt * Car.ACCELERATION_FACTOR_FORWARD * (1.1 - self.car.velocity / Car.MAX_VELOCITY_FORWARD))
                self.car.velocity = min(self.car.velocity, Car.MAX_VELOCITY_FORWARD)
        elif self.gas < 0:
            if self.car.velocity > 0:
                self.car.brake(dt * Car.BRAKING_FACTOR)
            else:
                self.car.accelerate(-dt * Car.ACCELERATION_FACTOR_BACKWARD * (1.1 - self.car.velocity / Car.MAX_VELOCITY_BACKWARD))
                self.car.velocity = max(-Car.MAX_VELOCITY_BACKWARD, self.car.velocity)

        if self.brake > 0:
            self.car.brake(dt * Car.BRAKING_FACTOR * self.brake)

        if self.steer != 0:
            self.car.rotate(math.radians(dt * 100) * self.steer)
            self.car.brake(dt * Car.STEER_DECAY_FACTOR)
