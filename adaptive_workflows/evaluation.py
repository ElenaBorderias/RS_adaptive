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

                ctv_high_bool = self.dose_eval.GetDoseAtRelativeVolumes(
                    RoiName="CTV_7000", RelativeVolumes=[0.98]) < 5125
                ctv_low_bool = self.dose_eval.GetDoseAtRelativeVolumes(
                    RoiName="CTV_5425", RelativeVolumes=[0.98]) < 6650

        self.delete_eval_dose()

        adaptation_needed = ctv_high_bool or ctv_low_bool
        print("Adaptation is needed for the fraction corresponding to ",
              self.adapt_image_name)

        return adaptation_needed


class EvaluatePlan:

    def __init__(self, adapt_image_name, reference_plan_name,ctv_strategy,oar_strategy):

        self.adapt_image_name = adapt_image_name
        self.reference_plan_name = reference_plan_name
        self.case = get_current("Case")
        self.patient = get_current("Patient")

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