-- generated by pyha 0.0.0 at 2017-03-01 00:53:25
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

-- Converts IQ to polar.
package ToPolar_0 is



    type next_t is record
        core: Cordic_1.self_t;
        out_abs: sfixed(0 downto -17);
        out_angle: sfixed(0 downto -17);
    end record;

    type self_t is record
        -- constants
        \_delay\: integer;

        core: Cordic_1.self_t;
        out_abs: sfixed(0 downto -17);
        out_angle: sfixed(0 downto -17);
        \next\: next_t;
    end record;

    procedure \_pyha_constants_self\(self: inout self_t);

    procedure \_pyha_reset_self\(self: inout self_t);

    procedure \_pyha_update_self\(self: inout self_t);

    -- :param c: baseband in, internal sizes are derived from this.
    -- :type c: ComplexSfix
    -- :return: abs (gain corrected) angle (in 1 to -1 range)
    procedure main(self:inout self_t; c: complex_sfix0_17; ret_0:out sfixed(0 downto -17); ret_1:out sfixed(0 downto -17));
end package;

package body ToPolar_0 is
    procedure \_pyha_constants_self\(self: inout self_t) is
    begin
        self.\_delay\ := 15;
        Cordic_1.\_pyha_constants_self\(self.core);
    end procedure;

    procedure \_pyha_reset_self\(self: inout self_t) is
    begin
        Cordic_1.\_pyha_reset_self\(self.core);
        self.\next\.out_abs := Sfix(0.0, 0, -17);
        self.\next\.out_angle := Sfix(0.0, 0, -17);
        \_pyha_update_self\(self);
    end procedure;

    procedure \_pyha_update_self\(self: inout self_t) is
    begin
        Cordic_1.\_pyha_update_self\(self.core);
        self.out_abs := self.\next\.out_abs;
        self.out_angle := self.\next\.out_angle;
        \_pyha_constants_self\(self);
    end procedure;



    -- :param c: baseband in, internal sizes are derived from this.
    -- :type c: ComplexSfix
    -- :return: abs (gain corrected) angle (in 1 to -1 range)
    procedure main(self:inout self_t; c: complex_sfix0_17; ret_0:out sfixed(0 downto -17); ret_1:out sfixed(0 downto -17)) is
        variable phase: sfixed(0 downto -24);
        variable x: sfixed(1 downto -16);
        variable y: sfixed(1 downto -16);
        variable \abs\: sfixed(1 downto -16);
        variable \_\: sfixed(1 downto -16);
        variable angle: sfixed(0 downto -24);
    begin
        phase := Sfix(0.0, 0, -24);

        -- give 1 extra bit, as there is stuff like CORDIC gain.. in some cases 2 bits may be needed!
        -- there will be CORDIC gain + abs value held by x can be > 1
        -- remove 1 bit from fractional part, to keep 18 bit numbers
        x := resize(c.real, left_index(c.real) + 1, right_index(c.real) + 1, round_style=>fixed_truncate);
        y := resize(c.imag, left_index(c.imag) + 1, right_index(c.imag) + 1, round_style=>fixed_truncate);

        Cordic_1.main(self.core, x, y, phase, ret_0=>\abs\, ret_1=>\_\, ret_2=>angle);

        -- get rid of CORDIC gain and extra bits
        self.\next\.out_abs := resize(\abs\ * (1.0 / 1.646760), c.imag, round_style=>fixed_truncate);
        self.\next\.out_angle := resize(angle, c.imag, round_style=>fixed_truncate);
        ret_0 := self.out_abs;
        ret_1 := self.out_angle;
        return;
    end procedure;
end package body;
