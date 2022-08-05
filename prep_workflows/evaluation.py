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
                ctv_low_bool = ctv_low_coverage < 5154

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
        self.index = adapt_image_name[-2:]
        self.def_reg_name = "HybridDefReg" + self.index

        self.ctv_names = ["CTVnR_5425", "CTVnL_5425", "CTVp_7000", "CTV_5425", "CTV_7000", "CTV_all"]

        self.oar_names_def =["Mandible", "Esophagus", "SpinalCord", "Parotid_R", "Parotid_L", "Submandibular_L", "Submandibular_R", "Brainstem",
                            "Oral_Cavity", "PharConsSup", "PharConsMid", "PharConsInf"]
        
        other_oars = ["Larynx","Cochlea_R", "Cochlea_L", "Retina_R", "Retina_L", "artifact"]
        other_ctvs = ["CTVp_5425", "CTVnR_7000", "CTVnL_7000", "CTVn_7000"]

        all_rois = self.case.PatientModel.StructureSets["pCT"].RoiGeometries
        self.roi_names = [x.OfRoi.Name for x in all_rois]

        for other_oar in other_oars:
            if other_oar in self.roi_names:
                self.oar_names_def.append(other_oar)
        
        for other_ctv in other_ctvs:
            if other_ctv in self.roi_names:
                self.ctv_names.append(other_ctv)

        self.oar_names_predict =  []

    def map_rois_deformably(self): 

        try:
            #create hybrid registration
            self.case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=self.def_reg_name, 
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
        except:
            print('Your deformable registration already existis')
        #map_rois
        if not self.case.PatientModel.StructureSets[self.adapt_image_name].RoiGeometries["CTV_7000"].HasContours():
            self.case.MapRoiGeometriesDeformably(RoiGeometryNames= self.ctv_names + self.oar_names_def, CreateNewRois=False, 
                                                StructureRegistrationGroupNames=[self.def_reg_name], 
                                                ReferenceExaminationNames=["pCT"], TargetExaminationNames=[self.adapt_image_name], 
                                                ReverseMapping=False, AbortWhenBadDisplacementField=True)
        if "artifact" in self.roi_names:
            self.case.PatientModel.RegionsOfInterest['BODY'].CreateAlgebraGeometry(Examination=self.case.Examinations[self.adapt_image_name], Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["BODY"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["rr_artifact","artifact"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            self.case.PatientModel.StructureSets[self.adapt_image_name].SimplifyContours(RoiNames=["BODY"], RemoveHoles3D=True, RemoveSmallContours=False, AreaThreshold=None, ReduceMaxNumberOfPointsInContours=False, MaxNumberOfPoints=None, CreateCopyOfRoi=False, ResolveOverlappingContours=False)

        self.patient.Save()

    def export_clinical_goals(self):
        return 