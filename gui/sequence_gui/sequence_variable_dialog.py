from gui.dialog_elements import *

# Custom Variable dialog
class Sequence_Variables_dialog(QtGui.QDialog):
    # Dialog for setting and getting task variables.
    def __init__(self, parent, board):
        super(QtGui.QDialog, self).__init__(parent)
        self.setWindowTitle('Set variables')
        self.layout = QtGui.QVBoxLayout(self)
        self.setWindowTitle('Sequence Variable Setter')
        self.variables_grid = Sequence_grid(self, board)
        self.layout.addWidget(self.variables_grid)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

    def process_data(self, new_data):
        self.variables_grid.sequence_gui.base_station.process_data(new_data)

class Sequence_grid(QtGui.QWidget):
    # Grid of variables to set/get, displayed within scroll area of dialog.
    def __init__(self, parent, board):
        super(QtGui.QWidget, self).__init__(parent)
        variables = board.sm_info['variables']
        self.grid_layout = QtGui.QGridLayout()
        initial_variables_dict = {v_name:v_value_str for (v_name, v_value_str) in sorted(variables.items())}
        self.sequence_gui = Sequence_GUI(self,self.grid_layout, board,initial_variables_dict)
        self.setLayout(self.grid_layout)

class Sequence_GUI(QtGui.QWidget):
   # For setting and getting a single variable.
    def __init__(self, parent, grid_layout, board,init_vars): # Should split into seperate init and provide info.
        super(QtGui.QWidget, self).__init__(parent) 
        self.board = board

        left_align = QtCore.Qt.AlignLeft
        def add_separator(layout,r,c,numR,numC):
            layout.addWidget(QtGui.QLabel('<hr>'),r,c,numR,numC)
        ##############  Sequence Scheduler ##############
        self.sequence_widget = QtGui.QWidget()
        self.sequence_layout = QtGui.QGridLayout()
        # create widgets
        self.reward_array = sequence_text_var(init_vars,'<b>Sequence(s)</b>','sequence_array_text',text_width=150)
        self.bout_length = two_var(init_vars,'<b>Bout Length Distribution</b>','µ', 1,500,1,'','bout_mean','σ', 1,500,1,'','bout_sd')
        self.next_bout = spin_var(init_vars,'<b>Trials Until New Bout</b>', 1,500,1,'','trials_until_change')
        # place widgets
        for i,var in enumerate([self.reward_array,self.bout_length,self.next_bout]):
            var.setBoard(board)
            var.add_to_grid(self.sequence_layout,i)

        i+=1
        add_separator(self.sequence_layout,i,0,1,4)
        i+=1
        ############## Reward Variables ##############
        # create widgets
        self.reward_vol = spin_var(init_vars,'<b>Reward Volume</b>', 1,500,25,' µL','reward_volume')
        self.correct_rate = spin_var(init_vars,'<b>Correct Reward Rate</b>',0,1,.05,'','correct_reward_rate')
        self.background_rate = spin_var(init_vars,'<b>Background Reward Rate</b>',0,1,.05,'','background_reward_rate')
        # place widgets
        for j,var in enumerate([self.reward_vol,self.correct_rate,self.background_rate]):
            var.setBoard(board)
            var.add_to_grid(self.sequence_layout,i+j)
        self.sequence_widget.setLayout(self.sequence_layout)

        i=i+j+1
        add_separator(self.sequence_layout,i,0,1,4)
        i+=1

        self.tone_enabled_lbl = QtGui.QLabel('<b>Tone Enabled</b>')
        self.tone_enabled_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.tone_checkbox = QtGui.QCheckBox()
        self.tone_checkbox.setChecked(eval(init_vars['tone_on']))
        i+=1
        self.sequence_layout.addWidget(self.tone_enabled_lbl,i,0)
        self.sequence_layout.addWidget(self.tone_checkbox,i,1)
        i+=1
        
        ############## Center Variables #################################################################################3
        self.center_widget = QtGui.QWidget()
        self.center_layout = QtGui.QGridLayout()
        
        self.center_hold_label = QtGui.QLabel('<b>Center Hold</b>')
        self.center_hold_label.setAlignment(QtCore.Qt.AlignRight)

        center_constant = eval(init_vars['center_hold_constant'])
        self.constant_center_radio = QtGui.QRadioButton('Constant')
        self.ramp_center_radio = QtGui.QRadioButton('Ramp Up')
        self.constant_center_radio.setChecked(center_constant)
        self.ramp_center_radio.setChecked(not center_constant)

        self.center_layout.addWidget(self.center_hold_label,0,0)
        self.center_layout.addWidget(self.constant_center_radio,0,1)
        self.center_layout.addWidget(self.ramp_center_radio,0,2,1,2)

        # create widgets
        self.forgive_window = spin_var(init_vars,'<b>Forgive Window</b>',0,1000,1,' ms','time_forgive')
        self.forgive_window.setHint('A window of time after exiting the center, where the rat can re-enter without penalty, as if he never left')
        self.center_delay = spin_var(init_vars,'<b>Duration</b>',0,10000,100,' ms','time_hold_center')
        self.center_delay.setHint('The duration the rat must hold its nose in center before the side choices are made available')
        self.hold_start = spin_var(init_vars,'<b>Start</b>',1,5000,10,' ms','center_hold_start')
        self.hold_increment = spin_var(init_vars,'<b>Increment</b>',1,500,1,' ms','center_hold_increment')
        self.hold_max = spin_var(init_vars,'<b>Max</b>',1,10000,10,' ms','center_hold_max')
        self.faulty_chance = spin_var(init_vars,'<b>Faulty Probability</b>',0,1,.05,'','faulty_chance')
        self.faulty_maxcount = spin_var(init_vars,'<b>Max Faulty Pokes</b>',0,10,1,'','max_consecutive_faulty')
        self.faulty_maxcount.setHint('Each time the center nosepoke is entered, there is a proability that the nosepoke is \"faulty\".\nThis variable adjusts the maximum number of consecutive \"faulty\" results that can occur')
        self.faulty_timer = spin_var(init_vars,'<b>Faulty Time Limit</b>',0,10000,10,' ms','faulty_time_limit')
        self.faulty_timer.setHint('If the rat leaves its nose in the poke for this amount of time, \nthen the center poke will be automatically retriggered, (and the faultiness dice will be rolled again)')
        # place widgets
        for i,var in enumerate([self.center_delay,self.hold_start,self.hold_increment,self.hold_max,self.forgive_window]):
            var.setBoard(board)
            var.add_to_grid(self.center_layout,i+1)

        i+=2
        add_separator(self.center_layout,i,0,1,4)
        i+=1
        for j,var in enumerate([self.faulty_chance,self.faulty_timer,self.faulty_maxcount]):
            var.setBoard(board)
            var.add_to_grid(self.center_layout,i+j)

        self.center_widget.setLayout(self.center_layout)
        self.show_center_options()
        
        ############## Side Variables ################################################################################33
        self.side_widget = QtGui.QWidget()
        self.side_layout = QtGui.QGridLayout()

        self.side_delay_label = QtGui.QLabel('<b>Side Delay</b>')
        self.side_delay_label.setAlignment(QtCore.Qt.AlignRight)

        side_constant = eval(init_vars['side_delay_constant'])
        self.constant_side_radio = QtGui.QRadioButton('Constant')
        self.ramp_side_radio = QtGui.QRadioButton('Ramp Up')
        self.constant_side_radio.setChecked(side_constant)
        self.ramp_side_radio.setChecked(not side_constant)

        self.side_layout.addWidget(self.side_delay_label,0,0)
        self.side_layout.addWidget(self.constant_side_radio,0,1)
        self.side_layout.addWidget(self.ramp_side_radio,0,2,1,2)
        # create widgets
        self.blink_rate = spin_var(init_vars,'<b>Blink Rate</b>',1,20,1,' Hz','time_blink_rate')
        self.blink_rate.setHint('While the outcome of the choice is being delayed,\n the chosen side will blink at this rate')
        self.side_delay = spin_var(init_vars,'<b>Duration</b>',0,10000,100,' ms','time_side_delay')
        self.side_start = spin_var(init_vars,'<b>Start</b>',1,5000,10,' ms','side_delay_start')
        self.side_increment = spin_var(init_vars,'<b>Increment</b>',1,500,1,' ms','side_delay_increment')
        self.side_max = spin_var(init_vars,'<b>Max</b>',1,10000,10,' ms','side_delay_max')
        # place widgets
        for i,var in enumerate([self.side_delay,self.side_start,self.side_increment,self.side_max,self.blink_rate]):
            var.setBoard(board)
            var.add_to_grid(self.side_layout,i+1)
        self.side_widget.setLayout(self.side_layout)
        self.show_side_options()

        ########################## Base Station #############################3
        self.base_station = base_station(self.board,init_vars)

        ###### Place groups into layout ############
        self.variable_tabs = QtGui.QTabWidget()
        self.variable_tabs.addTab(self.sequence_widget,"General")
        self.variable_tabs.addTab(self.center_widget,"Center Poke")
        self.variable_tabs.addTab(self.side_widget,"Side Pokes")
        self.variable_tabs.addTab(self.base_station.widget,"Cerebro")
        grid_layout.addWidget(self.variable_tabs,0,0,left_align)

        for layout in [self.sequence_layout,self.center_layout,self.side_layout,self.base_station.cerebro_layout]:
            layout.setRowStretch(15,1)
            layout.setColumnStretch(15,1)
        grid_layout.setRowStretch(10,1)

        self.constant_center_radio.clicked.connect(self.update_center)
        self.ramp_center_radio.clicked.connect(self.update_center)
        self.constant_side_radio.clicked.connect(self.update_side)
        self.ramp_side_radio.clicked.connect(self.update_side)
        self.tone_checkbox.clicked.connect(self.update_tone)

    def update_center(self):
        self.show_center_options()
        if self.board.framework_running: # Value returned later.
            self.board.set_variable('center_hold_constant',self.constant_center_radio.isChecked())

    def show_center_options(self):
        self.center_delay.setEnabled(self.constant_center_radio.isChecked())
        self.hold_start.setEnabled(not self.constant_center_radio.isChecked())
        self.hold_increment.setEnabled(not self.constant_center_radio.isChecked())
        self.hold_max.setEnabled(not self.constant_center_radio.isChecked())

    def update_side(self):
        self.show_side_options()
        if self.board.framework_running: # Value returned later.
            self.board.set_variable('side_delay_constant',self.constant_side_radio.isChecked())

    def show_side_options(self):
        self.side_delay.setEnabled(self.constant_side_radio.isChecked())
        self.side_start.setEnabled(not self.constant_side_radio.isChecked())
        self.side_increment.setEnabled(not self.constant_side_radio.isChecked())
        self.side_max.setEnabled(not self.constant_side_radio.isChecked())

    def update_tone(self):
        if self.board.framework_running: # Value returned later.
            self.board.set_variable('tone_on',self.tone_checkbox.isChecked()) 