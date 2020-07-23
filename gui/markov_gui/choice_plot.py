# Choice Plot --------------------------------------------------------
import pyqtgraph as pg
import numpy as np
from config.gui_settings import markov_history_len,markov_plot_window

class Markov_Plot():
    def __init__(self, parent_plot, data_len=100):
        self.plot_widget = parent_plot
        reward_color = pg.mkColor(0,255,0) # green
        no_reward_color = pg.mkColor(0,0,0) # black
        reject_color = pg.mkColor(255,255,0) # yellow
        error_color = pg.mkColor(255,0,0) # red
        self.my_colors = (reward_color,no_reward_color,error_color,reject_color)
        self.my_symbols = ('o','+','s') # circle, plus, square
        self.is_active = False
        self.do_update = True
        self.data_len = data_len
        self.left_prob  = None
        self.right_prob = None
        self.next_block_start = 0
        self.last_arrow = None
        
    def set_state_machine(self,sm_info):
        if not self.is_active: return
        self.setup_plot_widget()
    
    def setup_plot_widget(self):
        self.plot_widget.hideAxis('right')
        self.plot_widget.showAxis('left')
        self.plot_widget.setRange(xRange=[-1,markov_plot_window+5], padding=0)
        self.plot_widget.setMouseEnabled(x=True,y=False)
        self.plot_widget.showGrid(x=True,alpha=0.75)
        self.plot_widget.setLimits(xMin=-1)

        self.plot_widget.clear()
        self.plot_widget.getAxis('bottom').setLabel('Trial')
        self.plot_widget.getAxis('right').setWidth(75)
        self.plot_widget.getAxis('left').setWidth(50)

        self.plot_widget.setTitle('Choices and Outcomes')
        self.plot_widget.getAxis('left').setTicks([[(6.5,'Left'),(6.25,'Right'),(5.0,'0'),(5.2,'.2'),(5.4,'.4'),(5.6,'.6'),(5.8,'.8'),(6,'1')]])
        self.plot_widget.setYRange(5,6.5, padding=0.1)

        self.plot = self.plot_widget.plot(pen=None, symbol='o', symbolSize=6, symbolPen=None)
        self.plot2 = self.plot_widget.plot(pen=pg.mkPen(color = (255,154,0,), width=2))
        self.plot3 = self.plot_widget.plot(pen=pg.mkPen(color  = (0,222,255,128), width=2))

    def run_start(self):
        if not self.is_active: return
        self.plot.clear()
        self.plot2.clear()
        self.plot3.clear()
        self.plot_widget.removeItem(self.last_arrow)
        self.trial_num = -1
        self.data = np.zeros([self.data_len,6])

    def process_data(self, new_data):
        if not self.is_active: return
        '''Store new data from board.'''
        outcome_msgs = [nd for nd in new_data if nd[0] == 'P' and nd[2].split(',')[0]=='rslt'] 
        new_block_msgs = [nd for nd in new_data if nd[0] == 'P' and nd[2].split(',')[0]=='NB']
        probability_var_update_msgs = [nd for nd in new_data if nd[0] == 'V' and nd[2].split(' ')[0].find('reward_probability')>-1] 
        newBlock_var_update_msgs = [nd for nd in new_data if nd[0] == 'V' and nd[2].split(' ')[0].find('trial_new_block')>-1] 
        if outcome_msgs:
            n_new = len(outcome_msgs)
            self.data = np.roll(self.data, -n_new, axis=0)
            for i, ne in enumerate(outcome_msgs):
                trial_num_string,left_prob_string,right_prob_string,choice,outcome,isLaserTrial= ne[-1].split(',')[1:]
                self.left_prob = float(left_prob_string)
                self.right_prob = float(right_prob_string)
                self.trial_num = int(trial_num_string)
                if choice == 'L': 
                    side = 6.5
                elif choice == 'R':
                    side = 6.25
                else:
                    side = 0
                if outcome == 'Y': # was rewarded
                    color = 0
                    symbol = 0
                elif outcome == 'N': # was not rewarded
                    color = 1
                    symbol = 0
                elif outcome == 'X': # error
                    color = 2
                    symbol = 2
                elif outcome == 'R': # rejected tone
                    color = 3
                    symbol = 1
            
                self.data[-n_new+i,0] = self.trial_num
                self.data[-n_new+i,1] = side
                self.data[-n_new+i,2] = color
                self.data[-n_new+i,3] = symbol
                self.data[-n_new+i,4] = self.left_prob + 5
                self.data[-n_new+i,5] = self.right_prob + 5
                if self.trial_num < 2:
                    self.data[:,4] = self.left_prob + 5
                    self.data[:,5] = self.right_prob + 5
 
            self.plot.setData(self.data[:,0],self.data[:,1],symbol=[self.my_symbols[int(ID)] for ID in self.data[:,3]],symbolSize=10,symbolPen=[pg.mkPen('y') if symbol == 1 else pg.mkPen('w') for symbol in self.data[:,3]],symbolBrush=[self.my_colors[int(ID)] for ID in self.data[:,2]])
            self.plot2.setData(self.data[:,0],self.data[:,4])
            self.plot3.setData(self.data[:,0],self.data[:,5])
            self.update_title()
            if self.do_update:
                self.plot_widget.setRange(xRange=[self.trial_num-markov_plot_window,self.trial_num+5], padding=0)
        if new_block_msgs:
            for nb_msg in new_block_msgs:
                content = nb_msg[2].split(',')
                self.next_block_start = int(content[2])
                if self.trial_num>0: # remove old marker and place marker where probability change actually occured. This takes into account instances where the new bout was scheduled for a trial that already occured.
                    self.plot_widget.removeItem(self.last_arrow)
                    self.update_block_marker(self.trial_num+1)
                self.update_block_marker(self.next_block_start)
                self.update_title()
        if probability_var_update_msgs:
            for prob_update in probability_var_update_msgs:
                content = prob_update[2].split(' ')
                if content[0].find('right') > -1:
                    self.right_prob = content[1]
                elif content[0].find('left') > -1:
                    self.left_prob = content[1]
                self.update_title()
        if newBlock_var_update_msgs:
            for block_start_update in newBlock_var_update_msgs:
                content = block_start_update[2].split(' ')
                self.next_block_start = int(content[1])
                self.update_block_marker(self.next_block_start)
                self.update_title()

    def toggle_update(self):
        self.do_update = not self.do_update
        if self.do_update:
            self.plot_widget.setRange(xRange=[self.trial_num-markov_plot_window,self.trial_num+5], padding=0)

    def update_title(self):
        self.plot_widget.setTitle('<font size="4"><span>Completed {} trials---Current Probabilities: </span><span style="color: #FF9A00;">Left={}</span><span style="color: #00DEFF;"> Right={}</span>---New Block in {} trials (@ trial <span style="color:#FF1FE6;">{}</span></font>)'.format(
            self.trial_num,self.left_prob,self.right_prob,self.next_block_start-self.trial_num,self.next_block_start))

    def update_block_marker(self,xpos):
        self.plot_widget.removeItem(self.last_arrow)
        self.last_arrow = pg.ArrowItem(pos=(xpos,4.85),angle=-90,brush='#FF1FE6',pen='#FF1FE6',headLen=18)
        self.plot_widget.addItem(self.last_arrow)
    