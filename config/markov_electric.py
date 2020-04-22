from devices import *
import pyControl.hardware as _h

#2019080800 ## yearmonthdayrevision yyyymmddrr  

board = Breakout_dseries_1_6()

button      = _h.Digital_input(board.button,rising_event='button_release',falling_event='button',pull='up')

########## Top Row #############
Lpoke       = Nosepoke(board.port_1, nose_event = 'L_nose', lick_event = 'L_lick' )
Cpoke       = Nosepoke(board.port_2, nose_event = 'C_nose')
Rlever      = Lever_electric(board.port_3, lever_event = 'R_lever')
Llever      = Lever_electric(board.port_4, lever_event = 'L_lever')
Rpoke       = Nosepoke(board.port_5, nose_event = 'R_nose', lick_event = 'R_lick' )
houselight  = _h.Digital_output(board.port_6.POW_A)

######### Bottom Row ###########
# empty port 7
Speakers    = Teensy_audio(board.port_8)
# empty port 9
BaseStation = Base_station_serial(board.port_10) 
Rpump       = Syringe_pump(board.port_11)
Lpump       = Syringe_pump(board.port_12)