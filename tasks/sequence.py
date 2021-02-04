from pyControl.utility import *
from pyControl.competitor import *
import hardware_definition as hw
version = 2021020300 ## YearMonthDayRevision YYYYMMDDrr  can have up to 100 revisions/day
states= [
    'wait_for_center',
    'wait_for_choice',
    'wait_for_outcome'
    ]

events = [
    'L_nose','L_nose_out',
    'C_nose','C_nose_out',
    'R_nose','R_nose_out',
    'held_long_enough',
    'forgive_window_closed',
    'blink_timer',
    'side_delay_timer',
    'button',
    'check_serial',
    'Sync_pulse'
    ]

####### Hidden script variables ##########
v.trial_current_number___ = 0
v.chosen_side___ = ''
v.abandoned___ = False
v.in_center___ = False
v.hold_center___ = 0
v.side_delay___ = 0
v.sequence_index___ = -1
v.completed_sequences___ = 0
##### Configurable Variables #######

### Bout Variables
v.sequence_array_text = "LLR-RRL"
v.bout_mean = 175
v.bout_sd = 25
v.trials_until_change = 0
v.tone_on = True

### Reward Variables
v.reward_seq___ = 'LLR'
v.block_change_trial = 0
v.correct_reward_rate = 0.9
v.background_reward_rate = 0
v.reward_volume = 400 # microliters

### Center Variables
v.time_hold_center = 100 # milliseconds 
v.time_forgive = 200
v.center_hold_constant = True
v.center_hold_start = 500
v.center_hold_increment = 1
v.center_hold_max = 5000

### Side Variables
v.time_blink = 100 # milliseconds
v.time_side_delay = 10 # milliseconds
v.side_delay_constant = True
v.side_delay_start = 500
v.side_delay_increment = 1
v.side_delay_max = 8000

#Cerebro variables
v.diode_power_left = 0
v.diode_power_right = 0
v.pulse_train = False
v.start_delay = 0
v.on_time = 2
v.off_time = 0
v.train_dur = 0
v.ramp_dur = 0.3

#Other variables
v.current_sequence = '______' # up to 6 letter sequence
initial_state = 'wait_for_center'
competitor = Competitor()

def run_start():
    print("Task_Version,{}".format(version))
    for key in v.__dict__.keys():
        print("{},{}".format(key,getattr(v,key))) 
    print("Variables_End,~~~~~")
    start_new_block()
    hw.Speakers.set_volume(30)
    updateHold()
    updateSide()
    set_timer('check_serial',10)
    hw.Camera.frame_grab_trigger.pulse(50) # trigger frame grab at 50Hz for 50fps video
    hw.Camera.light.on()
    # hw.Camera.light.pulse(freq=5000,duty_cycle=50) # duty_cycle can be 10,25,50 or 75

def wait_for_center(event):
    if event == 'entry':
        hw.Cpoke.LED.on()
        hw.Rpoke.LED.off()
        hw.Lpoke.LED.off()
    elif event == 'C_nose':
        v.in_center___ = True
        if timer_remaining('held_long_enough') == 0: # the timer doesn't exist, we are at the start of holding our nose inside the poke
            set_timer('held_long_enough',v.hold_center___, output_event=True) # create this timer. when it is done check if we're still inside the nosepoke, and if so then we've held our nose long enough and can move on to next state
        else:
            disarm_timer('forgive_window_closed') #pretend like we never left the center nosepoke.
    elif event == 'C_nose_out':
        v.in_center___ = False
        set_timer('forgive_window_closed',v.time_forgive,output_event=True) # we just exited the center. we now have a limited window of time to return back to the center and be forgiven as if we never left.
    elif event == 'forgive_window_closed':
        disarm_timer('held_long_enough') # we exited the nosepoke a while ago and haven't returned within the window of forgiveness. Therefore our center hold timer is disarmed. We will have to make a new attempt at trying hold our nose in the center.
    elif event == 'held_long_enough':
        if v.in_center___: # if our nose is still in the port after all this time then we can now move to the next state.
            goto_state('wait_for_choice')
    elif event == 'exit':
        if v.tone_on:
            hw.Speakers.beep()

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
    elif event == 'exit':
        if v.tone_on:
            hw.Speakers.beep()

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
        if v.outcome___ == 'C':
            v.completed_sequences___ += 1
            if withprob(v.correct_reward_rate):
                giveReward(v.chosen_side___)
            else:
                v.outcome___ = 'W' # witheld
        elif v.outcome___ == 'B':
            giveReward(v.chosen_side___)
        goto_state('wait_for_center')
    elif event == 'C_nose': # abandon the choice (don't wait for outcome)
        v.abandoned___ = True
        v.in_center___ = True
        set_timer('held_long_enough',v.hold_center___, output_event=True)
        goto_state('wait_for_center')
    elif event == 'exit':
        disarm_timer('blink_timer')
        disarm_timer('side_delay_timer')
        print('rslt,{},{},{},{},{},{},{},{}'.format(v.trial_current_number___,v.reward_seq___,v.chosen_side___,v.outcome___,int(v.abandoned___),v.reward_volume,v.time_hold_center,v.time_side_delay))
        if v.abandoned___:
            competitor.update_competitor(v.chosen_side___,False)
        else:
            competitor.update_competitor(v.chosen_side___,v.outcome___)
        v.trials_until_change += -1
        if v.trials_until_change<=0:
            start_new_block()

