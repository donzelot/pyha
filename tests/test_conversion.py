import textwrap
from pathlib import Path

import pytest
from pyha import simulate
from pyha.common.core import Hardware
from pyha.common.fixed_point import Sfix
from pyha.conversion.conversion import Conversion, get_objects_rednode
from pyha.simulation.legacy import assert_sim_match


class T:
    pass


@pytest.fixture
def dut():
    class Dummy(Hardware):
        def main(self, a):
            return a

    o = Dummy()
    # train object
    o.main(1)
    o.main(2)
    return Conversion(o)


def test_get_objects_rednode(dut):
    red = get_objects_rednode(dut.obj)
    assert red.name == 'Dummy'


def test_get_objects_rednode_global():
    red = get_objects_rednode(T())
    assert red.name == 'T'


def test_get_objects_rednode_local():
    class T0:
        def b(self):
            pass

    red = get_objects_rednode(T0())
    assert red.dumps() == 'class T0:\n    def b(self):\n        pass\n'


def test_get_objects_rednode_local2():
    class T0:
        def a(self):
            pass

    red = get_objects_rednode(T0())
    assert red.dumps() == 'class T0:\n    def a(self):\n        pass\n'


def test_get_objects_rednode_local_two():
    class Dummy(Hardware):
        def main(self, a):
            return a

    class Dummy2(Hardware):
        def main(self, a):
            return a

    red = get_objects_rednode(Dummy())
    assert red.name == 'Dummy'

    red = get_objects_rednode(Dummy2())
    assert red.name == 'Dummy2'


def test_get_objects_rednode_selective():
    pytest.xfail('Will not work, since locals cannot be walked')

    def f0():
        class T0:
            def b(self):
                pass

        return T0()

    def f1():
        class T0:
            def a(self):
                pass

        return T0()

    red = get_objects_rednode(f0())
    assert red.dumps() == 'class T0:\n    def b(self):\n        pass\n'

    red = get_objects_rednode(f1())
    assert red.dumps() == 'class T0:\n    def a(self):\n        pass\n'


def test_write_vhdl_files(dut, tmpdir):
    tmpdir = Path(str(tmpdir))
    files = dut.write_vhdl_files(tmpdir)
    assert files[0] == tmpdir / 'Dummy_0.vhd' and files[0].is_file()
    assert files[1] == tmpdir / 'top.vhd' and files[0].is_file()


def test_convert_submodule():
    class Aa(Hardware):
        def __init__(self):
            self.reg = 0

        def main(self, a):
            self.reg = a
            return self.reg

    class B(Hardware):
        def __init__(self):
            self.sub = Aa()
            self.DELAY = 1

        def main(self, a):
            ret = self.sub.main(a)
            return ret

    x = list(range(16))
    expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    dut = B()

    assert_sim_match(dut, expected, x, dir_path='/home/gaspar/git/pyha/playground')


def test_convert_submodule_name_conflict():
    class A2(Hardware):
        def __init__(self):
            self.reg = 0

    class B2(Hardware):
        def __init__(self):
            self.sub = A2()
            self.sub2 = A2()

        def main(self, a):
            return a

    dut = B2()
    dut.main(1)
    conv = Conversion(dut)
    paths = conv.write_vhdl_files(Path('/tmp'))
    names = [x.name for x in paths]
    assert names == ['A2_0.vhd', 'B2_0.vhd', 'top.vhd']


def test_typedefs():
    class A(Hardware):
        def __init__(self):
            self.reg = [1, 2]

        def main(self):
            b = [False, True]
            pass

    class B(Hardware):
        def __init__(self):
            self.sub = A()
            self.l = [1, 2]
            self.s = [Sfix(0, 1, -5)] * 2

        def main(self, a):
            self.sub.main()
            return a

    dut = B()
    dut.main(1)
    conv = Conversion(dut)

    expect = textwrap.dedent("""\
        library ieee;
            use ieee.std_logic_1164.all;
            use ieee.numeric_std.all;
            use ieee.fixed_float_types.all;
            use ieee.fixed_pkg.all;
            use ieee.math_real.all;
            
        library work;
            use work.PyhaUtil.all;
            use work.all;
        
        package Typedefs is
            type integer_list_t is array (natural range <>) of integer;
            type boolean_list_t is array (natural range <>) of boolean;
            type sfixed1downto_5_list_t is array (natural range <>) of sfixed(1 downto -5);
        end package;
            """)

    defs = conv.build_typedefs_package()
    assert expect == defs[defs.find('\n') + 1:]


def test_element_with_none_bound():
    class Child(Hardware):
        def __init__(self):
            self.reg = Sfix()

        def main(self, a):
            self.reg = a

    class DUT(Hardware):
        def __init__(self):
            self.child1 = Child()
            self.child2 = Child()

        def main(self, a):
            self.child1.main(a)
            return a

    dut = DUT()
    inp = [0.1, 0.2, 0.3]
    with pytest.raises(Exception):
        sims = simulate(dut, inp, simulations=['PYHA', 'RTL'], conversion_path='/home/gaspar/git/pyha/playground')

# from pyhacores.filter import FIR
# from scipy import signal
# import numpy as np
# class ComplexFIR(Hardware):
#     def __init__(self, taps):
#         # registers
#         self.fir = [FIR(taps),
#                     # FIR(taps)
#                     ]
#
#         # constants (written in CAPS)
#         self.DELAY = self.fir[0].DELAY
#         self.TAPS = np.asarray(taps).tolist()
#
#     def main(self, x):
#         out = x
#         out.real = self.fir[0].main(x.real)
#         # out.imag = self.fir[1].main(x.imag)
#         return out
#
#     def model_main(self, x_full):
#         """ Golden output """
#         from scipy.signal import lfilter
#         return lfilter(self.TAPS, [1.0], x_full)
#
# # class ComplexFIR(Hardware):
# #     def __init__(self, taps):
# #         # registers
# #         self.fir = [FIR(taps), FIR(taps)]
# #         self.outreg = ComplexSfix()
# #
# #         # constants (written in CAPS)
# #         self.DELAY = self.fir[0].DELAY
# #         self.TAPS = np.asarray(taps).tolist()
# #
# #     def main(self, x):
# #         # out = x
# #         # out.real = self.fir[0].main(x.real)
# #         # out.imag = self.fir[1].main(x.imag)
# #         # return out
# #         self.outreg.real = self.fir[0].main(x.real)
# #         self.outreg.imag = self.fir[1].main(x.imag)
# #         return self.outreg
# #
# #     def model_main(self, x):
# #         """ Golden output """
# #         return signal.lfilter(self.TAPS, [1.0], x)
#
# def test_demo():
#     taps = signal.remez(8, [0, 0.1, 0.2, 0.5], [1, 0])
#     dut = ComplexFIR(taps)
#     input = [0.1 + 0.1j, 0.2 + 0.2j, 0.3 + 0.3j]
#
#     sims = simulate(dut, input,
#                     simulations=['MODEL', 'PYHA', 'RTL'],
#                     conversion_path='/home/gaspar/git/pyha_demo_project/conversion_src'
#                     )
