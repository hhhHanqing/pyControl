from devices import *
import pyControl.hardware as _h

#2019080800 ## yearmonthdayrevision yyyymmddrr  

board = Breakout_dseries_1_5()

# button      = _h.Digital_input(board.button,rising_event='button_release',falling_event='button',pull='up')

########## Top Row #############
Llever      = Lever_electric(board.port_1, lever_event = 'L_lever')
Rlever      = Lever_electric(board.port_2, lever_event = 'R_lever')
houselight  = _h.Digital_output(board.port_3.POW_A)
Lpoke       = Nosepoke(board.port_4, nose_event = 'L_nose', lick_event = 'L_lick' )
Cpoke       = Nosepoke(board.port_5, nose_event = 'C_nose')
Rpoke       = Nosepoke(board.port_6, nose_event = 'R_nose', lick_event = 'R_lick' )

######### Bottom Row ###########
# empty port 7
Speakers    = Teensy_audio(board.port_8)
# empty port 9
BaseStation = Base_station(board.port_10) 
Rpump       = Syringe_pump(board.port_11)
Lpump       = Syringe_pump(board.port_12)