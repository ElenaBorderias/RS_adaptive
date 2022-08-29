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

my_path = 'C:\\Elena\\results_NTCP\\dose_statistics' 
figures_path = 'C:\\Elena\\results_NTCP\\Figures'
#patient_list = ['ANON6','ANON12','ANON16','ANON29','ANON34','ANON38','ANON43']
#patient_list = ['ANON18','ANON26','ANON37']
patient_list = ['ANON6','ANON12','ANON16','ANON29','ANON34','ANON38','ANON43','ANON18','ANON26','ANON37']
model_list = ['0_NoAdapt','2_Mimick_ClinDose_rr_rois','3_Mimick_DefDose_def_rois','1_RSpred_RSmim_def_rois']

figures_to_plot = ["V_all_CTV","V_allOAR","V_NTCP","Catplot_OARs"]
all_figures = ["V_all_CTV","V_OAR1","V_OAR2","V_OAR3", "V_NTCP","V_HI","H_OAR_Dmean","H_CTVs", "V_all_organs"]

my_df = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Value','Value (Gy)'])
all_pat_df_planning = pd.DataFrame(columns=['Patient','Plan_name','ClinicalGoal','Abs_value','Value','Value (Gy)'])
for patient in patient_list:
    pat_df_planning = pd.read_excel(join(my_path,patient+'_initial_planning.xlsx'))
    pat_df_planning = pat_df_planning.rename(columns={"Value": "Abs_value"})
    all_pat_df_planning = all_pat_df_planning.append(pat_df_planning)
    for model in model_list:
        pat_df_model = pd.read_excel(join(my_path,patient+'_'+model+'.xlsx'))
        pat_df_model = pat_df_model.rename(columns={"Value": "Abs_value"})
        pat_df_model['Value'] =  pat_df_model['Abs_value'] - pat_df_planning['Abs_value']
        pat_df_model['Value (Gy)'] = pat_df_model['Value'].div(100)
        
        my_df = my_df.append(pat_df_model)

my_df.to_excel(join(my_path,"data_frame_for_plots.xlsx"))

blue_patch = mpatches.Patch(color=sns.color_palette()[0], label='NA')
orange_patch = mpatches.Patch(color=sns.color_palette()[1], label='OADR')
green_patch = mpatches.Patch(color=sns.color_palette()[2], label='OADEF')
red_patch = mpatches.Patch(color=sns.color_palette()[3], label='OAML')
##Analysis CTV
ctv_list = ["CTVp_7000_D98", "CTV_5425_D98", "CTVnL_5425_D98","CTVnR_5425_D98"]
ctv_list2 = ["CTVp_7000_D98", "CTV_5425_D98"]

df_ctv = my_df[my_df['ClinicalGoal'].isin(ctv_list)]
#sns.set_style("darkgrid")
##Analysis OAR

#####OAR 1 ######
oar_list1 = ["Parotid_L_Dmean","Parotid_R_Dmean","Submandibular_L_Dmean","Submandibular_R_Dmean"]
oar_list2 = ["PharConsSup_Dmean","PharConsMid_Dmean","PharConsInf_Dmean","Oral_Cavity_Dmean"]
oar_list3 = ["SpinalCord_D0_03cc","Brainstem_D0_03cc","BODY_D0_03cc"]

oar_list4 = oar_list1+oar_list2

