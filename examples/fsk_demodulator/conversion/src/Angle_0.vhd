-- generated by pyha 0.0.0 at 2017-03-01 00:53:24
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

-- Wrapper around ToPolar. Abs output will be optimized away.
package Angle_0 is



    type next_t is record
        core: ToPolar_0.self_t;
    end record;

    type self_t is record
        -- constants
        \_delay\: integer;

        core: ToPolar_0.self_t;
        \next\: next_t;
    end record;

    procedure \_pyha_constants_self\(self: inout self_t);

    procedure \_pyha_reset_self\(self: inout self_t);

    procedure \_pyha_update_self\(self: inout self_t);


    procedure main(self:inout self_t; c: complex_sfix0_17; ret_0:out sfixed(0 downto -17));
end package;

package body Angle_0 is
    procedure \_pyha_constants_self\(self: inout self_t) is
    begin
        self.\_delay\ := 15;
        ToPolar_0.\_pyha_constants_self\(self.core);
    end procedure;

    procedure \_pyha_reset_self\(self: inout self_t) is
    begin
        ToPolar_0.\_pyha_reset_self\(self.core);
        \_pyha_update_self\(self);
    end procedure;

    procedure \_pyha_update_self\(self: inout self_t) is
    begin
        ToPolar_0.\_pyha_update_self\(self.core);
        \_pyha_constants_self\(self);
    end procedure;


    procedure main(self:inout self_t; c: complex_sfix0_17; ret_0:out sfixed(0 downto -17)) is
        variable \_\: sfixed(0 downto -17);
        variable angle: sfixed(0 downto -17);
    begin
        ToPolar_0.main(self.core, c, ret_0=>\_\, ret_1=>angle);
        ret_0 := angle;
        return;
    end procedure;
end package body;
