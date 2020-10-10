import pyControl.hardware as _h

class Camera():
    def __init__(self, port, sync_event):
        self.frame_grab_trigger = _h.Digital_output(port.DIO_A, pulse_enabled=True)
        self.sync_pulse = _h.Rsync(port.DIO_B,sync_event, mean_IPI= 5000, pulse_dur= 50 )