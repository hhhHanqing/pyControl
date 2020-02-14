import pyControl.hardware as _h

class Base_station():
    def __init__(self, port):
        self.trigger_pin = _h.Digital_output(port.DIO_A)
        self.stop_pin = _h.Digital_output(port.DIO_B)
        self.trigger_pin.off()
        self.stop_pin.off()
    
    def trigger(self):
        self.trigger_pin.on()
        self.trigger_pin.on()
        self.trigger_pin.off()

    def stop(self):
        self.stop_pin.on()
        self.stop_pin.on()
        self.stop_pin.off()