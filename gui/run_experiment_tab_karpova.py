import os
import time
import json
from datetime import datetime
from collections import OrderedDict

from pyqtgraph.Qt import QtGui, QtCore
from serial import SerialException

from config.gui_settings import  update_interval
from config.paths import dirs
from com.pycboard import Pycboard, PyboardError
from com.data_logger import Data_logger
from gui.plotting import Experiment_plot
from gui.dialogs import Variables_dialog, Summary_variables_dialog
from gui.markov_gui.markov_variable_dialog import *
from gui.sequence_gui.sequence_variable_dialog import *
from gui.utility import variable_constants
from gui.telegram_notifications import *

class Run_experiment_tab(QtGui.QWidget):
    '''The run experiment tab is responsible for setting up, running and stopping
    an experiment that has been defined using the configure experiments tab.'''

    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)

        self.GUI_main = self.parent()
        self.experiment_plot = Experiment_plot(self)

        self.name_label = QtGui.QLabel('Experiment name:')
        self.name_text  = QtGui.QLineEdit()
        self.name_text.setReadOnly(True)
        self.plots_button =  QtGui.QPushButton('Show plots')
        self.plots_button.clicked.connect(self.experiment_plot.show)
        self.logs_button = QtGui.QPushButton('Hide logs')
        self.logs_button.clicked.connect(self.show_hide_logs)    
        self.startstopclose_all_button = QtGui.QPushButton()
        self.startstopclose_all_button.clicked.connect(self.startstopclose_all)

        self.Hlayout = QtGui.QHBoxLayout()
        self.Hlayout.addWidget(self.name_label)
        self.Hlayout.addWidget(self.name_text)
        self.Hlayout.addWidget(self.logs_button)
        self.Hlayout.addWidget(self.plots_button)
        self.Hlayout.addWidget(self.startstopclose_all_button)

        self.scroll_area = QtGui.QScrollArea(parent=self)
        self.scroll_inner = QtGui.QFrame(self)
        self.boxes_layout = QtGui.QGridLayout(self.scroll_inner)
        self.scroll_area.setWidget(self.scroll_inner)
        self.scroll_area.setWidgetResizable(True)

        self.Vlayout = QtGui.QVBoxLayout(self)
        self.Vlayout.addLayout(self.Hlayout)
        self.Vlayout.addWidget(self.scroll_area)

        self.subjectboxes = []

        self.update_timer = QtCore.QTimer() # Timer to regularly call update() during run.        
        self.update_timer.timeout.connect(self.update)

    def setup_experiment(self, experiment):
        '''Called when an experiment is loaded.'''
        # Setup tabs.
        self.experiment = experiment
        self.GUI_main.tab_widget.setTabEnabled(0, False) # Disable run task tab.
        self.GUI_main.tab_widget.setTabEnabled(2, False)  # Disable setups tab.
        self.GUI_main.experiments_tab.setCurrentWidget(self)
        self.experiment_plot.setup_experiment(experiment)
        self.logs_visible = True
        self.logs_button.setText('Hide logs')
        self.startstopclose_all_button.setText('Start All')
        # Setup controls box.
        self.name_text.setText(experiment['name'])
        self.startstopclose_all_button.setEnabled(False)
        self.logs_button.setEnabled(False)
        self.plots_button.setEnabled(False)
        # Setup Telegram
        telegram_json = self.get_settings_from_json()
        if telegram_json['notifications_on']:
            self.telegrammer = Telegram(self.subjectboxes,telegram_json['bot_token'],telegram_json['chat_id'])
        else:
            self.telegrammer = None
        # Setup subjectboxes
        subject_dict = experiment['subjects']
        subjects = subject_dict.keys()

        setup_subject_pairs = {}
        for subject in subjects:
            setup_subject_pairs[subject_dict[subject]['Setup']] = subject

        for i,key in enumerate(sorted(setup_subject_pairs.keys())):
            self.subjectboxes.append(
                Subjectbox('{} ---- {}'.format(key,setup_subject_pairs[key]), i, self))
            position = int(key.split('.')[-1])-1
            if position<5:
                row = 0
            else:
                row = 1
            self.boxes_layout.addWidget(self.subjectboxes[-1],row,position-5*row)
        # Create data folder if needed.
        if not os.path.exists(self.experiment['data_dir']):
            os.mkdir(self.experiment['data_dir'])        
        # Load persistent variables if they exist.
        self.pv_path = os.path.join(self.experiment['data_dir'], 'persistent_variables.json')
        if os.path.exists(self.pv_path):
            with open(self.pv_path, 'r') as pv_file:
                persistent_variables =  json.loads(pv_file.read())
        else:
            persistent_variables = {}
        self.persistent_variables = persistent_variables
        # Setup boards.
        self.GUI_main.app.processEvents()
        self.boards = []
        
        for i,key in enumerate(sorted(setup_subject_pairs.keys())):
            print_func = self.subjectboxes[i].print_to_log
            serial_port = self.GUI_main.setups_tab.get_port(key)
            # Connect to boards.
            print_func('Connecting to board.. ')
            try:
                self.boards.append(Pycboard(serial_port, print_func=print_func))
            except SerialException:
                print_func('Connection failed.')
                self.abort_experiment()
                return
            if not self.boards[i].status['framework']:
                print_func('\nInstall pyControl framework on board before running experiment.')
                self.abort_experiment()
                return                
            self.boards[i].subject = setup_subject_pairs[key]
            self.boards[i].board =  key
        # Hardware test.
        if experiment['hardware_test'] != 'no hardware test':
            reply = QtGui.QMessageBox.question(self, 'Hardware test', 'Run hardware test?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                try:
                    for i, board in enumerate(self.boards):
                            board.setup_state_machine(experiment['hardware_test'])
                            board.print('\nStarting hardware test.')
                            board.start_framework(data_output=False)
                            time.sleep(0.01)
                            board.process_data()
                    QtGui.QMessageBox.question(self, 'Hardware test', 
                        'Press OK when finished with hardware test.', QtGui.QMessageBox.Ok)
                    for i, board in enumerate(self.boards):
                        board.stop_framework()
                        time.sleep(0.05)
                        board.process_data()
                except PyboardError as e:
                    board.print('\n' + str(e))
                    self.abort_experiment()
                    return
        # Setup state machines.
        for i, board in enumerate(self.boards):
            try:
                board.data_logger = Data_logger(print_func=board.print, data_consumers=
                    [self.experiment_plot.subject_plots[i], self.subjectboxes[i]])
                board.setup_state_machine(experiment['task'])
            except PyboardError:
                self.abort_experiment()
                return
            # Set variables.
            board.subject_variables = [v for v in experiment['variables'] 
                                       if v['subject'] in ('all', board.subject)]
            if board.subject_variables:
                board.print('\nSetting variables.\n')
                board.variables_set_pre_run = []
                try:
                    try:
                        subject_pv_dict = persistent_variables[board.subject]
                    except KeyError:
                        subject_pv_dict = {}
                    for v in board.subject_variables:
                        if v['persistent'] and v['name'] in subject_pv_dict.keys(): # Use stored value.
                            v_value =  subject_pv_dict[v['name']]
                            board.variables_set_pre_run.append(
                                (v['name'], str(v_value), '(persistent value)'))
                        else:
                            if v['value'] == '':
                                continue
                            v_value = eval(v['value'], variable_constants) # Use value from variables table.
                            board.variables_set_pre_run.append((v['name'], v['value'], ''))
                        board.set_variable(v['name'], v_value)
                    # Print set variables to log.    
                    if board.variables_set_pre_run:
                        name_len  = max([len(v[0]) for v in board.variables_set_pre_run])
                        value_len = max([len(v[1]) for v in board.variables_set_pre_run])
                        for v_name, v_value, pv_str in board.variables_set_pre_run:
                            self.subjectboxes[i].print_to_log(
                                v_name.ljust(name_len+4) + v_value.ljust(value_len+4) + pv_str)
                except PyboardError as e:
                    board.print('Setting variable failed. ' + str(e))
                    self.subjectboxes[i].error()
                    self.abort_experiment()
                    return
        # Copy task file to experiments data folder.
        self.boards[0].data_logger.copy_task_file(self.experiment['data_dir'], dirs['tasks'])
        # Configure GUI ready to run.
        for i, board in enumerate(self.boards):
            self.subjectboxes[i].assign_board(board)
        self.experiment_plot.set_state_machine(board.sm_info)
        for i, board in enumerate(self.boards):
            self.subjectboxes[i].start_stop_button.setEnabled(True)
        self.logs_button.setEnabled(True)
        self.plots_button.setEnabled(True)
        self.startstopclose_all_button.setEnabled(True)
        self.setups_finished = 0
        self.setups_running  = 0

    def startstopclose_all(self):
        if self.setups_running == 0:
            for i, board in enumerate(self.boards):
                self.subjectboxes[i].start_stop_rig()
        elif self.setups_finished < len(self.boards):
            for i, board in enumerate(self.boards):
                self.subjectboxes[i].start_stop_rig()
        else:
            self.close_experiment()

    def stop_experiment(self):
        self.update_timer.stop()
        self.GUI_main.refresh_timer.start(self.GUI_main.refresh_interval)
        for i, board in enumerate(self.boards):
            time.sleep(0.05)
            board.process_data()
        # Summary and persistent variables.
        summary_variables = [v for v in self.experiment['variables'] if v['summary']]
        sv_dict = OrderedDict()
        if os.path.exists(self.pv_path):
            with open(self.pv_path, 'r') as pv_file:
                persistent_variables = json.loads(pv_file.read())
        else:
            persistent_variables = {}
        for i, board in enumerate(self.boards):
            #  Store persistent variables.
            subject_pvs = [v for v in board.subject_variables if v['persistent']]
            if subject_pvs:
                board.print('\nStoring persistent variables.')
                persistent_variables[board.subject] = {
                    v['name']: board.get_variable(v['name']) for v in subject_pvs}
            # Read summary variables.
            if summary_variables:
                sv_dict[board.subject] = {v['name']: board.get_variable(v['name'])
                                          for v in summary_variables}
                for v_name, v_value in sv_dict[board.subject].items():
                    board.data_logger.data_file.write('\nV -1 {} {}'.format(v_name, v_value))
                    board.data_logger.data_file.flush()
        if persistent_variables:
            with open(self.pv_path, 'w') as pv_file:
                pv_file.write(json.dumps(persistent_variables, sort_keys=True, indent=4))
        if summary_variables:
            Summary_variables_dialog(self, sv_dict).show()

    def abort_experiment(self):
        '''Called if an error occurs while the experiment is being set up.'''
        self.update_timer.stop()
        self.GUI_main.refresh_timer.start(self.GUI_main.refresh_interval)
        for i, board in enumerate(self.boards):
            # Stop running boards.
            if board.framework_running:
                board.stop_framework()
                time.sleep(0.05)
                board.process_data()
                self.subjectboxes[i].task_stopped()
        msg = QtGui.QMessageBox()
        msg.setWindowTitle('Error')
        msg.setText('There was an error. Closing Experiment')
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.exec()
        self.close_experiment()

    def close_experiment(self):
        self.GUI_main.tab_widget.setTabEnabled(0, True) # Enable run task tab.
        self.GUI_main.tab_widget.setTabEnabled(2, True) # Enable setups tab.
        self.GUI_main.experiments_tab.setCurrentWidget(self.GUI_main.configure_experiment_tab)
        self.experiment_plot.close_experiment()
        # Close boards.
        for board in self.boards:
            if board.data_logger: board.data_logger.close_files()
            board.close()
        # Clear subjectboxes.
        while len(self.subjectboxes) > 0:
            subjectbox = self.subjectboxes.pop() 
            subjectbox.setParent(None)
            subjectbox.deleteLater()
        
        if self.telegrammer:
            self.telegrammer.updater.stop()

    def show_hide_logs(self):
        '''Show/hide the log textboxes in subjectboxes.'''
        if self.logs_visible:
            for subjectbox in self.subjectboxes:
                subjectbox.log_textbox.hide()
            self.logs_visible = False
            self.logs_button.setText('Show logs')
        else:
            for subjectbox in self.subjectboxes:
                subjectbox.log_textbox.show()
            self.logs_visible = True
            self.logs_button.setText('Hide logs')

    def update(self):
        '''Called regularly while experiment is running'''
        boards_running = False
        for i, board in enumerate(self.boards):
            if board.framework_running:
                boards_running = True
                try:
                    board.process_data()
                    if not board.framework_running:
                        self.subjectboxes[i].task_stopped(stopped_by_task=True)
                    self.subjectboxes[i].time_text.setText(str(datetime.now()-self.subjectboxes[i].start_time).split('.')[0])
                except PyboardError:
                    self.subjectboxes[i].error()
        self.experiment_plot.update()
        if self.setups_running > 0:
            if self.setups_running == len(self.boards) and self.setups_finished == 0:
                self.startstopclose_all_button.setEnabled(True)
                self.startstopclose_all_button.setText('Stop All')
            else:
                self.startstopclose_all_button.setEnabled(False)
                if self.setups_finished == 0:
                    self.startstopclose_all_button.setText('Stop All')
                else:
                    self.startstopclose_all_button.setText('Close Experiment')

        if not boards_running and self.setups_finished == len(self.boards):
            self.startstopclose_all_button.setEnabled(True)
            self.stop_experiment()

    def get_settings_from_json(self):
        json_path = os.path.join(dirs['config'],'telegram.json')
        if os.path.exists(json_path):
            with open(json_path,'r') as f:
                telegram_settings = json.loads(f.read())
        else:
            telegram_settings = {} # missing json file
        return telegram_settings
# -----------------------------------------------------------------------------

class Subjectbox(QtGui.QGroupBox):
    '''Groupbox for displaying data from a single subject.'''

    def __init__(self, name, boxNum, parent=None):

        super(QtGui.QGroupBox, self).__init__("", parent=parent)
        self.board = None # Overwritten with board once instantiated.
        self.GUI_main = self.parent().GUI_main
        self.run_exp_tab = self.parent()
        self.state = 'pre_run'
        self.boxNum = boxNum
        self.parent_telegram = self.parent().telegrammer
        self.tabs = QtGui.QTabWidget()
        self.logTab = QtGui.QWidget()
        self.logTab.layout = QtGui.QVBoxLayout()
        self.varTab = QtGui.QWidget()
        self.varTab.layout = QtGui.QVBoxLayout()
        self.tabs.addTab(self.logTab,"Log")
        self.tabs.addTab(self.varTab,"Variables")

        self.boxTitle = QtGui.QLabel(name)
        self.boxTitle.setStyleSheet("font:15pt;color:blue;")

        self.start_stop_button = QtGui.QPushButton('Start')
        self.start_stop_button.setEnabled(False)
        self.time_label = QtGui.QLabel('Time:')
        self.time_text = QtGui.QLineEdit()
        self.time_text.setReadOnly(True)
        self.time_text.setFixedWidth(60)
        self.log_textbox = QtGui.QTextEdit()
        self.log_textbox.setMinimumWidth(415)
        self.log_textbox.setFont(QtGui.QFont('Courier', 9))
        self.log_textbox.setReadOnly(True)

        self.subjectGridLayout = QtGui.QGridLayout(self)
        self.subjectHeaderLayout = QtGui.QGridLayout()
        self.subjectHeaderLayout.addWidget(self.boxTitle,0,1)
        self.subjectHeaderLayout.addWidget(self.time_label,0,2,QtCore.Qt.AlignRight)
        self.subjectHeaderLayout.addWidget(self.time_text,0,3,QtCore.Qt.AlignLeft)
        self.subjectHeaderLayout.addWidget(self.start_stop_button,0,4)
        self.subjectHeaderLayout.setColumnStretch(0,1)
        self.subjectHeaderLayout.setColumnStretch(5,1)
        self.subjectGridLayout.addLayout(self.subjectHeaderLayout,0,0,1,2)
        self.subjectGridLayout.addWidget(self.tabs,1,0,1,2)
        self.logTab.layout.addWidget(self.log_textbox)
        self.logTab.setLayout(self.logTab.layout)
        
    def print_to_log(self, print_string, end='\n'):
        self.log_textbox.moveCursor(QtGui.QTextCursor.End)
        self.log_textbox.insertPlainText(print_string+end)
        self.log_textbox.moveCursor(QtGui.QTextCursor.End)
        self.GUI_main.app.processEvents()

    def assign_board(self, board):
        self.board = board
        if self.board.sm_info['name'] == 'markov':
            self.variables_dialog = Markov_Variables_dialog(self, self.board)
        elif self.board.sm_info['name'] == 'sequence':
            self.variables_dialog = Sequence_Variables_dialog(self, self.board)
        else:
            self.variables_dialog = Variables_dialog(self, self.board)
        self.board.data_logger.data_consumers.append(self.variables_dialog)
        # self.variables_box= QtGui.QGroupBox('Variables')
        self.varTab.setLayout(self.variables_dialog.layout)
        # self.subjectGridLayout.addWidget(self.variables_box,1,1)
        self.start_stop_button.clicked.connect(self.start_stop_rig)

    def start_stop_rig(self):
        if self.state == 'pre_run': 
            self.begin_rig()
        elif self.state == 'running':
            self.task_stopped()

    def begin_rig(self):
        self.state = 'running'
        self.run_exp_tab.experiment_plot.start_experiment(self.boxNum)
        self.start_time = datetime.now()
        ex = self.run_exp_tab.experiment
        board = self.board
        board.print('\nStarting experiment.\n')
        board.data_logger.open_data_file(ex['data_dir'], ex['name'], board.board, board.subject, datetime.now())
        if board.subject_variables: # Write variables set pre run to data file.
            for v_name, v_value, pv in self.board.variables_set_pre_run:
                board.data_logger.data_file.write('V 0 {} {}\n'.format(v_name, v_value))
        board.data_logger.data_file.write('\n')
        board.start_framework()

        self.start_stop_button.setText('Stop')
        self.run_exp_tab.setups_running += 1

        self.run_exp_tab.GUI_main.refresh_timer.stop()
        self.run_exp_tab.update_timer.start(update_interval)
        self.boxTitle.setStyleSheet("font:15pt;color:green;")

        if self.parent_telegram:
            self.parent_telegram.add_button(self.boxNum,self.boxTitle)

    def task_stopped(self,stopped_by_task=False):
        '''Called when task stops running.'''
        # Stop running board
        if self.board.framework_running:
            self.board.stop_framework()
        self.run_exp_tab.experiment_plot.active_plots.remove(self.boxNum)
        self.run_exp_tab.setups_finished += 1
        self.start_stop_button.setVisible(False)
        for widget in (self.boxTitle, self.time_label, self.time_text, self.varTab):
            widget.setEnabled(False)
        self.boxTitle.setStyleSheet("font:15pt;color:grey;")
        
        if self.parent_telegram:
            if stopped_by_task:
                self.parent_telegram.notify(
                    "<u><b>{}</b></u>\n\nTask automatically stopped\nSession duration= {}".format(self.boxTitle.text(),self.time_text.text())
                )
            self.parent_telegram.remove_button(self.boxNum)

    def process_data(self, new_data):
        pass
