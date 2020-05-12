
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
    ]

####### Hidden script variables ##########
v.trial___ = 0
##### Configurable Variables #######
v.background_reward_rate = .1
v.reward_seq = 'LLR'
v.reward_volume = 250 # microliters

#Other variables
v.current_sequence = '______' # up to 6 letter sequence
initial_state = 'wait_for_center'

def wait_for_center(event):
    if event == 'entry':
        hw.Cpoke.LED.on()
        hw.Rpoke.LED.off()
        hw.Lpoke.LED.off()
        v.trial___ += 1
        print(v.current_sequence)
    elif event == 'C_nose':
        goto_state('wait_for_choice')

def wait_for_choice(event):
    if event == 'entry':
        hw.Cpoke.LED.off()
        hw.Rpoke.LED.on()
        hw.Lpoke.LED.on()
    elif event == 'R_nose':
        decideReward('R')
    elif event == 'L_nose':
        decideReward('L')

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
    print('rslt,{},{},{},{},{}'.format(v.trial___,v.reward_seq,v.background_reward_rate,choice,outcome))
    goto_state('wait_for_center')

def giveReward(side):
    if side =='R':
        hw.Rpump.infuse(v.reward_volume)
    else:
        hw.Lpump.infuse(v.reward_volume)