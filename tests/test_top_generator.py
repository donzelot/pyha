import textwrap

import pytest

from pyha.common.core import Hardware
from pyha.common.fixed_point import Sfix
from pyha.conversion.top_generator import TopGenerator, NotTrainedError, NoInputsError, NoOutputsError


@pytest.fixture
def basic_obj():
    class Register(Hardware):
        def main(self, a, b, c=0):
            return a * 5, True, Sfix(0.0, 5, -8)

    dut = Register()
    dut._pyha_enable_function_profiling_for_types()
    dut.main(2, Sfix(1.0, 2, -17))
    dut.main(-57, Sfix(1.0, 2, -17))
    dut.main(-57, Sfix(1.0, 2, -17), c=True)
    return dut


def test_entity_inputs(basic_obj):
    dut = basic_obj
    expect = textwrap.dedent("""\
                in0: in std_logic_vector(31 downto 0);
                in1: in std_logic_vector(19 downto 0);
                in2: in std_logic_vector(0 downto 0);""")

    res = TopGenerator(dut)

    assert expect == res.make_entity_inputs()


def test_entity_outputs(basic_obj):
    dut = basic_obj
    expect = textwrap.dedent("""\
                out0: out std_logic_vector(31 downto 0);
                out1: out std_logic_vector(0 downto 0);
                out2: out std_logic_vector(13 downto 0);""")

    res = TopGenerator(dut)

    assert expect == res.make_entity_outputs()


def test_variables_output(basic_obj):
    dut = basic_obj
    expect = textwrap.dedent("""\
                variable var_out0: integer;
                variable var_out1: boolean;
                variable var_out2: sfixed(5 downto -8);""")

    res = TopGenerator(dut)

    assert expect == res.make_output_variables()


def test_output_type_conversion(basic_obj):
    dut = basic_obj
    expect = textwrap.dedent("""\
                out0(31 downto 0) <= std_logic_vector(to_signed(var_out0, 32));
                out1(0 downto 0) <= bool_to_logic(var_out1);
                out2(13 downto 0) <= to_slv(var_out2);
                """)

    res = TopGenerator(dut)

    assert expect == res.make_output_type_conversions()


def test_variables_input(basic_obj):
    dut = basic_obj
    expect = textwrap.dedent("""\
                variable var_in0: integer;
                variable var_in1: sfixed(2 downto -17);
                variable var_in2: boolean;""")

    res = TopGenerator(dut)

    assert expect == res.make_input_variables()


def test_input_type_conversion(basic_obj):
    dut = basic_obj
    expect = textwrap.dedent("""\
                var_in0 := to_integer(signed(in0(31 downto 0)));
                var_in1 := Sfix(in1(19 downto 0), 2, -17);
                var_in2 := logic_to_bool(in2(0 downto 0));
                """)

    res = TopGenerator(dut)

    assert expect == res.make_input_type_conversions()


def test_dut_name(basic_obj):
    dut = basic_obj
    expect = 'Register_1'

    res = TopGenerator(dut)

    assert expect == res.object_class_name()


def test_call_arguments(basic_obj):
    dut = basic_obj
    expect = 'var_in0, var_in1, c=>var_in2, ret_0=>var_out0, ret_1=>var_out1, ret_2=>var_out2'

    res = TopGenerator(dut)

    assert expect == res.make_call_arguments()


##################################
# SIMPLE OBJECT
##################################

@pytest.fixture
def simple_obj():
    class Simple(Hardware):
        def main(self, a):
            return a

    dut = Simple()
    dut._pyha_enable_function_profiling_for_types()
    dut.main(2)
    dut.main(2)
    return dut


def test_simple_call_arguments(simple_obj):
    dut = simple_obj
    expect = 'var_in0, ret_0=>var_out0'

    res = TopGenerator(dut)

    assert expect == res.make_call_arguments()


##################################
# MISC
##################################

def test_no_inputs():
    class Simple(Hardware):
        def main(self):
            return 1

    dut = Simple()
    dut._pyha_enable_function_profiling_for_types()
    dut.main()
    dut.main()

    with pytest.raises(NoInputsError):
        TopGenerator(dut)


def test_no_outputs():
    class Simple(Hardware):
        def main(self, a):
            pass

    dut = Simple()
    dut._pyha_enable_function_profiling_for_types()
    dut.main(1)
    dut.main(2)

    with pytest.raises(NoOutputsError):
        TopGenerator(dut)


def test_no_sim():
    class Simple(Hardware):
        def main(self, a):
            return a

    dut = Simple()
    dut._pyha_enable_function_profiling_for_types()

    with pytest.raises(NotTrainedError):
        TopGenerator(dut)
