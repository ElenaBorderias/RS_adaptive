from connect import *
import pandas as pd
import numpy as np

class EvaluationSummedDose:

    def __init__(self,doe_pct,oa_strategy,summed_dose_name):

        self.doe_pct = doe_pct
        self.oa_strategy = oa_strategy
        self.summed_dose_name = summed_dose_name

        self.case = get_current("Case")
        self.patient = get_current("Patient")

        self.baseline = 2
        self.location = 1

        ## DO NOT TOUCH ##

        self.modelparams_definitive_xero_grade2={"beta0": -2.2951, "beta_Parotid":0.0996, "beta_Subm":0.0182, "beta_baseline": [0,0.495,1.207]}
        self.modelparams_definitive_xero_grade3={"beta0": -3.7286, "beta_Parotid":0.0855, "beta_Subm":0.0156, "beta_baseline": [0,0.4249,1.0361]}

        self.modelparams_dysf_definitive_grade2={"beta0": -4.0536, "beta_Coral":0.03, "beta_PCMSup":0.0236, "beta_PCMMed":0.0095, "beta_PCMInf":0.0133, "beta_baseline": [0,0.9382,1.29], "beta_location":[0,-0.6281, -0.7711]}
        self.modelparams_dysf_definitive_grade3={"beta0": -7.6174, "beta_Coral":0.0259, "beta_PCMSup":0.0203, "beta_PCMMed":0.0303, "beta_PCMInf":0.0341, "beta_baseline": [0,0.5738,1.4718], "beta_location":[0,0.0387, -0.5303]}


    def find_dose_evaluation(self):

        for dose_eval in self.doe_pct.DoseEvaluations:
            print(dose_eval.Name)
            if dose_eval.Name == self.summed_dose_name:
                self.dose_evaluation = dose_eval

        return self.dose_evaluation

    def init_data_frame_results(self):
        self.df_results = pd.DataFrame(columns=["Patient", "Plan_name", "ClinicalGoal", "Value"])
    
    def append_clinical_goal_to_df(self,clinical_goal,value):
        self.df_results = self.df_results.append({'Patient' : self.patient.Name, 
                                'Plan_name' : self.oa_strategy, 
                                'ClinicalGoal' : clinical_goal,
                                'Value': value},
                                ignore_index = True)
        #print(self.df_results)
    
    # baseline_score: 0 not at all (EORTC QLQ-H&N35 Q41 score 1), 1 a bit (score 2), 2 moderate-severe (score 3-4)
    def NTCP_definitive_xero_grade2(self,baseline_score, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR):
        beta={}
        beta["Constant"] = self.modelparams_definitive_xero_grade2["beta0"]+self.modelparams_definitive_xero_grade2["beta_baseline"][baseline_score]
        beta["Parotid"] = self.modelparams_definitive_xero_grade2["beta_Parotid"]
        beta["Subm"] = self.modelparams_definitive_xero_grade2["beta_Subm"]

        Dmean_SubmComb=(Dmean_SubmL*Volume_SubmL+Dmean_SubmR*Volume_SubmR)/(Volume_SubmL+Volume_SubmR)
        Dmean_ParComb=np.sqrt(Dmean_ParL) + np.sqrt(Dmean_ParR)
        
        S=beta["Constant"]+beta["Parotid"]*Dmean_ParComb+beta["Subm"]*Dmean_SubmComb
        
        NTCP=1/(1+np.exp(-S))
        
        return NTCP

    # baseline_score: 0 not at all (EORTC QLQ-H&N35 Q41 score 1), 1 a bit (score 2), 2 moderate-severe (score 3-4)
    def NTCP_definitive_xero_grade3(self,baseline_score, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR):
        beta={}
        beta["Constant"] = self.modelparams_definitive_xero_grade3["beta0"]+self.modelparams_definitive_xero_grade3["beta_baseline"][baseline_score]
        beta["Parotid"] = self.modelparams_definitive_xero_grade3["beta_Parotid"]
        beta["Subm"] = self.modelparams_definitive_xero_grade3["beta_Subm"]

        Dmean_SubmComb=(Dmean_SubmL*Volume_SubmL+Dmean_SubmR*Volume_SubmR)/(Volume_SubmL+Volume_SubmR)
        Dmean_ParComb=np.sqrt(Dmean_ParL) + np.sqrt(Dmean_ParR)
        
        S=beta["Constant"]+beta["Parotid"]*Dmean_ParComb+beta["Subm"]*Dmean_SubmComb
        
        NTCP=1/(1+np.exp(-S))
        
        return NTCP

    # baseline_score: 0 grade 0-I, 1 grade II, 2 grade III-IV
    # location: 0 oral cavity, 1 farynx, 2 larynx
    def NTCP_definitive_dysf_grade2(self,baseline_score, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, location):
        beta={}
        beta["Constant"]=self.modelparams_dysf_definitive_grade2["beta0"]+self.modelparams_dysf_definitive_grade2["beta_baseline"][baseline_score]+self.modelparams_dysf_definitive_grade2["beta_location"][location]
        beta["Coral"]=self.modelparams_dysf_definitive_grade2["beta_Coral"]
        beta["PCMSup"]=self.modelparams_dysf_definitive_grade2["beta_PCMSup"]
        beta["PCMMed"]=self.modelparams_dysf_definitive_grade2["beta_PCMMed"]
        beta["PCMInf"]=self.modelparams_dysf_definitive_grade2["beta_PCMInf"]
            
        S=beta["Constant"]+beta["Coral"]*Dmean_Coral+beta["PCMSup"]*Dmean_PCMSup+beta["PCMMed"]*Dmean_PCMMed+beta["PCMInf"]*Dmean_PCMInf
        
        NTCP=1/(1+np.exp(-S))
        
        return NTCP

    # baseline_score: 0 grade 0-I, 1 grade II, 2 grade III-IV
    # location: 0 oral cavity, 1 farynx, 2 larynx
    def NTCP_definitive_dysf_grade3(self,baseline_score, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, location):
        beta={}
        beta["Constant"]=self.modelparams_dysf_definitive_grade3["beta0"]+self.modelparams_dysf_definitive_grade3["beta_baseline"][baseline_score]+self.modelparams_dysf_definitive_grade3["beta_location"][location]
        beta["Coral"]=self.modelparams_dysf_definitive_grade3["beta_Coral"]
        beta["PCMSup"]=self.modelparams_dysf_definitive_grade3["beta_PCMSup"]
        beta["PCMMed"]=self.modelparams_dysf_definitive_grade3["beta_PCMMed"]
        beta["PCMInf"]=self.modelparams_dysf_definitive_grade3["beta_PCMInf"]
            
        S=beta["Constant"]+beta["Coral"]*Dmean_Coral+beta["PCMSup"]*Dmean_PCMSup+beta["PCMMed"]*Dmean_PCMMed+beta["PCMInf"]*Dmean_PCMInf
        
        NTCP=1/(1+np.exp(-S))
        
        return NTCP
        
    def evaluate_dose_statistics(self):

        self.dose_eval = self.find_dose_evaluation()
        self.init_data_frame_results()

        #ctvs
        ctv_high_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_7000", RelativeVolumes=[0.98])),2)
        self.append_clinical_goal_to_df("CTV_7000_D98",ctv_high_D98)

        ctv_high_D2 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_7000", RelativeVolumes=[0.02])),2)
        self.append_clinical_goal_to_df("CTV_7000_D02",ctv_high_D2)

        ctv_p_high_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTVp_7000", RelativeVolumes=[0.98])),2)
        self.append_clinical_goal_to_df("CTVp_7000_D98",ctv_p_high_D98)

        ctv_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_5425", RelativeVolumes=[0.98])),2)
        self.append_clinical_goal_to_df("CTV_5425_D98",ctv_low_D98)

        ctv_low_D02 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_5425", RelativeVolumes=[0.02])),2)

        ctv_nL_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTVnL_5425", RelativeVolumes=[0.98])),2)
        self.append_clinical_goal_to_df("CTVnL_5425_D98",ctv_nL_low_D98)

        ctv_nR_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTVnR_5425", RelativeVolumes=[0.98])),2)
        self.append_clinical_goal_to_df("CTVnR_5425_D98",ctv_nR_low_D98)

        
        #oars dmean
        esophagus_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Esophagus", DoseType="Average")
        self.append_clinical_goal_to_df("Esophagus_Dmean",esophagus_Dmean)

        oral_cavity_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Oral_Cavity", DoseType="Average")
        self.append_clinical_goal_to_df("Oral_Cavity_Dmean",oral_cavity_Dmean)

        parotid_L_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Parotid_L", DoseType="Average")
        self.append_clinical_goal_to_df("Parotid_L_Dmean",parotid_L_Dmean)

        parotid_R_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Parotid_R", DoseType="Average")
        self.append_clinical_goal_to_df("Parotid_R_Dmean",parotid_R_Dmean)

        submand_L_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Submandibular_L", DoseType="Average")
        self.append_clinical_goal_to_df("Submandibular_L_Dmean",submand_L_Dmean)

        submand_R_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Submandibular_R", DoseType="Average")
        self.append_clinical_goal_to_df("Submandibular_R_Dmean",submand_R_Dmean)

        pcm_sup_Dmean = self.dose_eval.GetDoseStatistic(RoiName="PharConsSup", DoseType="Average")
        self.append_clinical_goal_to_df("PharConsSup_Dmean",pcm_sup_Dmean)

        pcm_mid_Dmean = self.dose_eval.GetDoseStatistic(RoiName="PharConsMid", DoseType="Average")
        self.append_clinical_goal_to_df("PharConsMid_Dmean",pcm_mid_Dmean)

        pcm_inf_Dmean = self.dose_eval.GetDoseStatistic(RoiName="PharConsInf", DoseType="Average")
        self.append_clinical_goal_to_df("PharConsInf_Dmean",pcm_inf_Dmean)

        #oars absolute volume
        abs_vol_spinalcord = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["SpinalCord"].GetRoiVolume()
        rel_vol_spinalcord = float((0.03*100)/abs_vol_spinalcord)
    
        abs_vol_brainstem = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["Brainstem"].GetRoiVolume()
        rel_vol_brainstem = float((0.03*100)/abs_vol_brainstem)

        abs_vol_body = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["BODY"].GetRoiVolume()
        rel_vol_body = float((0.03*100)/abs_vol_body)

        spinal_cord_D0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "SpinalCord", RelativeVolumes = [rel_vol_spinalcord/100])),2)
        self.append_clinical_goal_to_df("SpinalCord_D0_03cc",spinal_cord_D0_03)

        brainstem_D_0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "Brainstem", RelativeVolumes = [rel_vol_brainstem/100])),2)
        self.append_clinical_goal_to_df("Brainstem_D0_03cc",brainstem_D_0_03)

        body_D_0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "BODY", RelativeVolumes = [rel_vol_body/100])),2)
        self.append_clinical_goal_to_df("BODY_D0_03cc",body_D_0_03)

        #HI
        HI_CTV_7000 = round((ctv_high_D2 - ctv_high_D98)/7000,2)
        self.append_clinical_goal_to_df("HI_CTV_7000",HI_CTV_7000)

        HI_CTV_5425 = round((ctv_low_D02 - ctv_low_D98)/5425,2)
        self.append_clinical_goal_to_df("HI_CTVn_5425",HI_CTV_5425)

        #NTCP
        Volume_SubmL = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["Submandibular_L"].GetRoiVolume()
        Volume_SubmR = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["Submandibular_R"].GetRoiVolume()
        Dmean_ParL = parotid_L_Dmean*0.01
        Dmean_ParR = parotid_R_Dmean*0.01
        Dmean_SubmL = submand_L_Dmean*0.01
        Dmean_SubmR = submand_R_Dmean*0.01
        Dmean_Coral = oral_cavity_Dmean*0.01
        Dmean_PCMSup = pcm_sup_Dmean*0.01
        Dmean_PCMMed = pcm_mid_Dmean*0.01
        Dmean_PCMInf = pcm_inf_Dmean*0.01

        xero_grade2 = self.NTCP_definitive_xero_grade2(self.baseline, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR)
        xero_grade3 = self.NTCP_definitive_xero_grade3(self.baseline, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR)
        dysf_grade2 = self.NTCP_definitive_dysf_grade2(self.baseline, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, self.location)
        dysf_grade3 = self.NTCP_definitive_dysf_grade3(self.baseline, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, self.location)

        self.append_clinical_goal_to_df("xero_grade2",xero_grade2)
        self.append_clinical_goal_to_df("xero_grade3",xero_grade3)
        self.append_clinical_goal_to_df("dysf_grade2",dysf_grade2)
        self.append_clinical_goal_to_df("dysf_grade3",dysf_grade3)

        print(self.df_results)

        return self.df_results

