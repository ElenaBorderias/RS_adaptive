from connect import *
import pandas as pd


class EvaluationSummedDose:

    def __init__(self,doe_pct,oa_strategy,summed_dose_name):

        self.doe_pct = doe_pct
        self.oa_strategy = oa_strategy
        self.summed_dose_name = summed_dose_name

        self.case = get_current("Case")
        self.patient = get_current("Patient")

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

        print(self.df_results)

        return self.df_results

class EvaluationPlanningDose:
        def __init__(self,plan_name):

            self.case = get_current("Case")
            self.patient = get_current("Patient")

            self.plan_name = plan_name
            self.dose_eval = self.case.TreatmentPlans[self.plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose
        
        def append_clinical_goal_to_df(self,clinical_goal,value):
            self.df_results = self.df_results.append({'Patient' : self.patient.Name, 
                                'Plan_name' : self.plan_name, 
                                'ClinicalGoal' : clinical_goal,
                                'Value': value},
                                ignore_index = True)
        
        def init_data_frame_results(self):
            self.df_results = pd.DataFrame(columns=["Patient", "Plan_name", "ClinicalGoal", "Value"])
        
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

            print(self.df_results)

            return self.df_results
            
class NeedsAdaptation:

    def __init__(self, adapt_image_name, reference_plan_name):

        self.adapt_image_name = adapt_image_name
        self.reference_plan_name = reference_plan_name
        self.case = get_current("Case")
        self.patient = get_current("Patient")

    def evaluate_dose_examination(self):

        beam_set_eval = self.case.TreatmentPlans[self.reference_plan_name].BeamSets[0]
        beam_set_eval.ComputeDoseOnAdditionalSets(OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[
                                                  self.adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)

    def find_dose_evaluation(self):

        for doe in self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
            if doe.OnExamination.Name == self.adapt_image_name:
                self.dose_on_examination = doe

        return self.dose_on_examination

    def delete_eval_dose(self):
        self.dose_eval.DeleteEvaluationDose()
    
    def find_best_plan_and_check_adapt(self,plan_list):

        abs_difference = 10000
        best_plan_name = None
        adaptation_needed = True
        
        for plan in plan_list:
            beam_set_eval = self.case.TreatmentPlans[plan].BeamSets[0]
            beam_set_eval.ComputeDoseOnAdditionalSets(OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[
                                                  self.adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)
            doe = self.find_dose_evaluation()

            for dose_eval in doe.DoseEvaluations:
                if dose_eval.ForBeamSet.DicomPlanLabel == plan:

                    ctv_high_coverage = dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_7000", RelativeVolumes=[0.98])*35
                    ctv_low_coverage = dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_5425", RelativeVolumes=[0.98])*35

                    abs_difference_i = abs(ctv_high_coverage[0] - 6650) + abs(ctv_low_coverage[0] - 5125)
                    ctv_high_bool = ctv_high_coverage[0] < 6650
                    ctv_low_bool = ctv_low_coverage[0] < 5125
                    adaptation_needed_i = ctv_high_bool or ctv_low_bool

                    print(abs_difference_i,abs_difference,adaptation_needed_i, ctv_high_bool, ctv_low_bool)

                    if abs_difference_i < abs_difference and adaptation_needed_i == False:
                        abs_difference = abs_difference_i
                        best_plan_name = plan
                        adaptation_needed = adaptation_needed_i 
                        print('The plan ', plan, ' is a good candidate. I updated the values: abs diff: ', abs_difference, 'Best potential plan: ', best_plan_name)
                    
                    elif abs_difference_i > abs_difference and adaptation_needed_i == False:
                        print('There is better plan than ', plan)

                    else:
                        print('The plan ', plan, ' requires adaptation', adaptation_needed_i)
                        dose_eval.DeleteEvaluationDose()
            
        if adaptation_needed == True:
            print("ADAPT needed, none of the previous plans is good enough, a new plan is needed for the fraction corresponding to ", self.adapt_image_name)
            for dose_eval in reversed(doe.DoseEvaluations):
                dose_eval.DeleteEvaluationDose()

        elif adaptation_needed == False:
            print("A new plan is NOT required for the fraction corresponding to ", self.adapt_image_name, " the best adapted plan will be delivered : ", best_plan_name)
            for dose_eval in reversed(doe.DoseEvaluations):
                if dose_eval.ForBeamSet.DicomPlanLabel != best_plan_name:
                    dose_eval.DeleteEvaluationDose()
        else:
            print('Adaptation value is not boolean', adaptation_needed)

        return best_plan_name, adaptation_needed

    def check_adaptation_needed(self):

        self.evaluate_dose_examination()
        self.find_dose_evaluation()

        for dose_eval in self.dose_on_examination.DoseEvaluations:
            if dose_eval.ForBeamSet.DicomPlanLabel == self.reference_plan_name:
                self.dose_eval = dose_eval

                ctv_high_coverage = self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_7000", RelativeVolumes=[0.98])*35
                ctv_low_coverage = self.dose_eval.GetDoseAtRelativeVolumes(RoiName="CTV_5425", RelativeVolumes=[0.98])*35

                ctv_high_bool = ctv_high_coverage < 6650
                ctv_low_bool = ctv_low_coverage < 5125

       
        adaptation_needed = ctv_high_bool or ctv_low_bool
        print(adaptation_needed,ctv_high_bool,ctv_low_bool)

        if adaptation_needed:
            print("A new plan is needed for the fraction corresponding to ", self.adapt_image_name)
            self.delete_eval_dose()

        else:
            print("A new plan is NOT required for the fraction corresponding to ", self.adapt_image_name)

        return adaptation_needed
"""
class EvaluatePlan:

    def __init__(self, adapt_image_name, adap_strategy):

        self.adapt_image_name = adapt_image_name
        self.reference_plan_name = reference_plan_name
        self.case = get_current("Case")
        self.patient = get_current("Patient")***

        self.ctv_names = ["CTVnR_5425", "CTVnL_5425", "CTVp_5425", "CTVp_7000", "CTV_5425", "CTV_7000", "CTV_all"]

        self.oar_names_def =["Mandible", "Esophagus", "SpinalCord", "Parotid_R", "Parotid_L", "Larynx", "Submandibular_L", "Submandibular_R", "Brainstem",
                            "Oral_Cavity", "Cochlea_R", "Cochlea_L", "Retina_R", "Retina_L", "PharConsSup", "PharConsMid", "PharConsInf"]

        self.oar_names_predict =  []

    def map__rois(self): 
        self.case.MapRoiGeometriesDeformably(RoiGeometry= self.ctv_names + self.oar_names_def, CreateNewRois=False, 
                                                StructureRegistrationGroupNames=["HybridDefReg"], 
                                                ReferenceExaminationNames=["pCT"], TargetExaminationNames=[self.adapt_image_name], 
                                                ReverseMapping=False, AbortWhenBadDisplacementField=True)

    def export_clinical_goals(self):
        return 
"""