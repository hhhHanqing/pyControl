# A simple state machine which flashes the blue LED on the pyboard on and off.
# Does not require any hardware except micropython board.

from pyControl.utility import *
from devices import *
import hardware_definition as hw

# Define hardware (normally done in seperate hardware definition file).

blue_LED = Digital_output('B4')

# States and events.

states = ['LED_123',
          'LED_456']

events = []

initial_state = 'LED_123'
v.time_between = 3
        
# Define behaviour. 

def LED_123(event):
    if event == 'entry':
        timed_goto_state('LED_456', v.time_between * second)
        hw.Camera.light_123.on()
        hw.Camera.light_456.off()
        print('123')
    elif event == 'exit':
        hw.Camera.light_123.on()
        hw.Camera.light_456.on()

def LED_456(event):
    if event == 'entry':
        print('456')
        timed_goto_state('LED_123', v.time_between * second)