class EvaluationPlanningDose:
        def __init__(self,plan_name):

            self.case = get_current("Case")
            self.patient = get_current("Patient")

            self.plan_name = plan_name
            self.dose_eval = self.case.TreatmentPlans[self.plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose

            self.baseline = 2
            self.location = 1

            ## DO NOT TOUCH ##

            self.modelparams_definitive_xero_grade2={"beta0": -2.2951, "beta_Parotid":0.0996, "beta_Subm":0.0182, "beta_baseline": [0,0.495,1.207]}
            self.modelparams_definitive_xero_grade3={"beta0": -3.7286, "beta_Parotid":0.0855, "beta_Subm":0.0156, "beta_baseline": [0,0.4249,1.0361]}

            self.modelparams_dysf_definitive_grade2={"beta0": -4.0536, "beta_Coral":0.03, "beta_PCMSup":0.0236, "beta_PCMMed":0.0095, "beta_PCMInf":0.0133, "beta_baseline": [0,0.9382,1.29], "beta_location":[0,-0.6281, -0.7711]}
            self.modelparams_dysf_definitive_grade3={"beta0": -7.6174, "beta_Coral":0.0259, "beta_PCMSup":0.0203, "beta_PCMMed":0.0303, "beta_PCMInf":0.0341, "beta_baseline": [0,0.5738,1.4718], "beta_location":[0,0.0387, -0.5303]}

        def append_clinical_goal_to_df(self,clinical_goal,value):
            self.df_results = self.df_results.append({'Patient' : self.patient.Name, 
                                'Plan_name' : self.plan_name, 
                                'ClinicalGoal' : clinical_goal,
                                'Value': value},
                                ignore_index = True)
        
        def init_data_frame_results(self):
            self.df_results = pd.DataFrame(columns=["Patient", "Plan_name", "ClinicalGoal", "Value"])

        # baseline_score: 0 not at all (EORTC QLQ-H&N35 Q41 score 1), 1 a bit (score 2), 2 moderate-severe (score 3-4)
        def NTCP_definitive_xero_grade2(self,baseline_score, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR):
            beta={}
            beta["Constant"] = self.modelparams_definitive_xero_grade2["beta0"]+self.modelparams_definitive_xero_grade2["beta_baseline"][baseline_score]
            beta["Parotid"] = self.modelparams_definitive_xero_grade2["beta_Parotid"]
            beta["Subm"] = self.modelparams_definitive_xero_grade2["beta_Subm"]

            Dmean_SubmComb=(Dmean_SubmL*Volume_SubmL+Dmean_SubmR*Volume_SubmR)/(Volume_SubmL+Volume_SubmR)
            Dmean_ParComb=np.sqrt(Dmean_ParL) + np.sqrt(Dmean_ParR)
            
            S=beta["Constant"]+beta["Parotid"]*Dmean_ParComb+beta["Subm"]*Dmean_SubmComb
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP

        # baseline_score: 0 not at all (EORTC QLQ-H&N35 Q41 score 1), 1 a bit (score 2), 2 moderate-severe (score 3-4)
        def NTCP_definitive_xero_grade3(self,baseline_score, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR):
            beta={}
            beta["Constant"] = self.modelparams_definitive_xero_grade3["beta0"]+self.modelparams_definitive_xero_grade3["beta_baseline"][baseline_score]
            beta["Parotid"] = self.modelparams_definitive_xero_grade3["beta_Parotid"]
            beta["Subm"] = self.modelparams_definitive_xero_grade3["beta_Subm"]

            Dmean_SubmComb=(Dmean_SubmL*Volume_SubmL+Dmean_SubmR*Volume_SubmR)/(Volume_SubmL+Volume_SubmR)
            Dmean_ParComb=np.sqrt(Dmean_ParL) + np.sqrt(Dmean_ParR)
            
            S=beta["Constant"]+beta["Parotid"]*Dmean_ParComb+beta["Subm"]*Dmean_SubmComb
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP

        # baseline_score: 0 grade 0-I, 1 grade II, 2 grade III-IV
        # location: 0 oral cavity, 1 farynx, 2 larynx
        def NTCP_definitive_dysf_grade2(self,baseline_score, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, location):
            beta={}
            beta["Constant"]=self.modelparams_dysf_definitive_grade2["beta0"]+self.modelparams_dysf_definitive_grade2["beta_baseline"][baseline_score]+self.modelparams_dysf_definitive_grade2["beta_location"][location]
            beta["Coral"]=self.modelparams_dysf_definitive_grade2["beta_Coral"]
            beta["PCMSup"]=self.modelparams_dysf_definitive_grade2["beta_PCMSup"]
            beta["PCMMed"]=self.modelparams_dysf_definitive_grade2["beta_PCMMed"]
            beta["PCMInf"]=self.modelparams_dysf_definitive_grade2["beta_PCMInf"]
                
            S=beta["Constant"]+beta["Coral"]*Dmean_Coral+beta["PCMSup"]*Dmean_PCMSup+beta["PCMMed"]*Dmean_PCMMed+beta["PCMInf"]*Dmean_PCMInf
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP

        # baseline_score: 0 grade 0-I, 1 grade II, 2 grade III-IV
        # location: 0 oral cavity, 1 farynx, 2 larynx
        def NTCP_definitive_dysf_grade3(self,baseline_score, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, location):
            beta={}
            beta["Constant"]=self.modelparams_dysf_definitive_grade3["beta0"]+self.modelparams_dysf_definitive_grade3["beta_baseline"][baseline_score]+self.modelparams_dysf_definitive_grade3["beta_location"][location]
            beta["Coral"]=self.modelparams_dysf_definitive_grade3["beta_Coral"]
            beta["PCMSup"]=self.modelparams_dysf_definitive_grade3["beta_PCMSup"]
            beta["PCMMed"]=self.modelparams_dysf_definitive_grade3["beta_PCMMed"]
            beta["PCMInf"]=self.modelparams_dysf_definitive_grade3["beta_PCMInf"]
                
            S=beta["Constant"]+beta["Coral"]*Dmean_Coral+beta["PCMSup"]*Dmean_PCMSup+beta["PCMMed"]*Dmean_PCMMed+beta["PCMInf"]*Dmean_PCMInf
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP
        
        def evaluate_dose_statistics(self):

            self.init_data_frame_results()

            #ctvs
            ctv_high_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_7000", RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTV_7000_D98",ctv_high_D98)

            ctv_high_D2 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_7000", RelativeVolumes=[0.02])),2)
            self.append_clinical_goal_to_df("CTV_7000_D02",ctv_high_D2)

            ctv_p_high_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTVp_7000", RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTVp_7000_D98",ctv_p_high_D98)

            ctv_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_5425", RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTV_5425_D98",ctv_low_D98)

            ctv_low_D02 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_5425", RelativeVolumes=[0.02])),2)

            ctv_nL_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTVnL_5425", RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTVnL_5425_D98",ctv_nL_low_D98)

            ctv_nR_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTVnR_5425", RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTVnR_5425_D98",ctv_nR_low_D98)

            
            #oars dmean
            esophagus_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Esophagus", DoseType="Average")
            self.append_clinical_goal_to_df("Esophagus_Dmean",esophagus_Dmean)

            oral_cavity_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Oral_Cavity", DoseType="Average")
            self.append_clinical_goal_to_df("Oral_Cavity_Dmean",oral_cavity_Dmean)

            parotid_L_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Parotid_L", DoseType="Average")
            self.append_clinical_goal_to_df("Parotid_L_Dmean",parotid_L_Dmean)

            parotid_R_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Parotid_R", DoseType="Average")
            self.append_clinical_goal_to_df("Parotid_R_Dmean",parotid_R_Dmean)

            submand_L_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Submandibular_L", DoseType="Average")
            self.append_clinical_goal_to_df("Submandibular_L_Dmean",submand_L_Dmean)

            submand_R_Dmean = self.dose_eval.GetDoseStatistic(RoiName="Submandibular_R", DoseType="Average")
            self.append_clinical_goal_to_df("Submandibular_R_Dmean",submand_R_Dmean)

            pcm_sup_Dmean = self.dose_eval.GetDoseStatistic(RoiName="PharConsSup", DoseType="Average")
            self.append_clinical_goal_to_df("PharConsSup_Dmean",pcm_sup_Dmean)

            pcm_mid_Dmean = self.dose_eval.GetDoseStatistic(RoiName="PharConsMid", DoseType="Average")
            self.append_clinical_goal_to_df("PharConsMid_Dmean",pcm_mid_Dmean)

            pcm_inf_Dmean = self.dose_eval.GetDoseStatistic(RoiName="PharConsInf", DoseType="Average")
            self.append_clinical_goal_to_df("PharConsInf_Dmean",pcm_inf_Dmean)

            #oars absolute volume
            abs_vol_spinalcord = self.case.PatientModel.StructureSets[0].RoiGeometries["SpinalCord"].GetRoiVolume()
            rel_vol_spinalcord = float((0.03*100)/abs_vol_spinalcord)
        
            abs_vol_brainstem = self.case.PatientModel.StructureSets[0].RoiGeometries["Brainstem"].GetRoiVolume()
            rel_vol_brainstem = float((0.03*100)/abs_vol_brainstem)

            abs_vol_body = self.case.PatientModel.StructureSets[0].RoiGeometries["BODY"].GetRoiVolume()
            rel_vol_body = float((0.03*100)/abs_vol_body)

            spinal_cord_D0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "SpinalCord", RelativeVolumes = [rel_vol_spinalcord/100])),2)
            self.append_clinical_goal_to_df("SpinalCord_D0_03cc",spinal_cord_D0_03)

            brainstem_D_0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "Brainstem", RelativeVolumes = [rel_vol_brainstem/100])),2)
            self.append_clinical_goal_to_df("Brainstem_D0_03cc",brainstem_D_0_03)

            body_D_0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "BODY", RelativeVolumes = [rel_vol_body/100])),2)
            self.append_clinical_goal_to_df("BODY_D0_03cc",body_D_0_03)

            #HI
            HI_CTV_7000 = round((ctv_high_D2 - ctv_high_D98)/7000,2)
            self.append_clinical_goal_to_df("HI_CTV_7000",HI_CTV_7000)

            HI_CTV_5425 = round((ctv_low_D02 - ctv_low_D98)/5425,2)
            self.append_clinical_goal_to_df("HI_CTVn_5425",HI_CTV_5425)


            #NTCP
            Volume_SubmL = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["Submandibular_L"].GetRoiVolume()
            Volume_SubmR = self.case.PatientModel.StructureSets['pCT'].RoiGeometries["Submandibular_R"].GetRoiVolume()
            Dmean_ParL = parotid_L_Dmean*0.01
            Dmean_ParR = parotid_R_Dmean*0.01
            Dmean_SubmL = submand_L_Dmean*0.01
            Dmean_SubmR = submand_R_Dmean*0.01
            Dmean_Coral = oral_cavity_Dmean*0.01
            Dmean_PCMSup = pcm_sup_Dmean*0.01
            Dmean_PCMMed = pcm_mid_Dmean*0.01
            Dmean_PCMInf = pcm_inf_Dmean*0.01

            xero_grade2 = self.NTCP_definitive_xero_grade2(self.baseline, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR)
            xero_grade3 = self.NTCP_definitive_xero_grade3(self.baseline, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR)
            dysf_grade2 = self.NTCP_definitive_dysf_grade2(self.baseline, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, self.location)
            dysf_grade3 = self.NTCP_definitive_dysf_grade3(self.baseline, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, self.location)

            self.append_clinical_goal_to_df("xero_grade2",xero_grade2)
            self.append_clinical_goal_to_df("xero_grade3",xero_grade3)
            self.append_clinical_goal_to_df("dysf_grade2",dysf_grade2)
            self.append_clinical_goal_to_df("dysf_grade3",dysf_grade3)

            print(self.df_results)

            return self.df_results


