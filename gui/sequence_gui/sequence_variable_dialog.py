from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

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

        center = QtCore.Qt.AlignCenter

        ###### Other Variables Group #######
        # create widgets 
        self.other_box = QtGui.QGroupBox('Variables')
        self.other_layout = QtGui.QGridLayout()
        self.reward_seq = text_var(init_vars,'<b>Reward Sequence</b>','reward_seq')
        self.reward_vol = spin_var(init_vars,'<b>Reward Volume</b>', 1,500,25,' µL','reward_volume')
        self.background_rate = spin_var(init_vars,'<b>Background Reward Rate</b>',0,1,.05,'','background_reward_rate')
        # place widgets
        for i,var in enumerate([self.reward_seq,self.reward_vol,self.background_rate]):
            var.setBoard(board)
            var.add_to_grid(self.other_layout,i+1)
        self.other_box.setLayout(self.other_layout)

        grid_layout.addWidget(self.other_box,1,0,1,3)
        grid_layout.setColumnStretch(9,1)
        grid_layout.setRowStretch(10,1)

class spin_var():
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

class text_var():
    def __init__(self,init_var_dict,label,varname=''):
        center = QtCore.Qt.AlignCenter
        Vcenter = QtCore.Qt.AlignVCenter
        right = QtCore.Qt.AlignRight
        button_width = 35
        text_edit_width = 80
        self.label = QtGui.QLabel(label)
        self.label.setAlignment(right|Vcenter)
        # self.label.setToolTip(helpText)
        self.varname = varname

        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setAlignment(center)
        self.line_edit.setMaximumWidth(text_edit_width)
        self.line_edit.setText(eval(init_var_dict[varname]))

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
