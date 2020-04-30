
from pyControl.utility import *
from devices import *
import pyControl.hardware as _h

board = Breakout_dseries_1_6()
########## Top Row #############
Cpoke       = Nosepoke(board.port_2, nose_event = 'C_nose',debounce=100)
Rpoke       = Nosepoke(board.port_5, nose_event = 'R_nose')
Lpoke       = Nosepoke(board.port_1, nose_event = 'L_nose')
Rlever      = Lever_electric(board.port_3, lever_event = 'R_lever')
Llever      = Lever_electric(board.port_4, lever_event = 'L_lever')
button      = _h.Digital_input(board.button,rising_event='button_release',falling_event='button',pull='up')

states= [
    'wait_for_center_initiation',
    'offer_levers',
    'reject'
    ]

events = [
    'R_nose',
    'C_nose',
    'L_nose',
    'R_lever',
    'L_lever',
    'button',
    'update_left',
    'update_right'
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
v.calibration_left = 400
v.calibration_right = 400

initial_state = 'wait_for_center_initiation'


def wait_for_center_initiation(event):
    if event == 'entry':
        Cpoke.LED.on()
        Rpoke.LED.off()
    elif event == 'C_nose':
        goto_state('offer_levers')
    elif event == 'update_position':
        disarm_timer('update_position')
        Rlever.adjust.off()

def offer_levers(event):
    if event == 'entry':
        extend_levers()
    elif event == 'C_nose': 
        goto_state('reject')
    elif event == 'R_nose':
        goto_state('wait_for_center_initiation')
    elif event == 'L_lever':
        v.left_presses___ += 1
        if v.left_presses___ == v.required_presses_left:
            goto_state('wait_for_center_initiation')
    elif event == 'R_lever':
        v.right_presses___ +=1
        if v.right_presses___ == v.required_presses_right:
            goto_state('wait_for_center_initiation')
    elif event == 'update_left':
        disarm_timer('update_left')
        Llever.adjust.off()
    elif event == 'update_right':
        disarm_timer('update_right')
        Rlever.adjust.off()
    elif event == 'exit':
        retract_levers()

def reject(event):
    if event == 'entry':
        timed_goto_state('offer_levers',100)
    
def all_states(event):
   if event == 'button':
       Rlever.adjust.on()
       set_timer('update_right', v.calibration_right,True) 
   if event == 'L_nose':
       Llever.adjust.on()
       set_timer('update_left', v.calibration_left,True) 


################ helper functions ############
def extend_levers():
    Cpoke.LED.off()
    Rpoke.LED.on()
    Llever.extend()
    Rlever.extend()
    v.right_presses___ = 0
    v.left_presses___ = 0

def retract_levers():
    Llever.retract()
    Rlever.retract()    
    Cpoke.LED.on()
    Rpoke.LED.off()
