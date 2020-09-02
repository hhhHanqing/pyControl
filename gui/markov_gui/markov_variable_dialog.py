from gui.dialog_elements import *

# Custom Variable dialog
class Markov_Variables_dialog(QtGui.QDialog):
    # Dialog for setting and getting task variables.
    def __init__(self, parent, board):
        super(QtGui.QDialog, self).__init__(parent)
        self.setWindowTitle('Set variables')
        self.layout = QtGui.QVBoxLayout(self)
        self.setWindowTitle('Markov Variable Setter')
        self.variables_grid = Markov_grid(self, board)
        self.layout.addWidget(self.variables_grid)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

    def process_data(self, new_data):
        self.variables_grid.markov_gui.base_station.process_data(new_data)

class Markov_grid(QtGui.QWidget):
    # Grid of variables to set/get, displayed within scroll area of dialog.
    def __init__(self, parent, board):
        super(QtGui.QWidget, self).__init__(parent)
        variables = board.sm_info['variables']
        self.grid_layout = QtGui.QGridLayout()
        initial_variables_dict = {v_name:v_value_str for (v_name, v_value_str) in sorted(variables.items())}
        self.markov_gui = Markov_GUI(self,self.grid_layout, board,initial_variables_dict)
        self.setLayout(self.grid_layout)

