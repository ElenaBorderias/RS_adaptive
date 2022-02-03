from cProfile import run
from tkinter import image_names
from numpy import rollaxis
from connect import *

run_dirs = False
run_vcts = True

""" Pre-requistes - check
1. Imagining system 
2. External rois in both image_names
3. existing DIR between the two images 
4. VirtualCT algorithm  """


def create_rigid_reg(pct_name, cbct_name, rig_reg_name):
    case = get_current("Case")
    case.CreateNamedIdentityFrameOfReferenceRegistration(
        FromExaminationName=cbct_name, ToExaminationName=pct_name, RegistrationName=rig_reg_name, Description=None)
    case.ComputeGrayLevelBasedRigidRegistration(FloatingExaminationName=cbct_name, ReferenceExaminationName=pct_name,
        UseOnlyTranslations=False, HighWeightOnBones=True, InitializeImages=True, FocusRoisNames=[], RegistrationName=rig_reg_name)


def create_deformable_image_registration(pct_name, cbct_names_list):
    case = get_current("Case")
    dir_name = "DIR cbcts -> " + pct_name
    case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=dir_name,
                                                              ReferenceExaminationName=pct_name,
                                                              TargetExaminationNames=cbct_names_list,
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
    
    #patient.Cases[0].Registrations[0].StructureRegistrations[1].RenameStructureRegistration()                                                                

def create_vct(vct_name, ref_exam_name, target_exam_name,dir_name, fov_roi_name):
    case = get_current("Case")
    case.CreateNewVirtualCt(VirtualCtName = vct_name, ReferenceExaminationName = ref_exam_name,
                        TargetExaminationName =  target_exam_name, DeformableRegistrationName = dir_name,
                        FovRoiName = fov_roi_name)

# 1. Imagining system
# 2. External rois in both image_names
# 3. existing DIR between the two images
# 4. VirtualCT algorithm


case = get_current("Case")
pct_name = "pCT"

examinations = case.Examinations
exam_names = [x.Name for x in examinations]
rig_reg_names = [reg.Name for reg in case.Registrations]

if "pCT" in exam_names:
    print("pCT is in exam_names")
    print(exam_names.remove("pCT"))
    cbct_names_list = exam_names
    print(cbct_names_list)
else:
    print("pCT is not in exam_names")


for cbct_name in cbct_names_list:

    cbct_exam = case.Examinations[cbct_name]
    rig_reg_name = cbct_name + " -> " + pct_name

    # check if rigid reg exists
    if rig_reg_name in rig_reg_names:
        print("Your rigid reg alredy exists")
        print(case.Registrations[rig_reg_name])
    else:
        create_rigid_reg(pct_name, cbct_name, rig_reg_name)

    # check if external-ROI exists if not, crete it
    
    if not case.PatientModel.StructureSets[cbct_name].RoiGeometries["BODY"].HasContours():
        case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(
            Examination=cbct_exam, ThresholdLevel=-250)

if run_dirs:
    create_deformable_image_registration(pct_name, cbct_names_list)

if run_vcts:
    for cbct_name in cbct_names_list:
        index_cbct = cbct_name[-2:]
        vct_name = "vCT " + index_cbct
        rig_reg_name = cbct_name + " -> " + pct_name
        for reg in case.Registrations[rig_reg_name].StructureRegistrations:
            if reg.Name.startswith("DIR") and reg.ToExamination.Name == cbct_name and reg.FromExamination.Name == pct_name:
                dir_name = reg.Name

        fov_roi_name = "BODY"
        create_vct(vct_name,pct_name,cbct_name,dir_name, fov_roi_name)

