import numpy as np
import skfuzzy
import skfuzzy.control

from map import RayCastResult
from car import Car, CarController

class FuzzyCarController(CarController):
    def __init__(self, car: Car):
        super().__init__(car)

        # TODO: more dynamic, based on sensor names/angles

        left = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'left')
        left['CLOSE']    = skfuzzy.trapmf(left.universe, [0, 0, 50, 150])
        left['AWAY']     = skfuzzy.trapmf(left.universe, [      50, 150, 200, 200])

        head = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'head')
        head['CLOSE']    = skfuzzy.trapmf(head.universe, [0, 0, 50, 150])
        head['AWAY']     = skfuzzy.trapmf(head.universe, [      50, 150, 200, 200])

        right = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'right')
        right['CLOSE']   = skfuzzy.trapmf(right.universe, [0, 0, 50, 150])
        right['AWAY']    = skfuzzy.trapmf(right.universe, [      50, 150, 200, 200])

        self.inputs = [left, head, right]

    def update(self, dt: float, sensors: dict[str, RayCastResult], *args, **kwargs):
        super().update(dt, *args, **kwargs)

    def draw(self, surface):
        pass
