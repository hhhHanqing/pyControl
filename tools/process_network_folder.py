import os
import sys
top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not top_dir in sys.path: sys.path.insert(0, top_dir)
from markov_data_cleaner import *
from config.paths import data_dir, tasks_dir, network_dir

experiment = 'Markov_Training'
experiment_folder = '{}/{}'.format(data_dir,experiment)
file_list = []
for filename in os.listdir(experiment_folder):
    if filename.endswith(".txt"):
        file_list.append('{}/{}'.format(experiment_folder,filename))


# try:
for file in file_list:
    print('Processing:'+ file)
    Log_cleaner(file).clean()
# except:
#     print("no files to process")