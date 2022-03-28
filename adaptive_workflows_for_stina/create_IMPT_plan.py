#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
from connect import get_current
from genericpath import exists
import time
import SimpleITK as sitk
import numpy as np

class CreateIMPTPlan:

    def __init__(self, pct_name, plan_name, model_name, model_strategy, map_rois_strategy, dose_grid,needs_ref_dose):

        self.pct_name = pct_name
        self.ml_plan_name = plan_name
        self.ml_model_name = model_name
        self.ml_model_strategy = model_strategy
        
        self.case = get_current("Case")
        self.patient = get_current("Patient")
        self.machine_learning_db = get_current("MachineLearningDB")
        self.ml_models_info = self.machine_learning_db.QueryMachineLearningModelInfo()

        self.map_rois_strategy = map_rois_strategy # "DIR", "RigidReg"

        self.set_up_error = 0.4
        self.range_error = 0.03
        self.dose_grid = dose_grid
        self.needs_ref_dose = needs_ref_dose

        self.reference_plan = self.case.TreatmentPlans["ML_IMPT_plan"]
        self.reference_ct_name = "pCT"
        self.reference_ct = self.case.Examinations[self.reference_ct_name]
        self.rigid_reg_name = self.pct_name[-7:] + ' -> pCT'
        self.index = self.pct_name[-2:]
        self.def_reg_name = "HybridDefReg" + self.index
        


        self.ctv_names = ["CTVnR_5425", "CTVnL_5425", "CTVp_7000", "CTV_5425", "CTV_7000","CTV_7000+10mm","CTV54.25-CTV70+10mm", "CTV_all"]

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
    def run_DIR_pCT_adapt_image(self):
        try:
            #create hybrid registration 
            self.case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=self.def_reg_name, 
                                                                            ReferenceExaminationName="pCT", TargetExaminationNames=[self.pct_name], 
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
            print("Deformable registration already exists")

    def map_rois(self): 

        if self.map_rois_strategy == "DIR":
            #create hybrid registration
            self.run_DIR_pCT_adapt_image()
            #map_rois
            self.case.MapRoiGeometriesDeformably(RoiGeometryNames= self.ctv_names + self.oar_names_def, CreateNewRois=False, 
                                                    StructureRegistrationGroupNames=[self.def_reg_name], 
                                                    ReferenceExaminationNames=["pCT"], TargetExaminationNames=[self.pct_name], 
                                                    ReverseMapping=False, AbortWhenBadDisplacementField=True)
            if "artifact" in self.roi_names:
                self.case.PatientModel.RegionsOfInterest['BODY'].CreateAlgebraGeometry(Examination=self.case.Examinations[self.pct_name], Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["BODY"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["rr_artifact","artifact"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })


            self.patient.Save()
        else:
            print("No mapping needed, rr_rois already in the adapted image")

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
        print(corner)
        from_FOR = self.reference_plan.PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
        to_FOR = self.case.TreatmentPlans[self.ml_plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
        new_corner = self.case.TransformPointFromFoRToFoR(FromFrameOfReference=from_FOR,ToFrameOfReference=to_FOR,Point=corner)
        print(new_corner)

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

        if self.patient.Name == "ANON37":
            RS = ["RS40", "","RS40","RS40"]
            #RS = ["RS40", None,"RS40","RS40"]
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

        if self.map_rois_strategy == "RigidReg":
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
        
    def plan_already_exists(self):

        all_plans = self.case.TreatmentPlans
        plan_names = [plan.Name for plan in all_plans]
        if self.ml_plan_name in plan_names:
            return True
        else:
            return False

    def fetch_roi_matches_planning(self):

        if self.map_rois_strategy == "RigidReg":
            pct_matches_planning = "{\"CTV_High\":\"rr_CTV_7000\",\"CTV_Low\":\"rr_CTV_5425\",\"Brainstem\":\"rr_Brainstem\",\"SpinalCord\":\"rr_SpinalCord\",\"Parotid_L\":\"rr_Parotid_L\",\"Parotid_R\":\"rr_Parotid_R\",\"Glnd_Submand_L\":\"rr_Submandibular_L\",\"Glnd_Submand_R\":\"rr_Submandibular_R\",\"Cavity_Oral\":\"rr_Oral_Cavity\",\"Musc_Constrict_I\":\"rr_PharConsInf\",\"Musc_Constrict_M\":\"rr_PharConsMid\",\"Musc_Constrict_S\":\"rr_PharConsSup\",\"External\":\"BODY\",\"rr_CTV_High+10mm\":\"rr_CTV70+10mm\",\"CTV_Low-CTV_High+10mm\":\"rr_CTV54.25-CTV70+10mm\",\"Esophagus\":\"rr_Esophagus\"}"
        elif self.map_rois_strategy == "DefReg_PredOARs":
            pct_matches_planning = "{\"CTV_High\":\"CTV_7000\",\"CTV_Low\":\"CTV_5425\",\"Brainstem\":\"DL_Brainstem\",\"SpinalCord\":\"DL_SpinalCord\",\"Parotid_L\":\"DL_Parotid_L\",\"Parotid_R\":\"DR_Parotid_R\",\"Glnd_Submand_L\":\"DL_Submandibular_L\",\"Glnd_Submand_R\":\"DL_Submandibular_R\",\"Cavity_Oral\":\"DL_Oral_Cavity\",\"Musc_Constrict_I\":\"PharConsInf\",\"Musc_Constrict_M\":\"PharConsMid\",\"Musc_Constrict_S\":\"PharConsSup\",\"External\":\"BODY\",\"CTV_High+10mm\":\"CTV_7000+10mm\",\"CTV_Low-CTV_High+10mm\":\"CTV54.25-CTV70+10mm\",\"Esophagus\":\"DL_Esophagus\"}"
        else:
            pct_matches_planning = "{\"CTV_High\":\"CTV_7000\",\"CTV_Low\":\"CTV_5425\",\"Brainstem\":\"Brainstem\",\"SpinalCord\":\"SpinalCord\",\"Parotid_L\":\"Parotid_L\",\"Parotid_R\":\"Parotid_R\",\"Glnd_Submand_L\":\"Submandibular_L\",\"Glnd_Submand_R\":\"Submandibular_R\",\"Cavity_Oral\":\"Oral_Cavity\",\"Musc_Constrict_I\":\"PharConsInf\",\"Musc_Constrict_M\":\"PharConsMid\",\"Musc_Constrict_S\":\"PharConsSup\",\"External\":\"BODY\",\"CTV_High+10mm\":\"CTV_7000+10mm\",\"CTV_Low-CTV_High+10mm\":\"CTV54.25-CTV70+10mm\",\"Esophagus\":\"Esophagus\"}"
        
        return pct_matches_planning

    def fetch_roi_matches_running(self):
        
        if self.map_rois_strategy == "RigidReg":
            pct_roi_matches_run_planning = {'CTV_High': "rr_CTV_7000", 'CTV_Low': "rr_CTV_5425",
                                        'Brainstem': "rr_Brainstem", 'SpinalCord': "rr_SpinalCord",
                                        'Parotid_L': "rr_Parotid_L", 'Parotid_R': "rr_Parotid_R", 'Glnd_Submand_L': "rr_Submandibular_L",
                                        'Glnd_Submand_R': "rr_Submandibular_R", 'Cavity_Oral': "rr_Oral_Cavity", 'Musc_Constrict_I': "rr_PharConsInf",
                                        'Musc_Constrict_M': "rr_PharConsMid", 'Musc_Constrict_S': "rr_PharConsSup", 'External': "BODY",
                                        'CTV_High+10mm': "rr_CTV_7000+10mm", 'CTV_Low-CTV_High+10mm': "rr_CTV54.25-CTV70+10mm", 'Esophagus': "rr_Esophagus"}
            
        elif self.map_rois_strategy == "DefReg_PredOARs":
            pct_roi_matches_run_planning = {'CTV_High': "CTV_7000", 'CTV_Low': "CTV_5425",
                                        'Brainstem': "DL_Brainstem", 'SpinalCord': "DL_SpinalCord",
                                        'Parotid_L': "DL_Parotid_L", 'Parotid_R': "DL_Parotid_R", 'Glnd_Submand_L': "DL_Submandibular_L",
                                        'Glnd_Submand_R': "DL_Submandibular_R", 'Cavity_Oral': "DL_Oral_Cavity", 
                                        'Musc_Constrict_I': "PharConsInf",'Musc_Constrict_M': "PharConsMid", 'Musc_Constrict_S': "PharConsSup", 
                                        'External': "BODY",
                                        'CTV_High+10mm': "CTV_7000+10mm", 'CTV_Low-CTV_High+10mm': "CTV54.25-CTV70+10mm", 'Esophagus': "DL_Esophagus"}
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
        
        self.ml_plan = self.case.TreatmentPlans[self.ml_plan_name]
        self.fetch_roi_matches_planning()
        self.patient.Save()
        self.ml_plan.SetCurrent()
        
        return self.ml_plan

    def set_dose_grid(self):
        if self.dose_grid == "Default":
            dose_grid_size = 0.3
            print(self.ml_plan_name)
            self.case.TreatmentPlans[self.ml_plan_name].BeamSets[0].SetDefaultDoseGrid(VoxelSize={'x': dose_grid_size, 'y': dose_grid_size, 'z': dose_grid_size})
        
        if self.dose_grid == "Copy_from_plan":
            self.copy_dosegrid_from_plan_to_plan()

    def set_prescription(self):

        if self.map_rois_strategy == "RigidReg":
            roi_name = "rr_CTV_7000"
        else:
            roi_name = "CTV_7000"
        
        self.case.TreatmentPlans[self.ml_plan_name].BeamSets[0].AddRoiPrescriptionDoseReference(RoiName=roi_name, DoseVolume=0, PrescriptionType="MedianDose",
                                                DoseValue=7000, RelativePrescriptionLevel=1)
    
    def set_reference_predicted_dose_resampling(self):
        
        new_dgr = self.ml_plan.GetTotalDoseGrid()
        ref_dose_remsampled = self.reference_plan.PlanOptimizations[0].TreatmentCourseSource.TotalDose.GetTransformedAndResampledDoseValues(DoseGrid=new_dgr)
        po = self.case.TreatmentPlans[self.ml_plan_name].PlanOptimizations[0]

        model_dummy_guid = self.fetch_model_id()
       
        # set reference-"predicted" dose
        print("Model ID = ", model_dummy_guid)
        po.AddOptimizationReferenceDose(MachineLearningModelID=model_dummy_guid,
                                        MachineLearningModelVersion=0,
                                        MachineLearningParameters={"Name": 'Mimick dose', 'Strategy': "IMPT Demo", 
                                        'RoiMatches': self.fetch_roi_matches_planning(), 
                                        'BeamSet': self.ml_plan_name, 'HasRobustRois': "True", 'Approved': "False", 'ApprovedBy': "", 'ApprovalDate': None })
       
        self.case.TreatmentPlans[self.ml_plan_name].AutomaticPlanningPreprocessing()
        po.OptimizationReferenceDose.SetDoseValues(Dose=ref_dose_remsampled, CalculationInfo='ref_dose')

    def set_reference_predicted_dose_mapping(self):
        
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
       
        self.case.TreatmentPlans[self.ml_plan_name].AutomaticPlanningPreprocessing()
        po.OptimizationReferenceDose.SetDoseValues(Dose=self.ref_dose, CalculationInfo='ref_dose')

        #delete_evaluation
        #last_dose_eval.DeleteEvaluationDose()
    
    def map_dose_from_pct(self):

        #create deformable registration
        self.temp_reg_name = "Temp_reg_" + self.index
        try:
            self.case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=self.temp_reg_name,
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
        except:
            print('Your deformable registration already exists, ', self.temp_reg_name)
        
        for reg in self.case.Registrations:
            for structure_reg in reg.StructureRegistrations:
                if "Temp_reg" in structure_reg.Name and self.index in structure_reg.Name:
                    DIR_map_reg = structure_reg

        def_reg_DVF0 = self.set_deformation_field_to_zero(DIR_map_reg)

        dose_to_map = self.reference_plan.TreatmentCourse.TotalDose
        ref_dose_grid = self.case.TreatmentPlans[self.ml_plan_name].PlanOptimizations[0].OptimizationReferenceDose.InDoseGrid

        print('Lets map the dose using ', def_reg_DVF0)
        self.case.MapDose(FractionNumber=0,SetTotalDoseEstimateReference=False,DoseDistribution=dose_to_map, StructureRegistration=def_reg_DVF0,ReferenceDoseGrid=ref_dose_grid)

        return def_reg_DVF0
    
    def set_deformation_field_to_zero(self,def_reg_to_zero):

        fileName = f"c:\\temp\\perturbedDIR_"+self.patient.Name+'_'+self.index+".mhd"

        if not exists(fileName):
            def_reg_to_zero.ExportDeformableRegistrationAsMetaFile(MetaImageHeaderFileName = fileName)

        DIR = sitk.ReadImage(fileName)
        DVF = sitk.GetArrayFromImage(DIR)

        DIR = sitk.ReadImage(fileName)
        DVF = sitk.GetArrayFromImage(DIR)

        print(DVF.shape,len(DVF), type(DVF),np.sum(DVF))

        DVF_0 = np.zeros(DVF.shape)

        print(DVF_0.shape,len(DVF_0), type(DVF_0),np.sum(DVF_0))

        perturbedDIR = sitk.GetImageFromArray(DVF_0, isVector=True)
        perturbedDIR.CopyInformation(DIR)

        sitk.WriteImage(perturbedDIR, fileName)

        for reg in self.case.Registrations:
            for struct_reg in reg.StructureRegistrations:
                if self.temp_reg_name in struct_reg.Name:
                    dir_delete = struct_reg

        self.case.DeleteDeformableRegistration(StructureRegistration = dir_delete)

        self.case.ImportDeformableRegistrationFromMetaImageFile(ReferenceExaminationName = self.pct_name,
                                                        TargetExaminationName = self.reference_ct_name,
                                                        DeformableRegistrationGroupName = self.temp_reg_name+'_0',
                                                        MetaImageHeaderFileName = fileName)
        
        for reg in self.case.Registrations:
            for struct_reg in reg.StructureRegistrations:
                if self.temp_reg_name+'_0' in struct_reg.Name:
                    dir_def_0 = struct_reg

        return dir_def_0
        
    def run_run_eval(self,setup_error_eval,range_error_eval):

        self.ml_beam_set.CreateRadiationSetScenarioGroup(Name="rob_eval_28sc", UseIsotropicPositionUncertainty=False,
                                                    PositionUncertaintySuperior=setup_error_eval, PositionUncertaintyInferior=setup_error_eval, PositionUncertaintyPosterior=setup_error_eval,
                                                    PositionUncertaintyAnterior=setup_error_eval, PositionUncertaintyLeft=setup_error_eval, PositionUncertaintyRight=setup_error_eval,
                                                    PositionUncertaintyFormation="AxesAndDiagonalEndPoints", PositionUncertaintyList=None,
                                                    DensityUncertaintyPercent=range_error_eval, NumberOfDensityDiscretizationPoints=2, ComputeScenarioDosesAfterGroupCreation=False)

        self.case.TreatmentDelivery.RadiationSetScenarioGroups[self.case.TreatmentDelivery.RadiationSetScenarioGroups.Count-1].ComputeScenarioGroupDoseValues()
    
    def create_run_and_approve_IMPT_plan(self):
        start_time = time.time()
        self.add_IMPT_plan()
        self.add_beams_to_plan()
        self.map_rois()

        self.set_dose_grid()
        self.set_robustness_parameters()
        self.set_prescription()

        print(self.needs_ref_dose)
        if self.needs_ref_dose == 'True':
            self.set_reference_predicted_dose_mapping()
            #self.set_reference_predicted_dose_resampling()
        
        self.plan_generation_time = time.time() - start_time

        self.patient.Save()
        self.ml_plan = self.case.TreatmentPlans[self.ml_plan_name]
        self.ml_beam_set = self.ml_plan.BeamSets[0]

        self.patient.Save()

        print(self.ml_plan.Name)

        self.ml_plan.SetCurrent()

        start_time = time.time()
        try:
            #self.ml_beam_set.RunAutomaticPlanning(ModelName=self.ml_model_name, ModelStrategy=self.ml_model_strategy,
                                        #RoiMatches=self.fetch_roi_matches_running())
            print('I am testing for Stina')
        except:
            print("I couldn't run the automatic planning with model " + self.ml_model_name)

        self.optimization_time = time.time() - start_time

        #print("Your plan took ", self.optimization_time, " seconds to be optimize")

        #print("Patient : " + str(self.patient.Name) + "\t Plan Name : " + self.ml_plan_name + "\t Plan_generation_time : " + str(self.plan_generation_time/60) + "\t Optimization_time : " + str(self.optimization_time/60) + "\n")
        
        #self.patient.Save()

        return self.plan_generation_time, self.optimization_time