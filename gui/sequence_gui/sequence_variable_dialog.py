from gui.dialog_elements import *
import re

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
        self.diode_was_different=False

    def process_data(self, new_data):
        for data_array in new_data:
            if data_array[0]=='P': # printed miessage
                data_chunks = data_array[2].split(',')
                if data_chunks[0][0]=='[' and data_chunks[0][-1]==']': # is an incoming message from cerebro
                    try:
                        msg_type = data_chunks[1]
                        if msg_type == 'Btry':
                            self.variables_grid.sequence_gui.update_battery_status(int(data_chunks[2]))
                        elif msg_type == 'DP':
                            left_pwr,right_pwr = data_chunks[2].split('-')
                            if self.variables_grid.sequence_gui.diode_power_left.spn.value() != int(left_pwr) or self.variables_grid.sequence_gui.diode_power_right.spn.value() != int(right_pwr):
                                self.diode_was_different = True
                                QtCore.QTimer.singleShot(500, self.variables_grid.sequence_gui.set_diode_powers)
                            else:
                                if self.diode_was_different:
                                    QtCore.QTimer.singleShot(500, self.variables_grid.sequence_gui.update_task_diode_powers)
                                    self.diode_was_different = False
                        elif msg_type == 'Wave':
                            start_delay,on_time,off_time,train_dur,ramp_dur = data_chunks[2].split('-')
                            if self.variables_grid.sequence_gui.pulse_train_radio.isChecked():
                                if self.variables_grid.sequence_gui.start_delay.mills_str() != start_delay or self.variables_grid.sequence_gui.on_time.mills_str() != on_time or  self.variables_grid.sequence_gui.off_time.mills_str() != off_time or  self.variables_grid.sequence_gui.train_dur.mills_str() != train_dur or ramp_dur != '0': 
                                    QtCore.QTimer.singleShot(2500, self.variables_grid.sequence_gui.send_waveform_parameters)
                            else:
                                if self.variables_grid.sequence_gui.start_delay.mills_str() != start_delay or self.variables_grid.sequence_gui.on_time.mills_str() != on_time or off_time != '0' or train_dur != '0' or self.variables_grid.sequence_gui.ramp_dur.mills_str() != ramp_dur: 
                                    QtCore.QTimer.singleShot(2500, self.variables_grid.sequence_gui.send_waveform_parameters)
                    except:
                        print("bad chunk {}".format(data_chunks))

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

        ##############  Sequence Scheduler ##############
        self.sequence_group = QtGui.QGroupBox('Bout Variables')
        self.sequence_layout = QtGui.QGridLayout()
        # create widgets
        self.reward_array = sequence_text_var(init_vars,'<b>Sequence Array</b>','sequence_array_text',text_width=150)
        self.bout_length = two_var(init_vars,'<b>Bout Length Distribution</b>','µ', 1,500,1,'','bout_mean','σ', 1,500,1,'','bout_sd')
        self.next_bout = spin_var(init_vars,'<b>Trials Until New Bout</b>', 1,500,1,'','trials_until_change')
        # place widgets
        for i,var in enumerate([self.reward_array,self.bout_length,self.next_bout]):
            var.setBoard(board)
            var.add_to_grid(self.sequence_layout,i)
        self.sequence_group.setLayout(self.sequence_layout)

        ############## Reward Variables ##############
        self.reward_group = QtGui.QGroupBox('Reward Variables')
        self.reward_layout = QtGui.QGridLayout()
        # create widgets
        self.reward_vol = spin_var(init_vars,'💧<b>Reward Volume</b>', 1,500,25,' µL','reward_volume')
        self.correct_rate = spin_var(init_vars,'✅<b>Correct Reward Rate</b>',0,1,.05,'','correct_reward_rate')
        self.background_rate = spin_var(init_vars,'🎲<b>Background Reward Rate</b>',0,1,.05,'','background_reward_rate')
        # place widgets
        for i,var in enumerate([self.reward_vol,self.correct_rate,self.background_rate]):
            var.setBoard(board)
            var.add_to_grid(self.reward_layout,i)
        self.reward_group.setLayout(self.reward_layout)

        self.center_side_tabs = QtGui.QTabWidget()
        
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
        self.forgive_window = spin_var(init_vars,'<b>Forgive Window</b>',1,1000,1,' ms','time_forgive')
        self.center_delay = spin_var(init_vars,'<b>Duration</b>',0,10000,100,' ms','time_hold_center')
        self.hold_start = spin_var(init_vars,'<b>Start</b>',1,5000,10,' ms','center_hold_start')
        self.hold_increment = spin_var(init_vars,'<b>Increment</b>',1,500,1,' ms','center_hold_increment')
        self.hold_max = spin_var(init_vars,'<b>Max</b>',1,10000,10,' ms','center_hold_max')
        # place widgets
        for i,var in enumerate([self.center_delay,self.hold_start,self.hold_increment,self.hold_max,self.forgive_window]):
            var.setBoard(board)
            var.add_to_grid(self.center_layout,i+1)

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
        self.blink_delay = spin_var(init_vars,'<b>Blink Delay</b>',50,200,10,' ms','time_blink')
        self.side_delay = spin_var(init_vars,'<b>Duration</b>',0,10000,100,' ms','time_side_delay')
        self.side_start = spin_var(init_vars,'<b>Start</b>',1,5000,10,' ms','side_delay_start')
        self.side_increment = spin_var(init_vars,'<b>Increment</b>',1,500,1,' ms','side_delay_increment')
        self.side_max = spin_var(init_vars,'<b>Max</b>',1,10000,10,' ms','side_delay_max')
        # place widgets
        for i,var in enumerate([self.side_delay,self.side_start,self.side_increment,self.side_max,self.blink_delay]):
            var.setBoard(board)
            var.add_to_grid(self.side_layout,i+1)
        self.side_widget.setLayout(self.side_layout)
        self.show_side_options()

        ###### Place groups into layout ############
        grid_layout.addWidget(self.sequence_group,0,0,left_align)
        grid_layout.addWidget(self.reward_group,1,0,left_align)
        self.center_side_tabs.addTab(self.center_widget,"Center Variables")
        self.center_side_tabs.addTab(self.side_widget,"Side Variables")
        grid_layout.addWidget(self.center_side_tabs,2,0,left_align)
        grid_layout.setRowStretch(10,1)

        self.constant_center_radio.clicked.connect(self.update_center)
        self.ramp_center_radio.clicked.connect(self.update_center)
        self.constant_side_radio.clicked.connect(self.update_side)
        self.ramp_side_radio.clicked.connect(self.update_side)

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