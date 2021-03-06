from pyha import simulate, sims_close
from pyha.common.complex import Complex
from pyha.common.context_managers import AutoResize, RegisterBehaviour
from pyha.common.core import Hardware, PyhaList
from pyha.common.fixed_point import Sfix
from pyha.simulation.simulation_interface import assert_sim_match


class TestSfix:
    class A(Hardware):
        def __init__(self, overflow_style, round_style):
            self.a = Sfix(0, 0, -4, overflow_style=overflow_style, round_style=round_style)

            self.DELAY = 1

        def main(self, a):
            self.a = a
            return self.a

    def test_basic(self):
        dut = self.A('saturate', 'round')
        dut._pyha_enable_function_profiling_for_types()

        dut.main(Sfix(0.1, 2, -27))


        assert dut._pyha_next['a'].left == 0
        assert dut._pyha_next['a'].right == -4
        assert dut._pyha_next['a'].val == 0.125

    def test_round(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        expected = [0.0, 0.125, 0.1875, 0.3125, 0.375, 0.5, 0.625, 0.6875, 0.8125, 0.875]

        dut = self.A('saturate', 'round')
        assert_sim_match(dut, expected, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_truncate(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        expected = [0.0, 0.0625, 0.1875, 0.25, 0.375, 0.5, 0.5625, 0.6875, 0.75, 0.875]

        dut = self.A('saturate', 'truncate')
        assert_sim_match(dut, expected, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_saturation(self):
        x = [0.9, 1.0, 1.5, 2.0]
        expected = [0.875, 0.9375, 0.9375, 0.9375]

        dut = self.A('saturate', 'truncate')
        assert_sim_match(dut, expected, x, types=[Sfix(left=2, right=-17)],
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_wrap(self):
        x = [0.9, 1.0, 1.5, 2.0]
        expected = [0.875, -1, -0.5, 0]

        dut = self.A('wrap', 'truncate')
        assert_sim_match(dut, expected, x, types=[Sfix(left=2, right=-17)],
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])


class TestSfixList:
    class A1(Hardware):
        def __init__(self, overflow_style, round_style):
            self.a = [Sfix(0, 0, -4,
                           overflow_style=overflow_style,
                           round_style=round_style)] * 2

            self.DELAY = 1

        def main(self, a):
            self.a[0] = a
            self.a[1] = a
            return self.a[0], self.a[1]

    # def test_sfixlist_operation(self):
    #     a = [Sfix(0.1, 1, -27)] * 2
    #     b = PyhaList(a, Sfix(0, 0, -4, round_style='round'))
    #     with AutoResize.enable():
    #         b[0] = a[0]
    #
    #     assert b[0].left == 0
    #     assert b[0].right == -4
    #     assert b[0].val == 0.125

    def test_lists_to_sfixedlist(self):
        """ Metaclass shall turn lists of Sfix to SfixList """
        dut = self.A1('saturate', 'round')
        assert type(dut.a) == PyhaList
        assert type(dut._pyha_initial_self.a) == PyhaList

        # make sure types stay after sim
        assert_sim_match(dut, None, [0.1, 0.2], simulations=['HARDWARE'])

        assert type(dut.a) == PyhaList
        assert type(dut._pyha_initial_self.a) == PyhaList

    def test_basic(self):
        dut = self.A1('saturate', 'round')
        with RegisterBehaviour.enable():
            with AutoResize.enable():
                dut.main(Sfix(0.1, 2, -27))

                assert dut.a._pyha_next[0].left == 0
                assert dut.a._pyha_next[0].right == -4
                assert dut.a._pyha_next[0].val == 0.125

                assert dut.a._pyha_next[1].left == 0
                assert dut.a._pyha_next[1].right == -4
                assert dut.a._pyha_next[1].val == 0.125

    def test_round(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        expected = [
            [0.0, 0.125, 0.1875, 0.3125, 0.375, 0.5, 0.625, 0.6875, 0.8125, 0.875],
            [0.0, 0.125, 0.1875, 0.3125, 0.375, 0.5, 0.625, 0.6875, 0.8125, 0.875]
        ]

        dut = self.A1('saturate', 'round')
        assert_sim_match(dut, expected, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_truncate(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        expected = [
            [0.0, 0.0625, 0.1875, 0.25, 0.375, 0.5, 0.5625, 0.6875, 0.75, 0.875],
            [0.0, 0.0625, 0.1875, 0.25, 0.375, 0.5, 0.5625, 0.6875, 0.75, 0.875]
        ]

        dut = self.A1('saturate', 'truncate')
        assert_sim_match(dut, expected, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_saturation(self):
        x = [0.9, 1.0, 1.5, 2.0]
        expected = [
            [0.875, 0.9375, 0.9375, 0.9375],
            [0.875, 0.9375, 0.9375, 0.9375]
        ]

        dut = self.A1('saturate', 'truncate')
        assert_sim_match(dut, expected, x, types=[Sfix(left=2, right=-17)],
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_wrap(self):
        x = [0.9, 1.0, 1.5, 2.0]
        expected = [
            [0.875, -1, -0.5, 0],
            [0.875, -1, -0.5, 0]
        ]

        dut = self.A1('wrap', 'truncate')
        assert_sim_match(dut, expected, x, types=[Sfix(left=2, right=-17)],
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])


class TestComplex:
    class A2(Hardware):
        def __init__(self, overflow_style, round_style):
            self.a = Complex(0, 0, -4, overflow_style=overflow_style, round_style=round_style)
            self.DELAY = 1

        def main(self, a):
            self.a = Complex(a, a)
            # self.a.real = a
            # self.a.imag = a
            return self.a

    def test_basic(self):
        dut = self.A2('saturate', 'round')
        dut._pyha_enable_function_profiling_for_types()

        dut.main(Sfix(0.1, 2, -27))

        assert dut._pyha_next['a'].left == 0
        assert dut._pyha_next['a'].right == -4
        assert dut._pyha_next['a'].val == 0.125 + 0.125 * 1j

    def test_round(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        expected = [0.0 + 0.0j, 0.125 + 0.125j, 0.1875 + 0.1875j, 0.3125 + 0.3125j, 0.375 + 0.375j, 0.5 + 0.5j
            , 0.625 + 0.625j, 0.6875 + 0.6875j, 0.8125 + 0.8125j, 0.875 + 0.875j]

        dut = self.A2('saturate', 'round')
        assert_sim_match(dut, expected, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_truncate(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        expected = [0.0 + 0.0j, 0.0625 + 0.0625j, 0.1875 + 0.1875j, 0.25 + 0.25j, 0.375 + 0.375j, 0.5 + 0.5j
            , 0.5625 + 0.5625j, 0.6875 + 0.6875j, 0.75 + 0.75j, 0.875 + 0.875j]

        dut = self.A2('saturate', 'truncate')
        assert_sim_match(dut, expected, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_saturation(self):
        x = [0.9, 1.0, 1.5, 2.0]
        expected = [0.875 + 0.875j, 0.9375 + 0.9375j, 0.9375 + 0.9375j, 0.9375 + 0.9375j]

        dut = self.A2('saturate', 'truncate')
        assert_sim_match(dut, expected, x, types=[Sfix(left=2, right=-17)],
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_wrap(self):
        x = [0.9, 1.0, 1.5, 2.0]
        expected = [0.875 + 0.875j, -1 - 1j, -0.5 - 0.5j, 0 + 0j]

        dut = self.A2('wrap', 'truncate')
        assert_sim_match(dut, expected, x, types=[Sfix(left=2, right=-17)],
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])

    def test_full_assign(self):
        """ There shuld be no auto-resize when assigning fully """

        class A2(Hardware):
            def __init__(self, overflow_style, round_style):
                self.a = Complex(0.0, 0, -4, overflow_style=overflow_style, round_style=round_style)
                self.DELAY = 1

            def main(self, a):
                self.a = a
                return self.a

        x = [0.012 + 0.234j, -0.256 + 0.689j]

        dut = A2('saturate', 'round')
        sims = simulate(dut, x, simulations=['MODEL', 'HARDWARE', 'RTL'])
        assert sims_close(sims)


class TestLazySfix:
    class A3(Hardware):
        def __init__(self):
            self.a = Sfix()
            self.b = Sfix(left=1)
            self.c = Sfix(right=-4)

            self.DELAY = 1

        def main(self, a):
            self.a = a
            self.b = a
            self.c = a
            return self.a, self.b, self.c

    def test_basic(self):
        dut = self.A3()
        dut._pyha_enable_function_profiling_for_types()

        with AutoResize.enable():
            dut.main(Sfix(0.1, 2, -27))

            assert dut._pyha_next['a'].left == 2
            assert dut._pyha_next['a'].right == -27
            assert dut._pyha_next['a'].val == 0.09999999403953552

            assert dut._pyha_next['b'].left == 1
            assert dut._pyha_next['b'].right == -27
            assert dut._pyha_next['b'].val == 0.09999999403953552

            assert dut._pyha_next['c'].left == 2
            assert dut._pyha_next['c'].right == -4
            assert dut._pyha_next['c'].val == 0.0625

    def test_sim(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        dut = self.A3()
        assert_sim_match(dut, None, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])


class TestLazySfixList:
    class A4(Hardware):
        def __init__(self):
            self.a = [Sfix()] * 2
            self.b = [Sfix(left=1)] * 2
            self.c = [Sfix(right=-4)] * 2

            self.DELAY = 1

        def main(self, a):
            self.a[0] = a
            self.b[0] = a
            self.c[0] = a
            return self.a[0], self.b[0], self.c[0]

    def test_basic(self):
        dut = self.A4()
        dut._pyha_enable_function_profiling_for_types()

        with AutoResize.enable():
            dut.main(Sfix(0.1, 2, -27))

            assert dut.a._pyha_next[0].left == 2
            assert dut.a._pyha_next[0].right == -27
            assert dut.a._pyha_next[0].val == 0.09999999403953552

            assert dut.b._pyha_next[0].left == 1
            assert dut.b._pyha_next[0].right == -27
            assert dut.b._pyha_next[0].val == 0.09999999403953552

            assert dut.c._pyha_next[0].left == 2
            assert dut.c._pyha_next[0].right == -4
            assert dut.c._pyha_next[0].val == 0.0625

    def test_sim(self):
        x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        assert_sim_match(self.A4(), None, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])


# class TestLazyComplexSfix:
#     class A5(Hardware):
#         def __init__(self):
#             self.a = Complex()
#             self.b = Complex(left=1)
#             self.c = Complex(right=-4)
#
#             self.DELAY = 1
#
#         def main(self, a):
#             self.a.real = a
#             self.a.imag = a
#
#             self.b.real = a
#             self.b.imag = a
#
#             self.c.real = a
#             self.c.imag = a
#             return self.a, self.b, self.c
#
#     def test_basic(self):
#         dut = self.A5()
#
#         dut.main(Sfix(0.1, 2, -27))
#
#         assert dut.a._pyha_next['real'].left == 2
#         assert dut.a._pyha_next['real'].right == -27
#         assert dut.a._pyha_next['real'].val == 0.09999999403953552
#         assert dut.b._pyha_next['imag'].left == 1
#         assert dut.b._pyha_next['imag'].right == -27
#         assert dut.b._pyha_next['imag'].val == 0.09999999403953552
#         assert dut.c._pyha_next['real'].left == 2
#         assert dut.c._pyha_next['real'].right == -4
#         assert dut.c._pyha_next['real'].val == 0.0625
#
#     def test_sim(self):
#         x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
#
#         dut = self.A5()
#         assert_sim_match(dut, None, x,
#                          simulations=['HARDWARE', 'RTL', 'NETLIST'])


class TestAssignConstant:
    class A6(Hardware):
        def __init__(self):
            self.a = Sfix(0, 0, -17)
            self.b = Sfix(0, 2, -17)

            self.c = Complex(0, 0, -17)
            self.c2 = Complex(0, 0, -17)
            self.DELAY = 1

        def main(self, a):
            self.a = 0.123
            self.b = -2

            self.c = 0.78 - 0.56 * 1j
            self.c2 = 0.78 - 0.56j
            return self.a, self.b, self.c, self.c2

    def test_basic(self):
        dut = self.A6()
        dut._pyha_enable_function_profiling_for_types()

        with AutoResize.enable():
            dut.main(0)

            assert dut._pyha_next['a'].left == 0
            assert dut._pyha_next['a'].right == -17
            assert dut._pyha_next['a'].val == 0.12299346923828125

            assert dut._pyha_next['b'].left == 2
            assert dut._pyha_next['b'].right == -17
            assert dut._pyha_next['b'].val == -2

            assert dut._pyha_next['c'].left == 0
            assert dut._pyha_next['c'].right == -17
            assert dut._pyha_next['c'].val == 0.779998779296875 - 0.56000518798828125j

            assert dut._pyha_next['c2'].left == 0
            assert dut._pyha_next['c2'].right == -17
            assert dut._pyha_next['c2'].val == 0.779998779296875 - 0.56000518798828125j

    def test_sim(self):
        x = [1, 2]

        dut = self.A6()
        assert_sim_match(dut, None, x, simulations=['HARDWARE', 'RTL', 'NETLIST'])


class TestLocalsSfix:
    def test_no_resize(self):
        class A7B(Hardware):
            def main(self, arg):
                b = Sfix(0.5, 0, -17)
                b = Sfix(0.5, 5, -5)
                assert b.left == 5
                assert b.right == -5

                return arg

        x = [0.1, 0.2]

        dut = A7B()
        assert_sim_match(dut, None, x,
                         simulations=['HARDWARE'])

    def test_sim(self):
        class A7(Hardware):
            def main(self, arg):
                b = Sfix(0.5, 0, -17)
                c = Sfix(0.1, 5, -12)
                a = b
                b = c
                c = a

                return arg, a, b, c

        x = [0.1, 0.2]

        dut = A7()
        assert_sim_match(dut, None, x,
                         simulations=['HARDWARE', 'RTL', 'NETLIST'])
