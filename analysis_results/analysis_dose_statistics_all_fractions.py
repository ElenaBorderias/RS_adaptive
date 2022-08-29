# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 15:14:07 2021

@author: User
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

my_path = 'C:\\Elena\\results_all_fractions\\dose_statistics' 
figures_path = 'C:\\Elena\\results_all_fractions\\Figures'
patient_list = ['ANON6','ANON12','ANON16','ANON18','ANON26','ANON29','ANON34','ANON37','ANON38','ANON43']
#patient_list = ['ANON18','ANON26','ANON37']
model_list = ['0_NoAdapt','2_Mimick_ClinDose_rr_rois','3_Mimick_DefDose_def_rois','1_RSpred_RSmim_def_rois']

figures_to_plot = []
#figures_to_plot = ["V_all_CTV", "V_all_CTV_zoom","V_allOAR","V_NTCP"]
all_figures = ["V_all_CTV","V_OAR1","V_OAR2","V_OAR3", "V_NTCP","H_OAR_Dmean","H_CTVs", "V_all_organs"]

my_df = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Value','Value (Gy)'])
#all_pat_df_planning = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Value','Value (Gy)'])
for patient in patient_list:
    #pat_df_planning = pd.read_excel(join(my_path,patient+'_initial_planning.xlsx'))
    #pat_df_planning = pat_df_planning.append(pat_df_planning)
    #pat_df_planning = pat_df_planning.reset_index(drop=True)
    #pat_df_planning = pat_df_planning.rename(columns={"Value": "Abs_value"})
    #all_pat_df_planning = all_pat_df_planning.append(pat_df_planning)
    for model in model_list:
        pat_df_model = pd.read_excel(join(my_path,patient+'_'+model+'.xlsx'))
        pat_df_model = pat_df_model.rename(columns={"Value": "Abs_value"})
        #pat_df_model['Value'] =  pat_df_model['Abs_value'] - pat_df_planning['Abs_value']
        #pat_df_model['Value (Gy)'] = pat_df_model['Value'].div(100)
        
        my_df = my_df.append(pat_df_model)

my_df.to_excel(join(my_path,"data_frame_for_plots.xlsx"))


df_NA = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Strategy','Adapt_image','Needs_adapt','#Fraction'])
df_DR = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Strategy','Adapt_image','Needs_adapt','#Fraction'])
df_DEF = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Strategy','Adapt_image','Needs_adapt','#Fraction'])
df_ML = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Strategy','Adapt_image','Needs_adapt','#Fraction'])

for patient in patient_list:
    #DF NA
    df_NA_pat = pd.read_excel(join(my_path,patient+'_0_NoAdapt.xlsx'))
    df_NA_pat = df_NA_pat.rename(columns={"Value": "Abs_value"})
    df_NA = df_NA.append(df_NA_pat)
    #DF DR
    df_DR_pat = pd.read_excel(join(my_path,patient+'_2_Mimick_ClinDose_rr_rois.xlsx'))
    df_DR_pat = df_DR_pat.rename(columns={"Value": "Abs_value"})
    df_DR = df_DR.append(df_DR_pat)
    #DF DEF
    df_DEF_pat = pd.read_excel(join(my_path,patient+'_3_Mimick_DefDose_def_rois.xlsx'))
    df_DEF_pat = df_DEF_pat.rename(columns={"Value": "Abs_value"})
    df_DEF = df_DEF.append(df_DEF_pat)
    #DF ML
    df_ML_pat = pd.read_excel(join(my_path,patient+'_1_RSpred_RSmim_def_rois.xlsx'))
    df_ML_pat = df_ML_pat.rename(columns={"Value": "Abs_value"})
    df_ML = df_ML.append(df_ML_pat)
    
df_NA.drop(columns=['Unnamed: 0'])
df_DR.drop(columns=['Unnamed: 0'])
df_DEF.drop(columns=['Unnamed: 0'])
df_ML.drop(columns=['Unnamed: 0'])

##Analysis CTV
ctv_list = ["CTV_7000_D98","CTV_5425_D98"]
df_ctv = my_df[my_df['ClinicalGoal'].isin(ctv_list)]
df_ctv_NA = df_NA[df_NA['ClinicalGoal'].isin(ctv_list)]
df_ctv_DR = df_DR[df_DR['ClinicalGoal'].isin(ctv_list)]
df_ctv_DEF= df_DEF[df_DEF['ClinicalGoal'].isin(ctv_list)]
df_ctv_ML = df_ML[df_ML['ClinicalGoal'].isin(ctv_list)]

