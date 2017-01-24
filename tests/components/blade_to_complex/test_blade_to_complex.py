from pyha.common.sfix import Sfix
import numpy as np

from pyha.components.blade_to_complex import BladeToComplex
from pyha.simulation.simulation_interface import SIM_MODEL, SIM_HW_MODEL, SIM_RTL, SIM_GATE, \
    assert_sim_match


def test_from_signaltap():
    c = np.load('signaltap_balderf_iq.npy')

    dut = BladeToComplex()
    assert_sim_match(dut, [Sfix(left=4, right=-11)]*2,
                                 [], c.real, c.imag,
                                 rtol=1e-5,
                                 atol=1e-5,
                                 simulations=[SIM_MODEL, SIM_HW_MODEL, SIM_RTL, SIM_GATE],
                                 dir_path='/home/gaspar/git/pyha/playground/conv',
                                 )