class EvaluationPlanningDose_real_contours:

        def __init__(self,plan_name,ct_name, ct_index,real_contours):

            self.case = get_current("Case")
            self.patient = get_current("Patient")

            self.plan_name = plan_name
            self.strategy = plan_name[:-8]
            self.ct_name = ct_name
            self.ct_index = ct_index
            self.real_contours = real_contours

            
            if self.plan_name.startswith('0'):
                for doe in self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
                    if doe.OnExamination.Name == ct_name:
                        self.dose_eval = doe.DoseEvaluations[0]
            else:
                self.dose_eval = self.case.TreatmentPlans[self.plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose

            self.baseline = 2
            self.location = 1

            ## DO NOT TOUCH ##

            self.modelparams_definitive_xero_grade2={"beta0": -2.2951, "beta_Parotid":0.0996, "beta_Subm":0.0182, "beta_baseline": [0,0.495,1.207]}
            self.modelparams_definitive_xero_grade3={"beta0": -3.7286, "beta_Parotid":0.0855, "beta_Subm":0.0156, "beta_baseline": [0,0.4249,1.0361]}

            self.modelparams_dysf_definitive_grade2={"beta0": -4.0536, "beta_Coral":0.03, "beta_PCMSup":0.0236, "beta_PCMMed":0.0095, "beta_PCMInf":0.0133, "beta_baseline": [0,0.9382,1.29], "beta_location":[0,-0.6281, -0.7711]}
            self.modelparams_dysf_definitive_grade3={"beta0": -7.6174, "beta_Coral":0.0259, "beta_PCMSup":0.0203, "beta_PCMMed":0.0303, "beta_PCMInf":0.0341, "beta_baseline": [0,0.5738,1.4718], "beta_location":[0,0.0387, -0.5303]}

        def append_clinical_goal_to_df(self,clinical_goal,value):
            ntcp_list = ['xero_grade2','xero_grade3','dysf_grade2','dysf_grade3']
            if self.plan_name.startswith('0') and clinical_goal not in ntcp_list:
                value = value*35
            self.df_results = self.df_results.append({'Patient' : self.patient.Name, 
                                'Strategy': self.strategy,
                                'Adapt_image': self.ct_name,
                                'Plan_name' : self.plan_name, 
                                'ClinicalGoal' : clinical_goal,
                                'Value': value},
                                ignore_index = True)
        
        def init_data_frame_results(self):
            self.df_results = pd.DataFrame(columns=["Patient", "Strategy", "Adapt_image", "ClinicalGoal", "Value"])

        # baseline_score: 0 not at all (EORTC QLQ-H&N35 Q41 score 1), 1 a bit (score 2), 2 moderate-severe (score 3-4)
        def NTCP_definitive_xero_grade2(self,baseline_score, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR):
            beta={}
            beta["Constant"] = self.modelparams_definitive_xero_grade2["beta0"]+self.modelparams_definitive_xero_grade2["beta_baseline"][baseline_score]
            beta["Parotid"] = self.modelparams_definitive_xero_grade2["beta_Parotid"]
            beta["Subm"] = self.modelparams_definitive_xero_grade2["beta_Subm"]

            Dmean_SubmComb=(Dmean_SubmL*Volume_SubmL+Dmean_SubmR*Volume_SubmR)/(Volume_SubmL+Volume_SubmR)
            Dmean_ParComb=np.sqrt(Dmean_ParL) + np.sqrt(Dmean_ParR)
            
            S=beta["Constant"]+beta["Parotid"]*Dmean_ParComb+beta["Subm"]*Dmean_SubmComb
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP

        # baseline_score: 0 not at all (EORTC QLQ-H&N35 Q41 score 1), 1 a bit (score 2), 2 moderate-severe (score 3-4)
        def NTCP_definitive_xero_grade3(self,baseline_score, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR):
            beta={}
            beta["Constant"] = self.modelparams_definitive_xero_grade3["beta0"]+self.modelparams_definitive_xero_grade3["beta_baseline"][baseline_score]
            beta["Parotid"] = self.modelparams_definitive_xero_grade3["beta_Parotid"]
            beta["Subm"] = self.modelparams_definitive_xero_grade3["beta_Subm"]

            Dmean_SubmComb=(Dmean_SubmL*Volume_SubmL+Dmean_SubmR*Volume_SubmR)/(Volume_SubmL+Volume_SubmR)
            Dmean_ParComb=np.sqrt(Dmean_ParL) + np.sqrt(Dmean_ParR)
            
            S=beta["Constant"]+beta["Parotid"]*Dmean_ParComb+beta["Subm"]*Dmean_SubmComb
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP

        # baseline_score: 0 grade 0-I, 1 grade II, 2 grade III-IV
        # location: 0 oral cavity, 1 farynx, 2 larynx
        def NTCP_definitive_dysf_grade2(self,baseline_score, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, location):
            beta={}
            beta["Constant"]=self.modelparams_dysf_definitive_grade2["beta0"]+self.modelparams_dysf_definitive_grade2["beta_baseline"][baseline_score]+self.modelparams_dysf_definitive_grade2["beta_location"][location]
            beta["Coral"]=self.modelparams_dysf_definitive_grade2["beta_Coral"]
            beta["PCMSup"]=self.modelparams_dysf_definitive_grade2["beta_PCMSup"]
            beta["PCMMed"]=self.modelparams_dysf_definitive_grade2["beta_PCMMed"]
            beta["PCMInf"]=self.modelparams_dysf_definitive_grade2["beta_PCMInf"]
                
            S=beta["Constant"]+beta["Coral"]*Dmean_Coral+beta["PCMSup"]*Dmean_PCMSup+beta["PCMMed"]*Dmean_PCMMed+beta["PCMInf"]*Dmean_PCMInf
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP

        # baseline_score: 0 grade 0-I, 1 grade II, 2 grade III-IV
        # location: 0 oral cavity, 1 farynx, 2 larynx
        def NTCP_definitive_dysf_grade3(self,baseline_score, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, location):
            beta={}
            beta["Constant"]=self.modelparams_dysf_definitive_grade3["beta0"]+self.modelparams_dysf_definitive_grade3["beta_baseline"][baseline_score]+self.modelparams_dysf_definitive_grade3["beta_location"][location]
            beta["Coral"]=self.modelparams_dysf_definitive_grade3["beta_Coral"]
            beta["PCMSup"]=self.modelparams_dysf_definitive_grade3["beta_PCMSup"]
            beta["PCMMed"]=self.modelparams_dysf_definitive_grade3["beta_PCMMed"]
            beta["PCMInf"]=self.modelparams_dysf_definitive_grade3["beta_PCMInf"]
                
            S=beta["Constant"]+beta["Coral"]*Dmean_Coral+beta["PCMSup"]*Dmean_PCMSup+beta["PCMMed"]*Dmean_PCMMed+beta["PCMInf"]*Dmean_PCMInf
            
            NTCP=1/(1+np.exp(-S))
            
            return NTCP
        
        def get_correspondant_roi_name(self,ref_roi):
            if self.real_contours == 1:
                if self.ct_index == 1:
                    new_roi_name = 'eval_' + ref_roi + ' (1)'
                if self.ct_index == 2:
                    new_roi_name = 'eval_' + ref_roi + ' (2)'
            else:
                new_roi_name = ref_roi
            
            return new_roi_name

        
        def evaluate_dose_statistics(self):

            self.init_data_frame_results()

            #ctvs
            
            ctv_high_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTV_7000"), RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTV_7000_D98",ctv_high_D98)

            ctv_high_D2 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTV_7000"), RelativeVolumes=[0.02])),2)
            self.append_clinical_goal_to_df("CTV_7000_D02",ctv_high_D2)

            ctv_p_high_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTVp_7000"), RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTVp_7000_D98",ctv_p_high_D98)

            ctv_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTV_5425"), RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTV_5425_D98",ctv_low_D98)

            ctv_low_D02 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTV_5425"), RelativeVolumes=[0.02])),2)

            ctv_nL_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTVnL_5425"), RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTVnL_5425_D98",ctv_nL_low_D98)

            ctv_nR_low_D98 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName=self.get_correspondant_roi_name("CTVnR_5425"), RelativeVolumes=[0.98])),2)
            self.append_clinical_goal_to_df("CTVnR_5425_D98",ctv_nR_low_D98)

            
            #oars dmean
            esophagus_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("Esophagus"), DoseType="Average")
            self.append_clinical_goal_to_df("Esophagus_Dmean",esophagus_Dmean)

            oral_cavity_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("Oral_Cavity"), DoseType="Average")
            self.append_clinical_goal_to_df("Oral_Cavity_Dmean",oral_cavity_Dmean)

            parotid_L_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("Parotid_L"), DoseType="Average")
            self.append_clinical_goal_to_df("Parotid_L_Dmean",parotid_L_Dmean)

            parotid_R_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("Parotid_R"), DoseType="Average")
            self.append_clinical_goal_to_df("Parotid_R_Dmean",parotid_R_Dmean)

            submand_L_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("Submandibular_L"), DoseType="Average")
            self.append_clinical_goal_to_df("Submandibular_L_Dmean",submand_L_Dmean)

            submand_R_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("Submandibular_R"), DoseType="Average")
            self.append_clinical_goal_to_df("Submandibular_R_Dmean",submand_R_Dmean)

            pcm_sup_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("PharConsSup"), DoseType="Average")
            self.append_clinical_goal_to_df("PharConsSup_Dmean",pcm_sup_Dmean)

            pcm_mid_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("PharConsMid"), DoseType="Average")
            self.append_clinical_goal_to_df("PharConsMid_Dmean",pcm_mid_Dmean)

            pcm_inf_Dmean = self.dose_eval.GetDoseStatistic(RoiName=self.get_correspondant_roi_name("PharConsInf"), DoseType="Average")
            self.append_clinical_goal_to_df("PharConsInf_Dmean",pcm_inf_Dmean)

            #oars absolute volume
            abs_vol_spinalcord = self.case.PatientModel.StructureSets[self.ct_name].RoiGeometries[self.get_correspondant_roi_name("SpinalCord")].GetRoiVolume()
            rel_vol_spinalcord = float((0.03*100)/abs_vol_spinalcord)
        
            abs_vol_brainstem = self.case.PatientModel.StructureSets[self.ct_name].RoiGeometries[self.get_correspondant_roi_name("Brainstem")].GetRoiVolume()
            rel_vol_brainstem = float((0.03*100)/abs_vol_brainstem)

            abs_vol_body = self.case.PatientModel.StructureSets[self.ct_name].RoiGeometries["BODY"].GetRoiVolume()
            rel_vol_body = float((0.03*100)/abs_vol_body)

            spinal_cord_D0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= self.get_correspondant_roi_name("SpinalCord"), RelativeVolumes = [rel_vol_spinalcord/100])),2)
            self.append_clinical_goal_to_df("SpinalCord_D0_03cc",spinal_cord_D0_03)

            brainstem_D_0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= self.get_correspondant_roi_name("Brainstem"), RelativeVolumes = [rel_vol_brainstem/100])),2)
            self.append_clinical_goal_to_df("Brainstem_D0_03cc",brainstem_D_0_03)

            body_D_0_03 = round(float(self.dose_eval.GetDoseAtRelativeVolumes(RoiName= "BODY", RelativeVolumes = [rel_vol_body/100])),2)
            self.append_clinical_goal_to_df("BODY_D0_03cc",body_D_0_03)

            #HI
            HI_CTV_7000 = round((ctv_high_D2 - ctv_high_D98)/7000,2)
            self.append_clinical_goal_to_df("HI_CTV_7000",HI_CTV_7000)

            HI_CTV_5425 = round((ctv_low_D02 - ctv_low_D98)/5425,2)
            self.append_clinical_goal_to_df("HI_CTVn_5425",HI_CTV_5425)


            #NTCP
            Volume_SubmL = self.case.PatientModel.StructureSets[self.ct_name].RoiGeometries[self.get_correspondant_roi_name("Submandibular_L")].GetRoiVolume()
            Volume_SubmR = self.case.PatientModel.StructureSets[self.ct_name].RoiGeometries[self.get_correspondant_roi_name("Submandibular_R")].GetRoiVolume()
            Dmean_ParL = parotid_L_Dmean*0.01
            Dmean_ParR = parotid_R_Dmean*0.01
            Dmean_SubmL = submand_L_Dmean*0.01
            Dmean_SubmR = submand_R_Dmean*0.01
            Dmean_Coral = oral_cavity_Dmean*0.01
            Dmean_PCMSup = pcm_sup_Dmean*0.01
            Dmean_PCMMed = pcm_mid_Dmean*0.01
            Dmean_PCMInf = pcm_inf_Dmean*0.01

            xero_grade2 = self.NTCP_definitive_xero_grade2(self.baseline, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR)
            xero_grade3 = self.NTCP_definitive_xero_grade3(self.baseline, Dmean_ParL, Dmean_ParR, Dmean_SubmL, Dmean_SubmR, Volume_SubmL, Volume_SubmR)
            dysf_grade2 = self.NTCP_definitive_dysf_grade2(self.baseline, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, self.location)
            dysf_grade3 = self.NTCP_definitive_dysf_grade3(self.baseline, Dmean_Coral, Dmean_PCMSup, Dmean_PCMMed, Dmean_PCMInf, self.location)

            self.append_clinical_goal_to_df("xero_grade2",xero_grade2)
            self.append_clinical_goal_to_df("xero_grade3",xero_grade3)
            self.append_clinical_goal_to_df("dysf_grade2",dysf_grade2)
            self.append_clinical_goal_to_df("dysf_grade3",dysf_grade3)

            print(self.df_results)

            return self.df_results