############## LEGEND FOR FIGURES ###############
blue_patch = mpatches.Patch(color=sns.color_palette()[0], label='NoAdapt')
orange_patch = mpatches.Patch(color=sns.color_palette()[1], label='Clin+Mim')
green_patch = mpatches.Patch(color=sns.color_palette()[2], label='Def+Mim')
red_patch = mpatches.Patch(color=sns.color_palette()[3], label='Pred+Mim')
sns.set_style("darkgrid")
############# FIGURE 1#################

if "V_all_CTV" in figures_to_plot:
    
    fig1, ax1 = plt.subplots()
    
    f1 = sns.boxplot(data=df_ctv,x='ClinicalGoal',y='Value (Gy)',hue='Strategy',order = ctv_list, dodge=True)
    
    ax1.set(xticklabels=["CTVp_7000","CTV_5425","CTVnL_5425","CTVnR_5425"])
    f1.legend_.set_title("Mimicking strategy")
    
    
    
    ax1.set(xlabel="D98(CTV_Prescription)",ylabel= "Difference respect\n planning [Gy]")
    plt.axvline(x=1.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axvline(x=0.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axvline(x=2.5, color='grey', linestyle='-',linewidth = 0.5)
    # Shrink current axis by 20%
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    # Put a legend to the right of the current axis
    ax1.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", loc='center left', bbox_to_anchor=(1, 0.5),fancybox=True)
    
    plt.show()
    fig1.savefig(figures_path+"\\CTV_evaluation.png", format='png', dpi=1200, bbox_inches='tight')
if "V_all_CTV_zoom" in figures_to_plot:
    
    ############# FIGURE 2 CTV #################
    sns.set_style("darkgrid")
    
    fig2_ctv, ax2_ctv = plt.subplots()
    
    strategies = ['1_Auto','2_MimCl','3_MimDef'] 
    df_ctv_2 = df_ctv[df_ctv['Strategy'].isin(strategies)]
    
    f2_ctv = sns.boxplot(data=df_ctv_2,x='ClinicalGoal',y='Value (Gy)',hue='Strategy',order = ctv_list, dodge=True)
    
    ax2_ctv.set(xticklabels=["CTVp_7000","CTV_5425","CTVnL_5425","CTVnR_5425"])
    f2_ctv.legend_.set_title("Mimicking strategy")
    
    ax2_ctv.set(xlabel="D98(CTV_Prescription)",ylabel= "Difference respect\n planning [Gy]")
    plt.axvline(x=1.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axvline(x=0.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axvline(x=2.5, color='grey', linestyle='-',linewidth = 0.5)
    color_index = [1,2,3,1,2,3,1,2,3,1,2,3]
    for i in range(0,len(color_index)):
        mybox = f2_ctv.artists[i]
        mybox.set_facecolor(sns.color_palette()[color_index[i]])
    # Shrink current axis by 20%
    box = ax2_ctv.get_position()
    ax2_ctv.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    # Put a legend to the right of the current axis
    ax2_ctv.legend(handles=[orange_patch, green_patch,red_patch], fontsize="large", loc='center left', bbox_to_anchor=(1, 0.5),fancybox=True)
    
    plt.show()
    fig2_ctv.savefig(figures_path+"\\CTV_evaluation_2.png", format='png', dpi=1200, bbox_inches='tight')

##Analysis OAR

oar_list1 = ["Parotid_L_Dmean","Parotid_R_Dmean","Submandibular_L_Dmean","Submandibular_R_Dmean"]
oar_list2 = ["PharConsSup_Dmean","PharConsMid_Dmean","PharConsInf_Dmean","Oral_Cavity_Dmean"]
oar_list3 = ["SpinalCord_D0_03cc","Brainstem_D0_03cc","BODY_D0_03cc"]
oar_list4 = oar_list1+oar_list2

df_oars1 =  my_df[my_df['ClinicalGoal'].isin(oar_list1)]
df_oars2 =  my_df[my_df['ClinicalGoal'].isin(oar_list2)]
df_oars3 =  my_df[my_df['ClinicalGoal'].isin(oar_list3)]
df_oars4 =  my_df[my_df['ClinicalGoal'].isin(oar_list4)]

if "V_OAR1" in figures_to_plot:
    
    #####OAR 1 ######
    fig2, ax2 = plt.subplots()
    f2 = sns.boxplot(data=df_oars1,x='ClinicalGoal',y='Value (Gy)',hue='Strategy',order = oar_list1 , dodge=True)
    ax2.set(xlabel="OAR metric",ylabel= "Difference respect\n planning [Gy]")
    f2.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    ax2.set(xticklabels=["Parotid_L \n Dmean","Parotid_R \n Dmean", "Submand_L \n Dmean","Submand_R \n Dmean"])
    plt.show()
    fig2.savefig(figures_path+"\\OAR1_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if "V_OAR2" in figures_to_plot:
    
    #####OAR 2 #####
    fig3, ax3 = plt.subplots()
    f3 = sns.boxplot(data=df_oars2,x='ClinicalGoal',y='Value (Gy)',hue='Strategy',order = oar_list2 , dodge=True)
    ax3.set(xlabel="OAR metric",ylabel= "Difference respect\n planning [Gy]")
    f3.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    ax3.set(xticklabels=["PCMSup \n Dmean","PCMMid \n Dmean", "PCMInf \n Dmean","Oral_Cav \n Dmean"])
    plt.show()
    fig3.savefig(figures_path+"\\OAR2_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if "V_OAR3" in figures_to_plot:
   
    #####OAR 3 ######
    fig4, ax4 = plt.subplots()
    f4 = sns.boxplot(data=df_oars3,x='ClinicalGoal',y='Value (Gy)',hue='Strategy',order = oar_list3 , dodge=True)
    ax4.set(xlabel="OAR metric",ylabel= "Difference respect\n planning [Gy]")
    f4.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    plt.show()
    fig4.savefig(figures_path+"\\OAR3_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if "V_NTCP" in figures_to_plot:
    ## Analysis NTCP
    ntcp_list = ["xero_grade2", "xero_grade3", "dysf_grade2","dysf_grade3"]
    #strategies = ['1_Auto','2_MimCl','3_MimDef'] 
    df_ntcp =  my_df[my_df['ClinicalGoal'].isin(ntcp_list)]
    #df_ntcp =  df_ntcp[df_ntcp['Strategy'].isin(strategies)]
    
    df_ntcp = df_ntcp.rename(columns={"Value": "Delta_NTCP[%]"})
    #df_ntcp["Delta_NTCP[%]"] = df_ntcp["Value"].div(0.01)
    
    fig5, ax5 = plt.subplots()
    f5 = sns.boxplot(data=df_ntcp,x='ClinicalGoal',y='Delta_NTCP[%]',hue='Strategy',order = ntcp_list , dodge=True)
    ax5.set(xlabel="",ylabel= "Delta NTCP  [%]")
    #ax5.set_ylim([-1, 4.5])
    f5.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    ax5.set(xticklabels=["Xerostomia \n Grade 2","Xerostomia \n Grade 3", "Dysfagia \n Grade 2","Dysfagia \n Grade 3"])
    plt.show()
    fig5.savefig(figures_path+"\\NTCP_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if "V_HI" in figures_to_plot:
##### Homogeneity index (HI) ######
    HI_list = ["HI_CTV_7000", "HI_CTVn_5425"]
    df_HI =  my_df[my_df['ClinicalGoal'].isin(HI_list)]
    all_pat_df_planning_HI = all_pat_df_planning[all_pat_df_planning['ClinicalGoal'].isin(HI_list)]
    
    df_HI_total = all_pat_df_planning_HI.append(df_HI)
    
    fig6, ax6 = plt.subplots()
    f6 = sns.boxplot(data=df_HI_total,x='ClinicalGoal',y='Abs_value',hue='Strategy',order = HI_list, dodge=True)
    ax6.set(xlabel="",ylabel= "Homogeneity Index (HI)")
    #f6.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    purple_patch = mpatches.Patch(color=sns.color_palette()[4], label = 'Planning')
    f6.legend(handles=[purple_patch,red_patch, blue_patch, orange_patch, green_patch], fontsize="large", fancybox=True)
    
    color_index = [4,0,1,2,3,4,0,1,2,3]
    for i in range(0,len(color_index)):
        mybox = f6.artists[i]
        mybox.set_facecolor(sns.color_palette()[color_index[i]])
        
    ax6.set(xticklabels=["HI(CTV7000)","HI(CTVn5425)"])
    plt.show()
    fig6.savefig(figures_path+"\\HI_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if "H_OAR_Dmean" in figures_to_plot:
    ##### OAR 4 - horizontal ######
    
    sns.set_style("white")
    
    fig7, ax7 = plt.subplots()
    #sns.set_style("darkgrid", {"grid.color": "0", "grid.linestyle": "-"})
    sns.set_style("white")
    for i in range(0,len(oar_list4)):
        plt.axhline(y=i+0.5, color='grey', linestyle='-',linewidth = 0.5)
    
    f7 = sns.boxplot(data=df_oars4,x='Value (Gy)',y='ClinicalGoal',hue='Strategy', dodge=True)
    
    ax7.set(ylabel="OAR Dmean ",xlabel= "Difference respect to clinical plan [Gy]")
    ax7.set(yticklabels=["Parotid L","Parotid R","SMG L","SMG R","PCMSup","PCMMid", "PCMInf","OralCavity"])
    f7.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", loc='center left', bbox_to_anchor=(1, 0.5),fancybox=True)
    f7.legend_.set_title("Autoplanning strategy")
    plt.axvline(x=0, color='grey', linestyle='-',linewidth = 0.5)
    plt.title(' ← Lower dose to OARs | Higher dose to OARs  →')
    plt.show()
    fig7.savefig(figures_path+"\\OAR4_evaluation_horizontal.png", format='png', dpi=1200, bbox_inches='tight')
    
    for ticklabel in ax7.get_xticklabels():
        print(ticklabel.get_text())
    
if "H_CTVs" in figures_to_plot:

    ##Analysis CTV horizontal boxplots
    ############# FIGURE 8#################
    #ctv_hlist = ["CTVp_7000_D98", "CTV_5425_D98"]
    ctv_hlist = ["CTVp_7000_D98", "CTV_5425_D98","CTVnR_5425_D98","CTVnL_5425_D98"]
    dfh_ctv = my_df[my_df['ClinicalGoal'].isin(ctv_hlist)]
    
    #sum_column = dfh_ctv["ClinicalGoal"] + dfh_ctv["Scenario"]
    #dfh_ctv["New ClinicalGoal"] = sum_column
    #ctvh_list = ["CTVp_7000_D98nominal", "CTVn_5425_D98nominal", "CTVp_7000_D98worst-case", "CTVn_5425_D98worst-case"]
    
    fig8, ax8 = plt.subplots()
    for i in range(0,len(ctv_hlist)):
        plt.axhline(y=i+0.5, color='grey', linestyle='-',linewidth = 0.5)
        
    #f8 = sns.boxplot(data=dfh_ctv,y='New ClinicalGoal',x='Delta_Value(Gy)',hue='Plan_name',order = ctvh_list , dodge=True)
    f8 = sns.boxplot(data=dfh_ctv,y='ClinicalGoal',x='Value (Gy)',hue='Strategy',order = ctv_hlist , dodge=True)
    
    ax8.set(xlabel= "Difference respect to clinical plan [Gy]",ylabel= "")
    #ax8.set(yticklabels=["D98(CTV70)\n Nominal","CTV54.25\n Nominal","CTV70 \n WorstCase","CTV54.25\n WorstCase"])
    ax8.set(yticklabels=["CTV70","CTVn 54.25","CTVnR 54.25","CTVnL 54.25"])
    
    f8.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", loc='center left', bbox_to_anchor=(1, 0.5),fancybox=True)
    f8.legend_.set_title("Autoplanning strategy")
    plt.axvline(x=0, color='grey', linestyle='-',linewidth = 0.5)
    plt.title('← Lower CTV coverage | Higher CTV coverage  →')
    
    plt.show()
    fig8.savefig(figures_path+"\\CTV_evaluation_horizontal.png", format='png', dpi=1200, bbox_inches='tight')

if "V_allOAR" in figures_to_plot:
#####OAR 3 ######
    
    fig9, ax9 = plt.subplots()
    f9 = sns.boxplot(data=df_oars4,x='ClinicalGoal',y='Value (Gy)',hue='Strategy',order = oar_list4 , dodge=True)
    for i in range(0,len(oar_list4)):
        plt.axvline(x=i+0.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axhline(y=0, color='grey', linestyle='-',linewidth = 0.5)
    ax9.set(xlabel="Dmean OAR",ylabel= "Difference respect planning [Gy] \n  ← Lower dose to OARs | Higher dose to OARs  →")
    ax9.set_xticklabels(ax9.get_xticks()-0.5, rotation = 30)
    ax9.set(xticklabels=['Parotid L','Parotid R','SMG L','SMG R','PCMSup','PCMMid','PCMInf','Oral Cavity'])
    
    f9.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    plt.show()
    fig9.savefig(figures_path+"\\Dmean_OARs_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

"""
#### DELIVERY ###
my_path_schedules = 'C:\\Elena\\results\\different_ttmt_schedules'
models = ['1_RSpred_RSmim_def_rois','2_Mimick_ClinDose_rr_rois','3_Mimick_DefDose_def_rois']
patient_list_delivery = ['ANON6','ANON12','ANON16','ANON29','ANON34','ANON38','ANON43']

adapt_strategies = ['Best_plan','Last_plan']

for adapt_st in adapt_strategies:
    print(adapt_st)
    for patient in patient_list_delivery:
        for model in models:
            pat_model_path = join(join(my_path_schedules, adapt_st),patient+'_delivery_for_'+model+'.xlsx')
            schedule_df =  pd.read_excel(pat_model_path)
            adaptation_rate = sum(schedule_df['Needs_new_plan'])
            
            print(patient, model, adaptation_rate)
            
"""       
############# Metrics analysis #####################
####### CTV 7000 ######
ctv7000_val =  df_ctv[df_ctv['ClinicalGoal'] == 'CTV_7000_D98']
print("############ STATS CTV7000 ############")
print("############ ONLY ADAPTED FRACTIONS ############")
model_list = ["0_NA","2_MimCl_","3_MimDef_","1_Auto_"]

for model in model_list:
    ctv7000_val_temp = ctv7000_val[ctv7000_val['Strategy'] == model]
    ctv7000_val_temp = ctv7000_val_temp[ctv7000_val_temp['Needs_adapt'] == 1]
    print("#FRACTIONS #", len(ctv7000_val_temp))
    min_ctv7000 = min(ctv7000_val_temp['Abs_value'])
    max_ctv7000 = max(ctv7000_val_temp['Abs_value'])
    median_ctv7000 = statistics.median(ctv7000_val_temp['Abs_value'])
    print(model, 'Min: ', min_ctv7000, 'Max: ', max_ctv7000,', median: ', median_ctv7000)
    fail_cases = ctv7000_val_temp.apply(lambda x: x['Abs_value'] < 6650, axis=1).sum()
    
    print(model, 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv7000_val_temp),'%')


print("############ ALL FRACTIONS ############")

ctv70_t_na = df_ctv_NA[df_ctv_NA['ClinicalGoal'] == 'CTV_7000_D98']
len(ctv70_t_na)
print("#FRACTIONS #", len(ctv70_t_na))
min_ctv7000_na = min(ctv70_t_na['Abs_value'])
max_ctv7000_na = max(ctv70_t_na['Abs_value'])
median_ctv7000_na = statistics.median(ctv70_t_na['Abs_value'])
print("NA", 'Min: ', min_ctv7000_na, 'Max: ', max_ctv7000_na,', median: ', median_ctv7000_na)
print("NA", 'Min: ', min_ctv7000_na/7000, 'Max: ', max_ctv7000_na/7000,', median: ', median_ctv7000_na/7000)
fail_cases = ctv70_t_na.apply(lambda x: x['Abs_value'] < 6650, axis=1).sum()

print("NA", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv70_t_na),'%')

ctv70_t_dr = df_ctv_DR[df_ctv_DR['ClinicalGoal'] == 'CTV_7000_D98']
len(ctv70_t_dr)
print("#FRACTIONS #", len(ctv70_t_dr))
min_ctv7000_dr = min(ctv70_t_dr['Abs_value'])
max_ctv7000_dr = max(ctv70_t_dr['Abs_value'])
median_ctv7000_dr = statistics.median(ctv70_t_dr['Abs_value'])
print("DR", 'Min: ', min_ctv7000_dr, 'Max: ', max_ctv7000_dr,', median: ', median_ctv7000_dr)
print("DR", 'Min: ', min_ctv7000_dr/7000, 'Max: ', max_ctv7000_dr/7000,', median: ', median_ctv7000_dr/7000)
fail_cases = ctv70_t_dr.apply(lambda x: x['Abs_value'] < 6650, axis=1).sum()

print("DR", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv70_t_dr),'%')

ctv70_t_def = df_ctv_DEF[df_ctv_DEF['ClinicalGoal'] == 'CTV_7000_D98']
len(ctv70_t_def)
print("#FRACTIONS #", len(ctv70_t_def))
min_ctv7000_def = min(ctv70_t_def['Abs_value'])
max_ctv7000_def = max(ctv70_t_def['Abs_value'])
median_ctv7000_def = statistics.median(ctv70_t_def['Abs_value'])
print("DEF", 'Min: ', min_ctv7000_def, 'Max: ', max_ctv7000_def,', median: ', median_ctv7000_def)
print("DEF", 'Min: ', min_ctv7000_def/7000, 'Max: ', max_ctv7000_def/7000,', median: ', median_ctv7000_def/7000)

fail_cases = ctv70_t_def.apply(lambda x: x['Abs_value'] < 6650, axis=1).sum()
print("DEF", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv70_t_def),'%')


ctv70_t_ml = df_ctv_ML[df_ctv_ML['ClinicalGoal'] == 'CTV_7000_D98']
len(ctv70_t_ml)
print("#FRACTIONS #", len(ctv70_t_ml))
min_ctv7000_ml = min(ctv70_t_ml['Abs_value'])
max_ctv7000_ml = max(ctv70_t_ml['Abs_value'])
median_ctv7000_ml = statistics.median(ctv70_t_ml['Abs_value'])
print("ML", 'Min: ', min_ctv7000_ml, 'Max: ', max_ctv7000_ml,', median: ', median_ctv7000_ml)
print("ML", 'Min: ', min_ctv7000_ml/7000, 'Max: ', max_ctv7000_ml/7000,', median: ', median_ctv7000_ml/7000)

fail_cases = ctv70_t_ml.apply(lambda x: x['Abs_value'] < 6650, axis=1).sum()
print("ML", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv70_t_ml),'%')


"""   
for model in model_list:
    ctv7000_val_temp = ctv7000_val[ctv7000_val['Strategy'] == model]
    min_ctv7000 = min(ctv7000_val_temp['Value (Gy)'])
    median_ctv7000 = statistics.median(ctv7000_val_temp['Value (Gy)'])
    iqr_ctv7000 = stats.iqr(ctv7000_val_temp['Value (Gy)'])
    print(model, ' DELTA Min abs value CTVp  7000: ', min_ctv7000, ', DELTA median: ', median_ctv7000, ',  DELTA iqr: ', iqr_ctv7000)
"""   

####### CTV 5425 ######
ctv5425_val =  df_ctv[df_ctv['ClinicalGoal'] == 'CTV_5425_D98']
print("############ STATS CTV5425 ############")
print("############ ONLY ADAPTED FRACTIONS ############")

for model in model_list:
    ctv5425_val_temp = ctv5425_val[ctv5425_val['Strategy'] == model]
    min_ctv5425 = min(ctv5425_val_temp['Abs_value'])
    max_ctv5425 = max(ctv5425_val_temp['Abs_value'])
    median_ctv5425 = statistics.median(ctv5425_val_temp['Abs_value'])
    print("#FRACTIONS #", len(ctv5425_val_temp))
    print(model, 'Min: ', min_ctv5425, 'Max: ', max_ctv5425, ', median: ', median_ctv5425)
    fail_cases = ctv5425_val_temp.apply(lambda x: x['Abs_value'] < 5153.7, axis=1).sum()
    print(model, 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv5425_val_temp),'%')

print("############ ALL FRACTIONS ############")

ctv54_t_na = df_ctv_NA[df_ctv_NA['ClinicalGoal'] == 'CTV_5425_D98']
len(ctv54_t_na)
print("#FRACTIONS #", len(ctv54_t_na))
min_ctv54_na = min(ctv54_t_na['Abs_value'])
max_ctv54_na = max(ctv54_t_na['Abs_value'])
median_ctv54_na = statistics.median(ctv54_t_na['Abs_value'])
print("NA", 'Min: ', min_ctv54_na, 'Max: ', max_ctv54_na,', median: ', median_ctv54_na)
print("NA", 'Min: ', min_ctv54_na/5425, 'Max: ', max_ctv54_na/5425,', median: ', median_ctv54_na/5425)

fail_cases = ctv54_t_na.apply(lambda x: x['Abs_value'] < 5153.7, axis=1).sum()

print("NA", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv70_t_na),'%')

ctv54_t_dr = df_ctv_DR[df_ctv_DR['ClinicalGoal'] == 'CTV_5425_D98']
len(ctv54_t_dr)
print("#FRACTIONS #", len(ctv54_t_dr))
min_ctv54_dr = min(ctv54_t_dr['Abs_value'])
max_ctv54_dr = max(ctv54_t_dr['Abs_value'])
median_ctv54_dr = statistics.median(ctv54_t_dr['Abs_value'])
print("DR", 'Min: ', min_ctv54_dr, 'Max: ', max_ctv54_dr,', median: ', median_ctv54_dr)
print("DR", 'Min: ', min_ctv54_dr/5425, 'Max: ', max_ctv54_dr/5425,', median: ', median_ctv54_dr/5425)

fail_cases = ctv54_t_dr.apply(lambda x: x['Abs_value'] < 5153.7, axis=1).sum()

print("DR", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv54_t_dr),'%')

ctv54_t_def = df_ctv_DEF[df_ctv_DEF['ClinicalGoal'] == 'CTV_5425_D98']
len(ctv54_t_def)
print("#FRACTIONS #", len(ctv54_t_def))
min_ctv54_def = min(ctv54_t_def['Abs_value'])
max_ctv54_def = max(ctv54_t_def['Abs_value'])
median_ctv54_def = statistics.median(ctv54_t_def['Abs_value'])
print("DEF", 'Min: ', min_ctv54_def, 'Max: ', max_ctv54_def,', median: ', median_ctv54_def)
print("DEF", 'Min: ', min_ctv54_def/5425, 'Max: ', max_ctv54_def/5425,', median: ', median_ctv54_def/5425)

fail_cases = ctv54_t_def.apply(lambda x: x['Abs_value'] < 5153.7, axis=1).sum()
print("DEF", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv54_t_def),'%')


ctv54_t_ml = df_ctv_ML[df_ctv_ML['ClinicalGoal'] =='CTV_5425_D98']
len(ctv54_t_ml)
print("#FRACTIONS #", len(ctv54_t_ml))
min_ctv54_ml = min(ctv54_t_ml['Abs_value'])
max_ctv54_ml = max(ctv54_t_ml['Abs_value'])
median_ctv54_ml = statistics.median(ctv54_t_ml['Abs_value'])
print("ML", 'Min: ', min_ctv54_ml, 'Max: ', max_ctv54_ml,', median: ', median_ctv54_ml)
print("ML", 'Min: ', min_ctv54_ml/5425, 'Max: ', max_ctv54_ml/5425,', median: ', median_ctv54_ml/5425)

fail_cases = ctv54_t_ml.apply(lambda x: x['Abs_value'] < 5153.7, axis=1).sum()
print("ML", 'Abs failure: ', fail_cases, ', % failure: ', fail_cases*100/len(ctv54_t_ml),'%')

"""
for model in model_list:
    ctv5425_val_temp = ctv5425_val[ctv5425_val['Strategy'] == model]
    min_ctv5425 = min(ctv5425_val_temp['Value (Gy)'])
    median_ctv5425 = statistics.median(ctv5425_val_temp['Value (Gy)'])
    iqr_ctv5425 = stats.iqr(ctv5425_val_temp['Value (Gy)'])
    print(model, ' DELTA Min abs value CTVp  5425: ', min_ctv5425, ', DELTA median: ', median_ctv5425, ',  DELTA iqr: ', iqr_ctv5425)


################ Statistical significance analysis ############

######  STATISTICAL SIGNIFICANCE RESPECTO TO PLANNING values ########
print("######  STATISTICAL SIGNIFICANCE RESPECTO TO PLANNING values ########")
ctv_list = ["CTVp_7000_D98", "CTV_5425_D98"]

df_stats_ctv = pd.DataFrame(index=range(0,len(ctv_list)*len(model_list),1),columns=['CTV_stat','Plan_name','p-value','Is stat sig'])
df_stats_oar = pd.DataFrame(index=range(0,len(oar_list4)*len(model_list),1),columns=['OAR_stat','Plan_name','p-value','Is stat sig'])

i=0
for ctv_stat in ctv_list:
    df_ctv_temp = df_ctv[df_ctv['ClinicalGoal'] == ctv_stat]
    df_ctv_planning_temp = all_pat_df_planning[all_pat_df_planning['ClinicalGoal'] == ctv_stat]
    for model in model_list:  
        df_ctv_temp_model = df_ctv_temp[df_ctv_temp['Strategy'] == model]
        p_value = stats.wilcoxon(df_ctv_planning_temp['Abs_value'],  df_ctv_temp_model['Abs_value']).pvalue
        df_stats_ctv['CTV_stat'][i] = ctv_stat
        df_stats_ctv['Plan_name'][i] = model
        df_stats_ctv['p-value'][i]  = p_value
        if p_value<0.05:
            df_stats_ctv['Is stat sig'][i] = 'Yes'  
        elif p_value >= 0.05:
            df_stats_ctv['Is stat sig'][i] = 'No'  

        i=i+1

print(df_stats_ctv)

i=0
for oar_stat in oar_list4:
    df_oar_temp = df_oars4[df_oars4['ClinicalGoal'] ==  oar_stat]
    df_oar_planning_temp = all_pat_df_planning[all_pat_df_planning['ClinicalGoal'] == oar_stat]
    for model in model_list:  
        df_oar_temp_model = df_oar_temp[df_oar_temp['Strategy'] == model]
        p_value = stats.wilcoxon(df_oar_planning_temp['Abs_value'],  df_oar_temp_model['Abs_value']).pvalue
        df_stats_oar['OAR_stat'][i] = oar_stat
        df_stats_oar['Plan_name'][i] = model
        df_stats_oar['p-value'][i]  = p_value
        if p_value<0.05:
            df_stats_oar['Is stat sig'][i] = 'Yes'  
        elif p_value >= 0.05:
            df_stats_oar['Is stat sig'][i] = 'No'  

        i=i+1

print(df_stats_oar)

######  STATISTICAL SIGNIFICANCE BETWEEN STRATEGIES ########
print("######  STATISTICAL SIGNIFICANCE BETWEEN STRATEGIES ########")
# 1 '0_NA' - '2_MimCl" = 0_NA vs 2_MimCl
# 2 '0_NA' - '3_MimDef' = 0_NA vs 3_MimDef
# 3 '0_NA' - '1_Auto' = 0_NA vs 1_Auto
# 4 '2_MimCl' -  '3_MimDef' = 2_MimCl vs 3_MimDef
# 5 '2_MimCl' - '1_Auto' = 2_MimCl vs 1_Auto
# 6 '3_MimDef' - '1_Auto' = 3_MimDef vs 1_Auto

scenarios = [{"name":"sc1:NA-DR","plan_1": "0_NA", "plan_2": "2_MimCl"},
            { "name":"sc2:NA-Def", "plan_1": "0_NA", "plan_2": "3_MimDef"},
            { "name":"sc3:NA-Auto","plan_1": "0_NA", "plan_2": "1_Auto"},
            { "name":"sc4:DR-Def","plan_1": "2_MimCl", "plan_2": "3_MimDef"},
            { "name":"sc5:DR-Auto","plan_1": "2_MimCl", "plan_2": "1_Auto"},
            { "name":"sc6:Def-Auto","plan_1": "3_MimDef", "plan_2": "1_Auto"},
            ]


df_stats_ctv_relative = pd.DataFrame(index=range(0,len(ctv_list)*len(scenarios),1),columns=['CTV_stat','Scenario_name','p-value','Is stat sig'])
i=0
for ctv_stat in ctv_list:
    df_ctv_scenarios = df_ctv[df_ctv['ClinicalGoal'] == ctv_stat]
    
    for scenario in scenarios:  
        df_ctv_temp_sc1 = df_ctv_scenarios[df_ctv_scenarios['Strategy'] == scenario['plan_1']]
        df_ctv_temp_sc2 = df_ctv_scenarios[df_ctv_scenarios['Strategy'] == scenario['plan_2']]
        
        p_value = stats.wilcoxon(df_ctv_temp_sc1['Abs_value'],  df_ctv_temp_sc2['Abs_value']).pvalue
        
        df_stats_ctv_relative['CTV_stat'][i] = ctv_stat
        df_stats_ctv_relative['Scenario_name'][i] = scenario['name']
        df_stats_ctv_relative['p-value'][i]  = p_value
        if p_value<0.05:
            df_stats_ctv_relative['Is stat sig'][i] = 'Yes'  
        elif p_value >= 0.05:
            df_stats_ctv_relative['Is stat sig'][i] = 'No'  

        i=i+1

print(df_stats_ctv_relative)

df_stats_oar_relative = pd.DataFrame(index=range(0,len(oar_list4)*len(scenarios),1),columns=['OAR_stat','Scenario_name','p-value','Is stat sig'])
i=0
for oar_stat in oar_list4:
    df_oar_scenarios = df_oars4[df_oars4['ClinicalGoal'] == oar_stat]
    for scenario in scenarios:  
        df_oar_temp_sc1 = df_oar_scenarios[df_oar_scenarios['Strategy'] == scenario['plan_1']]
        df_oar_temp_sc2 = df_oar_scenarios[df_oar_scenarios['Strategy'] == scenario['plan_2']]
        
        p_value = stats.wilcoxon(df_oar_temp_sc1['Abs_value'],  df_oar_temp_sc2['Abs_value']).pvalue
        
        df_stats_oar_relative['OAR_stat'][i] = oar_stat
        df_stats_oar_relative['Scenario_name'][i] = scenario['name']
        df_stats_oar_relative['p-value'][i]  = p_value
        if p_value<0.05:
            df_stats_oar_relative['Is stat sig'][i] = 'Yes'  
        elif p_value >= 0.05:
            df_stats_oar_relative['Is stat sig'][i] = 'No'  

        i=i+1

print(df_stats_oar_relative)

"""