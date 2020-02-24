from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

class Markov_setter(QtGui.QWidget):
   # For setting and getting a single variable.
    def __init__(self, grid_layout, parent, board,init_vars): # Should split into seperate init and provide info.
        super(QtGui.QWidget, self).__init__(parent) 
        self.board = board

        center = QtCore.Qt.AlignCenter
        self.left_right_box = QtGui.QGroupBox('Left and Right Variables')
        self.left_right_layout = QtGui.QGridLayout()

        self.left_lbl = QtGui.QLabel('<b>Left</b>')
        self.left_lbl.setAlignment(center)
        self.right_lbl = QtGui.QLabel('<b>Right</b>')
        self.right_lbl.setAlignment(center)
        self.reward_probability = left_right_vars(init_vars,'<b>Reward Prob 🎲 </b>',0,1,.1,'','reward_probability')
        self.req_presses = left_right_vars(init_vars,'<b>Presses 👇 </b>',1,100,1,'','required_presses')
        self.reward_volume = left_right_vars(init_vars,'<b>Reward Vol 💧 </b>',1,500,25,' µL','reward_volume')

        self.left_right_layout.addWidget(self.left_lbl,0,1)
        self.left_right_layout.addWidget(self.right_lbl,0,2)
        for i,var in enumerate([self.reward_probability, self.req_presses, self.reward_volume]):
            var.setBoard(board)
            row = i+1
            var.add_to_grid(self.left_right_layout,row)
        self.left_right_box.setLayout(self.left_right_layout)
        
        self.other_box = QtGui.QGroupBox('Other Variables')
        self.other_layout = QtGui.QGridLayout()
        self.speaker_volume = single_var(init_vars,'<b>Speaker Volume 🔈</b>',1,31,1,'','speaker_volume')
        self.error_duration = single_var(init_vars,'<b>Error Duration</b>', .5,120,.5,' s','time_error_freeze_seconds')
        self.tone_duration = single_var(init_vars,'<b>Tone Duration</b>', 1,10,.5,' s','time_tone_duration_seconds')
        self.tone_repeats = single_var(init_vars,'<b>Maximum Repeats</b>',0,20,1,'','max_tone_repeats')
        self.trial_new_block = single_var(init_vars,'<b>New Block on Trial...',0,5000,1,'','trial_new_block')
        self.continuous_tone_lbl = QtGui.QLabel('<b>Continuous Tone</b>')
        self.continuous_tone_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.other_layout.addWidget(self.continuous_tone_lbl,0,0)
        self.tone_checkbox = QtGui.QCheckBox()
        self.tone_checkbox.setChecked(eval(init_vars['continuous_tone']))
        self.other_layout.addWidget(self.tone_checkbox,0,1)
        self.tone_duration.setEnabled(not eval(init_vars['continuous_tone']))
        for i,var in enumerate([self.tone_duration,self.error_duration,self.tone_repeats,self.trial_new_block,self.speaker_volume]):
            var.setBoard(board)
            var.add_to_grid(self.other_layout,i+1)
        self.other_box.setLayout(self.other_layout)
        self.tone_checkbox.clicked.connect(self.update_tone)

        self.laser_group = QtGui.QGroupBox('Laser Variables')
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
        self.laser_probability = single_var(init_vars,'<b>Laser Probability</b>',0,1,.05,'','laser_probability')
        self.laser_probability.setBoard(board)
        self.laser_probability.setEnabled(laserIsChecked)
        self.laser_layout.addWidget(self.laser_enabled_lbl,0,0)
        self.laser_layout.addWidget(self.laser_onset_lbl,1,0)
        self.laser_layout.addWidget(self.laser_checkbox,0,1)
        self.laser_layout.addWidget(self.with_tone,1,1)
        self.laser_layout.addWidget(self.with_collection,1,2,1,2)
        self.laser_probability.add_to_grid(self.laser_layout,2)
        self.laser_group.setLayout(self.laser_layout)

        self.cerebro_group = QtGui.QGroupBox('Cerebro')
        self.cerebro_layout = QtGui.QGridLayout()
        self.single_shot = QtGui.QRadioButton('Single Shot')
        self.pulse_train = QtGui.QRadioButton('Pulse Train')
        self.start_delay = single_var(init_vars,'<b>Start Delay</b>',0,65.535,0.05,' s', 'start_delay')
        self.on_time = single_var(init_vars,'<b>On Time</b>',0,65.535,0.05,' s', 'on_time')
        self.off_time = single_var(init_vars,'<b>Off Time</b>',0,65.535,0.05,' s', 'off_time')
        self.train_dur = single_var(init_vars,'<b>Train Duration</b>',0,9999.999,0.250,' s', 'train_dur')
        self.ramp_dur = single_var(init_vars,'<b>Ramp Down</b>',.1,65.5,0.1,' s', 'ramp_dur')
        self.send_waveform_btn = QtGui.QPushButton('Send New Waveform Parameters')
        self.cerebro_layout.addWidget(self.single_shot,0,0)
        self.cerebro_layout.addWidget(self.pulse_train,0,1)
        self.start_delay.add_to_grid(self.cerebro_layout,1)
        self.on_time.add_to_grid(self.cerebro_layout,2)
        self.off_time.add_to_grid(self.cerebro_layout,3)
        self.train_dur.add_to_grid(self.cerebro_layout,4)
        self.ramp_dur.add_to_grid(self.cerebro_layout,5)
        self.cerebro_layout.addWidget(self.send_waveform_btn,6,0,1,2)
        self.cerebro_group.setLayout(self.cerebro_layout)


        grid_layout.addWidget(self.left_right_box,0,0,1,4)
        grid_layout.addWidget(self.other_box,1,0,1,3)
        grid_layout.addWidget(self.laser_group,2,0,1,2)
        grid_layout.addWidget(self.cerebro_group,3,0)
        grid_layout.setColumnStretch(9,1)
        grid_layout.setRowStretch(10,1)

        self.laser_checkbox.clicked.connect(self.update_laser)
        self.with_tone.clicked.connect(self.update_laser)
        self.with_collection.clicked.connect(self.update_laser)
        self.send_waveform_btn.clicked.connect(self.send_waveform_parameters)

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

    def send_waveform_parameters(self):
        def mills_str(parameter):
            return str(1000*round(parameter.spn.value(),3))[:-2]

        if self.board.framework_running: # Value returned later.
            self.board.set_waveform(mills_str(self.start_delay),
                                    mills_str(self.on_time),
                                    mills_str(self.off_time),
                                    mills_str(self.train_dur),
                                    mills_str(self.ramp_dur)
                                    )
        # else:
        #     self.board.exec('smd.hw.Cpoke.LED.toggle()')

