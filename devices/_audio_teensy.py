from machine import UART
from array import array

class Teensy_audio():
    def __init__(self, port):
        assert port.UART is not None, '! Teensy Audio Player needs a port with UART.'
        self.uart = UART(port.UART, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1, timeout=1)
        self.uart.write('S')

    def play(self, side):
        if side == 'Left':
            self.uart.write('L')
        elif side == 'Right':
            self.uart.write('R')
        return True

    def beep(self):
        self.uart.write('L')

    def stop(self):
        self.uart.write('S')
        return False

    def set_volume(self, volume): # Between 1 - 65
        self.uart.write('V,{}'.format(volume))