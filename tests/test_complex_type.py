import textwrap

import pytest
from pathlib import Path

from pyha.common.hwsim import HW
from pyha.common.sfix import Sfix, ComplexSfix
from pyha.conversion.conversion import get_conversion, Conversion
from pyha.conversion.extract_datamodel import DataModel
from pyha.conversion.top_generator import TopGenerator
from pyha.simulation.simulation_interface import assert_sim_match, SIM_HW_MODEL, SIM_RTL


def test_py_implementation():
    a = ComplexSfix()
    assert a.real == Sfix(0.0, 0, 0, overflow_style='SATURATE')
    assert a.imag == Sfix(0.0, 0, 0, overflow_style='SATURATE')

    a = ComplexSfix(0)
    assert a.real == Sfix(0.0, 0, 0, overflow_style='SATURATE')
    assert a.imag == Sfix(0.0, 0, 0, overflow_style='SATURATE')

    a = ComplexSfix(0.5 + 1.2j, 1, -12)
    assert a.real == Sfix(0.5, 1, -12, overflow_style='SATURATE')
    assert a.imag == Sfix(1.2, 1, -12, overflow_style='SATURATE')

    a = ComplexSfix(0.699 + 0.012j, 0, -4)
    assert a.real.val == 0.6875
    assert a.imag.val == 0
    assert a.init_val == 0.699 + 0.012j
    assert a.left == 0
    assert a.right == -4


def test_fixed_value():


@pytest.fixture
def reg():
    class A(HW):
        def __init__(self):
            self.reg = ComplexSfix(0.5 + 1.2j, 1, -12)

        def main(self, x):
            self.next.reg = x
            return self.reg

    dut = A()
    dut.main(ComplexSfix(0.5 + 1.2j, 1, -12))
    dut.main(ComplexSfix(0.5 + 1.2j, 1, -12))
    return dut


def test_reg_datamodel(reg):
    datamodel = DataModel(reg)
    assert datamodel.locals['main']['x'] == ComplexSfix(0.5 + 1.2j, 1, -12)
    assert datamodel.self_data['reg'] == ComplexSfix(0.5 + 1.2j, 1, -12)


def test_reg_conversion_datamodel(reg):
    conv = get_conversion(reg)

    expect = textwrap.dedent("""\
            type register_t is record
                reg: complex_sfix1_12;
            end record;

            type self_t is record
                reg: complex_sfix1_12;
                \\next\\: register_t;
            end record;""")
    dm = conv.get_datamodel()
    assert expect == dm


def test_reg_conversion_reset(reg):
    conv = get_conversion(reg)

    expect = textwrap.dedent("""\
        procedure reset(self_reg: inout register_t) is
        begin
            self_reg.reg := (real=>to_sfixed(0.5, 1, -12), imag=>to_sfixed(1.2, 1, -12));
        end procedure;""")

    assert expect == str(conv.get_reset_str())


def test_reg_conversion_top_entity(reg):
    dut = reg
    res = TopGenerator(dut)
    # input
    assert 'in0: in std_logic_vector(27 downto 0);' == res.make_entity_inputs()
    assert 'variable var_in0: complex_sfix1_12;' == res.make_input_variables()
    assert 'var_in0 := ' \
           '(real=>to_sfixed(in0(27 downto 14), 1, -12), imag=>to_sfixed(in0(13 downto 0), 1, -12));' \
           == res.make_input_type_conversions()

    # output
    assert 'out0: out std_logic_vector(27 downto 0);' == res.make_entity_outputs()
    assert 'variable var_out0: complex_sfix1_12;' == res.make_output_variables()
    assert 'out0 <= to_slv(var_out0.real) & to_slv(var_out0.imag);' == res.make_output_type_conversions()


def test_reg_complex_types_generation(reg):
    conv = Conversion(reg)
    expect = textwrap.dedent("""\
        library ieee;
            use ieee.fixed_pkg.all;

        package ComplexTypes is
        type complex_sfix1_12 is record
            real: sfixed(1 downto -12);
            imag: sfixed(1 downto -12);
        end record;
        end package;""")

    files = conv.write_vhdl_files(Path('/tmp/'))
    with files[0].open('r') as f:
        assert expect == f.read()



def test_reg_simulate(reg):
    dut = reg
    x = [0.5 + 0.1j, 0.5 - 0.09j, -0.5 + 0.1j, 0.14 + 0.1j, 0.5 + 0.89j]
    expected = [0.5 + 1.2j, 0.5 + 0.1j, 0.5 - 0.09j, -0.5 + 0.1j, 0.14 + 0.1j]

    assert_sim_match(dut, [ComplexSfix(left=1, right=-12)], expected, x, rtol=1e-3,
                     simulations=[SIM_HW_MODEL, SIM_RTL])

# list of complex!
# top converter duplicate definitions?
