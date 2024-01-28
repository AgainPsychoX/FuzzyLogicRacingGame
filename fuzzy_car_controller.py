import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import skfuzzy
import skfuzzy.control

from map import RayCastResult
from car import Car, CarController
from visualization import MyFuzzyVariableVisualizer

class FuzzyCarController(CarController):
    def __init__(self, car: Car):
        super().__init__(car)

        self.fig = None

        # TODO: more dynamic, based on sensor names/angles
        self.setup_inputs()
        self.setup_outputs()
        self.setup_control_system()
        self.simulation = skfuzzy.control.ControlSystemSimulation(self.control_system)

    def setup_inputs(self):
        velocity = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'velocity')
        velocity['SLOW']    = skfuzzy.trapmf(velocity.universe, [0,    0,   0, 150])
        velocity['MEDIUM']  = skfuzzy.trapmf(velocity.universe, [50, 100, 100, 150])
        velocity['FAST']    = skfuzzy.trapmf(velocity.universe, [     50, 200, 200, 200])

        left = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'left')
        left['CLOSE']       = skfuzzy.trapmf(left.universe, [0,   0,   0, 150])
        left['AWAY']        = skfuzzy.trapmf(left.universe, [    50, 200, 200, 200])

        head = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'head')
        head['CLOSE']       = skfuzzy.trapmf(head.universe, [0,   0,   0, 150])
        head['AWAY']        = skfuzzy.trapmf(head.universe, [    50, 200, 200, 200])

        right = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'right')
        right['CLOSE']      = skfuzzy.trapmf(right.universe, [0,   0,   0, 150])
        right['AWAY']       = skfuzzy.trapmf(right.universe, [    50, 200, 200, 200])

        self.inputs = [velocity, left, head, right]

    def setup_outputs(self):
        gas = skfuzzy.control.Consequent(np.arange(0, 1 + 0.05, 0.05), 'gas')
        gas['NONE']         = skfuzzy.trapmf(gas.universe, [0, 0, 0, 0.25])
        gas['SOFT']         = skfuzzy.trapmf(gas.universe, [0, 0.5, 0.5, 1])
        gas['HARD']         = skfuzzy.trapmf(gas.universe, [0.75, 1, 1, 1])

        brake = skfuzzy.control.Consequent(np.arange(0, 1 + 0.05, 0.05), 'brake')
        brake['NONE']       = skfuzzy.trapmf(brake.universe, [0, 0, 0, 0.25])
        brake['SOFT']       = skfuzzy.trapmf(brake.universe, [0, 0.5, 0.5, 1])
        brake['HARD']       = skfuzzy.trapmf(brake.universe, [0.75, 1, 1, 1])

        steer = skfuzzy.control.Consequent(np.arange(-1, 1 + 0.05, 0.05), 'steer')
        steer['RIGHT']      = skfuzzy.trapmf(steer.universe, [-1, 0, 0, 0])
        steer['NONE']       = skfuzzy.gaussmf(steer.universe, 0, 0.25)
        steer['LEFT']       = skfuzzy.trapmf(steer.universe, [0, 0, 0, 1])

        self.outputs = [gas, brake, steer]

    def setup_control_system(self):
        c = skfuzzy.control
        velocity, left, head, right = self.inputs
        gas, brake, steer = self.outputs

        self.control_system = c.ControlSystem([
            c.Rule(left['CLOSE'], steer['RIGHT']),
            c.Rule(right['CLOSE'], steer['LEFT']),
            c.Rule(left['CLOSE'] & right['CLOSE'], steer['NONE']),
            c.Rule(left['AWAY'] & right['AWAY'], steer['NONE']),
            # c.Rule((left['AWAY'] & right['AWAY']) | (left['AWAY'] & left['AWAY']), steer['NONE']),

            c.Rule(head['CLOSE'], brake['HARD']),
            c.Rule(velocity['FAST'] & (left['CLOSE'] | right['CLOSE']), brake['SOFT']),

            c.Rule(left['AWAY'] & right['AWAY'] & head['AWAY'], (gas['HARD'], brake['NONE'])),
            c.Rule(head['AWAY'] & velocity['SLOW'], (gas['SOFT'], brake['NONE'])),
            c.Rule(~velocity['SLOW'], gas['NONE']),
        ])

    def update_simulation(self, sensors: dict[str, RayCastResult]):
        self.simulation.input['velocity'] = self.car.velocity
        self.simulation.input['left'] = sensors['left'].distance
        self.simulation.input['head'] = sensors['head'].distance
        self.simulation.input['right'] = sensors['right'].distance
        self.simulation.compute()
        self.gas = self.simulation.output['gas']
        self.brake = self.simulation.output['brake']
        self.steer = self.simulation.output['steer']

    def update(self, dt: float, *args, **kwargs):
        # self.update_simulation(sensors) # need to be called separately
        super().update(dt, *args, **kwargs)

    def setup_visualization(self, width: float, height: float):
        velocity, left, head, right = self.inputs
        gas, brake, steer = self.outputs

        dpi = 100 # assume it's default
        fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        gs = gridspec.GridSpec(3, 3, figure=fig)

        self.visualizers = [
            MyFuzzyVariableVisualizer(velocity, plt.subplot(gs[0, 2])),
            MyFuzzyVariableVisualizer(left,     plt.subplot(gs[1, 0])),
            MyFuzzyVariableVisualizer(head,     plt.subplot(gs[1, 1])),
            MyFuzzyVariableVisualizer(right,    plt.subplot(gs[1, 2])),
            MyFuzzyVariableVisualizer(gas,      plt.subplot(gs[2, 0])),
            MyFuzzyVariableVisualizer(brake,    plt.subplot(gs[2, 1])),
            MyFuzzyVariableVisualizer(steer,    plt.subplot(gs[2, 2])),
        ]
        self.fig = fig

        print('Done visualization setup')

    def visualize(self, width: float, height: float):
        if self.fig is None:
            self.setup_visualization(width, height)

        for v in self.visualizers:
            v.view(sim=self.simulation)

        return self.fig
