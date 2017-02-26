-- generated by pyha 0.0.0 at 2017-02-26 21:27:17
library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;
    use ieee.fixed_float_types.all;
    use ieee.fixed_pkg.all;
    use ieee.math_real.all;

library work;
    use work.ComplexTypes.all;
    use work.PyhaUtil.all;
    use work.all;

-- This module has a Sfix register and an A0 submodule registers
package A1_0 is



    type next_t is record
        submodule: A0_0.self_t;
        reg: sfixed(0 downto -17);
    end record;

    type self_t is record
        -- constants
        \_delay\: integer;

        submodule: A0_0.self_t;
        reg: sfixed(0 downto -17);
        \next\: next_t;
    end record;

    procedure \_pyha_constants_self\(self: inout self_t);

    procedure \_pyha_reset_self\(self: inout self_t);

    procedure \_pyha_update_self\(self: inout self_t);


    procedure main(self:inout self_t; \new\: sfixed(0 downto -17); ret_0:out sfixed(0 downto -17); ret_1:out sfixed(0 downto -17));
end package;

package body A1_0 is
    procedure \_pyha_constants_self\(self: inout self_t) is
    begin
        self.\_delay\ := 2;
        A0_0.\_pyha_constants_self\(self.submodule);
    end procedure;

    procedure \_pyha_reset_self\(self: inout self_t) is
    begin
        A0_0.\_pyha_reset_self\(self.submodule);
        self.\next\.reg := Sfix(0.98, 0, -17);
        \_pyha_update_self\(self);
    end procedure;

    procedure \_pyha_update_self\(self: inout self_t) is
    begin
        A0_0.\_pyha_update_self\(self.submodule);
        self.reg := self.\next\.reg;
        \_pyha_constants_self\(self);
    end procedure;




    procedure main(self:inout self_t; \new\: sfixed(0 downto -17); ret_0:out sfixed(0 downto -17); ret_1:out sfixed(0 downto -17)) is
        variable r: sfixed(0 downto -17);
    begin
        -- call submodule
        A0_0.main(self.submodule, \new\, ret_0=>r);
        self.\next\.reg := \new\;
        ret_0 := r;
        ret_1 := self.reg;
        return;

    end procedure;
end package body;