class left_right_vars():
    def __init__(self,initial_vars_dict,label,min,max,step,suffix,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 35
        spin_width = 70
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
        self.leftVar = varname+'_left'
        self.rightVar = varname+'_right'
        
        if isinstance(min,float) or isinstance(max,float) or isinstance(step,float):
            self.left_spn, self.right_spn = QtGui.QDoubleSpinBox(),QtGui.QDoubleSpinBox()
        else:
            self.left_spn, self.right_spn = QtGui.QSpinBox(), QtGui.QSpinBox()

        for spn in [self.left_spn,self.right_spn]:
            spn.setRange(min,max)
            spn.setSingleStep(step)
            spn.setSuffix(suffix)
            spn.setAlignment(center)

        self.left_spn.setValue(eval(initial_vars_dict[self.leftVar]))
        self.right_spn.setValue(eval(initial_vars_dict[self.rightVar]))
        
        self.left_spn.setMaximumSize(100,100)
        self.right_spn.setMaximumSize(100,100)

        self.get_btn = QtGui.QPushButton('Get')
        self.get_btn.setMaximumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn .setMaximumWidth(button_width)
        self.set_btn.setAutoDefault(False)
        self.set_btn.clicked.connect(self.set)
        
        # self.left_spn.editingFinished.connect(self.set)
        # self.right_spn.editingFinished.connect(self.set)
    
    def setBoard(self,board):
        self.board = board

    def add_to_grid(self,grid,row):
        grid.addWidget(self.label,row,0)
        grid.addWidget(self.left_spn,row,1)
        grid.addWidget(self.right_spn,row,2)
        grid.addWidget(self.get_btn,row,3)
        grid.addWidget(self.set_btn,row,4)

    def get(self):
        if self.board.framework_running: # Value returned later.
            self.board.get_variable(self.leftVar)
            self.board.get_variable(self.rightVar)
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.left_spn.setValue(self.board.get_variable(self.leftVar))
            self.right_spn.setValue(self.board.get_variable(self.rightVar))

    def set(self):
        if self.board.framework_running: # Value returned later.
            self.board.set_variable(self.leftVar,round(self.left_spn.value(),2))
            self.board.set_variable(self.rightVar,round(self.right_spn.value(),2))
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.left_spn.setValue(self.board.get_variable(self.leftVar))
            self.right_spn.setValue(self.board.get_variable(self.rightVar))

    def reload(self):
        '''Reload value from sm_info.  sm_info is updated when variables are output
        during framework run due to get/set.'''
        self.left_spn.setValue(eval(str(self.board.sm_info['variables'][self.leftVar])))
        self.right_spn.setValue(eval(str(self.board.sm_info['variables'][self.rightVar])))


class single_var():
    def __init__(self,init_var_dict,label,min,max,step,suffix,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 35
        spin_width = 80
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
        # self.label.setToolTip(helpText)
        self.varname = varname

        if isinstance(min,float) or isinstance(max,float) or isinstance(step,float):
            self.spn = QtGui.QDoubleSpinBox()
        else:
            self.spn = QtGui.QSpinBox() 

        self.spn.setRange(min,max)
        self.spn.setValue(eval(init_var_dict[varname]))
        self.spn.setSingleStep(step)
        self.spn.setSuffix(suffix)
        self.spn.setAlignment(center)
        self.spn.setMaximumWidth(spin_width)

        self.get_btn = QtGui.QPushButton('Get')
        self.get_btn.setMaximumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn.setMaximumWidth(button_width)
        self.set_btn.setAutoDefault(False)
        self.set_btn.clicked.connect(self.set)
        # self.spn.editingFinished.connect(self.set)

    def add_to_grid(self,grid,row):
        grid.addWidget(self.label,row,0)
        grid.addWidget(self.spn,row,1)
        grid.addWidget(self.get_btn,row,2)
        grid.addWidget(self.set_btn,row,3)

    def setEnabled(self,doEnable):
        self.label.setEnabled(doEnable)
        self.spn.setEnabled(doEnable)
        self.get_btn.setEnabled(doEnable)
        self.set_btn.setEnabled(doEnable)

    def setBoard(self,board):
        self.board = board

    def get(self):
        if self.board.framework_running: # Value returned later.
            self.board.get_variable(self.varname)
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.spn.setValue(self.board.get_variable(self.varname))

    def set(self):
        if self.board.framework_running: # Value returned later.
            self.board.set_variable(self.varname,round(self.spn.value(),2))
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.spn.setValue(self.board.get_variable(self.varname))
    
    def reload(self):
        '''Reload value from sm_info.  sm_info is updated when variables are output
        during framework run due to get/set.'''
        self.spn.setValue(eval(str(self.board.sm_info['variables'][self.varname])))