"""
There are 2 general outcomes, rewarded or not rewarded.
There are 5 different paths for arriving at those outcomes.
Below is the decision tree and descriptions of the 5 paths.


                               Correct Sequence?
                                       +
                                       |
                                 NO    |    YES
 Favorable outcome with    <-----------+----------->  Favorable outcome with
"background_reward_rate"?                              "correct_reward_rate"?
             +                                                  +
             |                                                  |
   NO        |         YES                             NO       |       YES
   +---------+-----------+                             +--------+---------+
   |                     |                             |                  |
   |                     |                             |                  |
   |                     v                             |                  |
   |         Predicted by competitor?                  |                  |
   |                     +                             |                  |
   |                     |                             |                  |
   |             NO      |      YES                    |                  |
   |             +-------+--------+                    |                  |
   |             |                |                    |                  |
   |             |                |                    |                  |
   v             v                v                    v                  v

  'N'           'B'              'P'                  'W'                'C'
              Rewarded                                                 Rewarded

N: not rewarded
B: background rewarded
P: predicted
W: withheld
C: correct choice rewarded

"""

def all_states(event):
    if event == 'check_serial':
        set_timer('check_serial',10)
        msg = hw.BaseStation.check_for_serial()
        if msg:
            print(msg)
    Lmsg = hw.Lpump.check_for_serial()
    if Lmsg:
        print("Stoping task. Left pump empty")
        stop_framework()
    Rmsg = hw.Rpump.check_for_serial()
    if Rmsg:
        print("Stopping task. Right pump empty")
        stop_framework()
    if event == 'button':
        pass

def run_end():
    hw.BaseStation.set_to_zero()

################ helper functions ############
def start_new_block ():
    v.sequence_index___+=1
    sequence_array = v.sequence_array_text.upper().split('-')
    
    # get new sequence
    if v.sequence_index___ == len(sequence_array): # loop around to the start if we're at the end of the sequence array
        v.sequence_index___ = 0
    v.reward_seq___ = sequence_array[v.sequence_index___]

    # get upcoming sequence
    next_index = v.sequence_index___ + 1
    if next_index == len(sequence_array): # loop around to the start if we're at the end of the sequence array
        next_index = 0
    next_seq = sequence_array[next_index]

    # set new block_change_trial
    v.trials_until_change =  int(gauss_rand(v.bout_mean,v.bout_sd))
    print('NB,{},{},{}'.format(v.reward_seq___,v.trials_until_change,next_seq))

def getOutcome(choice):
    v.current_sequence = v.current_sequence[1:] + choice
    v.chosen_side___ = choice

    updateHold()
    updateSide()

    ## set outcome variable
    v.outcome___ = 'N' # not rewarded
    if str(v.current_sequence[-len(v.reward_seq___):]) == str(v.reward_seq___):
        v.outcome___ = 'C' #reward from correct sequence
    elif withprob(v.background_reward_rate):
        if choice == competitor.predict():
            v.outcome___ = 'P' # predicted
        else:
            v.outcome___ = 'B' # reward from background for being unpredictable
    if v.chosen_side___ =='L':
        hw.Rpoke.LED.off()
    else:
        hw.Lpoke.LED.off()
    hw.Cpoke.LED.on()
    goto_state('wait_for_outcome')

def giveReward(side):
    if side =='R':
        hw.Rpump.infuse(v.reward_volume)
    else:
        hw.Lpump.infuse(v.reward_volume)

def updateHold():
    if v.center_hold_constant:
        v.hold_center___ = v.time_hold_center
    else:
        v.hold_center___ = min(v.center_hold_start + v.trial_current_number___ * v.center_hold_increment, v.center_hold_max )

def updateSide():
    if v.side_delay_constant:
        v.side_delay___ = v.time_side_delay
    else:
        v.side_delay___ = min(v.side_delay_start + v.trial_current_number___ * v.side_delay_increment, v.side_delay_max )