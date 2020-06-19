import tools.data_import as di
import pandas as pd
import os
from config.paths import network_dir
cleaner_version = 2019121700 ## YearMonthDayRevision YYYYMMDDrr  can have up to 100 revisions/day
class Log_cleaner():
    def __init__(self,file_path):
        self.txt_file = file_path
        self.folder_path = network_dir 

        session = di.Session(self.txt_file)
        self.session = session
        self.session_name = session.file_name[:-4]

        self.task_version = session.print_lines[0].split(",")[-1]
        for i,line in enumerate(session.print_lines):
            if line.find('Variables_End,~~~~')>-1:
                break

        self.data = pd.DataFrame(session.print_lines[i+1:])

    def clean(self):
        self.create_folders()
        self.create_dataframes()
        self.expand_results()
        self.create_html_table()
        self.create_bokeh_graph()
        self.save_json()
        self.move_raw_txtfile()

    def create_folders(self):
        rat = self.session.subject_ID
        try:
            os.mkdir('{}/{}'.format(self.folder_path,rat)) #make directory if it doesn't already exist
            print('made new directory')
        except:
            pass

        folder_names = ['raw','outcome_data','tables','bokeh_plots']

        for fn in folder_names:
            try:
                newFolder = '{}/{}/{}'.format(self.folder_path,rat,fn)
                os.mkdir(newFolder)
                print('Created {}/{}'.format(rat,fn))
            except:
                pass # folder already exists

    def create_dataframes(self):
        space_split = self.data[0].str.split(expand=True)
        space_split.rename(columns={0:"Timestamp"},inplace=True)
        timestamps = space_split['Timestamp']
        otherData = space_split[1]
        comma_split = otherData.str.split(",",expand=True)
        comma_split.rename(columns={0:'Msg',1:'Trial'},inplace=True)
        all_data = pd.concat([timestamps, comma_split], axis=1)

        new_bout_mask = all_data['Msg']=='NB'
        self.new_bout_data = all_data[new_bout_mask][['Timestamp','Msg','Trial']].copy()
        self.new_bout_data.reset_index(drop=True,inplace=True)

        rslt_mask = all_data['Msg']=='rslt'
        self.rslt_data = all_data[rslt_mask].copy()
        self.rslt_data.rename(columns={2:'Left_prob',3:'Right_prob',4:'Choice',5:'Outcome',6:'LaserTrial'},inplace=True)
        self.rslt_data.reset_index(drop=True,inplace=True)
        
    def expand_results(self):
        import numpy as np
        right_mask = self.rslt_data['Choice']=='R'
        left_mask = self.rslt_data['Choice']=='L'
        rewarded_mask = self.rslt_data['Outcome']=='Y'
        unrewarded_mask = self.rslt_data['Outcome']=='N'
        reject_mask = self.rslt_data['Outcome']=='R'
        error_mask = self.rslt_data['Outcome']=='X'
        laser_mask = self.rslt_data['LaserTrial']=='True'
        self.rslt_data.drop(columns=['Msg','LaserTrial'],inplace=True)

        outcome_truth_table = pd.DataFrame(np.zeros((len(self.rslt_data), 8),dtype=int),
                    columns=['Left_rewarded','Left_unrewarded','Left_rejected','Left_error',
                            'Right_rewarded','Right_unrewarded','Right_rejected','Right_error'])

        outcome_truth_table.loc[left_mask&rewarded_mask,'Left_rewarded']=1
        outcome_truth_table.loc[left_mask&unrewarded_mask,'Left_unrewarded']=1
        outcome_truth_table.loc[left_mask&reject_mask,'Left_rejected']=1
        outcome_truth_table.loc[left_mask&error_mask,'Left_error']=1

        outcome_truth_table.loc[right_mask&rewarded_mask,'Right_rewarded']=1
        outcome_truth_table.loc[right_mask&unrewarded_mask,'Right_unrewarded']=1
        outcome_truth_table.loc[right_mask&reject_mask,'Right_rejected']=1
        outcome_truth_table.loc[right_mask&error_mask,'Right_error']=1

        self.rslt_data.loc[laser_mask,'Laser_trial']= 1
        self.rslt_data.loc[~laser_mask,'Laser_trial']= 0
        self.rslt_data['Laser_trial'] = self.rslt_data['Laser_trial'].astype(np.int64)

        self.combined = pd.concat([self.rslt_data, outcome_truth_table], axis=1)
    
    def create_html_table(self):

        pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

        css_string = '''
        .mystyle {
            font-size: 11pt;
            font-family: Arial;
            border-collapse: collapse;
            border: 1px solid silver;
        }

        .mystyle td,
        th {
            padding: 5px;
        }

        .mystyle tr:nth-child(even) {
            background: #E0E0E0;
        }

        .mystyle tr:hover {
            background: silver;
            cursor: pointer;
        }
        '''

        html_string = '''
        <html>
        <head><title>Raw Dataframe</title>
        <style>
        {css}
        </style>
        </head>  
        
        <body>
            {table}
        </body>
        </html>.
        '''

        # OUTPUT AN HTML FILE
        saveName = '{}/{}/tables/{}_table.html'.format(self.folder_path,self.session.subject_ID,self.session_name)
        with open(saveName, 'w') as f:
            f.write(html_string.format(css=css_string,table=self.combined.to_html(classes='mystyle')))


    def create_bokeh_graph(self):
        def getSeries(colName,rename):
            series = self.combined.loc[self.combined[colName]==1,colName]
            series[:] = rename
            return series

        L_Rwd = getSeries('Left_rewarded','Left')
        L_NRwd = getSeries('Left_unrewarded','Left')
        L_Rej = getSeries('Left_rejected','Left')
        L_Err = getSeries('Left_error','Left')

        R_Rwd = getSeries('Right_rewarded','Right')
        R_NRwd = getSeries('Right_unrewarded','Right')
        R_Rej = getSeries('Right_rejected','Right')
        R_Err = getSeries('Right_error','Right')

        import bokeh.plotting as bk
        from bokeh.models import Legend,RangeTool
        from bokeh.layouts import column

        background_color = 'white'
        correct_color = "green"
        error_color = "red"
        reject_color = "blue"

        figWidth = 1250

        p = bk.figure(
            width = figWidth,
            height=200,
            tools="xwheel_zoom,xpan,reset,save",
            active_scroll = "xwheel_zoom",
            title='Rat {} ---- {} trials ---- {}'.format(self.session.subject_ID,len(self.combined),self.session.datetime_string),
            y_range = ['Right','Left'],
            x_range = [0,80],
            background_fill_color = background_color,
            x_axis_location="below",
            toolbar_location="above",
        )

        p.ygrid.visible = False
        p.xgrid.visible = True
        markerSize = 10
        left_full = p.circle(L_Rwd.index,L_Rwd,size=markerSize,line_color=correct_color,fill_color=correct_color)
        left_empty = p.circle(L_NRwd.index,L_NRwd,size=markerSize,line_color=correct_color,fill_color=background_color)
        left_cross = p.cross(L_Rej.index,L_Rej,size=markerSize,line_color=reject_color,line_width=2)
        left_square = p.square(L_Err.index,L_Err,size=markerSize,line_color=error_color,fill_color=error_color)

        right_full = p.circle(R_Rwd.index,R_Rwd,size=markerSize,line_color=correct_color,fill_color=correct_color)
        right_empty = p.circle(R_NRwd.index,R_NRwd,size=markerSize,line_color=correct_color,fill_color=background_color)
        right_cross = p.cross(R_Rej.index,R_Rej,size=markerSize,line_color=reject_color,line_width=2)
        right_square = p.square(R_Err.index,R_Err,size=markerSize,line_color=error_color,fill_color=error_color)

        outcome_legend = Legend(items=[
            ("Reward",   [left_full]),
            ("No Reward", [left_empty]),
            ("Reject",   [left_cross]),
            ("Error", [left_square]),    
        ], location="center")

        p.add_layout(outcome_legend, 'left')
        p.legend.title="Choice Outcome"
        p.legend.title_text_font_style = "bold"
        ####################################################################################################
        probabilities = bk.figure(plot_height=150,
                        plot_width=figWidth,
                        y_range=[0,1],
                        x_range=p.x_range,
                        tools="",
                        toolbar_location=None,
                        background_fill_color="white",
                        y_axis_label='Reward Probability',
                        y_minor_ticks=None,
                        x_axis_location=None
        )
        right_line = probabilities.line(self.combined['Right_prob'].index,self.combined['Right_prob'],line_width=5,alpha=.5)
        left_line = probabilities.line(self.combined['Left_prob'].index,self.combined['Left_prob'],color='orange',line_width=5,alpha=.5)

        legend = Legend(items=[
            ("Left",   [left_line]),
            ("Right", [right_line]),
        ], location="center")

        probabilities.add_layout(legend, 'left')
        probabilities.legend.title="Side"
        probabilities.legend.title_text_font_style = "bold"
        ####################################################################################################
        select = bk.figure(plot_height=100,
                        plot_width=figWidth,
                        y_range=[0,1],
                        tools="",
                        toolbar_location=None,
                        background_fill_color="white",
                        x_axis_label='Trial',
                        y_axis_location=None
        )

        range_tool = RangeTool(x_range=p.x_range)
        range_tool.overlay.fill_color = "yellow"
        range_tool.overlay.fill_alpha = 0.3

        right_line = select.line(self.combined['Right_prob'].index,self.combined['Right_prob'],line_width=2,alpha=.5)
        left_line = select.line(self.combined['Left_prob'].index,self.combined['Left_prob'],color='orange',line_width=2,alpha=.5)

        select.add_tools(range_tool)
        select.toolbar.active_multi = range_tool

        bk.output_file('{}/{}/bokeh_plots/{}_plots.html'.format(self.folder_path,self.session.subject_ID,self.session_name))
        bk.save(column(p,probabilities,select))

    def save_json(self):
        import json

        json_dictionary = {}

        #convert dataframe to dictionary
        for col in self.combined.columns:
            json_dictionary[col] = self.combined[col].values.tolist()

        # add session information
        session_dict = {
            'task':self.session.task_name,
            'task_version':self.task_version,
            'subject':self.session.subject_ID,
            'datetime':self.session.datetime_string,
            'cleaning_script_version':str(cleaner_version)
        }

        json_dictionary['Session_info'] = session_dict   
            
        saveName = '{}/{}/outcome_data/{}.json'.format(self.folder_path,self.session.subject_ID,self.session_name)
        with open(saveName,'w') as f:
            json.dump(json_dictionary,f)

        print('done')

    def move_raw_txtfile(self):
        import shutil
        text_in_raw_folder = '{}/{}/raw/{}.txt'.format(self.folder_path,self.session.subject_ID,self.session_name)
        shutil.move(self.txt_file,text_in_raw_folder)