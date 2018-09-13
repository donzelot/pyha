from pyha import Hardware, sims_close, Complex, hardware_sims_equal, scalb, Simulator, simulate
import numpy as np
from pyha.common.shift_register import ShiftRegister

# def simulate(model, *args, simulations=None, conversion_path=None, input_types=None, pipeline_flush=0):
#     extra_simulations = []
#     if simulations is None:
#         extra_simulations = ['RTL', 'NETLIST']
#     else:
#         if 'RTL' in simulations:
#             extra_simulations += ['RTL']
#         if 'GATE' in simulations:
#             extra_simulations += ['NETLIST']
#
#     sims = Simulator(model, extra_simulations=extra_simulations, output_dir=conversion_path, pipeline_flush=pipeline_flush)
#     sims = sims.run(*args)
#
#     ret = {}
#     if simulations is None:
#         if hasattr(model, 'model_main'):
#             ret['MODEL'] = sims.out[0]
#         ret['PYHA'] = sims.out[1]
#         ret['RTL'] = sims.out[2]
#         ret['GATE'] = sims.out[3]
#     else:
#         if 'MODEL' in simulations:
#             if hasattr(model, 'model_main'):
#                 ret['MODEL'] = sims.out[0]
#         if 'PYHA' in simulations:
#             ret['PYHA'] = sims.out[1]
#         if 'RTL' in simulations:
#             ret['RTL'] = sims.out[2]
#         if 'GATE' in simulations:
#             ret['GATE'] = sims.out[3]
#
#     return ret


def test_loopback():
    class T(Hardware):
        def main(self, x):
            return x

    dut = T()
    inp = np.random.uniform(-1, 1, 2) + np.random.uniform(-1, 1, 2) * 1j

    sims = simulate(dut, inp, simulations=['PYHA', 'RTL'])
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_register():
    class T(Hardware):
        def __init__(self):
            self.DELAY = 1
            self.reg = Complex()  # TODO: this should resize to 0, -17??

        def main(self, x):
            self.reg = x
            return self.reg

    dut = T()
    inp = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, inp)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


# def test_register_negative_left():
#     class T(Hardware):
#         def __init__(self):
#             dut._pyha_simulation_input_callback = (dtype=Complex(0, -1, -21, round_style='round'))
#             self.reg = Complex(0.0, -1, -18)
#             self.DELAY = 1
#
#         def main(self, x):
#             self.reg = x
#             return self.reg
#
#         def model_main(self, x):
#             return x
#
#     dut = T()
#     inp = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
#     inp *= 0.5
#     Simulator(dut).run(inp).assert_equal(rtol=1e-30, atol=1e-30)


def test_old_shiftreg():
    class T(Hardware):
        def __init__(self):
            self.reg = [Complex() for _ in range(16)]
            self.DELAY = 1

        def main(self, x):
            self.reg = [x] + self.reg[:-1]
            return self.reg[-1]

    dut = T()
    inp = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, inp, simulations=['PYHA', 'RTL', 'GATE'])
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_new_shiftreg():
    class T(Hardware):
        def __init__(self):
            self.reg = ShiftRegister([Complex() for _ in range(16)])
            self.DELAY = 1

        def main(self, x):
            self.reg.push_next(x)
            return self.reg.peek()

    dut = T()
    inp = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, inp, simulations=['PYHA', 'RTL', 'GATE'])
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_multiply():
    class T(Hardware):
        def main(self, a, b):
            return a * b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_add():
    class T(Hardware):
        def main(self, a, b):
            return a + b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_sub():
    class T(Hardware):
        def main(self, a, b):
            return a - b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_rshift():
    class T(Hardware):
        def main(self, a, b):
            return a >> b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.randint(0, 17, 256)

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_lshift():
    class T(Hardware):
        def main(self, a, b):
            return a << b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.randint(0, 17, 256)

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    # assert sims_close(sims)


def test_scalb():
    class T(Hardware):
        def __init__(self, scalbi):
            self.SCALB_I = scalbi

        def main(self, a):
            # ret = scalb(a, b)
            return scalb(a, self.SCALB_I)

    dut = T(-1)
    a = [0.125 + 0.25j]

    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)

    dut = T(0)
    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)

    dut = T(1)
    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_scalb_bug():
    """ Result with negative integer bits were mishandled.. """

    # TODO: probably not fully resolved...
    class T(Hardware):
        def __init__(self, scalbi):
            self.SCALB_I = scalbi

        def main(self, a):
            ret = scalb(a, self.SCALB_I)
            return ret

    dut = T(-1)
    a = [0.125 + 0.25j]

    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_part_access():
    class T(Hardware):
        def main(self, a):
            return a.real, a.imag

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_part_access_submod():
    """ Bug: 'a.elem' was merged to 'aelem', see https://github.com/PyCQA/redbaron/issues/161 """

    class A(Hardware):
        def __init__(self, elem):
            self.elem = elem

    class T(Hardware):
        def main(self, a):
            return a.elem.real, a.elem.imag

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    a = [A(x) for x in a]

    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_add_float():
    class T(Hardware):
        def main(self, a, b):
            return a + b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256)

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_sub_float():
    class T(Hardware):
        def main(self, a, b):
            return a - b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256)

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_sub_uneven_types():
    """ Failed if a and b were different sizes, bug was in minimum function, that acted as maximum """

    class T(Hardware):
        def main(self, a, b):
            return a - b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256)

    sims = simulate(dut, a, b, input_types=[Complex(0, 0, -17), Complex(0, 0, -18)], simulations=['PYHA', 'RTL'],
                    conversion_path='/home/gaspar/git/pyhacores/playground')
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_mult_float():
    class T(Hardware):
        def main(self, a, b):
            return a * b

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j
    b = np.random.uniform(-1, 1, 256)

    sims = simulate(dut, a, b)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_floatconst_operations():
    class T(Hardware):
        def main(self, a):
            q = a + 0.24
            w = a - 0.2
            e = a * 0.4
            return q, w, e

    dut = T()
    a = np.random.uniform(-1, 1, 256) + np.random.uniform(-1, 1, 256) * 1j

    sims = simulate(dut, a)
    assert hardware_sims_equal(sims)
    assert sims_close(sims)


def test_complex_constants():
    class T(Hardware):
        def __init__(self):
            self.DELAY = 1
            self.reg = Complex(0, 0, -17)
            self.reg2 = Complex(0, 0, -17)
            self.reg3 = Complex(0, 0, -17)

        def main(self, x):
            self.reg = self.reg + x - (x * x)  # this was incorrectly parsed as complex constant!
            self.reg2 = 0.0 + 0.5j
            self.reg3 = 0.0 + 0.5 * 1j
            return self.reg, self.reg2

    dut = T()
    inputs = [0 + 0j, 0.1 + 0.2j, -0.1 + 0.3j]

    sims = simulate(dut, inputs, simulations=['PYHA', 'RTL'],
                    conversion_path='/home/gaspar/git/pyhacores/playground')
    assert sims_close(sims)
