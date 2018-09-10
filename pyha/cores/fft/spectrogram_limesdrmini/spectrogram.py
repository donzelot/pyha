import logging

import numpy as np
import pytest

from pyha import Hardware, simulate, sims_close, Complex, default_complex, Sfix
from pyha.cores import DataValidToNumpy, NumpyToDataValid, SDRSource, DataValid, Spectrogram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('spectrogram')


class SpectrogramLimeSDRMini(Hardware):
    def __init__(self, fft_size, avg_freq_axis=2, avg_time_axis=1, window_type='hanning', fft_twiddle_bits=18,
                 window_bits=18):
        self._pyha_simulation_input_callback = NumpyToDataValid(dtype=default_complex)
        self._pyha_simulation_output_callback = DataValidToNumpy()

        # components
        self.source = SDRSource()
        self.spect = Spectrogram(fft_size, avg_freq_axis, avg_time_axis, window_type, fft_twiddle_bits, window_bits)
        self.out = DataValid(Sfix(0, -4, -35))  # format to 32 bits

    def main(self, real, imag):
        complex_stream = self.source.main(real, imag)
        spect = self.spect.main(complex_stream)

        self.out.data = spect.data
        self.out.valid = spect.valid

        return self.out

    def model_main(self, real, imag):
        complex_stream = self.source.main(real, imag)
        spect = self.spect.main(complex_stream)

        self.out.data = spect.data
        self.out.valid = spect.valid

        return self.out


@pytest.mark.parametrize("avg_freq_axis", [1, 2, 4, 8, 16])
@pytest.mark.parametrize("avg_time_axis", [2, 4, 8])
@pytest.mark.parametrize("fft_size", [128, 256])
@pytest.mark.parametrize("input_power", [0.25, 0.001])
def test_all(fft_size, avg_freq_axis, avg_time_axis, input_power):
    np.random.seed(0)
    input_size = (avg_time_axis) * fft_size
    orig_inp = (np.random.uniform(-1, 1, size=input_size) + np.random.uniform(-1, 1,
                                                                              size=input_size) * 1j) * input_power
    dut = Spectrogram(fft_size, avg_freq_axis, avg_time_axis)

    orig_inp_quant = np.vectorize(lambda x: complex(Complex(x, 0, -17)))(orig_inp)
    sims = simulate(dut, orig_inp_quant, simulations=['MODEL', 'PYHA'])
    assert sims_close(sims, rtol=1e-7, atol=1e-7)


def test_simple():
    pytest.skip()
    # TWID: 10b, WINDOW: 8b
    # Flow Status	Successful - Wed Jun 20 12:38:29 2018
    # Quartus Prime Version	17.1.0 Build 590 10/25/2017 SJ Lite Edition
    # Revision Name	quartus_project
    # Top-level Entity Name	top
    # Family	Cyclone IV E
    # Device	EP4CE40F23C8
    # Timing Models	Final
    # Total logic elements	11,729 / 39,600 ( 30 % )
    # Total registers	955
    # Total pins	107 / 329 ( 33 % )
    # Total virtual pins	0
    # Total memory bits	312,408 / 1,161,216 ( 27 % )
    # Embedded Multiplier 9-bit elements	104 / 232 ( 45 % )
    # Total PLLs	0 / 4 ( 0 % )

    # NO DC REMOVAL
    # TWID: 9b, WINDOW: 8b
    # Family	Cyclone IV E
    # Device	EP4CE40F23C8
    # Timing Models	Final
    # Total logic elements	10,146 / 39,600 ( 26 % )
    # Total registers	955
    # Total pins	107 / 329 ( 33 % )
    # Total virtual pins	0
    # Total memory bits	312,408 / 1,161,216 ( 27 % )
    # Embedded Multiplier 9-bit elements	104 / 232 ( 45 % )
    # Total PLLs	0 / 4 ( 0 % )

    # WITH DC REMOVAL + PIPELINED FFT, FMAX 80M
    # TWID: 9b, WINDOW: 8b
    # Device	EP4CE40F23C8
    # Timing Models	Final
    # Total logic elements	10,206 / 39,600 ( 26 % )
    # Total registers	2782
    # Total pins	107 / 329 ( 33 % )
    # Total virtual pins	0
    # Total memory bits	349,179 / 1,161,216 ( 30 % )
    # Embedded Multiplier 9-bit elements	104 / 232 ( 45 % )
    # Total PLLs	0 / 4 ( 0 % )

    np.random.seed(0)
    fft_size = 1024 * 8
    avg_time_axis = 2

    dut = Spectrogram(fft_size, avg_freq_axis=16, avg_time_axis=avg_time_axis, fft_twiddle_bits=9, window_bits=8)

    packets = avg_time_axis
    inp = np.random.uniform(-1, 1, fft_size * packets) + np.random.uniform(-1, 1, fft_size * packets) * 1j
    inp *= 0.5 * 0.001

    sims = simulate(dut, inp,
                    simulations=['MODEL', 'PYHA',
                                 'GATE',
                                 # 'RTL'
                                 ],
                    conversion_path='/home/gaspar/git/pyhacores/playground')

    # import matplotlib.pyplot as plt
    # plt.plot(np.hstack(sims['MODEL']))
    # plt.plot(np.hstack(sims['PYHA']))
    # plt.plot(np.hstack(sims['RTL']))
    # plt.show()

    sims['MODEL'] = np.array(sims['MODEL']) / np.array(sims['MODEL']).max()
    sims['PYHA'] = np.array(sims['PYHA']) / np.array(sims['PYHA']).max()
    # sims['RTL'] = np.array(sims['RTL']) / np.array(sims['RTL']).max()
    # sims['GATE'] = np.array(sims['GATE']) / np.array(sims['GATE']).max()
    assert sims_close(sims, rtol=1e-1, atol=1e-4)