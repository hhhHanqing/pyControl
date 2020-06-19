
from pyControl.utility import *
import hardware_definition as hw

states= [
    'wait_for_center',
    'wait_for_choice'
    ]

events = [
    'R_nose',
    'C_nose',
    'L_nose',
    'blink_toggle'
    ]

####### Hidden script variables ##########
v.trial_current_number___ = 0
##### Configurable Variables #######
v.background_reward_rate = .1
v.reward_seq = 'LLR'
v.reward_volume = 250 # microliters
v.time_blink = 100

#Other variables
v.current_sequence = '______' # up to 6 letter sequence
initial_state = 'wait_for_center'

def wait_for_center(event):
    if event == 'entry':
        hw.Cpoke.LED.on()
        hw.Rpoke.LED.off()
        hw.Lpoke.LED.off()
        v.trial_current_number___ += 1
        set_timer('blink_toggle', v.time_blink)
    elif event == 'C_nose':
        goto_state('wait_for_choice')
    elif event == 'blink_toggle':
        hw.Cpoke.LED.toggle()
        set_timer('blink_toggle', v.time_blink)

def wait_for_choice(event):
    if event == 'entry':
        hw.Cpoke.LED.off()
        hw.Rpoke.LED.on()
        hw.Lpoke.LED.on()
    elif event == 'R_nose':
        decideReward('R')
    elif event == 'L_nose':
        decideReward('L')

def all_states(event):
    Lmsg = hw.Lpump.check_for_serial()
    if Lmsg:
        print("Stoping task. Left pump empty")
        stop_framework()
    Rmsg = hw.Rpump.check_for_serial()
    if Rmsg:
        print("Stopping task. Right pump empty")
        stop_framework()

################ helper functions ############
def decideReward(choice):
    v.current_sequence = v.current_sequence[1:] + choice
    outcome = 'N' # not rewarded
    if str(v.current_sequence[-len(v.reward_seq):]) == str(v.reward_seq):
        giveReward(choice)  
        outcome = 'S' #reward from correct sequence
    elif withprob(v.background_reward_rate):
        giveReward(choice)
        outcome = 'B' # reward from background
    print('rslt,{},{},{},{},{}'.format(v.trial_current_number___,v.reward_seq,v.background_reward_rate,choice,outcome))
    goto_state('wait_for_center')

def giveReward(side):
    if side =='R':
        hw.Rpump.infuse(v.reward_volume)
    else:
        hw.Lpump.infuse(v.reward_volume)