from connect import *


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

        self.delete_eval_dose()

        adaptation_needed = ctv_high_bool or ctv_low_bool
        print(adaptation_needed,ctv_high_bool,ctv_low_bool)

        if adaptation_needed:
            print("Adaptation is needed for the fraction corresponding to ", self.adapt_image_name)
        else:
            print("No adaptation is required for the fraction corresponding to ", self.adapt_image_name)

        return adaptation_needed, ctv_low_coverage, ctv_high_coverage


class EvaluateClinicalPlan:

    def __init__(self, adapt_image_name, reference_plan_name):

        #def __init__(self, adapt_image_name, reference_plan_name,ctv_strategy,oar_strategy)
        self.adapt_image_name = adapt_image_name
        self.reference_plan_name = reference_plan_name
        self.case = get_current("Case")
        self.patient = get_current("Patient")
        self.rigid_reg_name = adapt_image_name[-7:] + ' -> pCT'

        self.ctv_names = ["CTVnR_5425", "CTVnL_5425", "CTVp_5425", "CTVp_7000", "CTV_5425", "CTV_7000", "CTV_all"]

        self.oar_names_def =["Mandible", "Esophagus", "SpinalCord", "Parotid_R", "Parotid_L", "Larynx", "Submandibular_L", "Submandibular_R", "Brainstem",
                            "Oral_Cavity", "Cochlea_R", "Cochlea_L", "Retina_R", "Retina_L", "PharConsSup", "PharConsMid", "PharConsInf"]

        self.oar_names_predict =  []

    def map_rois_deformably(self): 

        #create hybrid registration
        self.case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName="HybridDefReg", 
                                                                        ReferenceExaminationName="pCT", TargetExaminationNames=[self.adapt_image_name], 
                                                                        ControllingRoiNames=[], ControllingPoiNames=[], FocusRoiNames=[], 
                                                                        AlgorithmSettings={ 'NumberOfResolutionLevels': 3, 
                                                                        'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
                                                                        'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.25 }, 
                                                                        'InitialGaussianSmoothingSigma': 2, 
                                                                        'FinalGaussianSmoothingSigma': 0.333333333333333, 
                                                                        'InitialGridRegularizationWeight': 1500, 
                                                                        'FinalGridRegularizationWeight': 1000, 
                                                                        'ControllingRoiWeight': 0.5, 
                                                                        'ControllingPoiWeight': 0.1, 
                                                                        'MaxNumberOfIterationsPerResolutionLevel': 1000, 
                                                                        'ImageSimilarityMeasure': "CorrelationCoefficient", 
                                                                        'DeformationStrategy': "Default", 'ConvergenceTolerance': 1E-05 })
        #map_rois
        self.case.MapRoiGeometriesDeformably(RoiGeometryNames= self.ctv_names + self.oar_names_def, CreateNewRois=False, 
                                                StructureRegistrationGroupNames=["HybridDefReg"], 
                                                ReferenceExaminationNames=["pCT"], TargetExaminationNames=[self.adapt_image_name], 
                                                ReverseMapping=False, AbortWhenBadDisplacementField=True)
        #delete_DIR
        self.case.DeleteDeformableRegistration(StructureRegistration = self.case.Registrations[self.rigid_reg_name].StructureRegistrations["HybridDefReg1"])

        self.patient.Save()

    def export_clinical_goals(self):
        return 