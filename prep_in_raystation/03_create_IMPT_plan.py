#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""

from tokenize import maybe
from connect import get_current


analytical_plan_name = "IMPT_plan"
ml_plan_name = "Adap_ML"
xt_plan_name = "Empty plan"
pCT_name = "vCT 01"
ml_model_name = "model_try_1"
ml_strategy = "IMPT Demo"

run_analytical_plan = False
run_ml_plan = True

def copy_dosegrid_from_plan_to_plan(from_plan, to_plan):
    # get dose grid
    dgr = from_plan.GetTotalDoseGrid()
    VoxSizeX = dgr.VoxelSize.x
    VoxSizeY = dgr.VoxelSize.y
    VoxSizeZ = dgr.VoxelSize.z
    NrVoxX = dgr.NrVoxels.x
    NrVoxY = dgr.NrVoxels.y
    NrVoxZ = dgr.NrVoxels.z

    CornerX = dgr.Corner.x
    CornerY = dgr.Corner.y
    CornerZ = dgr.Corner.z

    # set dose grid
    beam_set = to_plan.BeamSets[0]
    beam_set.UpdateDoseGrid(Corner={'x': CornerX, 'y': CornerY, 'z': CornerZ},
                            VoxelSize={'x': VoxSizeX,
                                       'y': VoxSizeY, 'z': VoxSizeZ},
                            NumberOfVoxels={'x': NrVoxX, 'y': NrVoxY, 'z': NrVoxZ})


def add_beams_to_plan(plan_name, ct_name):

    ###################################
    ##### Define beam parameters ######
    ###################################
    case = get_current('Case')

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

    plan = case.TreatmentPlans[plan_name]
    beam_set = plan.BeamSets[0]

   
    if ct_name.startswith("vCT"):
        iso_data = case.PatientModel.StructureSets[ct_name].RoiGeometries["rr_CTV_all"].GetCenterOfRoi()
    else:
        iso_data = case.PatientModel.StructureSets[ct_name].RoiGeometries["CTV_all"].GetCenterOfRoi()

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


def add_optimization_objectives(plan_name):

    case = get_current('Case')
    plan = case.TreatmentPlans[plan_name]
    func_type = ["MinDose", "MinDose", "MaxDose", "MaxDose"]
    rois = ["CTV_5425", "CTV_7000", "CTV_all", "CTV54.25-CTV70+6mm"]
    dose_levels = [5425, 7000, 7200, 5700]
    rob = ["True", "True", "True", "False"]

    for i, roi in enumerate(rois):
        print(i, roi)
        po = plan.PlanOptimizations[0]
        po.AddOptimizationFunction(FunctionType=func_type[i], RoiName=roi,
                                   IsConstraint=False, RestrictAllBeamsIndividually=False,
                                   RestrictToBeam=None, IsRobust=rob[i], RestrictToBeamSet=None,
                                   UseRbeDose=False)
        po.Objective.ConstituentFunctions[i].DoseFunctionParameters.DoseLevel = dose_levels[i]


def set_robustness_parameters(plan_name, setup_error, range_error):

    case = get_current('Case')
    plan = case.TreatmentPlans[plan_name]
    po = plan.PlanOptimizations[0]
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


patient = get_current("Patient")
case = get_current("Case")
machine_learning_db = get_current("MachineLearningDB")
ml_models_info = machine_learning_db.QueryMachineLearningModelInfo()

xt_plan = case.TreatmentPlans[xt_plan_name]