class Markov_GUI(QtGui.QWidget):
   # For setting and getting a single variable.
    def __init__(self, parent, grid_layout, board,init_vars): # Should split into seperate init and provide info.
        super(QtGui.QWidget, self).__init__(parent) 
        self.board = board

        center_align = QtCore.Qt.AlignCenter
        left_align = QtCore.Qt.AlignLeft
        ###### Left and Right Group #######
        # create widgets 
        self.left_right_widget = QtGui.QWidget()
        self.left_right_layout = QtGui.QGridLayout()
        self.left_lbl = QtGui.QLabel('<b>Left</b>')
        self.left_lbl.setAlignment(center_align)
        self.right_lbl = QtGui.QLabel('<b>Right</b>')
        self.right_lbl.setAlignment(center_align)
        self.reward_probability = left_right_vars(init_vars,'🎲 <b>Reward Prob</b>',0,1,.1,'','reward_probability')
        self.req_presses = left_right_vars(init_vars,'👇<b>Lever Presses</b>',1,100,1,'','required_presses')
        self.reward_volume = left_right_vars(init_vars,'💧 <b>Reward Vol</b>',1,500,25,' µL','reward_volume')

        # place widgets in layout
        self.left_right_layout.addWidget(self.left_lbl,0,1)
        self.left_right_layout.addWidget(self.right_lbl,0,2)
        for i,var in enumerate([self.reward_probability, self.req_presses, self.reward_volume]):
            var.setBoard(board)
            row = i+1
            var.add_to_grid(self.left_right_layout,row)
        self.left_right_widget.setLayout(self.left_right_layout)
        

        ###### Other Variables Group #######
        # create widgets 
        self.other_widget = QtGui.QWidget()
        self.other_layout = QtGui.QGridLayout()
        self.speaker_volume = spin_var(init_vars,'🔈 <b>Speaker Volume</b>',1,31,1,'','speaker_volume')
        self.error_duration = spin_var(init_vars,'❌ <b>Error Duration</b>', .5,120,.5,' s','time_error_freeze_seconds')
        self.tone_duration = spin_var(init_vars,'<b>Tone Duration</b>', 1,10,.5,' s','time_tone_duration_seconds')
        self.tone_repeats = spin_var(init_vars,'<b>Maximum Repeats</b>',0,20,1,'','max_tone_repeats')
        self.trial_new_block = spin_var(init_vars,'<b>New Block on Trial...',0,5000,1,'','trial_new_block')
        self.continuous_tone_lbl = QtGui.QLabel('<b>Continuous Tone</b>')
        self.continuous_tone_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.other_layout.addWidget(self.continuous_tone_lbl,0,0)
        self.tone_checkbox = QtGui.QCheckBox()
        self.tone_checkbox.setChecked(eval(init_vars['continuous_tone']))
        # place widgets
        self.other_layout.addWidget(self.tone_checkbox,0,1)
        self.tone_duration.setEnabled(not eval(init_vars['continuous_tone']))
        for i,var in enumerate([self.tone_duration,self.error_duration,self.tone_repeats,self.trial_new_block,self.speaker_volume]):
            var.setBoard(board)
            var.add_to_grid(self.other_layout,i+1)
        self.other_widget.setLayout(self.other_layout)
        self.tone_checkbox.clicked.connect(self.update_tone)

        ###### Laser Group #######
        # create widgets 
        self.laser_widget = QtGui.QWidget()
        self.laser_layout = QtGui.QGridLayout()
        self.laser_enabled_lbl = QtGui.QLabel('<b>Laser Enabled</b>')
        self.laser_enabled_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.laser_checkbox = QtGui.QCheckBox()
        withToneChecked,withCollectionChecked = eval(init_vars['laser_with_tone']), eval(init_vars['laser_with_collection'])
        if  withToneChecked or withCollectionChecked:
            laserIsChecked = True
        else:
            laserIsChecked = False
        self.laser_checkbox.setChecked(laserIsChecked)
        self.laser_onset_lbl = QtGui.QLabel('<b>Laser Onset</b>')
        self.laser_onset_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.laser_onset_lbl.setEnabled(laserIsChecked)
        self.with_tone = QtGui.QRadioButton('With Tone')
        self.with_tone.setEnabled(laserIsChecked)
        self.with_tone.setChecked(withToneChecked)
        self.with_collection = QtGui.QRadioButton('With Collection')
        self.with_collection.setEnabled(laserIsChecked)
        self.with_collection.setChecked(withCollectionChecked)
        self.laser_probability = spin_var(init_vars,'<b>Laser Probability</b>',0,1,.05,'','laser_probability')
        self.laser_probability.setBoard(board)
        self.laser_probability.setEnabled(laserIsChecked)
        # place widgets
        self.laser_layout.addWidget(self.laser_enabled_lbl,0,0)
        self.laser_layout.addWidget(self.laser_onset_lbl,1,0)
        self.laser_layout.addWidget(self.laser_checkbox,0,1)
        self.laser_layout.addWidget(self.with_tone,1,1)
        self.laser_layout.addWidget(self.with_collection,1,2,1,2)
        self.laser_probability.add_to_grid(self.laser_layout,2)
        self.laser_widget.setLayout(self.laser_layout)

        ########################## Base Station #############################3
        self.base_station = base_station(self.board,init_vars)

        self.variable_tabs = QtGui.QTabWidget()
        grid_layout.addWidget(self.variable_tabs,0,0,left_align)
        self.variable_tabs.addTab(self.left_right_widget,"Left/Right")
        self.variable_tabs.addTab(self.other_widget,"Other")
        self.variable_tabs.addTab(self.laser_widget,"Laser")
        self.variable_tabs.addTab(self.base_station.widget,"Cerebro")


        for layout in [self.left_right_layout,self.other_layout,self.laser_layout,self.base_station.cerebro_layout]:
            layout.setRowStretch(15,1)
            layout.setColumnStretch(15,1)
        grid_layout.setRowStretch(15,1)

        self.laser_checkbox.clicked.connect(self.update_laser)
        self.with_tone.clicked.connect(self.update_laser)
        self.with_collection.clicked.connect(self.update_laser)


    def update_laser(self):
        self.with_collection.setEnabled(self.laser_checkbox.isChecked())
        self.with_tone.setEnabled(self.laser_checkbox.isChecked())
        self.laser_probability.setEnabled(self.laser_checkbox.isChecked())
        self.laser_onset_lbl.setEnabled(self.laser_checkbox.isChecked())
        if self.laser_checkbox.isChecked():
            if self.board.framework_running: # Value returned later.
                self.board.set_variable('laser_with_tone',self.with_tone.isChecked())
                self.board.set_variable('laser_with_collection',self.with_collection.isChecked())
        else:
            if self.board.framework_running:
               self.board.set_variable('laser_with_tone',False)
               self.board.set_variable('laser_with_collection',False) 

    def update_tone(self):
        self.tone_duration.setEnabled(not self.tone_checkbox.isChecked())
        if self.board.framework_running:
            self.board.set_variable('continuous_tone',self.tone_checkbox.isChecked())
