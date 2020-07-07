from pyControl.utility import *
import hardware_definition as hw

states= [
    'wait_for_center',
    'wait_for_choice',
    'wait_for_outcome'
    ]

events = [
    'R_nose',
    'C_nose','C_nose_out',
    'L_nose',
    'center_hold_timer',
    'forgive_timer',
    'blink_timer',
    'side_delay_timer'
    ]

####### Hidden script variables ##########
v.trial_current_number___ = 0
v.chosen_side___ = ''
v.abandoned___ = False
v.in_center___ = False
##### Configurable Variables #######
v.correct_reward_rate = 0.9
v.background_reward_rate = .1
v.reward_seq = 'LLR'
v.reward_volume = 250 # microliters
v.time_blink = 100 # milliseconds
v.time_side_delay = 500 # milliseconds
v.time_hold_center = 1500 # milliseconds 
v.time_forgive = 500

#Other variables
v.current_sequence = '______' # up to 6 letter sequence
initial_state = 'wait_for_center'

def wait_for_center(event):
    if event == 'entry':
        hw.Cpoke.LED.on()
        hw.Rpoke.LED.off()
        hw.Lpoke.LED.off()
    elif event == 'C_nose':
        v.in_center___ = True
        if timer_remaining('center_hold_timer') == 0: # the timer doesn't exist
            set_timer('center_hold_timer',v.time_hold_center, output_event=True)
        else:
            disarm_timer('forgive_timer')
    elif event == 'C_nose_out':
        v.in_center___ = False
        set_timer('forgive_timer',v.time_forgive,output_event=True)
    elif event == 'forgive_timer':
        disarm_timer('center_hold_timer')
    elif event == 'center_hold_timer':
        if v.in_center___:
            goto_state('wait_for_choice')

def wait_for_choice(event):
    if event == 'entry':
        hw.Cpoke.LED.off()
        hw.Rpoke.LED.on()
        hw.Lpoke.LED.on()
        v.trial_current_number___ += 1
    elif event == 'R_nose':
        getOutcome('R')
    elif event == 'L_nose':
        getOutcome('L')

def wait_for_outcome(event):
    if event == 'entry':
        v.abandoned___ = False
        set_timer('blink_timer', v.time_blink)
        set_timer('side_delay_timer', v.time_side_delay, output_event=True)
    elif event == 'blink_timer':
        if v.chosen_side___ == 'L' :
            hw.Lpoke.LED.toggle()
        else:
            hw.Rpoke.LED.toggle()
        set_timer('blink_timer', v.time_blink)
    elif event == 'side_delay_timer':
        if v.outcome___ != 'N':
            if withprob(v.correct_reward_rate):
                giveReward(v.chosen_side___)
            else:
                print('\t\tBAD LUCK')
        goto_state('wait_for_center')
    elif event == 'C_nose':
        v.abandoned___ = True
        goto_state('wait_for_choice')
    elif event == 'exit':
        disarm_timer('blink_timer')
        disarm_timer('side_delay_timer')
        print('rslt,{},{},{},{},{},{}'.format(v.trial_current_number___,v.reward_seq,v.background_reward_rate,v.chosen_side___,v.outcome___,v.abandoned___))

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
def getOutcome(choice):
    v.current_sequence = v.current_sequence[1:] + choice
    v.chosen_side___ = choice
    if str(v.current_sequence[-len(v.reward_seq):]) == str(v.reward_seq):
        v.outcome___ = 'S' #reward from correct sequence
    elif withprob(v.background_reward_rate):
        v.outcome___ = 'B' # reward from background
    else:
        v.outcome___ = 'N' # not rewarded
    if v.chosen_side___ =='L':
        hw.Rpoke.LED.off()
    else:
        hw.Lpoke.LED.off()
    hw.Cpoke.LED.on()
    goto_state('wait_for_outcome')

def giveReward(side):
    if side =='R':
        hw.Rpump.infuse(v.reward_volume)
        print('\t\tRIGHT REWARD')
    else:
        hw.Lpump.infuse(v.reward_volume)
        print('\t\tLEFT REWARD')