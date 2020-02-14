import pyControl.hardware as _h

class Nosepoke():
    def __init__(self, port, nose_event, lick_event = None, debounce = 5):
        self.nose = _h.Digital_input(port.DIO_A,  nose_event,  nose_event+'_out',  debounce)
        if lick_event:
            self.lick = _h.Digital_input(port.DIO_B, lick_event, None, debounce)
        self.LED = _h.Digital_output(port.POW_A)