from venv import create
from connect import *

patient = get_current("Patient")
case = get_current("Case")
pct_name = "pCT"
examination = case.Examinations[pct_name]

all_rois = case.PatientModel.StructureSets[examination.Name].RoiGeometries
roi_names = [x.OfRoi.Name for x in all_rois]

print(roi_names)

oars = [r"Parotid_L", r"Parotid_R", r"Submandibular_L", r"Submandibular_R", r"PharConsSup", r"PharConsMid", r"PharConsInf", r"Oral_Cavity",
        r"Mandible", r"SupraglotLarynx", r"Larynx", r"Esophagus_upper", r"Esophagus", r"Cochlea_L", r"Cochlea_R", r"GlotticArea", r"Brain", r"Brainstem", r"SpinalCord", r"BODY"]

other_oars_all = [r"Mandible", r"SupraglotLarynx", r"Esophagus_upper",
                  r"Cochlea_L", r"Cochlea_R", r"GlotticArea", r"Brainstem", r"SpinalCord"]

oars_model = [r"Brainstem", r"SpinalCord",
              r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
              r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
              r"Esophagus", r"BODY"]

targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all",
                 r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

other_oars_selected = []

for ooa in other_oars_all:
    if ooa in roi_names:
        other_oars_selected.append(ooa)

print(other_oars_selected)


def create_roi(roi_name, color, type):
    case.PatientModel.CreateRoi(Name=roi_name, Color=color, Type=type,
                                TissueName=None, RbeCellTypeName=None, RoiMaterial=None)


def algebra_several_rois(to_roi, examination, roisA, expansionA, roisB, expansionB, operation, expansionC):

    if len(roisB) == 0:
        operation = "None"

    to_roi.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': roisA,
                                             'MarginSettings': {'Type': "Expand",
                                                                'Superior': expansionA, 'Inferior': expansionA,
                                                                'Anterior': expansionA, 'Posterior': expansionA,
                                                                'Right': expansionA, 'Left': expansionA}},

                                ExpressionB={'Operation': "Union", 'SourceRoiNames': roisB,
                                             'MarginSettings': {'Type': "Expand",
                                                                'Superior': expansionB, 'Inferior': expansionB,
                                                                'Anterior': expansionB, 'Posterior': expansionB,
                                                                'Right': expansionB, 'Left': expansionB}},
                                ResultOperation=operation,
                                ResultMarginSettings={'Type': "Expand",
                                                      'Superior': expansionC, 'Inferior': expansionC,
                                                      'Anterior': expansionC, 'Posterior': expansionC,
                                                      'Right': expansionC, 'Left': expansionC})

    to_roi.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "CTV_5425" not in roi_names and "CTVnR_5425" in roi_names and "CTVnL_5425" in roi_names:
    create_roi("CTV_5425", "Blue", "CTV")
    roisA_5425 = ["CTVnR_5425"]

    if "CTVp_5425" in roi_names:
        roisA_5425.append("CTVp_5425")

    algebra_several_rois(case.PatientModel.RegionsOfInterest["CTV_5425"], case.Examinations["pCT"], roisA_5425, 0, [
                         "CTVnL_5425"], 0, "Union", 0)

if "CTV_7000" not in roi_names:

    create_roi("CTV_7000", "Magenta", "CTV")

    roisB_7000 = []
    if "CTVn_7000" in roi_names:
        roisB_7000.append("CTVn_7000")
    if "CTVnR_7000" in roi_names:
        roisB_7000.append("CTVnR_7000")
    if "CTVnL_7000" in roi_names:
        roisB_7000.append("CTVnL_7000")
    
    algebra_several_rois(case.PatientModel.RegionsOfInterest["CTV_7000"], case.Examinations["pCT"], [
                         "CTVp_7000"], 0, roisB_7000, 0, "Union", 0)

if "CTV_all" not in roi_names:

    create_roi("CTV_all", "Yellow", "CTV")
    algebra_several_rois(case.PatientModel.RegionsOfInterest["CTV_all"], case.Examinations["pCT"], [
                         "CTV_5425"], 0, ["CTV_7000"], 0, "Union", 0)

if "CTV_7000+10mm" not in roi_names:

    with CompositeAction('Expand (CTV_7000+10mm)'):

        create_roi("CTV_7000+10mm", "Orange", "CTV")
        algebra_several_rois(case.PatientModel.RegionsOfInterest["CTV_7000+10mm"], case.Examinations["pCT"],
                             ["CTV_7000"], 1.0, [], 0, "Union", 0)


if "CTV54.25-CTV70+10mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25-CTV70+10mm", Color="Orange", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {
                                  'Type': "Expand", 'Superior': 1.0, 'Inferior': 1.0, 'Anterior': 1.0, 'Posterior': 1.0, 'Right': 1.0, 'Left': 1.0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

patientmodel = case.PatientModel
rois = patientmodel.RegionsOfInterest
patient_db = get_current("PatientDB")
template_materials = patient_db.GetTemplateMaterials()

model_rois = targets_model + oars_model
model_rois.remove("BODY")

possible_rois = ["Contrast", "contrast", "artifact", "artefact", "NS_Contrast", "NS_Artifact","NS_artifact"]
for poss_roi in possible_rois:
    if poss_roi in roi_names:
        model_rois.append(poss_roi)


for mat in template_materials:
    if mat.Material.Name == "Water":
        water_material = mat.Material

    if mat.Material.Name == "Muscle":
        muscle_material = mat.Material

for ROI in rois:
    if (ROI.OrganData.OrganType != 'Target' and ROI.Name not in oars and not ROI.Name.startswith("rr") and not ROI.Name in model_rois):
        ROI.OrganData.OrganType = 'Other'

    if ROI.Name == "CouchSurface":
        case.PatientModel.RegionsOfInterest[ROI.Name].Type = "Control"
        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(
            Material=None)

    if ROI.Name == "CouchInterior":
        case.PatientModel.RegionsOfInterest[ROI.Name].Type = "Control"
        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(
            Material=None)

    if "artifact" in ROI.Name or "artefact" in ROI.Name or "Artefact" in ROI.Name or "Artifact" in ROI.Name:

        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(
            Material=muscle_material)

    if "Contrast" in ROI.Name or "contrast" in ROI.Name:

        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(
            Material=water_material)

for m_roi in model_rois:

    roi = case.PatientModel.StructureSets[pct_name].RoiGeometries[m_roi]
    color = roi.OfRoi.Color
    roi_type = roi.OfRoi.Type
    new_name = "rr_" + m_roi
    print(new_name)
    if new_name not in roi_names:
        
        create_roi(new_name, color, roi_type)
        case.PatientModel.RegionsOfInterest[new_name].CreateMarginGeometry(Examination=examination, SourceRoiName=m_roi, MarginSettings={
                                                                            'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        try: 
            roi_material_name = case.PatientModel.StructureSets[pct_name].RoiGeometries[m_roi].OfRoi.RoiMaterial.OfMaterial.Name
            for mat in template_materials:
                if mat.Material.Name == roi_material_name:
                    roi_material = mat.Material
            case.PatientModel.RegionsOfInterest[new_name].SetRoiMaterial(Material=roi_material)
        except:
            print("This roi has no material specified")

if "BODY" not in roi_names:
        
    with CompositeAction('Create external (BODY, Image set: pCT)'):

        retval_0 = case.PatientModel.CreateRoi(Name="BODY", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None)

        retval_0.CreateExternalGeometry(Examination=examination, ThresholdLevel=-250)

patient.Save()
