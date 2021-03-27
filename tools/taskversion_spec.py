
# this script should include task version specific functions for all different pycontrol tasks codes.

import pandas as pd

def get_rslt_data(rslt_data, task, task_version):
    tv = float(task_version)
    
    def rslt_columns(tv):
        '''
        *** only for reference ***
            for tv <= 2021031400, printed rslt should be read like this:
            {1:'Trial',2:'Seq_raw',3:'Choice_ltr',4:'Outcome',5:'Abandoned',6:'Reward_vol',7:'Center_hold',8:'Side_delay',9:'Faulty_chance',10:'Max_consecutive_faulty',11:'Faulty_time_limit'}
        '''
        # the columns are unified to the latest version
        return ['Timestamp', 'Msg', 'Trial', 'Seq_raw', 'Choice_ltr', 'Outcome', 'Reward_vol', 'Center_hold', 'Side_delay', 'Faulty_chance', 'Max_consecutive_faulty', 'Faulty_time_limit']
    
    def clean_abandonment(rslt_data, tv):
        if tv <= 2021031400:        # 4:'Outcome',5:'Abandoned'
            abandoned_mask = rslt_data.loc[:, 5] == 1
            rslt_data.loc[abandoned_mask, 4] = 'A'
            rslt_data.drop(columns=[5],inplace=True)
        else:       # for tv > 2021031400, this is already done.
            pass
        return rslt_data
    
    if task == 'markov':
        rslt_data.rename(columns={1:'Trial',2:'Left_prob',3:'Right_prob',4:'Choice_ltr',5:'Outcome',6:'LaserTrial'},inplace=True)
    elif task == 'sequence':
        if len(rslt_data) == 0:
            rslt_data = pd.DataFrame(columns=rslt_columns(tv))
        else:
            rslt_data = clean_abandonment(rslt_data, tv)
            raw_columns = list(rslt_data.columns)
            rslt_data.rename(columns=dict(zip(raw_columns, rslt_columns(tv))), inplace=True)
    rslt_data.reset_index(drop=True,inplace=True)
    return rslt_data
