from examples.present.stage0 import Demo
from pyha.common.hwsim import Hardware
from pyha.simulation.simulation_interface import *

""" Demo massiive """


class ArrayDemo(Hardware):
    def __init__(self):
        self.components = [Demo(), Demo(), Demo(), Demo()]

    def main(self, coef, input):
        out = [x.main(coef, input) for x in self.components]
        return out

    def main_sew(self, coef, input):
        out = self.components[0].main(coef, input)
        for x in self.components[1:]:
            out = x.main(coef, out)

        return out

def test_demo():
    """ Siin vist testi pole mõtet näidata ..."""
    coefs = list(range(8))
    inputs = list(range(8))

    model = DualDemo()
    sims = simulate(model, coefs, inputs, simulations=[SIM_MODEL, SIM_HW_MODEL, SIM_RTL])

    print(sims['MODEL'])
    print(sims['HW_MODEL'])
    # plt.plot(sims['MODEL'])
    # plt.plot(sims['HW_MODEL'])
    # plt.plot(sims['RTL'])
    # plt.show()

    print(sims)
