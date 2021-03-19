import tools.data_import as di
import pandas as pd
import numpy as np
import os
from config.paths import dirs

cleaner_version = 2021031900 ## YearMonthDayRevision YYYYMMDDrr  can have up to 100 revisions/day

class Log_cleaner():
    def __init__(self,file_path):
        self.txt_file = file_path

        session = di.Session(self.txt_file)
        self.session = session
        # Hanqing: I added the prefix here so that I don't need to update the task version
        self.session_name = "pyLog_" + session.file_name[:-4]

        self.task_version = session.print_lines[0].split(",")[-1]
        for i,line in enumerate(session.print_lines):
            if line.find('Variables_End,~~~~')>-1:
                break

        self.print_data = pd.DataFrame(session.print_lines[i+1:])

        self.data_folder_path = dirs['network_dir']

    def clean(self):
        self.create_folders()
        self.create_dataframes(self.session.task_name)
        self.expand_results(self.session.task_name)
        self.save_json()
        self.move_raw_txtfile()

    def create_folders(self):
        rat = str(self.session.subject_ID)
        try:
            new_dir = os.path.join(self.data_folder_path,rat)
            os.mkdir(new_dir)
            print(F'Animal directory not found, therefore creating new directory {new_dir}')
        except:
            pass

    def create_dataframes(self,task):
        space_split = self.print_data[0].str.split(expand=True)
        space_split.rename(columns={0:"Timestamp"},inplace=True)
        timestamps = space_split['Timestamp']
        otherData = space_split[1]
        comma_split = otherData.str.split(",",expand=True)
        comma_split.rename(columns={0:'Msg'},inplace=True)
        print_DF = pd.concat([timestamps, comma_split], axis=1)
        
        self.print_DF = print_DF

        new_bout_mask = print_DF['Msg']=='NB'
        if task == 'sequence':
            self.new_bout_data = print_DF.iloc[:,0:5].copy()
            self.new_bout_data = self.new_bout_data[new_bout_mask]
            self.new_bout_data.rename(columns={1:'Reward_seq',2:'Bout_length',3:'Next_seq'},inplace=True)
            self.new_bout_data.reset_index(drop=True,inplace=True)

        rslt_mask = print_DF['Msg']=='rslt'
        self.rslt_data = print_DF[rslt_mask].copy()
        if task == 'markov':
            self.rslt_data.rename(columns={1:'Trial',2:'Left_prob',3:'Right_prob',4:'Choice_ltr',5:'Outcome',6:'LaserTrial'},inplace=True)
        elif task == 'sequence':
            self.rslt_data.rename(columns={1:'Trial',2:'Seq_raw',3:'Choice_ltr',4:'Outcome',5:'Abandoned',6:'Reward_vol',7:'Center_hold',8:'Side_delay',9:'Faulty_chance',10:'Max_consecutive_faulty',11:'Faulty_time_limit'},inplace=True)
        self.rslt_data.reset_index(drop=True,inplace=True)

    def expand_results(self,task):
        right_mask = self.rslt_data['Choice_ltr']=='R'
        left_mask = self.rslt_data['Choice_ltr']=='L'

        if task == 'markov':
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

        elif task == 'sequence':
            self.rslt_data.drop(columns=['Timestamp','Msg'],inplace=True)

            abandoned_mask = self.rslt_data['Abandoned']=='1'
            self.rslt_data['Abandoned'] = self.rslt_data['Abandoned'].astype(np.int64)

            nothing_mask     = self.rslt_data['Outcome']=='N'
            background_mask  = self.rslt_data['Outcome']=='B' # rewarded
            predicted_mask   = self.rslt_data['Outcome']=='P'
            withheld_mask    = self.rslt_data['Outcome']=='W'
            correct_mask     = self.rslt_data['Outcome']=='C' # rewarded
            faulty_mask      = self.rslt_data['Outcome']=='F' 

            correct_sequence_mask = withheld_mask|correct_mask
            reward_dispensed_mask = (correct_mask|background_mask)&~abandoned_mask

            outcome_truth_table = pd.DataFrame(np.zeros((len(self.rslt_data), 6),dtype=int),
                        columns=['Seq_int','Seq_length','Left_choice','Seq_completed','Reward_dispensed','Faulty_choice'])

            outcome_truth_table.loc[correct_sequence_mask,'Seq_completed']=1
            outcome_truth_table.loc[reward_dispensed_mask,'Reward_dispensed']=1
            outcome_truth_table.loc[left_mask,'Left_choice']=1
            outcome_truth_table.loc[faulty_mask,'Faulty_choice']=1

            def seq_to_int(sequence):
                seq = sequence.replace('L','1').replace('R','0')
                return int(seq,2)
            
            outcome_truth_table['Seq_int'] = self.rslt_data['Seq_raw'].apply(seq_to_int)
            outcome_truth_table['Seq_length'] = self.rslt_data['Seq_raw'].apply(len)

            self.combined = pd.concat([self.rslt_data, outcome_truth_table], axis=1)
            self.combined = self.combined[['Trial','Reward_vol','Center_hold','Side_delay','Faulty_chance','Max_consecutive_faulty','Faulty_time_limit','Seq_raw','Seq_int','Seq_length','Choice_ltr','Outcome','Left_choice','Seq_completed','Abandoned','Reward_dispensed','Faulty_choice']] # reorder columns
    
    def save_json(self):
        import json

        # https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable/50916741
        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                else:
                    return super(NpEncoder, self).default(obj)
                
        json_dictionary = {}

        session_dict = {
                'task':self.session.task_name,
                'task_version':self.task_version,
                'task_hash':self.session.task_hash,
                'setup':self.session.setup_ID,
                'subject':self.session.subject_ID,
                'datetime':self.session.datetime_string,
                'cleaning_script_version':str(cleaner_version)
            }
        json_dictionary['Session_info'] = session_dict   

        outcome_dictionary = {}
        for col in self.combined.columns:
            outcome_dictionary[col] = self.combined[col].values.tolist()
        json_dictionary['Outcomes'] = outcome_dictionary   

        new_bout_dictionary = {}
        for col in self.new_bout_data.columns:
            new_bout_dictionary[col] = self.new_bout_data[col].values.tolist()
        json_dictionary['Bouts'] = new_bout_dictionary   
        event_dictionary = {}
        for event_type in self.session.times:
            event_dictionary[event_type] = list(self.session.times[event_type])
        json_dictionary['Events'] = event_dictionary

        saveName = os.path.join(self.data_folder_path,str(self.session.subject_ID),self.session_name+".json")
        with open(saveName,'w') as f:
            json.dump(json_dictionary,f,cls=NpEncoder)

        print(F'json saved at {saveName}\n')

    def move_raw_txtfile(self):
        import shutil
        text_in_raw_folder = os.path.join(self.data_folder_path,str(self.session.subject_ID),self.session_name+".txt")
        shutil.move(self.txt_file,text_in_raw_folder)