if "V_all_CTV" in figures_to_plot:
    
    ############# FIGURE 1#################    
    fig1, ax1 = plt.subplots()
    sns.set(style = "darkgrid", font_scale=1.1)

    f1 = sns.boxplot(data=df_ctv,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = ctv_list, dodge=True)
    #f1 = sns.swarmplot(data=df_ctv,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = ctv_list, dodge=True)
    
    ax1.set(xticklabels=["High-risk \n CTV","Low-risk \n CTV","Low-risk \n CTVnL","Low-risk \n CTVnR"])
    f1.legend_.set_title("Mimicking strategy")
    
    ax1.set(xlabel="Dose at 98% volume of CTV: D98 (CTV)",ylabel= "Difference respect planning [Gy] \n ← Lower coverage | Higher coverage  →")
    plt.axvline(x=1.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axvline(x=0.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axvline(x=2.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axhline(y=0, color='grey', linestyle='--',linewidth = 0.5)
    
    # Shrink current axis by 20%
    #box = ax1.get_position()
    #ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    plt.tight_layout()
    # Put a legend to the right of the current axis
    plt.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=11.5, ncol = 4, loc=(0,1.05), fancybox=True)

    plt.show()
    fig1.savefig(figures_path+"\\CTV_evaluation.png", format='png', dpi=1200, bbox_inches='tight')
    
    ########CTV catplot 1 ###########
    sns.set(font_scale=1.1)
    df_ctv2 =  my_df[my_df['ClinicalGoal'].isin(ctv_list2)]
    g0=sns.catplot(x = 'Plan_name', y="Value (Gy)", col="ClinicalGoal", 
                data=df_ctv2, kind="box", height=4, aspect=.7, legend = True)
    g0.set_xticklabels(["","","",""], fontsize = 12)
    g0.map(plt.axhline, y=0, ls='--', color='grey', linewidth=1)
    g0.set_axis_labels(x_var=" ", y_var="Difference respect planning [Gy] \n  ← Lower dose | Higher dose  →", fontsize = 17)
    
    axes = g0.axes.flatten()
    axes[0].set_title("D98 (High-risk CTV)", fontsize = 15)
    axes[1].set_title("D98 (Low-risk CTV)", fontsize = 15)
    plt.tight_layout()
    
    plt.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=14, ncol = 4, loc=(-1.4,1.2), fancybox=True)
    g0.savefig(figures_path+"\\CTV2_catplot.png", format='png', dpi=1200, bbox_inches='tight')
    

df_oars1 =  my_df[my_df['ClinicalGoal'].isin(oar_list1)]
if "V_OAR1" in figures_to_plot:
    #####OAR 1######
    
    fig2, ax2 = plt.subplots()
    f2 = sns.boxplot(data=df_oars1,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = oar_list1 , dodge=True)
    ax2.set(xlabel="OAR metric",ylabel= "Difference respect\n planning [Gy]")
    f2.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    ax2.set(xticklabels=["Parotid_L \n Dmean","Parotid_R \n Dmean", "Submand_L \n Dmean","Submand_R \n Dmean"])
    plt.show()
    fig2.savefig(figures_path+"\\OAR1_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

df_oars2 =  my_df[my_df['ClinicalGoal'].isin(oar_list2)]
if "V_OAR2" in figures_to_plot:
    #####OAR 2 ######
    
    fig3, ax3 = plt.subplots()
    f3 = sns.boxplot(data=df_oars2,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = oar_list2 , dodge=True)
    ax3.set(xlabel="OAR metric",ylabel= "Difference respect\n planning [Gy]")
    f3.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    ax3.set(xticklabels=["PCMSup \n Dmean","PCMMid \n Dmean", "PCMInf \n Dmean","OralCavity \n Dmean"])
    plt.show()
    fig3.savefig(figures_path+"\\OAR2_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

df_oars3 =  my_df[my_df['ClinicalGoal'].isin(oar_list3)]
if "V_OAR3" in figures_to_plot:
    
    #####OAR 3 ######
    
    fig4, ax4 = plt.subplots()
    f4 = sns.boxplot(data=df_oars3,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = oar_list3 , dodge=True)
    ax4.set(xlabel="OAR metric",ylabel= "Difference respect\n planning [Gy]")
    f4.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    plt.show()
    fig4.savefig(figures_path+"\\OAR3_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if  "V_NTCP" in figures_to_plot:
    ## Analysis NTCP
    ntcp_list = ["xero_grade2", "xero_grade3", "dysf_grade2","dysf_grade3"]
    df_ntcp =  my_df[my_df['ClinicalGoal'].isin(ntcp_list)]
    df_ntcp = df_ntcp.rename(columns={"Value (Gy)": "Delta_NTCP[%]"})
    df_ntcp["Delta_NTCP[%]"] = df_ntcp["Value"].div(0.01)
    
    
    fig5, ax5 = plt.subplots()
    f5 = sns.boxplot(data=df_ntcp,x='ClinicalGoal',y='Delta_NTCP[%]',hue='Plan_name',order = ntcp_list , dodge=True)
    ax5.set(xlabel="",ylabel= "Delta NTCP  [%]")
    ax5.set_ylim([-1, 4.5])
    f5.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=11.5, ncol = 4, loc=(0,1.01), fancybox=True)
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
    f6 = sns.boxplot(data=df_HI_total,x='ClinicalGoal',y='Abs_value',hue='Plan_name',order = HI_list, dodge=True)
    ax6.set(xlabel="",ylabel= "Homogeneity Index (HI)")
    #f6.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", fancybox=True)
    purple_patch = mpatches.Patch(color=sns.color_palette()[4], label = 'Planning')
    f6.legend(handles=[purple_patch,red_patch, blue_patch, orange_patch, green_patch], fontsize="large", fancybox=True)
    
    color_index = [4,0,1,2,3,4,0,1,2,3]
    for i in range(0,10):
        mybox = f6.artists[i]
        mybox.set_facecolor(sns.color_palette()[color_index[i]])
        
    ax6.set(xticklabels=["HI(CTV7000)","HI(CTVn5425)"])
    plt.show()
    fig6.savefig(figures_path+"\\HI_evaluation.png", format='png', dpi=1200, bbox_inches='tight')
    
##### OAR 4 - horizontal ######
oar_list4 = oar_list1+oar_list2
df_oars4 =  my_df[my_df['ClinicalGoal'].isin(oar_list4)]
sns.set_style("white")

if "H_OAR_Dmean" in figures_to_plot:

    fig7, ax7 = plt.subplots()
    #sns.set_style("darkgrid", {"grid.color": "0", "grid.linestyle": "-"})
    sns.set_style("white")
    for i in range(0,len(oar_list4)):
        plt.axhline(y=i+0.5, color='grey', linestyle='-',linewidth = 0.5)
    
    f7 = sns.boxplot(data=df_oars4,x='Value (Gy)',y='ClinicalGoal',hue='Plan_name', dodge=True)
    
    ax7.set(ylabel="OAR Dmean ",xlabel= "Difference respect to clinical plan [Gy]")
    ax7.set(yticklabels=["Parotid L","Parotid R","SMG L","SMG R","PCMSup","PCMMid", "PCMInf","OralCavity"])
    f7.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize="large", loc='center left', bbox_to_anchor=(1, 0.5),fancybox=True)
    f7.legend_.set_title("Autoplanning strategy")
    plt.axvline(x=0, color='grey', linestyle='-',linewidth = 0.5)
    plt.title(' ← Lower dose | Higher dose  →')
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
    f8 = sns.boxplot(data=dfh_ctv,y='ClinicalGoal',x='Value (Gy)',hue='Plan_name',order = ctv_hlist , dodge=True)
    
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
    #sns.set(font_scale=1.1)
    fig9, ax9 = plt.subplots()
    f9 = sns.boxplot(data=df_oars4,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = oar_list4 , dodge=True)
    for i in range(0,len(oar_list4)):
        plt.axvline(x=i+0.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axhline(y=0, color='grey', linestyle='-',linewidth = 0.5)
    ax9.set(xlabel="Dmean OAR",ylabel= "Difference respect planning [Gy] \n  ← Lower dose | Higher dose  →")
    ax9.set_xticklabels(ax9.get_xticks()-0.5, rotation = 30)
    ax9.set(xticklabels=['Parotid L','Parotid R','SMG L','SMG R','PCMSup','PCMMid','PCMInf','Oral Cavity'])
    
    f9.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=11.5, ncol = 4, loc=(0,1.05), fancybox=True)

    plt.show()
    fig9.savefig(figures_path+"\\Dmean_OARs_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

    #####OAR 5 ######
    
    #sns.set(style="white", font_scale=1.5)
    #sns.set(style="darkgrid", font_scale=1.5)
    fig10, ax10 = plt.subplots()
    oar_list5 = oar_list4 + oar_list3
    df_oars5 = my_df[my_df['ClinicalGoal'].isin(oar_list5)]
    
    f10 = sns.boxplot(data=df_oars5,x='ClinicalGoal',y='Value (Gy)',hue='Plan_name',order = oar_list5 ,dodge=True)
    for i in range(0,len(oar_list5)):
        plt.axvline(x=i+0.5, color='grey', linestyle='-',linewidth = 0.5)
    plt.axhline(y=0, color='grey', linestyle='--',linewidth = 0.5)
    ax10.set(xlabel="OAR Metric",ylabel= "Difference respect planning [Gy] \n  ← Lower dose | Higher dose  →")
    ax10.set_xticklabels(ax10.get_xticks()-0.5, rotation = 45)
    ax10.set(xticklabels=['Parotid L','Parotid R','SMG L','SMG R','PCMSup','PCMMid','PCMInf','Oral Cavity',"SpinalCord \n D0.03cc","Brainstem \n D0.03cc","Body \n D0.03cc"])
    plt.gcf().set_size_inches(10, 6)
    plt.tight_layout()
    f10.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=15.5, ncol = 4, loc=(0.1,1.05), fancybox=True)

    plt.show()
    fig10.savefig(figures_path+"\\All_V_OARs_evaluation.png", format='png', dpi=1200, bbox_inches='tight')

if "Catplot_OARs" in figures_to_plot:
    
    ########OAR 1 ###########
    #sns.set(font_scale=1.1)
    g1=sns.catplot(x = 'Plan_name', y="Value (Gy)", col="ClinicalGoal", 
                data=df_oars1,kind="box", height=4, aspect=.7, legend = True)
    g1.set_xticklabels(["","","",""], fontsize = 12)
    g1.map(plt.axhline, y=0, ls='--', color='grey', linewidth=1)
    g1.set_axis_labels(x_var=" ", y_var="Difference respect planning [Gy] \n  ← Lower dose | Higher dose  →", fontsize = 17)
    
    axes = g1.axes.flatten()
    axes[0].set_title("Dmean (Parotid L)", fontsize = 15)
    axes[1].set_title("Dmean (Parotid R)", fontsize = 15)
    axes[2].set_title("Dmean (SMG L)", fontsize = 15)
    axes[3].set_title("Dmean (SMG R)", fontsize = 15)
    
    plt.tight_layout()
    plt.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=15, ncol = 4, loc=(-2.35,1.2), fancybox=True)
    plt.show()
    
    g1.savefig(figures_path+"\\OAR1_catplot.png", format='png', dpi=1200, bbox_inches='tight')
    
    ########OAR 2 ########### 
    sns.set(font_scale=1.1)
    g2=sns.catplot(x="Plan_name", y="Value (Gy)", col="ClinicalGoal",
                data=df_oars2,kind="box", height=4, aspect=.7)
    g2.set_xticklabels(["","","",""], fontsize = 12)
    g2.map(plt.axhline, y=0, ls='--', color='grey', linewidth=1)
    g2.set_axis_labels(x_var=" ", y_var="Difference respect planning [Gy] \n  ← Lower dose | Higher dose  →", fontsize = 17)
    
    axes = g2.axes.flatten()
    axes[0].set_title("Dmean (Oral Cavity)", fontsize = 15)
    axes[1].set_title("Dmean (PCM Superior)", fontsize = 15)
    axes[2].set_title("Dmean (PCM Medium)", fontsize = 15)
    axes[3].set_title("Dmean (SMG Inferiour)", fontsize = 15)
        
    plt.tight_layout()
    plt.legend(handles=[blue_patch, orange_patch, green_patch,red_patch], fontsize=15, ncol = 4, loc=(-2.35,1.2), fancybox=True)
    
    plt.show()
    g2.savefig(figures_path+"\\OAR2_catplot.png", format='png', dpi=1200, bbox_inches='tight')

    ########OAR 3 ########### 
    sns.set(font_scale=1.1)
    g3=sns.catplot(x="Plan_name", y="Value (Gy)", col="ClinicalGoal",
                data=df_oars3,kind="box", height=4, aspect=.7)

    g3.set_xticklabels(["","","",""], fontsize = 12)
    g3.map(plt.axhline, y=0, ls='--', color='grey', linewidth=1)
    g3.set_axis_labels(x_var="", y_var="Difference respect planning [Gy] \n  ← Lower dose | Higher dose  →", fontsize = 14)
   
    axes = g3.axes.flatten()
    axes[0].set_title("D0.03cc (Spinal Cord)")
    axes[1].set_title("D0.03cc (Brain Stem)")
    axes[2].set_title("D0.03cc (Body)")
    
    plt.tight_layout()

    plt.show()
    g3.savefig(figures_path+"\\OAR3_catplot.png", format='png', dpi=1200, bbox_inches='tight')


#### DELIVERY ###
my_path_schedules = 'C:\\Elena\\results\\different_ttmt_schedules'
patient_list_schedule = ['ANON6','ANON12','ANON16','ANON29','ANON34','ANON38','ANON43','ANON18','ANON26','ANON37']
models = ['2_Mimick_ClinDose_rr_rois','3_Mimick_DefDose_def_rois','1_RSpred_RSmim_def_rois']

adapt_strategies = ['Best_plan','Last_plan']
print("#### DELIVERY ###")
for adapt_st in adapt_strategies:
    print(adapt_st)
    for patient in patient_list_schedule:
        for model in models:
            pat_model_path = join(join(my_path_schedules, adapt_st),patient+'_delivery_for_'+model+'.xlsx')
            schedule_df =  pd.read_excel(pat_model_path)
            adaptation_rate = sum(schedule_df['Needs_new_plan'])
            
            print(patient, model, adaptation_rate)
"""     
############# Metrics analysis #####################
####### CTV 7000 ######
ctv7000_val =  df_ctv[df_ctv['ClinicalGoal'] == 'CTVp_7000_D98']
print("############ STATS CTV7000 ############")
for model in model_list:
    ctv7000_val_temp = ctv7000_val[ctv7000_val['Plan_name'] == model]
    min_ctv7000 = min(ctv7000_val_temp['Abs_value'])
    median_ctv7000 = statistics.median(ctv7000_val_temp['Abs_value'])
    max_ctv7000 = max(ctv7000_val_temp['Abs_value'])
    median_ctv7000 = statistics.median(ctv7000_val_temp['Abs_value'])
    print(model, 'Min: ', min_ctv7000, 'Max: ', max_ctv7000,', median: ', median_ctv7000)
    print(model, 'Min: ', min_ctv7000*100/7000, 'Max: ', max_ctv7000*100/7000,', median: ', median_ctv7000*100/7000)
    fail_cases = ctv7000_val_temp.apply(lambda x: x['Abs_value'] < 6650, axis=1).sum()
    print(model, 'Abs failure: ', fail_cases, '% failure: ', fail_cases*100/20,'%')

for model in model_list:
    ctv7000_val_temp = ctv7000_val[ctv7000_val['Plan_name'] == model]
    min_ctv7000 = min(ctv7000_val_temp['Value (Gy)'])
    median_ctv7000 = statistics.median(ctv7000_val_temp['Value (Gy)'])
    iqr_ctv7000 = stats.iqr(ctv7000_val_temp['Value (Gy)'])
    print(model, ' DELTA Min abs value CTVp  7000: ', min_ctv7000, ', DELTA median: ', median_ctv7000, ',  DELTA iqr: ', iqr_ctv7000)

####### CTV 5425 ######
ctv5425_val =  df_ctv[df_ctv['ClinicalGoal'] == 'CTV_5425_D98']
print("############ STATS CTV5425 ############")
for model in model_list:
    ctv5425_val_temp = ctv5425_val[ctv5425_val['Plan_name'] == model]
    min_ctv5425 = min(ctv5425_val_temp['Abs_value'])
    median_ctv5425 = statistics.median(ctv5425_val_temp['Abs_value'])
    max_ctv5425 = max(ctv5425_val_temp['Abs_value'])
    median_ctv5425 = statistics.median(ctv5425_val_temp['Abs_value'])
    print(model, 'Min: ', min_ctv5425, 'Max: ', max_ctv5425, ', median: ', median_ctv5425)
    print(model, 'Min: ', min_ctv5425*100/5425, 'Max: ', max_ctv5425*100/542, ', median: ', median_ctv5425*100/542)
    fail_cases = ctv5425_val_temp.apply(lambda x: x['Abs_value'] < 5150, axis=1).sum()
    print(model, 'Abs failure: ', fail_cases, '% failure: ', fail_cases*100/10,'%')

for model in model_list:
    ctv5425_val_temp = ctv5425_val[ctv5425_val['Plan_name'] == model]
    min_ctv5425 = min(ctv5425_val_temp['Value (Gy)'])
    median_ctv5425 = statistics.median(ctv5425_val_temp['Value (Gy)'])
    iqr_ctv5425 = stats.iqr(ctv5425_val_temp['Value (Gy)'])
    print(model, ' DELTA Min abs value CTVp  5425: ', min_ctv5425, ', DELTA median: ', median_ctv5425, ',  DELTA iqr: ', iqr_ctv5425)

################ Statistical significance analysis ############

######  STATISTICAL SIGNIFICANCE RESPECTO TO PLANNING values ########
print("######  STATISTICAL SIGNIFICANCE RESPECTO TO PLANNING values ########")
ctv_list = ["CTVp_7000_D98", "CTV_5425_D98"]
ntcp_list = ['xero_grade2','xero_grade3','dysf_grade2','dysf_grade3']

df_stats_ctv = pd.DataFrame(index=range(0,len(ctv_list)*len(model_list),1),columns=['CTV_stat','Plan_name','p-value','Is stat sig'])
df_stats_oar = pd.DataFrame(index=range(0,len(oar_list4)*len(model_list),1),columns=['OAR_stat','Plan_name','p-value','Is stat sig'])
df_stats_ntcp = pd.DataFrame(index=range(0,len(ntcp_list)*len(model_list),1),columns=['NTCP_stat','Plan_name','p-value','Is stat sig'])

i=0
for ctv_stat in ctv_list:
    df_ctv_temp = df_ctv[df_ctv['ClinicalGoal'] == ctv_stat]
    df_ctv_planning_temp = all_pat_df_planning[all_pat_df_planning['ClinicalGoal'] == ctv_stat]
    for model in model_list:  
        df_ctv_temp_model = df_ctv_temp[df_ctv_temp['Plan_name'] == model]
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
        df_oar_temp_model = df_oar_temp[df_oar_temp['Plan_name'] == model]
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

i=0
for ntcp_stat in ntcp_list:
    df_ntcp_temp = df_ntcp[df_ntcp['ClinicalGoal'] == ntcp_stat]
    df_ntcp_planning_temp = all_pat_df_planning[all_pat_df_planning['ClinicalGoal'] == ntcp_stat]
    for model in model_list:  
        df_ntcp_temp_model = df_ntcp_temp[df_ntcp_temp['Plan_name'] == model]
        p_value = stats.wilcoxon(df_ntcp_planning_temp['Abs_value'],  df_ntcp_temp_model['Abs_value']).pvalue
        df_stats_ntcp['NTCP_stat'][i] = ntcp_stat
        df_stats_ntcp['Plan_name'][i] = model
        df_stats_ntcp['p-value'][i]  = p_value
        if p_value<0.05:
            df_stats_ntcp['Is stat sig'][i] = 'Yes'  
        elif p_value >= 0.05:
            df_stats_ntcp['Is stat sig'][i] = 'No'  

        i=i+1

print(df_stats_ntcp)

######  STATISTICAL SIGNIFICANCE BETWEEN STRATEGIES ########
print("######  STATISTICAL SIGNIFICANCE BETWEEN STRATEGIES ########")
# 1 '0_NA' - '2_MimCl" = 0_NA vs 2_MimCl
# 2 '0_NA' - '3_MimDef' = 0_NA vs 3_MimDef
# 3 '0_NA' - '1_Auto' = 0_NA vs 1_Auto
# 4 '2_MimCl' -  '3_MimDef' = 2_MimCl vs 3_MimDef
# 5 '2_MimCl' - '1_Auto' = 2_MimCl vs 1_Auto
# 6 '3_MimDef' - '1_Auto' = 3_MimDef vs 1_Auto

scenarios = [{"name":"sc1:NA-DR","plan_1": "0_NoAdapt", "plan_2": "2_Mimick_ClinDose_rr_rois"},
            { "name":"sc2:NA-Def", "plan_1": "0_NoAdapt", "plan_2": "3_Mimick_DefDose_def_rois"},
            { "name":"sc3:NA-Auto","plan_1": "0_NoAdapt", "plan_2": "1_RSpred_RSmim_def_rois"},
            { "name":"sc4:DR-Def","plan_1": "2_Mimick_ClinDose_rr_rois", "plan_2": "3_Mimick_DefDose_def_rois"},
            { "name":"sc5:DR-Auto","plan_1": "2_Mimick_ClinDose_rr_rois", "plan_2": "1_RSpred_RSmim_def_rois"},
            { "name":"sc6:Def-Auto","plan_1": "3_Mimick_DefDose_def_rois", "plan_2": "1_RSpred_RSmim_def_rois"},
            ]


df_stats_ctv_relative = pd.DataFrame(index=range(0,len(ctv_list)*len(scenarios),1),columns=['CTV_stat','Scenario_name','p-value','Is stat sig'])
i=0
for ctv_stat in ctv_list:
    df_ctv_scenarios = df_ctv[df_ctv['ClinicalGoal'] == ctv_stat]
    
    for scenario in scenarios:  
        df_ctv_temp_sc1 = df_ctv_scenarios[df_ctv_scenarios['Plan_name'] == scenario['plan_1']]
        df_ctv_temp_sc2 = df_ctv_scenarios[df_ctv_scenarios['Plan_name'] == scenario['plan_2']]
        
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
        df_oar_temp_sc1 = df_oar_scenarios[df_oar_scenarios['Plan_name'] == scenario['plan_1']]
        df_oar_temp_sc2 = df_oar_scenarios[df_oar_scenarios['Plan_name'] == scenario['plan_2']]
        
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

df_stats_ntcp_relative = pd.DataFrame(index=range(0,len(ntcp_list)*len(scenarios),1),columns=['NTCP_stat','Scenario_name','p-value','Is stat sig'])
i=0
for ntcp_stat in ntcp_list:
    df_ntcp_scenarios = df_ntcp[df_ntcp['ClinicalGoal'] == ntcp_stat]
    for scenario in scenarios:  
        df_ntcp_temp_sc1 = df_ntcp_scenarios[df_ntcp_scenarios['Plan_name'] == scenario['plan_1']]
        df_ntcp_temp_sc2 = df_ntcp_scenarios[df_ntcp_scenarios['Plan_name'] == scenario['plan_2']]
        
        p_value = stats.wilcoxon(df_ntcp_temp_sc1['Abs_value'],  df_ntcp_temp_sc2['Abs_value']).pvalue
        
        df_stats_ntcp_relative['NTCP_stat'][i] = ntcp_stat
        df_stats_ntcp_relative['Scenario_name'][i] = scenario['name']
        df_stats_ntcp_relative['p-value'][i]  = p_value
        if p_value<0.05:
            df_stats_ntcp_relative['Is stat sig'][i] = 'Yes'  
        elif p_value >= 0.05:
            df_stats_ntcp_relative['Is stat sig'][i] = 'No'  

        i=i+1

print(df_stats_ntcp_relative)

""" 
