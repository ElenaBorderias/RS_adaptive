from cProfile import run
from re import A
from tkinter import image_names
from turtle import st
from venv import create
from numpy import rollaxis
from connect import *

def create_rigid_reg(pct_name, cbct_name, rig_reg_name):
    case = get_current("Case")
    case.CreateNamedIdentityFrameOfReferenceRegistration(
        FromExaminationName=cbct_name, ToExaminationName=pct_name, RegistrationName=rig_reg_name, Description=None)
    case.ComputeGrayLevelBasedRigidRegistration(FloatingExaminationName=cbct_name, ReferenceExaminationName=pct_name,
        UseOnlyTranslations=False, HighWeightOnBones=True, InitializeImages=True, FocusRoisNames=[], RegistrationName=rig_reg_name)

def create_deformable_image_registration(pct_name, cbct_name, rigid_reg):
    case = get_current("Case")
    dir_name = "DIR " + cbct_name + " -> " + pct_name
    case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=dir_name,
                                                              ReferenceExaminationName=pct_name,
                                                              TargetExaminationNames=[cbct_name],
                                                              ControllingRoiNames=[], ControllingPoiNames=[],
                                                              FocusRoiNames=[],
                                                              AlgorithmSettings={'NumberOfResolutionLevels': 3,
                                                                                 'InitialResolution': {'x': 0.5, 'y': 0.5, 'z': 0.5},
                                                                                 'FinalResolution': {'x': 0.25, 'y': 0.25, 'z': 0.25},
                                                                                 'InitialGaussianSmoothingSigma': 2,
                                                                                 'FinalGaussianSmoothingSigma': 0.333333333333333,
                                                                                 'InitialGridRegularizationWeight': 400,
                                                                                 'FinalGridRegularizationWeight': 400,
                                                                                 'ControllingRoiWeight': 0.5,
                                                                                 'ControllingPoiWeight': 0.1,
                                                                                 'MaxNumberOfIterationsPerResolutionLevel': 1000,
                                                                                 'ImageSimilarityMeasure': "CorrelationCoefficient",
                                                                                 'DeformationStrategy': "Default",
                                                                                 'ConvergenceTolerance': 1E-05})
    for st_reg in rigid_reg.StructureRegistrations:
        if st_reg.Name.startswith("DIR") and st_reg.FromExamination.Name == 'pCT' and st_reg.ToExamination.Name == cbct_name:
            dir_name = st_reg.Name

    case.PatientModel.StructureRegistrationGroups[dir_name].DeformableStructureRegistrations[0].Approve()
    return dir_name

def check_and_create_rigid_registration(pct_name, cbct_name):
    case = get_current("Case")
    rig_reg_names = [reg.Name for reg in case.Registrations]

    rig_reg_name = cbct_name + " -> " + pct_name

    # check if rigid reg exists
    if rig_reg_name in rig_reg_names:
        print("Your rigid reg alredy exists")
        print(case.Registrations[rig_reg_name])
    else:
        create_rigid_reg(pct_name, cbct_name, rig_reg_name)

    return case.Registrations[rig_reg_name]

def check_and_contour_external_contour(cbct_name):
    case = get_current("Case")
    if not case.PatientModel.StructureSets[cbct_name].RoiGeometries["BODY"].HasContours():
        case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(
            Examination=case.Examinations[cbct_name], ThresholdLevel=-250)

def check_and_get_dir_name(pct_name,cbct_name):

    case = get_current("Case")
    rig_reg_name = cbct_name + " -> " + pct_name
    missing_dir = True
    for reg in case.Registrations[rig_reg_name].StructureRegistrations:
        if reg.Name.startswith("DIR") and reg.ToExamination.Name == cbct_name and reg.FromExamination.Name == pct_name:
            dir_name = reg.Name
            missing_dir = False

    if missing_dir:
        dir_name = create_deformable_image_registration(pct_name, cbct_name,case.Registrations[rig_reg_name])

    return dir_name

