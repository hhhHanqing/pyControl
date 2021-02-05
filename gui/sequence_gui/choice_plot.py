# Choice Plot --------------------------------------------------------
import pyqtgraph as pg
import numpy as np
from config.gui_settings import choice_history_len,choice_plot_window,choice_plot_look_ahead
from PyQt5.QtCore import Qt

class Sequence_Plot():
    def __init__(self, parent_plot, data_len=100):
        self.plot_widget = parent_plot
        reward_color = pg.mkColor(0,255,0) # green
        abandoned_reward_color = pg.mkColor(0,255,0,128) # faded green
        no_reward_color = pg.mkColor(0,0,0) # black
        background_reward_color = pg.mkColor(255,255,0) # yellow
        faulty_color = pg.mkColor(255,0,0) # red
        self.my_colors = (reward_color, no_reward_color,background_reward_color,faulty_color,abandoned_reward_color)
        self.my_symbols = ('o','+','s','t') # circle, plus, square,triangle
        self.is_active = False
        self.do_update = True
        self.data_len = data_len
        self.new_bout_line = pg.InfiniteLine(angle=90,pen='#FF1FE6')
        self.bout_text = pg.TextItem("testing", anchor=(0, .5))

    def set_state_machine(self,sm_info):
        if not self.is_active: return
        self.setup_plot_widget()
    
    def setup_plot_widget(self):
        self.last_choice = ''
        self.reward_seq = ''
        self.label_new_bout = False
        self.next_seq = ''
        self.bout_start_trial = 0
        self.next_block_start = 0

        self.rewarded_trials = 0
        
        self.plot_widget.hideAxis('right')
        self.plot_widget.showAxis('left')
        self.plot_widget.setRange(xRange=[-1,choice_plot_window+choice_plot_look_ahead], padding=0)
        self.plot_widget.setMouseEnabled(x=True,y=False)
        self.plot_widget.showGrid(x=True,alpha=0.75)
        self.plot_widget.setLimits(xMin=-1)

        self.plot_widget.clear()
        self.plot_widget.getAxis('bottom').setLabel('Rat Perceived Trial')
        self.plot_widget.getAxis('right').setWidth(75)
        self.plot_widget.getAxis('left').setWidth(50)

        self.plot_widget.setYRange(4,9, padding=0.1)
        self.plot = self.plot_widget.plot(pen=None, symbol='o', symbolSize=6, symbolPen=None)

        self.plot_widget.setTitle('Choices and Outcomes')
        self.plot_widget.getAxis('left').setTicks([[(7,'Left'),(6,'Right')]])

    def run_start(self):
        if not self.is_active: return
        self.plot.clear()
        self.trial_num = 0
        self.data = np.zeros([self.data_len,6])
        self.plot_widget.addItem(self.bout_text)
        self.plot_widget.addItem(self.new_bout_line)

    def process_data(self, new_data):
        if not self.is_active: return
        '''Store new data from board.'''
        outcome_msgs = [nd for nd in new_data if nd[0] == 'P' and nd[2].split(',')[0]=='rslt'] 
        new_block_msgs = [nd for nd in new_data if nd[0] == 'P' and nd[2].split(',')[0]=='NB']
        newBlock_var_update_msgs = [nd for nd in new_data if nd[0] == 'V' and nd[2].split(' ')[0].find('trials_until_change')>-1] 
        if outcome_msgs:
            n_new = len(outcome_msgs)
            self.data = np.roll(self.data, -n_new, axis=0)
            for i, ne in enumerate(outcome_msgs):
                trial_num_string,self.reward_seq,choice,outcome,abandoned,reward_vol,center_hold,side_delay,faulty_chance,faulty_maxcount,faulty_time_limit = ne[-1].split(',')[1:]
                self.trial_num = int(trial_num_string)
                if choice == 'L':
                    if self.last_choice == 'L':
                        self.consecutive_adjustment += .2
                    else:
                        self.consecutive_adjustment = 0
                    side = 7 + self.consecutive_adjustment
                elif choice == 'R':
                    if self.last_choice == 'R':
                        self.consecutive_adjustment += .2
                    else:
                        self.consecutive_adjustment = 0
                    side = 6 - self.consecutive_adjustment
                else:
                    side = 0
                self.last_choice = choice

                if outcome == 'C' or outcome == 'W': # was rewarded
                    self.rewarded_trials += 1
                    color = 0
                elif outcome == 'N' or outcome == 'P': # was not rewarded
                    color = 1
                elif outcome == 'B': # background reward
                    color = 2

                if abandoned=='1':
                    symbol = 3
                    if color == 0:
                        color = 4 
                else:
                    symbol = 2

                if outcome == 'F': # this "rat percieved trial" occured after a faulty nosepoke
                    color = 3
                    symbol = 0
                    self.next_block_start +=1
                    self.new_bout_line.setValue(self.next_block_start)
                    self.bout_text.setPos(self.next_block_start, 6.5)
                    self.bout_text.setText(str(self.next_block_start - self.trial_num))

                    
                self.data[-n_new+i,0] = self.trial_num
                self.data[-n_new+i,1] = side
                self.data[-n_new+i,2] = color
                self.data[-n_new+i,3] = symbol
 
            self.plot.setData(self.data[:,0],self.data[:,1],
            symbol=[self.my_symbols[int(ID)] for ID in self.data[:,3]],
            symbolSize=10,
            symbolPen=pg.mkPen(color=(150,150,150),width=1),
            # symbolPen=[pg.mkPen(color=(150,150,150),width=1) if symbol == 2 else pg.mkPen('w',width=1) for symbol in self.data[:,3]],
            symbolBrush=[self.my_colors[int(ID)] for ID in self.data[:,2]])
            self.update_title()
            if self.do_update:
                self.plot_widget.setRange(xRange=[self.trial_num-choice_plot_window,self.trial_num+choice_plot_look_ahead], padding=0)
        if new_block_msgs:
            for nb_msg in new_block_msgs:
                # label old bout change
                transition_line = pg.InfiniteLine(angle=90,pen=pg.mkPen(color='#FF1FE6',style=Qt.DashLine))
                transition_line.setValue(self.next_block_start + .5)
                self.plot_widget.addItem(transition_line)
                self.label_new_bout = True


                content = nb_msg[2].split(',')
                # add new bout change
                self.next_block_start = int(content[2]) + self.trial_num
                self.next_seq = content[3]
                self.new_bout_line.setValue(self.next_block_start + .5)
                self.bout_text.setPos(self.next_block_start + .5, 6.5)

            # update title
                self.reward_seq = content[1]
                self.update_title()
                
        if newBlock_var_update_msgs:
            for block_start_update in newBlock_var_update_msgs:
                content = block_start_update[2].split(' ')
                self.next_block_start = int(content[1]) + self.trial_num
                self.new_bout_line.setValue(self.next_block_start)
                self.bout_text.setPos(self.next_block_start, 6.5)
                self.bout_text.setText(str(self.next_block_start - self.trial_num))
        if newBlock_var_update_msgs:
                self.update_title()

    def toggle_update(self):
        self.do_update = not self.do_update
        if self.do_update:
            self.plot_widget.setRange(xRange=[self.trial_num-choice_plot_window,self.trial_num+choice_plot_look_ahead], padding=0)

    def update_title(self):
        if self.trial_num:
            reward_percentage = round(self.rewarded_trials/self.trial_num*100,2)
        else:
            reward_percentage = 0
        self.plot_widget.setTitle('<font size="4"><span style="color:white;">{}</span> Rat Perceived Choices made --- <span style="color:white;">{}%</span> Perceived Trials Rewarded --- Current Reward Sequence:{}</font>'.format(
            self.trial_num,reward_percentage,self.create_color_string(self.reward_seq)))
        self.bout_text.setHtml('{} in {} real trials'.format(self.create_color_string(self.next_seq),str(self.next_block_start - self.trial_num)))
        if self.label_new_bout:
            self.label_new_bout = False
            current_seq_text = pg.TextItem(html = self.create_color_string(self.reward_seq), anchor=(0, .5))
            current_seq_text.setPos(self.trial_num +.5, 6.5)
            self.plot_widget.addItem(current_seq_text)

            if self.trial_num != 0: #don't do this for start of session
                previous_bout_length_text = pg.TextItem(str(self.trial_num - self.bout_start_trial), anchor=(1, .5))
                previous_bout_length_text.setPos(self.trial_num +.5, 6.5)
                self.plot_widget.addItem(previous_bout_length_text)
                self.bout_start_trial = self.trial_num

    def update_block_marker(self,xpos):
        pass

    def create_color_string(self,sequence_string):
        blue,orange = '#00DEFF','#FF9A00'
        output_string = ''
        for letter in sequence_string:
            if letter == 'L':
                color = orange
            else:
                color = blue
            output_string += '<span style="color: {};">{}</span>'.format(color,letter)
        return output_string