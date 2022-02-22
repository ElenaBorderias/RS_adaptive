#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
from connect import get_current
import time

class CreateIMPTPlan:

    def __init__(self, pct_name, plan_name, model_name, model_strategy, dose_grid,needs_ref_dose):

        self.pct_name = pct_name
        self.ml_plan_name = plan_name
        self.ml_model_name = model_name
        self.ml_model_strategy = model_strategy
        
        self.case = get_current("Case")
        self.patient = get_current("Patient")
        self.machine_learning_db = get_current("MachineLearningDB")
        self.ml_models_info = self.machine_learning_db.QueryMachineLearningModelInfo()

        self.set_up_error = 0.4
        self.range_error = 0.03
        self.dose_grid = dose_grid
        self.needs_ref_dose = needs_ref_dose

        self.reference_plan = self.case.TreatmentPlans["ML_IMPT_plan"]
        self.reference_ct_name = "pCT"
        self.reference_ct = self.case.Examinations[self.reference_ct_name]

    def copy_dosegrid_from_plan_to_plan(self):

        # get dose grid
        dgr = self.reference_plan.GetTotalDoseGrid()
        VoxSizeX = dgr.VoxelSize.x
        VoxSizeY = dgr.VoxelSize.y
        VoxSizeZ = dgr.VoxelSize.z
        NrVoxX = dgr.NrVoxels.x
        NrVoxY = dgr.NrVoxels.y
        NrVoxZ = dgr.NrVoxels.z

        CornerX = dgr.Corner.x
        CornerY = dgr.Corner.y
        CornerZ = dgr.Corner.z

        corner={'x': CornerX, 'y': CornerY, 'z': CornerZ}
        from_FOR = self.reference_plan.PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
        to_FOR = self.case.TreatmentPlans[self.ml_plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
        new_corner = self.case.TransformPointFromFoRToFoR(FromFrameOfReference=from_FOR,ToFrameOfReference=to_FOR,Point=corner)

        # set dose grid
        beam_set = self.case.TreatmentPlans[self.ml_plan_name].BeamSets[0]

        beam_set.UpdateDoseGrid(Corner=new_corner,
                                VoxelSize={'x': VoxSizeX,
                                        'y': VoxSizeY, 'z': VoxSizeZ},
                                NumberOfVoxels={'x': NrVoxX, 'y': NrVoxY, 'z': NrVoxZ})

    def add_beams_to_plan(self):

        ###################################
        ##### Define beam parameters ######
        ###################################

        BN = ["LAO", "LPO", "RPO", "RAO"]  # Beam Name
        beam_num = len(BN)
        GA = [60, 120, 240, 300]  # Gantry Angle
        CA = [10, 350, 10, 350]  # Couch rotation angle
        SN = ["SNOUT_XL"]*len(BN)  # Snout ID
        RS = ["RS40"]*len(BN)  # Range shifter ID
        AG = [6.0]*len(BN)  # Minimum Air GAP

        energy_layer_sep_factor = 0.9  # energy layer separation factor
        energy_selection_mode = "Automatic"
        fixed_spot_tune_id = "3.0"
        #intensity_selection_mode = "Automatic"
        spot_pattern = "Hexagonal"  # spot pattern
        distal = 1  # spot selection distal target layer margin
        # lm = ""  # spot selection lateral margin
        lm_mode = "Automatic"  # spot selection lateral margin mode
        lm_sf = 0.5  # spot selection lateral margin scale factor
        pt_layermargin = 1  # spot selectionproximal target later margin
        sss_factor = 0.7  # spot spacing separation factor

        plan = self.case.TreatmentPlans[self.ml_plan_name]
        beam_set = plan.BeamSets[0]

        if self.pct_name.startswith("vCT") or self.pct_name.startswith("Corrected"):
            iso_data = self.case.PatientModel.StructureSets[self.pct_name].RoiGeometries["rr_CTV_all"].GetCenterOfRoi()
        else:
            iso_data = self.case.PatientModel.StructureSets[self.pct_name].RoiGeometries["CTV_all"].GetCenterOfRoi()

        print(iso_data)

        # add all beams
        for i in range(beam_num):

            print(i)
            print(SN[i])
            print(RS[i])
            print(AG[i])
            print(iso_data)
            print(BN[i])
            print(GA[i])
            print(CA[i])

            if i == 0:
                beam_set.CreatePBSIonBeam(SnoutId=SN[i], SpotTuneId=fixed_spot_tune_id, RangeShifter=RS[i],
                                        MinimumAirGap=AG[i], MetersetRateSetting="", IsocenterData={'Position': {'x': iso_data.x, 'y': iso_data.y, 'z': iso_data.z}, 'NameOfIsocenterToRef': "", 'Name': "Proton 1", 'Color': "98, 184, 234"},
                                        Name=BN[i], Description="", GantryAngle=GA[i], CouchRotationAngle=CA[i],
                                        CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=0)
            else:
                beam_set.CreatePBSIonBeam(SnoutId=SN[i], SpotTuneId=fixed_spot_tune_id, RangeShifter=RS[i],
                                        MinimumAirGap=AG[i], MetersetRateSetting="", IsocenterData={'Position': {'x': iso_data.x, 'y': iso_data.y, 'z': iso_data.z}, 'NameOfIsocenterToRef': "Proton 1", 'Name': "Proton 1", 'Color': "98, 184, 234"},
                                        Name=BN[i], Description="", GantryAngle=GA[i], CouchRotationAngle=CA[i],
                                        CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=0)

            # scanned beam properties
            po = plan.PlanOptimizations[0]
            scanned_beam_properties = po.OptimizationParameters.TreatmentSetupSettings[
                0].BeamSettings[i].ScannedBeamProperties

            scanned_beam_properties.EnergyLayerSeparationFactor = energy_layer_sep_factor
            scanned_beam_properties.EnergySelectionMode = energy_selection_mode

            scanned_beam_properties.SpotPattern = spot_pattern
            scanned_beam_properties.SpotSelectionDistalTargetLayerMargin = distal
            #scanned_beam_properties.SpotSelectionLateralMargin = lm
            scanned_beam_properties.SpotSelectionLateralMarginMode = lm_mode
            scanned_beam_properties.SpotSelectionLateralMarginScaleFactor = lm_sf
            scanned_beam_properties.SpotSelectionProximalTargetLayerMargin = pt_layermargin
            scanned_beam_properties.SpotSpacingSeparationFactor = sss_factor

    def set_robustness_parameters(self):

        plan = self.case.TreatmentPlans[self.ml_plan_name]
        po = plan.PlanOptimizations[0]
        setup_error = self.set_up_error
        range_error = self.range_error

        po.OptimizationParameters.SaveRobustnessParameters(PositionUncertaintyAnterior=setup_error,
                                                        PositionUncertaintyPosterior=setup_error,
                                                        PositionUncertaintySuperior=setup_error,
                                                        PositionUncertaintyInferior=setup_error,
                                                        PositionUncertaintyLeft=setup_error,
                                                        PositionUncertaintyRight=setup_error,
                                                        DensityUncertainty=range_error,
                                                        PositionUncertaintySetting="Universal", IndependentLeftRight=True,
                                                        IndependentAnteriorPosterior=True, IndependentSuperiorInferior=True,
                                                        ComputeExactScenarioDoses=False, NamesOfNonPlanningExaminations=[],
                                                        PatientGeometryUncertaintyType="PerTreatmentCourse",
                                                        PositionUncertaintyType="PerTreatmentCourse", TreatmentCourseScenariosFactor=1000)
        
        po.OptimizationParameters.DoseCalculation.ComputeFinalDose = 'True'

    def plan_already_exists(self):

        all_plans = self.case.TreatmentPlans
        plan_names = [plan.Name for plan in all_plans]
        if self.ml_plan_name in plan_names:
            return True
        else:
            return False

    def fetch_roi_matches_planning(self):

        if self.pct_name.startswith("vCT") or self.pct_name.startswith("Corrected"):
            vct_matches_planning = "{\"CTV_High\":\"rr_CTV_7000\",\"CTV_Low\":\"rr_CTV_5425\",\"Brainstem\":\"rr_Brainstem\",\"SpinalCord\":\"rr_SpinalCord\",\"Parotid_L\":\"rr_Parotid_L\",\"Parotid_R\":\"rr_Parotid_R\",\"Glnd_Submand_L\":\"rr_Submandibular_L\",\"Glnd_Submand_R\":\"rr_Submandibular_R\",\"Cavity_Oral\":\"rr_Oral_Cavity\",\"Musc_Constrict_I\":\"rr_PharConsInf\",\"Musc_Constrict_M\":\"rr_PharConsMid\",\"Musc_Constrict_S\":\"rr_PharConsSup\",\"External\":\"BODY\",\"rr_CTV_High+10mm\":\"rr_CTV70+10mm\",\"CTV_Low-CTV_High+10mm\":\"rr_CTV54.25-CTV70+10mm\",\"Esophagus\":\"rr_Esophagus\"}"
            return  vct_matches_planning
        else:
            pct_matches_planning = "{\"CTV_High\":\"CTV_7000\",\"CTV_Low\":\"CTV_5425\",\"Brainstem\":\"Brainstem\",\"SpinalCord\":\"SpinalCord\",\"Parotid_L\":\"Parotid_L\",\"Parotid_R\":\"Parotid_R\",\"Glnd_Submand_L\":\"Submandibular_L\",\"Glnd_Submand_R\":\"Submandibular_R\",\"Cavity_Oral\":\"Oral_Cavity\",\"Musc_Constrict_I\":\"PharConsInf\",\"Musc_Constrict_M\":\"PharConsMid\",\"Musc_Constrict_S\":\"PharConsSup\",\"External\":\"BODY\",\"CTV_High+10mm\":\"CTV_7000+10mm\",\"CTV_Low-CTV_High+10mm\":\"CTV54.25-CTV70+10mm\",\"Esophagus\":\"Esophagus\"}"
            return pct_matches_planning

    def fetch_roi_matches_running(self):
        
        if self.pct_name.startswith("vCT") or self.pct_name.startswith("Corrected"):
            vct_roi_matches_run_planning = {'CTV_High': "rr_CTV_7000", 'CTV_Low': "rr_CTV_5425",
                                        'Brainstem': "rr_Brainstem", 'SpinalCord': "rr_SpinalCord",
                                        'Parotid_L': "rr_Parotid_L", 'Parotid_R': "rr_Parotid_R", 'Glnd_Submand_L': "rr_Submandibular_L",
                                        'Glnd_Submand_R': "rr_Submandibular_R", 'Cavity_Oral': "rr_Oral_Cavity", 'Musc_Constrict_I': "rr_PharConsInf",
                                        'Musc_Constrict_M': "rr_PharConsMid", 'Musc_Constrict_S': "rr_PharConsSup", 'External': "BODY",
                                        'CTV_High+10mm': "rr_CTV_7000+10mm", 'CTV_Low-CTV_High+10mm': "rr_CTV54.25-CTV70+10mm", 'Esophagus': "rr_Esophagus"}
            
            return vct_roi_matches_run_planning
        
        else:
            pct_roi_matches_run_planning = {'CTV_High': "CTV_7000", 'CTV_Low': "CTV_5425",
                                        'Brainstem': "Brainstem", 'SpinalCord': "SpinalCord",
                                        'Parotid_L': "Parotid_L", 'Parotid_R': "Parotid_R", 'Glnd_Submand_L': "Submandibular_L",
                                        'Glnd_Submand_R': "Submandibular_R", 'Cavity_Oral': "Oral_Cavity", 'Musc_Constrict_I': "PharConsInf",
                                        'Musc_Constrict_M': "PharConsMid", 'Musc_Constrict_S': "PharConsSup", 'External': "BODY",
                                        'CTV_High+10mm': "CTV_7000+10mm", 'CTV_Low-CTV_High+10mm': "CTV54.25-CTV70+10mm", 'Esophagus': "Esophagus"}
            
            return pct_roi_matches_run_planning
    
    def fetch_model_id(self):
        self.ml_model_id = False
        for ml_mod in self.ml_models_info:
            if ml_mod["Name"] == self.ml_model_name:
                self.ml_model_id = ml_mod["UUId"]
                print("This is the model you were looking for!")
                break

        #print("No matching machine learning model for the given name ", self.ml_model_name)
        return self.ml_model_id
    
    def add_IMPT_plan(self):

        if self.plan_already_exists():
            print("I will delete the plan")

        self.case.AddNewPlan(PlanName=self.ml_plan_name,
                                    PlannedBy=self.ml_plan_name, Comment=self.ml_plan_name,
                                    ExaminationName=self.pct_name,
                                    IsMedicalOncologyPlan=False,
                                    AllowDuplicateNames=False)

        ml_plan = self.case.TreatmentPlans[self.ml_plan_name]
        ml_plan.AddNewAutomaticPlanningBeamSet(MachineLearningModelID=self.fetch_model_id(),
                                                            AutomaticPlanningParameters={'Name': self.ml_model_name, 'Strategy': self.ml_model_strategy,
                                                                                        'BeamSetList': "[\"Proton\"]",
                                                                                        'RoiMatches': self.fetch_roi_matches_planning(),
                                                                                        'BeamSet': "null", 'HasRobustRois': "True", 'Approved': "False", 'ApprovedBy': "", 'ApprovalDate': None},
                                                            Name=self.ml_plan_name, ExaminationName=self.pct_name,
                                                            MachineName="UMCG_P1_MC5_0", Modality="Protons",
                                                            TreatmentTechnique="ProtonPencilBeamScanning", PatientPosition="HeadFirstSupine",
                                                            NumberOfFractions=35, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False,
                                                            UseUserSelectedIsocenterSetupIsocenter=False, Comment=self.ml_plan_name, RbeModelName=None,
                                                            EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[],
                                                            MotionSynchronizationTechniqueSettings={
                                                                'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined"},
                                                            Custom=None,
                                                            ToleranceTableLabel=None)
        
        self.ml_plan = ml_plan
        self.fetch_roi_matches_planning()
        self.patient.Save()
        return self.ml_plan

    def set_dose_grid(self):
        if self.dose_grid == "Default":
            dose_grid_size = 0.3
            print(self.ml_plan_name)
            self.case.TreatmentPlans[self.ml_plan_name].BeamSets[0].SetDefaultDoseGrid(VoxelSize={'x': dose_grid_size, 'y': dose_grid_size, 'z': dose_grid_size})
        
        if self.dose_grid == "Copy_from_plan":
            self.copy_dosegrid_from_plan_to_plan()

    def set_prescription(self):

        if self.pct_name.startswith("vCT") or self.pct_name.startswith("Corrected"):
            roi_name = "rr_CTVp_7000"
        else:
            roi_name = "CTVp_7000"
        
        self.case.TreatmentPlans[self.ml_plan_name].BeamSets[0].AddRoiPrescriptionDoseReference(RoiName=roi_name, DoseVolume=0, PrescriptionType="MedianDose",
                                                DoseValue=7000, RelativePrescriptionLevel=1)
    
    def set_reference_predicted_dose(self):
        
        self.DIR_map_reg = self.map_dose_from_pct()

        for doe in self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
            if doe.OnExamination.Name == self.pct_name:
                self.dose_on_examination = doe

        last_dose_eval = self.dose_on_examination.DoseEvaluations[self.dose_on_examination.DoseEvaluations.Count-1]
        self.ref_dose = last_dose_eval.DoseValues.DoseData

        po = self.case.TreatmentPlans[self.ml_plan_name].PlanOptimizations[0]

        model_dummy_guid = self.fetch_model_id()
       
        # set reference-"predicted" dose
        print("Model ID = ", model_dummy_guid)
        po.AddOptimizationReferenceDose(MachineLearningModelID=model_dummy_guid,
                                        MachineLearningModelVersion=0,
                                        MachineLearningParameters={"Name": 'Mimick dose', 'Strategy': "IMPT Demo", 
                                        'RoiMatches': self.fetch_roi_matches_planning(), 
                                        'BeamSet': self.ml_plan_name, 'HasRobustRois': "True", 'Approved': "False", 'ApprovedBy': "", 'ApprovalDate': None })
        #'BeamSet': "\"2_Mim_CBCT 01\""


        self.case.TreatmentPlans[self.ml_plan_name].AutomaticPlanningPreprocessing()
        po.OptimizationReferenceDose.SetDoseValues(Dose=self.ref_dose, CalculationInfo='ref_dose')

        #delete_evaluation_and_DIR 
        last_dose_eval.DeleteEvaluationDose()
        self.case.DeleteDeformableRegistration(StructureRegistration = self.DIR_map_reg)

    def map_dose_from_pct(self):

        #create deformable registration
        self.case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName="Temp_reg",
                                                                       ReferenceExaminationName=self.pct_name,
                                                                       TargetExaminationNames=[self.reference_ct_name],
                                                                       ControllingRoiNames=[], ControllingPoiNames=[], FocusRoiNames=[],
                                                                       AlgorithmSettings={'NumberOfResolutionLevels': 3,
                                                                                          'InitialResolution': {'x': 0.5, 'y': 0.5, 'z': 0.5},
                                                                                          'FinalResolution': {'x': 0.25, 'y': 0.25, 'z': 0.25},
                                                                                          'InitialGaussianSmoothingSigma': 2,
                                                                                          'FinalGaussianSmoothingSigma': 0.333333333333333,
                                                                                          'InitialGridRegularizationWeight': 1500,
                                                                                          'FinalGridRegularizationWeight': 1000,
                                                                                          'ControllingRoiWeight': 0.5, 'ControllingPoiWeight': 0.1,
                                                                                          'MaxNumberOfIterationsPerResolutionLevel': 1000,
                                                                                          'ImageSimilarityMeasure': "CorrelationCoefficient",
                                                                                          'DeformationStrategy': "Default", 'ConvergenceTolerance': 1E-05})
        
        for reg in self.case.Registrations:
            for structure_reg in reg.StructureRegistrations:
                if structure_reg.Name  == "Temp_reg1":
                    DIR_map_reg = structure_reg

        #set deformation field to 0
        data = DIR_map_reg.DeformationMatrix
        disp_field = len(data)*[0]
        disp_field = bytearray(disp_field)
        DIR_map_reg.SetDisplacementField(DisplacementField = disp_field)

        #map dose to converted image
        dose_to_map = self.reference_plan.TreatmentCourse.TotalDose
        ref_dose_grid = self.case.TreatmentPlans[self.ml_plan_name].PlanOptimizations[0].OptimizationReferenceDose.InDoseGrid

        self.case.MapDose(FractionNumber=0,SetTotalDoseEstimateReference=False,
            DoseDistribution=dose_to_map, StructureRegistration=DIR_map_reg,ReferenceDoseGrid=ref_dose_grid)

        return DIR_map_reg
    
    def run_run_eval(self,setup_error_eval,range_error_eval):

        self.ml_beam_set.CreateRadiationSetScenarioGroup(Name="rob_eval_28sc", UseIsotropicPositionUncertainty=False,
                                                    PositionUncertaintySuperior=setup_error_eval, PositionUncertaintyInferior=setup_error_eval, PositionUncertaintyPosterior=setup_error_eval,
                                                    PositionUncertaintyAnterior=setup_error_eval, PositionUncertaintyLeft=setup_error_eval, PositionUncertaintyRight=setup_error_eval,
                                                    PositionUncertaintyFormation="AxesAndDiagonalEndPoints", PositionUncertaintyList=None,
                                                    DensityUncertaintyPercent=range_error_eval, NumberOfDensityDiscretizationPoints=2, ComputeScenarioDosesAfterGroupCreation=False)

    def create_run_and_approve_IMPT_plan(self):
        start_time = time.time()
        self.add_IMPT_plan()
        self.add_beams_to_plan()
        self.set_dose_grid()
        self.set_robustness_parameters()
        self.set_prescription()
        if self.needs_ref_dose:
            self.set_reference_predicted_dose()
        plan_generation_time = time.time() - start_time

        self.patient.Save()
        self.ml_plan = self.case.TreatmentPlans[self.ml_plan_name]
        self.ml_beam_set = self.ml_plan.BeamSets[0]

        print(self.ml_plan)

        start_time = time.time()
        try:
            self.ml_beam_set.RunAutomaticPlanning(ModelName=self.ml_model_name, ModelStrategy=self.ml_model_strategy,
                                        RoiMatches=self.fetch_roi_matches_running())
        except:
            print("I couldn't run the automatic planning with model " + self.ml_model_name)
        optimization_time = time.time() - start_time

        print("Your plan took ", optimization_time, " seconds to be optimize")

        f_results_timing = open(r"C:\\Elena\\results\\Timings_log_files.txt", "w+")
        f_results_timing.write("Patient : " + str(self.patient.Name) + "\t Plan Name : " + self.ml_plan_name + "\t Plan_generation_time : " + str(plan_generation_time/60) + "\t Optimization_time : " + str(optimization_time/60) + "\n")
        f_results_timing.close()

        self.ml_beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)

        self.run_run_eval(0.1,4) #setup error in mm and range error in % 

        self.patient.Save()

        return plan_generation_time, optimization_time