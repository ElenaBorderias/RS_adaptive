# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 15:14:07 2021

@author: elena_borderias
"""

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
from os.path import join 
import statistics
from scipy import stats

my_path = 'C:\\Elena\\results_NTCP\\volume_statistics' 
figures_path = 'C:\\Elena\\results_NTCP\\Figures'

patient_list = ['ANON6','ANON12','ANON16','ANON29','ANON34','ANON38','ANON43','ANON18','ANON26','ANON37']
#patient_list = ['ANON6']

all_pat_df = pd.DataFrame(columns=['Patient','CTV5425','CTV7000','BODY'])
for patient in patient_list:
    pat_df=pd.read_excel(join(my_path,patient+'_volumes.xlsx'))
    planning_values = pat_df[pat_df['Image'] == 'pCT']
    rcts_values = pat_df[pat_df['Image'] != 'pCT']
    min_ctv7000 = round(min(rcts_values['CTV70vol'])*100/planning_values['CTV70vol'][0],2)
    min_ctv54 = round(min(rcts_values['CTV54.25vol'])*100/planning_values['CTV54.25vol'][0],2)
    min_body = round(min(rcts_values['BODYvol'])*100/planning_values['BODYvol'][0],2)
    
    max_ctv7000 = round(max(rcts_values['CTV70vol'])*100/planning_values['CTV70vol'][0],2)
    max_ctv54 = round(max(rcts_values['CTV54.25vol'])*100/planning_values['CTV54.25vol'][0],2)
    max_body = round(max(rcts_values['BODYvol'])*100/planning_values['BODYvol'][0],2)
    
    
    my_df = pd.DataFrame(columns=['Patient','CTV5425','CTV7000','BODY'])
    my_df = my_df.append({'Patient': patient, 
                          'CTV5425': str(round(planning_values['CTV54.25vol'][0],2)) + ' (' + str(min_ctv54)+',' + str(max_ctv54) + ')', 
                          'CTV7000': str(round(planning_values['CTV70vol'][0],2)) + ' (' + str(min_ctv7000)+',' + str(max_ctv7000) + ')',
                          'BODY': str(round(planning_values['BODYvol'][0],2)) + ' (' + str(min_body)+',' + str(max_body) + ')'}, 
                         ignore_index=True)

    print(my_df)
    all_pat_df = all_pat_df.append(my_df)
    
all_pat_df.to_excel(join(my_path,"data_frame_for_plots.xlsx"))
