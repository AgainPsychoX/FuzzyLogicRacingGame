import pygame
import math

car_image = pygame.transform.scale(pygame.image.load('car.png'), (33, 22))

class Car(pygame.sprite.Sprite):
    MAX_VELOCITY_FORWARD = 200
    MAX_VELOCITY_BACKWARD = 20
    ACCELERATION_FACTOR_FORWARD = 100
    ACCELERATION_FACTOR_BACKWARD = 100
    BRAKING_FACTOR = 100
    IDLE_DECAY_FACTOR = 5
    STEER_DECAY_FACTOR = 5

    def __init__(self, position):
        super().__init__()
        self.base_image = car_image
        self.position = list(position)
        self.velocity = 0
        self.angle = 0 # radians
        self.total_velocity = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if self.velocity < 0:
                self.brake(dt * Car.BRAKING_FACTOR)
            else:
                self.accelerate(dt * Car.ACCELERATION_FACTOR_FORWARD * (1.1 - self.velocity / Car.MAX_VELOCITY_FORWARD))
                self.velocity = min(self.velocity, Car.MAX_VELOCITY_FORWARD)
        if keys[pygame.K_DOWN]:
            if self.velocity > 0:
                self.brake(dt * Car.BRAKING_FACTOR)
            else:
                self.accelerate(-dt * Car.ACCELERATION_FACTOR_BACKWARD * (1.1 - self.velocity / Car.MAX_VELOCITY_BACKWARD))
                self.velocity = max(-Car.MAX_VELOCITY_BACKWARD, self.velocity)
        if keys[pygame.K_LEFT]:
            self.rotate(math.radians(dt * 100))
            self.brake(dt * Car.STEER_DECAY_FACTOR)
        if keys[pygame.K_RIGHT]:
            self.rotate(-math.radians(dt * 100))
            self.brake(dt * Car.STEER_DECAY_FACTOR)

        # speed decay
        self.brake(dt * Car.IDLE_DECAY_FACTOR)

        self.position[0] += self.velocity * math.sin(self.angle) * dt
        self.position[1] += self.velocity * math.cos(self.angle) * dt

        self.image = pygame.transform.rotate(self.base_image, math.degrees(self.angle) - 90)
        self.rect = self.image.get_rect(center=self.position)

    def accelerate(self, value):
        self.velocity += value

    def brake(self, value):
        s = math.copysign(1.0, self.velocity)
        self.velocity = s * max(0, abs(self.velocity) - value)

    def rotate(self, angle_delta):
        self.angle += angle_delta