def create_FOV_roi(cbct_name):
    case = get_current("Case")
    all_rois = case.PatientModel.StructureSets[cbct_name].RoiGeometries
    roi_names = [x.OfRoi.Name for x in all_rois]
    fov_roi_name = "FOV CBCT"

    if fov_roi_name not in roi_names:

        with CompositeAction('Field-of-view ROI (Field-of-view-CBCT 01, Image set: CBCT 01)'):

            retval_0 = case.PatientModel.CreateRoi(Name=fov_roi_name, Color="Red", Type="FieldOfView", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            retval_0.CreateFieldOfViewROI(ExaminationName=cbct_name)

    elif not case.PatientModel.StructureSets[cbct_name].RoiGeometries['FOV CBCT'].HasContours():  
        case.PatientModel.RegionsOfInterest['FOV CBCT'].CreateFieldOfViewROI(ExaminationName=cbct_name)

    else:
        print("FOV_roi already exists")

    return fov_roi_name

def set_callibration_curve_cbct(cbct_name):
    case = get_current("Case")
    cbct = case.Examinations[cbct_name]

    cbct.EquipmentInfo.SetImagingSystemReference(ImagingSystemName="Varian OBI")
    cbct.DeleteLaserExportReferencePoint()

    densityThresholds = cbct.GetDensityThresholdsForCbctImage()
    cbct.EquipmentInfo.SetCtToDensityTableForCbctImage(DensityThresholds=densityThresholds)

def create_vct(vct_name, ref_exam_name, target_exam_name):

    case = get_current("Case")
    
    # 1. Imagining system
    set_callibration_curve_cbct(target_exam_name)

    # 2. External rois in both image_names
    check_and_contour_external_contour(target_exam_name)

    # 3. Existing rigid registration between pct and cbct
    rigid_registration = check_and_create_rigid_registration(ref_exam_name,target_exam_name)

    # 4. Existing DIR between the two images
    dir_name = check_and_get_dir_name(ref_exam_name,target_exam_name)

    # 5. Create FOV roi for cbct
    fov_roi_name = create_FOV_roi(target_exam_name)

    # 6. VirtualCT algorithm
    case.CreateNewVirtualCt(VirtualCtName = vct_name, ReferenceExaminationName = ref_exam_name,
                        TargetExaminationName =  target_exam_name, DeformableRegistrationName = dir_name,
                        FovRoiName = fov_roi_name)

def check_and_copy_rois_to_cbct(pct_name,cbct_name,model_rois):
    case = get_current("Case")
    all_rois = case.PatientModel.StructureSets[pct_name].RoiGeometries
    roi_names = [x.OfRoi.Name for x in all_rois]

    rr_rois = []
    print(model_rois)
    #model_rois.remove("BODY")
    for ml_roi in model_rois:
        rr_rois.append("rr_" + ml_roi)

    rois_to_copy = []
    for roi in roi_names:
        if roi.startswith("rr_"):
            rois_to_copy.append(roi)
    
    if sorted(rr_rois) == sorted(rois_to_copy):

        rois_exist_in_cbct = False

        for roi in rois_to_copy:
            if case.PatientModel.StructureSets[cbct_name].RoiGeometries[roi].HasContours():
                rois_exist_in_cbct = True
            else:
                rois_exist_in_cbct = False
                print("Your rr rois are not defined in your CBCT")
                break

        if not rois_exist_in_cbct:
            print("Let's copy them")
            case.PatientModel.CopyRoiGeometries(SourceExamination=case.Examinations[pct_name], 
                                            TargetExaminationNames=[cbct_name], RoiNames=rois_to_copy, ImageRegistrationNames=[], 
                                            TargetExaminationNamesToSkipAddedReg=[cbct_name])
    else:
        print(sorted(rr_rois))
        print(sorted(rois_to_copy))
        print("Your are missing some crucial rr_ROIS")

pct_name = "pCT"
cbct_names_list = ['CBCT 01','CBCT 02']
oars_model = [r"Brainstem", r"SpinalCord",
              r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
              r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
              r"Esophagus", r"BODY"]

targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all",
                 r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

model_rois = targets_model + oars_model

case = get_current("Case")

for cbct_name in cbct_names_list:
    index_cbct = cbct_name[-2:]
    vct_name = "vCT " + index_cbct
    check_and_copy_rois_to_cbct(pct_name,cbct_name, model_rois)
    create_vct(vct_name,pct_name,cbct_name)
    case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(Examination=case.Examinations[vct_name], ThresholdLevel=-250)

