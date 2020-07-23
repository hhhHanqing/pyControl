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
    'side_delay_timer',
    'button',
    ]

####### Hidden script variables ##########
v.trial_current_number___ = 0
v.chosen_side___ = ''
v.abandoned___ = False
v.in_center___ = False
v.hold_center___ = 0
v.side_delay___ = 0
v.sequence_index___ = -1
##### Configurable Variables #######

### Bout Variables
v.sequence_array_text = "LLR-RRL-RRLRR-LLL"
v.bout_mean = 10
v.bout_sd = 4
v.trials_until_change = 0

### Reward Variables
v.reward_seq___ = 'LLR'
v.block_change_trial = 0
v.correct_reward_rate = 0.9
v.background_reward_rate = .1
v.reward_volume = 250 # microliters

### Center Variables
v.time_hold_center = 100 # milliseconds 
v.time_forgive = 500
v.center_hold_constant = True
v.center_hold_start = 500
v.center_hold_increment = 1
v.center_hold_max = 5000

### Side Variables
v.time_blink = 100 # milliseconds
v.time_side_delay = 500 # milliseconds
v.side_delay_constant = True
v.side_delay_start = 500
v.side_delay_increment = 1
v.side_delay_max = 8000

#Other variables
v.current_sequence = '______' # up to 6 letter sequence
initial_state = 'wait_for_center'

def run_start():
    start_new_block()
    # assign bout lengths
    # start_new_block()

def wait_for_center(event):
    if event == 'entry':
        hw.Cpoke.LED.on()
        hw.Rpoke.LED.off()
        hw.Lpoke.LED.off()
    elif event == 'C_nose':
        v.in_center___ = True
        if timer_remaining('center_hold_timer') == 0: # the timer doesn't exist
            set_timer('center_hold_timer',v.hold_center___, output_event=True)
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
        set_timer('blink_timer', v.time_blink) # start blinking
        set_timer('side_delay_timer', v.side_delay___, output_event=True)
    elif event == 'blink_timer': # blink every time_blink
        if v.chosen_side___ == 'L' :
            hw.Lpoke.LED.toggle()
        else:
            hw.Rpoke.LED.toggle()
        set_timer('blink_timer', v.time_blink)
    elif event == 'side_delay_timer': # side delay has expired, can now deliver reward and/or move on to next trial initiation
        if v.outcome___ != 'N':
            if withprob(v.correct_reward_rate):
                giveReward(v.chosen_side___)
            else:
                print('\t\tBAD LUCK')
        goto_state('wait_for_center')
    elif event == 'C_nose': # abandon the choice (don't wait for outcome)
        v.abandoned___ = True
        v.in_center___ = True
        set_timer('center_hold_timer',v.hold_center___, output_event=True)
        goto_state('wait_for_center')
    elif event == 'exit':
        disarm_timer('blink_timer')
        disarm_timer('side_delay_timer')
        print('rslt,{},{},{},{},{},{}'.format(v.trial_current_number___,v.reward_seq___,v.background_reward_rate,v.chosen_side___,v.outcome___,v.abandoned___))
        v.trials_until_change += -1
        if v.trials_until_change<=0:
            start_new_block()

def all_states(event):
    Lmsg = hw.Lpump.check_for_serial()
    if Lmsg:
        print("Stoping task. Left pump empty")
        stop_framework()
    Rmsg = hw.Rpump.check_for_serial()
    if Rmsg:
        print("Stopping task. Right pump empty")
        stop_framework()
    elif event == 'button':
        start_new_block()

################ helper functions ############
def start_new_block ():
    v.sequence_index___+=1
    sequence_array = v.sequence_array_text.upper().split('-')
    
    if v.sequence_index___ == len(sequence_array): # loop around to the start if we're at the end of the sequence array
        v.sequence_index___ = 0

    v.reward_seq___ = sequence_array[v.sequence_index___]
    # get next sequence from array
    # set new block_change_trial
    v.trials_until_change =  int(gauss_rand(v.bout_mean,v.bout_sd))
    # update sequence count
    # if new lap, update lap count
    print('NB,{},{}'.format(v.reward_seq___,v.trials_until_change))

def getOutcome(choice):
    v.current_sequence = v.current_sequence[1:] + choice
    v.chosen_side___ = choice

    updateHold()
    updateSide()

    ## set outcome variable
    if str(v.current_sequence[-len(v.reward_seq___):]) == str(v.reward_seq___):
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

def updateHold():
    if v.center_hold_constant:
        v.hold_center___ = v.time_hold_center
    else:
        v.hold_center___ = min(v.center_hold_start + v.trial_current_number___ * v.center_hold_increment, v.center_hold_max )
    print(v.hold_center___)

def updateSide():
    if v.side_delay_constant:
        v.side_delay___ = v.time_side_delay
    else:
        v.side_delay___ = min(v.side_delay_start + v.trial_current_number___ * v.side_delay_increment, v.side_delay_max )
    print(v.side_delay___)