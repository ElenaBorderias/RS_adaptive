from connect import *

class CreateConvertedImage:
    
    def __init__(self, pct_name, cbct_name, model_rois):

        self.pct_name = pct_name
        self.cbct_name = cbct_name
        self.case = get_current("Case")
        self.patient = get_current("Patient")

        self.rig_reg_name= cbct_name + " -> " + pct_name
        self.fov_roi_name = "FOV CBCT"
        self.dir_name = "DIR " + cbct_name + " -> " + pct_name
        self.model_rois = model_rois
        self.index_cbct=self.cbct_name[-2:]
        self.vct_name="vCT " + self.index_cbct
        self.corrected_cbct_name = "Corrected CBCT " + self.index_cbct

    def create_rigid_reg(self):
        self.case.CreateNamedIdentityFrameOfReferenceRegistration(
            FromExaminationName=self.cbct_name, ToExaminationName=self.pct_name, RegistrationName=self.rig_reg_name, Description=None)
        self.case.ComputeGrayLevelBasedRigidRegistration(FloatingExaminationName=self.cbct_name, ReferenceExaminationName=self.pct_name,
            UseOnlyTranslations=False, HighWeightOnBones=True, InitializeImages=True, FocusRoisNames=[], RegistrationName=self.rig_reg_name)

    def create_deformable_image_registration(self):
 
        self.case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=self.dir_name,
                                                                    ReferenceExaminationName=self.pct_name,
                                                                    TargetExaminationNames=[
                                                                        self.cbct_name],
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
        self.patient.Save()
        self.deformable_image_registration()

        """ self.case.PatientModel.StructureRegistrationGroups[self.dir_name].DeformableStructureRegistrations[0].RenameStructureRegistration(
                NewName=self.dir_name, Description='only one pct') """
        
    def rigid_registration(self):

        rig_reg_names=[reg.Name for reg in self.case.Registrations]

        # check if rigid reg exists
        if self.rig_reg_name in rig_reg_names:
            print("Your rigid reg alredy exists")
            print(self.case.Registrations[self.rig_reg_name])
            return self.case.Registrations[self.rig_reg_name]
        else:
            return self.create_rigid_reg()

    def deformable_image_registration(self):
        DIR_is_missing = True
        for DIR_reg in self.case.Registrations[self.rig_reg_name].StructureRegistrations:
            
            if DIR_reg.Name.startswith("DIR") and DIR_reg.FromExamination.Name == self.pct_name and DIR_reg.ToExamination.Name == self.cbct_name:
                self.dir_name = DIR_reg.Name
                print("DIR name is " + DIR_reg.Name)
                DIR_is_missing = False

        if DIR_is_missing:
            self.create_deformable_image_registration()
        
        self.patient.Save()

    def check_and_create_external_contour(self):
        if not self.case.PatientModel.StructureSets[self.cbct_name].RoiGeometries["BODY"].HasContours():
            self.case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(
                Examination=self.case.Examinations[self.cbct_name], ThresholdLevel=-250)

    def create_FOV_roi(self):

        all_rois= self.case.PatientModel.StructureSets[self.cbct_name].RoiGeometries
        roi_names=[x.OfRoi.Name for x in all_rois]

        if self.fov_roi_name not in roi_names:

            with CompositeAction('Field-of-view ROI (Field-of-view-CBCT 01, Image set: CBCT 01)'):

                retval_0=self.case.PatientModel.CreateRoi(Name=self.fov_roi_name, Color="Red", Type="FieldOfView", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
                retval_0.CreateFieldOfViewROI(ExaminationName=self.cbct_name)

        elif not self.case.PatientModel.StructureSets[self.cbct_name].RoiGeometries[self.fov_roi_name].HasContours():
            self.case.PatientModel.RegionsOfInterest[self.fov_roi_name].CreateFieldOfViewROI(
                ExaminationName=self.cbct_name)

        else:
            print("FOV_roi already exists")

    def set_callibration_curve_cbct(self):
        cbct=self.case.Examinations[self.cbct_name]

        cbct.EquipmentInfo.SetImagingSystemReference(ImagingSystemName="Varian OBI")
        #cbct.DeleteLaserExportReferencePoint()

        densityThresholds=cbct.GetDensityThresholdsForCbctImage()
        cbct.EquipmentInfo.SetCtToDensityTableForCbctImage(DensityThresholds=densityThresholds)

        self.patient.Save()

    def initial_structures(self):
        # 1. Imagining system
        self.set_callibration_curve_cbct()

        # 2. External rois in both image_names
        self.check_and_create_external_contour()

        # 3. Existing rigid registration between pct and cbct
        self.rigid_registration()

        # 4. Existing DIR between the two images
        self.deformable_image_registration()

        # 5. Create FOV roi for cbct
        self.create_FOV_roi()
    
    def create_vct(self):

        self.initial_structures()
        self.case.CreateNewVirtualCt(VirtualCtName=self.vct_name, ReferenceExaminationName=self.pct_name,
                            TargetExaminationName=self.cbct_name, DeformableRegistrationName=self.dir_name,
                            FovRoiName=self.fov_roi_name)

        self.case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(Examination=self.case.Examinations[self.vct_name], ThresholdLevel=-250)
        self.patient.Save()
        print("VirtualCT created successfully")

    def check_and_copy_rois_to_cbct(self):

        all_rois=self.case.PatientModel.StructureSets[self.pct_name].RoiGeometries
        roi_names=[x.OfRoi.Name for x in all_rois]

        rr_rois=[]
        print(self.model_rois)
        # model_rois.remove("BODY")
        for ml_roi in self.model_rois:
            rr_rois.append("rr_" + ml_roi)

        rois_to_copy=[]
        for roi in roi_names:
            if roi.startswith("rr_"):
                rois_to_copy.append(roi)

        if sorted(rr_rois) == sorted(rois_to_copy):

            rois_exist_in_cbct=False

            for roi in rois_to_copy:
                if self.case.PatientModel.StructureSets[self.cbct_name].RoiGeometries[roi].HasContours():
                    rois_exist_in_cbct=True
                else:
                    rois_exist_in_cbct=False
                    print("Your rr rois are not defined in your CBCT")
                    break

            if not rois_exist_in_cbct:
                print("Let's copy them")
                self.case.PatientModel.CopyRoiGeometries(SourceExamination=self.case.Examinations[self.pct_name],
                                                TargetExaminationNames=[
                                                    self.cbct_name], RoiNames=rois_to_copy, ImageRegistrationNames=[],
                                                TargetExaminationNamesToSkipAddedReg=[self.cbct_name])
        else:
            print(sorted(rr_rois))
            print(sorted(rois_to_copy))
            print("Your are missing some crucial rr_ROIS")

    def create_corrected_cbct(self):

        self.initial_structures()
        self.case.CreateNewCorrectedCbct(CorrectedCbctName=self.corrected_cbct_name, ReferenceExaminationName=self.pct_name, 
                                TargetExaminationName=self.cbct_name, FovRoiName=self.fov_roi_name, 
                                DeformableRegistrationName=self.dir_name)
        self.case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(Examination=self.case.Examinations[self.corrected_cbct_name], ThresholdLevel=-250)
        self.patient.Save()
        print("CorrectedCBCT created successfully")

        return self.corrected_cbct_name