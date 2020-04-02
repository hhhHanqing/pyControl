import pyControl.hardware as _h

class Lever_electric():
    def __init__(self, port, lever_event, debounce = 100):
        self.press = _h.Digital_input(port.DIO_B, rising_event=lever_event, debounce = debounce, pull='up')
        self.motor = _h.Digital_output(port.DIO_A)
        self.adjust = _h.Digital_output(port.DIO_C)
    def retract(self):
        self.motor.off()
    def extend(self):
        self.motor.on()