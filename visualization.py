"""
Code in this file is adapting parts of original skfuzzy/control/visualization 
from scikit-fuzzy 0.4.2, in hopes to improve performance and visuals.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from skfuzzy.fuzzymath.fuzzy_ops import interp_membership
from skfuzzy.control.fuzzyvariable import FuzzyVariable, Term
from skfuzzy.control.controlsystem import CrispValueCalculator, ControlSystem, ControlSystemSimulation


class MyFuzzyVariableVisualizer(object):
    def __init__(self, fuzzy_var, ax=None, fig=None):
        """
        Initialize the fuzzy variable plot.

        Parameters
        ----------
        fuzzy_var : FuzzyVariable or Term to plot
        """
        

        # self.term allows us to know if this is a Term quickly, later
        self.term = None
        if isinstance(fuzzy_var, Term):
            self.term = fuzzy_var.label
            self.fuzzy_var = fuzzy_var.parent
        elif isinstance(fuzzy_var, FuzzyVariable):
            self.fuzzy_var = fuzzy_var
        else:
            raise ValueError("`FuzzyVariableVisualizer` can only be called "
                             "with a `FuzzyVariable` or a `Term`.")

        if ax is not None:
            self.fig = fig
            self.ax = ax
        else:
            self.fig, self.ax = plt.subplots()

        self.plots = {}

    def view(self, sim=None, *args, **kwargs):
        """
        Visualize this variable and its membership functions with Matplotlib.

        The current output membership function will be shown in bold.

        Returns
        -------
        fig : matplotlib Figure
            The hosting Figure object.
        ax : matplotlib Axis
            The Axis upon which the plot is drawn.

        Notes
        -----
        Matplotlib is used, but ``plt.show()`` is not called. Instead, the
        Figure and Axis are returned, allowing further user customization if
        desired.  In a Jupyter notebook, ``.view()`` will be displayed inline.
        """


        if sim is None:
            # Create an empty simulation so we can view with default values
            sim = ControlSystemSimulation(ControlSystem())

        self._init_plot()

        crispy = CrispValueCalculator(self.fuzzy_var, sim)
        ups_universe, output_mf, cut_mfs = crispy.find_memberships()

        # Plot the output membership functions
        cut_plots = {}
        zeros = np.zeros_like(ups_universe, dtype=np.float64)


        for label, mf_plot in self.plots.items():
            # Only attempt to plot those with cuts
            if label in cut_mfs:
                # Harmonize color between mf plots and filled overlays
                color = mf_plot[0].get_color()
                cut_plots[label] = self.ax.fill_between(
                    ups_universe, zeros, cut_mfs[label],
                    facecolor=color, alpha=0.4)

        # Plot crisp value if available
        if len(cut_mfs) > 0 and not all(output_mf == 0):
            crisp_value = None
            if hasattr(self.fuzzy_var, 'input'):
                crisp_value = self.fuzzy_var.input[sim]
            elif hasattr(self.fuzzy_var, 'output'):
                crisp_value = self.fuzzy_var.output[sim]

            # Draw the crisp value at the actual cut height
            if crisp_value is not None:
                y = 0.
                for key, term in self.fuzzy_var.terms.items():
                    if key in cut_mfs:
                        y = max(y, interp_membership(self.fuzzy_var.universe,
                                                     term.mf, crisp_value))

                # Small cut values are hard to see, so simply set them to 1
                if y < 0.1:
                    y = 1.

                self.ax.plot([crisp_value] * 2, [0, y],
                             color='k', lw=3, label='crisp value')

        return self.fig, self.ax

    def _init_plot(self):
        # start = time.time()
        # end = time.time()
        # print((end - start))
        
        # Formatting: limits
        self.ax.set_ylim([0, 1.01])
        self.ax.set_xlim([self.fuzzy_var.universe.min(),
                          self.fuzzy_var.universe.max()])

        # Make the plots
        for key, term in self.fuzzy_var.terms.items():
            # If this is a Term, bold the active mf
            lw = 1
            if self.term == key:
                lw = 3

            self.plots[key] = self.ax.plot(self.fuzzy_var.universe,
                                           term.mf,
                                           label=key,
                                           linewidth=lw)

        # Place legend in upper left
        self.ax.legend(framealpha=0.5)

        # Turn off top/right axes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()

        # Ticks outside the axes
        self.ax.tick_params(direction='out')

        # Label the axes
        self.ax.set_ylabel('Membership')
        self.ax.set_xlabel(self.fuzzy_var.label)

