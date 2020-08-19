from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

class left_right_vars():
    def __init__(self,initial_vars_dict,label,min,max,step,suffix,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 35
        spin_width = 85
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
        
        self.left_spn.setMinimumWidth(spin_width)
        self.right_spn.setMinimumWidth(spin_width)

        self.get_btn = QtGui.QPushButton('Get')
        self.get_btn.setMinimumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn.setMinimumWidth(button_width)
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

class spin_var():
    def __init__(self,init_var_dict,label,min,max,step,suffix,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 65
        spin_width = 85
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
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
        self.spn.setMinimumWidth(spin_width)

        self.get_btn = QtGui.QPushButton('Get')
        self.get_btn.setMinimumWidth(button_width)
        self.get_btn.setMaximumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn.setMinimumWidth(button_width)
        self.set_btn.setMaximumWidth(button_width)
        self.set_btn.setAutoDefault(False)
        self.set_btn.clicked.connect(self.set)

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

    def setVisible(self,makeVisible):
        self.label.setVisible(makeVisible)
        self.spn.setVisible(makeVisible)
        self.get_btn.setVisible(makeVisible)
        self.set_btn.setVisible(makeVisible)
        
class two_var():
    def __init__(self,init_var_dict,label0,label,min,max,step,suffix,varname,label2,min2,max2,step2,suffix2,varname2):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 65
        spin_width = 55 
        self.label0 = QtGui.QLabel(label0)
        self.label0.setAlignment(right|Vcenter)

        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
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
        self.spn.setMinimumWidth(spin_width)


        self.label2 = QtGui.QLabel(label2)
        self.label2.setAlignment(right|Vcenter)
        self.varname2 = varname2

        if isinstance(min2,float) or isinstance(max2,float) or isinstance(step2,float):
            self.spn2 = QtGui.QDoubleSpinBox()
        else:
            self.spn2 = QtGui.QSpinBox() 

        self.spn2.setRange(min,max)
        self.spn2.setValue(eval(init_var_dict[varname2]))
        self.spn2.setSingleStep(step2)
        self.spn2.setSuffix(suffix2)
        self.spn2.setAlignment(center)
        self.spn2.setMinimumWidth(spin_width)


        self.get_btn = QtGui.QPushButton('Get')
        self.get_btn.setMinimumWidth(button_width)
        self.get_btn.setMaximumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn.setMinimumWidth(button_width)
        self.set_btn.setMaximumWidth(button_width)
        self.set_btn.setAutoDefault(False)
        self.set_btn.clicked.connect(self.set)

    def add_to_grid(self,grid,row):
        grid.addWidget(self.label0,row,0)
        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spn)
        layout.addWidget(self.label2)
        layout.addWidget(self.spn2)
        layout.setContentsMargins(0,0,0,0)
        widget.setLayout(layout)
        grid.addWidget(widget,row,1)
        grid.addWidget(self.get_btn,row,2)
        grid.addWidget(self.set_btn,row,3)

    def setEnabled(self,doEnable):
        self.label.setEnabled(doEnable)
        self.spn.setEnabled(doEnable)
        self.label2.setEnabled(doEnable)
        self.spn2.setEnabled(doEnable)
        self.get_btn.setEnabled(doEnable)
        self.set_btn.setEnabled(doEnable)

    def setBoard(self,board):
        self.board = board

    def get(self):
        if self.board.framework_running: # Value returned later.
            self.board.get_variable(self.varname)
            self.board.get_variable(self.varname2)
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.spn.setValue(self.board.get_variable(self.varname))
            self.spn2.setValue(self.board.get_variable(self.varname2))

    def set(self):
        if self.board.framework_running: # Value returned later.
            self.board.set_variable(self.varname,round(self.spn.value(),2))
            self.board.set_variable(self.varname2,round(self.spn2.value(),2))
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.spn.setValue(self.board.get_variable(self.varname))
            self.spn2.setValue(self.board.get_variable(self.varname2))
    
    def reload(self):
        '''Reload value from sm_info.  sm_info is updated when variables are output
        during framework run due to get/set.'''
        self.spn.setValue(eval(str(self.board.sm_info['variables'][self.varname])))
        self.spn2.setValue(eval(str(self.board.sm_info['variables'][self.varname2])))

    def setVisible(self,makeVisible):
        self.label.setVisible(makeVisible)
        self.spn.setVisible(makeVisible)
        self.label2.setVisible(makeVisible)
        self.spn2.setVisible(makeVisible)
        self.get_btn.setVisible(makeVisible)
        self.set_btn.setVisible(makeVisible)

class text_var():
    def __init__(self,init_var_dict,label,varname='',text_width=80):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 65
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
        self.varname = varname

        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setAlignment(center)
        self.line_edit.setMinimumWidth(text_width)
        self.line_edit.setMaximumWidth(text_width)
        self.line_edit.setText(eval(init_var_dict[varname]))

        self.get_btn = QtGui.QPushButton('Get')
        self.get_btn.setMinimumWidth(button_width)
        self.get_btn.setMaximumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn.setMinimumWidth(button_width)
        self.set_btn.setMaximumWidth(button_width)
        self.set_btn.setAutoDefault(False)
        self.set_btn.clicked.connect(self.set)

    def add_to_grid(self,grid,row):
        grid.addWidget(self.label,row,0)
        grid.addWidget(self.line_edit,row,1)
        grid.addWidget(self.get_btn,row,2)
        grid.addWidget(self.set_btn,row,3)

    def setEnabled(self,doEnable):
        self.label.setEnabled(doEnable)
        self.line_edit.setEnabled(doEnable)
        self.get_btn.setEnabled(doEnable)
        self.set_btn.setEnabled(doEnable)

    def setBoard(self,board):
        self.board = board

    def get(self):
        if self.board.framework_running: # Value returned later.
            self.board.get_variable(self.varname)
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.line_edit.setText(self.board.get_variable(self.varname))

    def set(self):
        if self.board.framework_running: # Value returned later.
            self.board.set_variable(self.varname,self.line_edit.text().upper())
            QtCore.QTimer.singleShot(200, self.reload)
        else: # Value returned immediately.
            self.line_edit.setText(self.board.get_variable(self.varname))
    
    def reload(self):
        '''Reload value from sm_info.  sm_info is updated when variables are output
        during framework run due to get/set.'''
        self.line_edit.setText(str(self.board.sm_info['variables'][self.varname]))

class sequence_text_var(text_var):
    def set(self):
        if self.board.framework_running: # Value returned later.
            # can't be blank/
            # only lrLR-
            good_letters = re.compile('[^lrLR-]')
            single_dashes = re.compile('[-]{2,}') # single dashes only
            new_sequence_string = self.line_edit.text()
            if good_letters.search(new_sequence_string) == None:
                if single_dashes.search(new_sequence_string):
                    msg = QtGui.QMessageBox()
                    msg.setIcon(QtGui.QMessageBox.Warning)
                    msg.setText("Invalid Input")
                    msg.setInformativeText("There is more than 1 \"-\" somehwere")
                    msg.setWindowTitle("Input Error")
                    msg.exec()
                else:
                    self.board.set_variable(self.varname,self.line_edit.text().upper())
                    QtCore.QTimer.singleShot(200, self.reload)
            else:
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.setText("Invalid Input")
                msg.setInformativeText('Sequences can only be made up of letters \"L\" and \"R\" and should be separated by a single \"-\"')
                msg.setWindowTitle("Input Error")
                msg.exec()
        else: # Value returned immediately.
            self.line_edit.setText(self.board.get_variable(self.varname))


class wave_var():
    def __init__(self,init_var_dict,label,min,max,step,suffix,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 35
        spin_width = 80
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
        self.varname = varname

        if isinstance(min,float) or isinstance(max,float) or isinstance(step,float):
            self.spn = QtGui.QDoubleSpinBox()
        else:
            self.spn = QtGui.QSpinBox() 

        self.spn.setRange(min,max)
        if varname != '':
            self.spn.setValue(eval(init_var_dict[varname]))
        self.spn.setSingleStep(step)
        self.spn.setSuffix(suffix)
        self.spn.setAlignment(center)
        self.spn.setMaximumWidth(spin_width)

    def mills_str(self):
            return str(1000*round(self.spn.value(),3))[:-2]

    def add_to_grid(self,grid,row,col_offset=0):
        grid.addWidget(self.label,row,0+col_offset)
        grid.addWidget(self.spn,row,1+col_offset)

    def setVisible(self,makeVisible):
        self.label.setVisible(makeVisible)
        self.spn.setVisible(makeVisible)
    
    def setEnabled(self,enable):
        self.label.setEnabled(enable)
        self.spn.setEnabled(enable)

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


class single_var():
    def __init__(self,init_var_dict,label,min,max,step,suffix,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 35
        spin_width = 80
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
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
        self.get_btn.setMinimumWidth(button_width)
        self.get_btn.setAutoDefault(False)
        self.get_btn.clicked.connect(self.get)

        self.set_btn = QtGui.QPushButton('Set')
        self.set_btn.setMinimumWidth(button_width)
        self.set_btn.setAutoDefault(False)
        self.set_btn.clicked.connect(self.set)

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


class base_station():

    def __init__(self,board,init_vars):
        self.board = board
        self.diode_was_different=False


        # create widgets 
        self.cerebro_group = QtGui.QGroupBox('Cerebro')
        self.cerebro_layout = QtGui.QGridLayout()
        self.cerebro_channel = wave_var(init_vars,'<b>Cerebro Channel</b>',0,120,1,'')
        self.cerebro_channel.setBoard(board)
        self.diode_power_left = wave_var(init_vars,'<b>Left Power</b>',0,1023,1,'','diode_power_left')
        self.diode_power_right = wave_var(init_vars,'<b>Right Power</b>',0,1023,1,'','diode_power_right')
        self.blink_base_btn = QtGui.QPushButton('Blink Base Station')
        self.blink_base_btn.setAutoDefault(False)
        self.cerebro_connect_btn = QtGui.QPushButton('Connect To Cerebro')
        self.cerebro_connect_btn.setAutoDefault(False)
        self.cerebro_refresh_btn = QtGui.QPushButton('Refresh')
        self.cerebro_refresh_btn.setAutoDefault(False)
        self.battery_indicator = QtGui.QProgressBar()
        self.battery_indicator.setRange(0,100)
        self.battery_indicator.setValue(0)
        self.battery_indicator.setFormat("%p%")
        self.single_shot_radio = QtGui.QRadioButton('Single Shot')
        self.pulse_train_radio = QtGui.QRadioButton('Pulse Train')
        self.start_delay = wave_var(init_vars,'<b>Start Delay</b>',0,65.535,0.05,' s', 'start_delay')
        self.on_time = wave_var(init_vars,'<b>On Time</b>',0,65.535,0.05,' s', 'on_time')
        self.off_time = wave_var(init_vars,'<b>Off Time</b>',0,65.535,0.05,' s', 'off_time')
        self.train_dur = wave_var(init_vars,'<b>Train Duration</b>',0,9999.999,0.250,' s', 'train_dur')
        self.ramp_dur = wave_var(init_vars,'<b>Ramp Down</b>',0,65.5,0.1,' s', 'ramp_dur')
        self.send_waveform_btn = QtGui.QPushButton('Send New Waveform Parameters')
        self.send_waveform_btn.setAutoDefault(False)
        self.test_btn = QtGui.QPushButton('Click=Trigger      \n Shift+Click=Stop')
        self.test_btn.setAutoDefault(False)
        # place widgets
        self.cerebro_layout.addWidget(self.blink_base_btn,0,1,1,2)
        self.cerebro_channel.add_to_grid(self.cerebro_layout,1)
        self.cerebro_layout.addWidget(self.cerebro_connect_btn,3,2,1,2)
        self.diode_power_left.add_to_grid(self.cerebro_layout,2)
        self.diode_power_right.add_to_grid(self.cerebro_layout,3,0)
        self.cerebro_layout.addWidget(self.battery_indicator,4,0,1,3)
        self.cerebro_layout.addWidget(self.cerebro_refresh_btn,4,3)
        self.cerebro_layout.addWidget(self.single_shot_radio,5,0)
        self.cerebro_layout.addWidget(self.pulse_train_radio,5,1)
        self.start_delay.add_to_grid(self.cerebro_layout,6,0)
        self.on_time.add_to_grid(self.cerebro_layout,7,0)
        self.off_time.add_to_grid(self.cerebro_layout,8,0)
        self.ramp_dur.add_to_grid(self.cerebro_layout,9,0)
        self.train_dur.add_to_grid(self.cerebro_layout,10,0)
        self.cerebro_layout.addWidget(self.send_waveform_btn,10,2,1,2)
        self.cerebro_layout.addWidget(self.test_btn,11,0,2,4)
        self.cerebro_group.setLayout(self.cerebro_layout)

        is_pulse_train = (eval(init_vars['pulse_train']))
        self.single_shot_radio.setChecked(not is_pulse_train)
        self.pulse_train_radio.setChecked(is_pulse_train)
        if is_pulse_train:
            self.ramp_dur.setEnabled(False)
        else:
            self.off_time.setEnabled(False)
            self.train_dur.setEnabled(False)

        self.blink_base_btn.clicked.connect(self.blink_station)
        self.cerebro_connect_btn.clicked.connect(self.connect_to_cerebro)
        self.cerebro_refresh_btn.clicked.connect(self.get_battery)
        self.single_shot_radio.clicked.connect(self.update_cerebro_input)
        self.pulse_train_radio.clicked.connect(self.update_cerebro_input)
        self.send_waveform_btn.clicked.connect(self.send_waveform_parameters)
        self.test_btn.clicked.connect(self.test_trigger_stop)


    def connect_to_cerebro(self):
        if self.board.framework_running:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                self.board.set_cerebro_serial(self.cerebro_channel.spn.value())
            else:
                self.board.initialize_cerebro_connection(self.cerebro_channel.spn.value())

    def set_diode_powers(self):
        if self.board.framework_running:
            self.board.set_diode_powers(self.diode_power_left.spn.value(),self.diode_power_right.spn.value())

    def update_task_diode_powers(self):
        if self.board.framework_running:
            self.board.set_variable('diode_power_left',self.diode_power_left.spn.value())
            self.board.set_variable('diode_power_right',self.diode_power_right.spn.value())

    def get_battery(self):
        if self.board.framework_running:
            self.board.get_cerebro_battery()

    def test_trigger_stop(self):
        if self.board.framework_running:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                self.board.test_base_stop()
            else:
                self.board.test_base_trigger()

    def update_cerebro_input(self):
        if self.pulse_train_radio.isChecked():
            self.off_time.setEnabled(True)
            self.train_dur.setEnabled(True)
            self.ramp_dur.setEnabled(False)
        else:
            self.off_time.setEnabled(False)
            self.train_dur.setEnabled(False)
            self.ramp_dur.setEnabled(True)

    def send_waveform_parameters(self):
        if self.board.framework_running: # Value returned later.
            if self.pulse_train_radio.isChecked():
                self.board.set_waveform(self.start_delay.mills_str(),
                                        self.on_time.mills_str(),
                                        self.off_time.mills_str(),
                                        self.train_dur.mills_str(),
                                        '0' 
                                        )
            else:
                self.board.set_waveform(self.start_delay.mills_str(),
                                        self.on_time.mills_str(),
                                        '0',
                                        '0',
                                        self.ramp_dur.mills_str()
                                        )

            self.board.set_variable('pulse_train',self.pulse_train_radio.isChecked())
            self.board.set_variable('start_delay',self.start_delay.spn.value())
            self.board.set_variable('on_time',self.on_time.spn.value())
            self.board.set_variable('off_time',self.off_time.spn.value())
            self.board.set_variable('train_dur',self.train_dur.spn.value())
            self.board.set_variable('ramp_dur',self.ramp_dur.spn.value())

    def update_battery_status(self,battery_percentage):
        self.battery_indicator.setValue(battery_percentage)

    def blink_station(self):
        self.board.blink_base()
        
    def process_data(self,new_data):
        for data_array in new_data:
            if data_array[0]=='P': # printed miessage
                data_chunks = data_array[2].split(',')
                if data_chunks[0][0]=='[' and data_chunks[0][-1]==']': # is an incoming message from cerebro
                    try:
                        msg_type = data_chunks[1]
                        if msg_type == 'Btry':
                            self.update_battery_status(int(data_chunks[2]))
                        elif msg_type == 'DP':
                            left_pwr,right_pwr = data_chunks[2].split('-')
                            if self.diode_power_left.spn.value() != int(left_pwr) or self.diode_power_right.spn.value() != int(right_pwr):
                                self.diode_was_different = True
                                QtCore.QTimer.singleShot(500, self.set_diode_powers)
                            else:
                                if self.diode_was_different:
                                    QtCore.QTimer.singleShot(500, self.update_task_diode_powers)
                                    self.diode_was_different = False
                        elif msg_type == 'Wave':
                            start_delay,on_time,off_time,train_dur,ramp_dur = data_chunks[2].split('-')
                            if self.pulse_train_radio.isChecked():
                                if self.start_delay.mills_str() != start_delay or self.on_time.mills_str() != on_time or  self.off_time.mills_str() != off_time or  self.train_dur.mills_str() != train_dur or ramp_dur != '0': 
                                    QtCore.QTimer.singleShot(2500, self.send_waveform_parameters)
                            else:
                                if self.start_delay.mills_str() != start_delay or self.on_time.mills_str() != on_time or off_time != '0' or train_dur != '0' or self.ramp_dur.mills_str() != ramp_dur: 
                                    QtCore.QTimer.singleShot(2500, self.send_waveform_parameters)
                    except:
                        print("bad chunk {}".format(data_chunks))