reference_XT_dose = case.TreatmentPlans[xt_plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose

all_oars = ["Parotid_L", "Parotid_R",
            "Submandibular_R", "Submandibular_L",
            "PharConsSup", "PharConsMid", "PharConsInf",
            "SpinalCord", "Brain", "Brainstem",
            "SupraglotLarynx", "Esophagus", "Oral_Cavity", "Mandible", "Larynx",
            "Lens_R", "Lens_L", "Cochlea_R", "Cochlea_L"]

oar_to_maintain = []

all_rois = case.PatientModel.StructureSets[pCT_name].RoiGeometries
roi_names = [x.OfRoi.Name for x in all_rois]


all_plans = case.TreatmentPlans
plan_names = [plan.Name for plan in all_plans]

for oar in all_oars:
    if oar in roi_names:
        oar_to_maintain.append(oar)

oar_to_improve = ["Parotid_L", "Parotid_R", "Larynx",
                  "Submandibular_R", "Submandibular_L",
                  "PharConsSup", "PharConsMid", "PharConsInf",
                  "SpinalCord", "Brainstem"]

targets_to_maintain = ["CTV_all", "CTV_7000", "CTV_5425",
                       "CTVp_7000", "CTVnL_5425", "CTVnR_5425"]

maybe_targets = ["CTVnL_7000", "CTVnR_7000", "CTVp_5425"]

for extra_ctv in maybe_targets:
    if extra_ctv in roi_names:
        targets_to_maintain.append(extra_ctv)

if run_analytical_plan:
    if analytical_plan_name not in plan_names:

        retval_0 = case.AddNewPlan(PlanName=analytical_plan_name, PlannedBy="", Comment="",
                                   ExaminationName=pCT_name, IsMedicalOncologyPlan=False, AllowDuplicateNames=False)
        retval_1 = retval_0.AddNewBeamSet(Name=analytical_plan_name, ExaminationName=pCT_name, MachineName="UMCG_P1_MC5_0", Modality="Protons", TreatmentTechnique="ProtonPencilBeamScanning", PatientPosition="HeadFirstSupine", NumberOfFractions=35, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None,
                                          EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], MotionSynchronizationTechniqueSettings={'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined"}, Custom=None, ToleranceTableLabel=None)
    else:
        print("Plan was already created")

    plan = case.TreatmentPlans[analytical_plan_name]
    po = plan.PlanOptimizations[0]

    add_beams_to_plan(analytical_plan_name, pCT_name)
    add_optimization_objectives(analytical_plan_name)
    set_robustness_parameters(analytical_plan_name, 0.4, 0.03)

    # run analytical plan optimization
    copy_dosegrid_from_plan_to_plan(xt_plan, plan)
    po.RunDoseMimicAndReduceOptimization(UseVoxelBasedMimickingForTargets=False,
                                         UseVoxelBasedMimickingForOrgansAtRisk=False,
                                         OrgansAtRiskToImprove=oar_to_improve,
                                         TargetsToMaintain=targets_to_maintain,
                                         OrgansAtRiskToMaintain=oar_to_maintain,
                                         NumberOfMimicOptimizations=1,
                                         MimicNominalScenarioDoseInAllScenarios=True,
                                         RunReduceOptimization=True,
                                         ReferenceDoseDistribution=reference_XT_dose)
if run_ml_plan:
    if ml_plan_name in plan_names:
        try:
            # delete beam_set
            case.TreatmentPlans[ml_plan_name].BeamSets[0].DeleteBeamSet()
        except:
            print("Your plan already exists\n")
    else:
        retval_0 = case.AddNewPlan(PlanName=ml_plan_name,
                                   PlannedBy=ml_plan_name, Comment=ml_plan_name,
                                   ExaminationName=pCT_name,
                                   IsMedicalOncologyPlan=False,
                                   AllowDuplicateNames=False)

        ml_plan = case.TreatmentPlans[ml_plan_name]

        for ml_mod in ml_models_info:
            print(ml_mod["Name"])
            if ml_mod["Name"] ==  ml_model_name:
                ml_model_id = ml_mod["UUId"]
                print("This is the model you were looking for!")
            else:
                print("No matching machine learning model for the given name ", ml_model_name)
        
        if pCT_name.startswith("vCT"):
            roi_matches_planning = "{\"CTV_High\":\"rr_CTV_7000\",\"CTV_Low\":\"rr_CTV_5425\",\"Brainstem\":\"rr_Brainstem\",\"SpinalCord\":\"rr_SpinalCord\",\"Parotid_L\":\"rr_Parotid_L\",\"Parotid_R\":\"rr_Parotid_R\",\"Glnd_Submand_L\":\"rr_Submandibular_L\",\"Glnd_Submand_R\":\"rr_Submandibular_R\",\"Cavity_Oral\":\"rr_Oral_Cavity\",\"Musc_Constrict_I\":\"rr_PharConsInf\",\"Musc_Constrict_M\":\"rr_PharConsMid\",\"Musc_Constrict_S\":\"rr_PharConsSup\",\"External\":\"BODY\",\"rr_CTV_High+10mm\":\"rr_CTV70+10mm\",\"CTV_Low-CTV_High+10mm\":\"rr_CTV54.25-CTV70+10mm\",\"Esophagus\":\"rr_Esophagus\"}"
        else:
            roi_matches_planning = "{\"CTV_High\":\"CTV_7000\",\"CTV_Low\":\"CTV_5425\",\"Brainstem\":\"Brainstem\",\"SpinalCord\":\"SpinalCord\",\"Parotid_L\":\"Parotid_L\",\"Parotid_R\":\"Parotid_R\",\"Glnd_Submand_L\":\"Submandibular_L\",\"Glnd_Submand_R\":\"Submandibular_R\",\"Cavity_Oral\":\"Oral_Cavity\",\"Musc_Constrict_I\":\"PharConsInf\",\"Musc_Constrict_M\":\"PharConsMid\",\"Musc_Constrict_S\":\"PharConsSup\",\"External\":\"BODY\",\"CTV_High+10mm\":\"CTV_7000+10mm\",\"CTV_Low-CTV_High+10mm\":\"CTV54.25-CTV70+10mm\",\"Esophagus\":\"Esophagus\"}"

        print(roi_matches_planning)                                                                                                                                            
        retval_1 = ml_plan.AddNewAutomaticPlanningBeamSet(MachineLearningModelID=ml_model_id,
                                                          AutomaticPlanningParameters={'Name': ml_model_name, 'Strategy': ml_strategy,
                                                                                       'BeamSetList': "[\"Proton\"]",
                                                                                       'RoiMatches':roi_matches_planning,
                                                                                       'BeamSet': "null", 'HasRobustRois': "True", 'Approved': "False", 'ApprovedBy': "", 'ApprovalDate': None},
                                                          Name=ml_plan_name, ExaminationName=pCT_name,
                                                          MachineName="UMCG_P1_MC5_0", Modality="Protons",
                                                          TreatmentTechnique="ProtonPencilBeamScanning", PatientPosition="HeadFirstSupine",
                                                          NumberOfFractions=35, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False,
                                                          UseUserSelectedIsocenterSetupIsocenter=False, Comment=ml_plan_name, RbeModelName=None,
                                                          EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[],
                                                          MotionSynchronizationTechniqueSettings={
                                                              'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined"},
                                                          Custom=None,
                                                          ToleranceTableLabel=None)
        add_beams_to_plan(ml_plan_name, pCT_name)

        dose_grid_size = 0.3
        retval_1.SetDefaultDoseGrid(
            VoxelSize={'x': dose_grid_size, 'y': dose_grid_size, 'z': dose_grid_size})

        retval_1.AddRoiPrescriptionDoseReference(RoiName="CTVp_7000", DoseVolume=0, PrescriptionType="MedianDose",
                                                 DoseValue=7000, RelativePrescriptionLevel=1)
        patient.Save()

    ml_plan = case.TreatmentPlans[ml_plan_name]
    ml_beam_set = ml_plan.BeamSets[0]

    set_robustness_parameters(ml_plan_name, 0.4, 0.03)
    if pCT_name.startswith("vCT"):
        roi_matches_run_planning = {'CTV_High': "rr_CTV_7000", 'CTV_Low': "rr_CTV_5425", 
                                    'Brainstem': "rr_Brainstem", 'SpinalCord': "rr_SpinalCord", 
                                    'Parotid_L': "rr_Parotid_L", 'Parotid_R': "rr_Parotid_R", 'Glnd_Submand_L': "rr_Submandibular_L",
                                    'Glnd_Submand_R': "rr_Submandibular_R", 'Cavity_Oral': "rr_Oral_Cavity", 'Musc_Constrict_I': "rr_PharConsInf", 
                                    'Musc_Constrict_M': "rr_PharConsMid", 'Musc_Constrict_S': "rr_PharConsSup", 'External': "BODY", 
                                    'CTV_High+10mm': "rr_CTV_7000+10mm", 'CTV_Low-CTV_High+10mm': "rr_CTV54.25-CTV70+10mm", 'Esophagus': "rr_Esophagus"}
    else:
        roi_matches_run_planning = {'CTV_High': "CTV_7000", 'CTV_Low': "CTV_5425", 
                                    'Brainstem': "Brainstem", 'SpinalCord': "SpinalCord", 
                                    'Parotid_L': "Parotid_L", 'Parotid_R': "Parotid_R", 'Glnd_Submand_L': "Submandibular_L",
                                    'Glnd_Submand_R': "Submandibular_R", 'Cavity_Oral': "Oral_Cavity", 'Musc_Constrict_I': "PharConsInf", 
                                    'Musc_Constrict_M': "PharConsMid", 'Musc_Constrict_S': "PharConsSup", 'External': "BODY", 
                                    'CTV_High+10mm': "CTV_7000+10mm", 'CTV_Low-CTV_High+10mm': "CTV54.25-CTV70+10mm", 'Esophagus': "Esophagus"}

    ml_beam_set.RunAutomaticPlanning(ModelName=ml_model_name, ModelStrategy=ml_strategy, 
                                    RoiMatches=roi_matches_run_planning)
    
    ml_beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)

    ml_plan.ApprovePlanThroughScripting()