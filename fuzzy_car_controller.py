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
        velocity['SLOW']    = skfuzzy.trapmf(velocity.universe, [0,    0,   0, 50])
        velocity['MEDIUM']  = skfuzzy.trapmf(velocity.universe, [50, 100, 100, 150])
        velocity['FAST']    = skfuzzy.trapmf(velocity.universe, [50, 200, 200, 200])

        balance = skfuzzy.control.Antecedent(np.arange(-200, 200 + 1, 1), 'balance')
        balance['LEFT']     = skfuzzy.trapmf(balance.universe, [-200, -200, -200, 0])
        balance['CENTER']   = skfuzzy.trapmf(balance.universe, [-50, 0, 0, 50])
        balance['RIGHT']    = skfuzzy.trapmf(balance.universe, [0, 200, 200, 200])

        side = skfuzzy.control.Antecedent(np.arange(-100, 100 + 1, 1), 'side')
        side['LEFT']    = skfuzzy.trapmf(side.universe, [-100, -100, -100, 0])
        side['CENTER']  = skfuzzy.trapmf(side.universe, [-25, 0, 0, 25])
        side['RIGHT']   = skfuzzy.trapmf(side.universe, [0, 100, 100, 100])

        head = skfuzzy.control.Antecedent(np.arange(0, 200 + 1, 1), 'head')
        head['CLOSE']   = skfuzzy.trapmf(head.universe, [ 0,  0,  25, 125])
        head['AWAY']    = skfuzzy.trapmf(head.universe, [75, 200, 200, 200])

        self.inputs = [velocity, balance, side, head]

    def setup_outputs(self):
        gas = skfuzzy.control.Consequent(np.arange(0 - 0.25, 1 + 0.02 + 0.25, 0.02), 'gas')
        gas['NONE'] = skfuzzy.sigmf(gas.universe, 0.05, -40)
        gas['SOFT'] = skfuzzy.sigmf(gas.universe, 0.33, -10)
        gas['HARD'] = skfuzzy.sigmf(gas.universe, 0.75, 20)

        brake = skfuzzy.control.Consequent(np.arange(0 - 0.25, 1 + 0.02 + 0.25, 0.02), 'brake')
        brake['NONE'] = skfuzzy.sigmf(brake.universe, 0.05, -40)
        brake['SOFT'] = skfuzzy.sigmf(brake.universe, 0.33, -10)
        brake['HARD'] = skfuzzy.sigmf(brake.universe, 0.75, 20)

        steer = skfuzzy.control.Consequent(np.arange(-1 - 0.5, 1 + 0.05 + 0.5, 0.05), 'steer')
        steer['RIGHT'] = skfuzzy.sigmf(steer.universe, -0.5, -10)
        steer['NONE']  = skfuzzy.gaussmf(steer.universe, 0, 0.10)
        steer['LEFT']  = skfuzzy.sigmf(steer.universe, 0.5, 10)

        self.outputs = [gas, brake, steer]

    def setup_control_system(self):
        c = skfuzzy.control
        velocity, balance, side, head = self.inputs
        gas, brake, steer = self.outputs

        self.control_system = c.ControlSystem([
            c.Rule(balance['LEFT'], steer['RIGHT']),
            c.Rule(balance['RIGHT'], steer['LEFT']),
            c.Rule(balance['CENTER'] & side['CENTER'], steer['NONE'] % 0.1),

            c.Rule(side['LEFT'], steer['RIGHT']),
            c.Rule(side['RIGHT'], steer['LEFT']),

            c.Rule(head['CLOSE'], (brake['HARD'], gas['NONE'])),
            c.Rule(head['AWAY'] & balance['CENTER'], (brake['NONE'], gas['HARD'])),
            c.Rule(head['AWAY'] & ~balance['CENTER'], (brake['NONE'], gas['SOFT'])),

            c.Rule(velocity['SLOW'], gas['SOFT']),
        ])

    def update_simulation(self, sensors: dict[str, RayCastResult]):
        self.simulation.input['velocity'] = self.car.velocity
        self.simulation.input['balance'] = sensors['left'].distance - sensors['right'].distance
        self.simulation.input['side'] = sensors['hard_left'].distance - sensors['hard_right'].distance
        self.simulation.input['head'] = sensors['head'].distance
        self.simulation.compute()
        self.gas = max(0, self.simulation.output['gas']) # other are properly clamped in the base car controller
        self.brake = self.simulation.output['brake']
        self.steer = self.simulation.output['steer']

    def update(self, dt: float, *args, **kwargs):
        # self.update_simulation(sensors) # need to be called separately
        super().update(dt, *args, **kwargs)

    def setup_visualization(self, width: float, height: float):
        velocity, balance, side, head = self.inputs
        gas, brake, steer = self.outputs

        dpi = 100 # assume it's default
        fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        gs = gridspec.GridSpec(3, 3, figure=fig)

        self.visualizers = [
            MyFuzzyVariableVisualizer(velocity, plt.subplot(gs[0, 2])),
            MyFuzzyVariableVisualizer(head,     plt.subplot(gs[1, 0])),
            MyFuzzyVariableVisualizer(balance,  plt.subplot(gs[1, 1])),
            MyFuzzyVariableVisualizer(side,     plt.subplot(gs[1, 2])),
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
