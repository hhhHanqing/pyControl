
from pyControl.utility import *
from devices import *
import pyControl.hardware as _h

board = Breakout_dseries_1_5()
########## Top Row #############
Cpoke       = Nosepoke(board.port_2, nose_event = 'C_nose',debounce=150)
Rpoke       = Nosepoke(board.port_5, nose_event = 'R_nose', debounce = 150)
Lpoke       = Nosepoke(board.port_1, nose_event = 'L_nose', debounce = 150)
BaseStation = Base_station_serial(board.port_10)
button      = _h.Digital_input(board.button,rising_event='button_release',falling_event='button',pull='up')

states= [
    'wait_for_center_initiation',
    ]

events = [
    'R_nose',
    'C_nose',
    'L_nose',
    'button',
    'check_serial'
    ]

####### Hidden script variables ##########
v.left_presses___ = 0
v.right_presses___ = 0

##### Configurable Variables #######
#Left variables
v.required_presses_left = 10 

#Right variables
v.required_presses_right = 10

#Other variables
v.retracted_position_1600 = 0

initial_state = 'wait_for_center_initiation'


def wait_for_center_initiation(event):
    if event == 'entry':
        Cpoke.LED.on()
        Rpoke.LED.off()
        set_timer('check_serial',10)
    elif event == 'check_serial':
        set_timer('check_serial',10)
        msg = BaseStation.check_for_serial()
        if msg:
            print(msg)
    elif event == 'C_nose':
        BaseStation.trigger()
    elif event == 'R_nose':
        BaseStation.stop()
