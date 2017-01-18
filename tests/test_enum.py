import textwrap
from enum import Enum

import pytest

from pyha.common.hwsim import HW
from pyha.conversion.conversion import get_conversion
from pyha.conversion.extract_datamodel import DataModel


class TestEnum(Enum):
    ENUM0, ENUM1, ENUM2, ENUM3 = range(4)


@pytest.fixture
def t0():
    class T0(HW):
        def __init__(self, mode):
            self.mode = mode

        def main(self):
            pass

    dut = T0(TestEnum.ENUM1)
    dut.main()
    dut.main()
    return dut


def test_datamodel(t0):
    datamodel = DataModel(t0)
    assert datamodel.self_data['mode'] == TestEnum.ENUM1


def test_vhdl_datamodel(t0):
    conv = get_conversion(t0)

    expect = textwrap.dedent("""\
            type register_t is record
                mode: TestEnum;
            end record;

            type self_t is record
                mode: TestEnum;
                \\next\\: register_t;
            end record;""")
    dm = conv.get_datamodel()
    assert expect == dm


def test_vhdl_enum_define(t0):
    conv = get_conversion(t0)
    expect = ['type TestEnum is (ENUM0,ENUM1,ENUM2,ENUM3);']
    dm = conv.get_enumdefs()
    assert expect == dm

def test_vhdl_reset(t0):
    conv = get_conversion(t0)

    expect = textwrap.dedent("""\
        procedure reset(self_reg: inout register_t) is
        begin
            self_reg.mode := ENUM1;
        end procedure;""")

    assert expect == str(conv.get_reset_str())
