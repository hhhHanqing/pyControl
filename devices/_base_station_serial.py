import pyControl.hardware as _h
from machine import UART

class Base_station_serial():
    def __init__(self, port):
        assert port.UART is not None, '! Base Station needs port with UART.'
        self.uart = UART(port.UART, 57600)
        self.uart.init(57600, bits=8, parity=None, stop=1, timeout=2, rxbuf = 150)
        self.uart.write('N')

    def trigger(self):
        self.uart.write('T')

    def stop(self):
        self.uart.write('A')

    def check_for_serial(self):
        if self.uart.any():
            return self.uart.readline().decode("utf-8").strip('\n')
        else:
            return None