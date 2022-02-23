from venv import create
from connect import *

patient = get_current("Patient")
case = get_current("Case")
examination = case.Examinations["pCT"]

all_rois = case.PatientModel.StructureSets[examination.Name].RoiGeometries
roi_names = [x.OfRoi.Name for x in all_rois]

print(roi_names)

oars = [r"Parotid_L", r"Parotid_R", r"Submandibular_L", r"Submandibular_R", r"PharConsSup", r"PharConsMid", r"PharConsInf", r"Oral_Cavity",
        r"Mandible", r"SupraglotLarynx", r"Larynx", r"Esophagus_upper", r"Esophagus", r"Cochlea_L", r"Cochlea_R", r"GlotticArea", r"Brain", r"Brainstem", r"SpinalCord",r"BODY"]

other_oars_all = [r"Mandible", r"SupraglotLarynx", r"Esophagus_upper",
                  r"Cochlea_L", r"Cochlea_R", r"GlotticArea", r"Brainstem", r"SpinalCord"]

oars_model = [r"Brain", r"Brainstem", r"SpinalCord",
              r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
              r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
              r"Esophagus", r"BODY"]

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

    algebra_several_rois(case.PatientModel.RegionsOfInterest["CTV_7000"], case.Examinations["pCT"], [
                         "CTVp_7000"], 0, roisB_7000, 0, "Union", 0)

if "CTV_all" not in roi_names:

    create_roi("CTV_all", "Yellow", "CTV")
    algebra_several_rois(case.PatientModel.RegionsOfInterest["CTV_all"], case.Examinations["pCT"], [
                         "CTV_5425"], 0, ["CTV_7000"], 0, "Union", 0)

if "CTV70+18mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+18mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.8, 'Inferior': 1.8, 'Anterior': 1.8, 'Posterior': 1.8, 'Right': 1.8, 'Left': 1.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "CTV70+13mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+13mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV70+4mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+4mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.4, 'Inferior': 0.4, 'Anterior': 0.4, 'Posterior': 0.4, 'Right': 0.4, 'Left': 0.4}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV70+6mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+6mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV70+1mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+1mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "CTV70+3mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+3mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0,  'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV70+10mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+10mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.0, 'Inferior': 1.0, 'Anterior': 1.0, 'Posterior': 1.0, 'Right': 1.0, 'Left': 1.0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "CTV70+15mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+15mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV70+20mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+20mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 2.0, 'Inferior': 2.0, 'Anterior': 2.0, 'Posterior': 2.0, 'Right': 2.0, 'Left': 2.0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "CTV70+30mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV70+30mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 3.0, 'Inferior': 3.0, 'Anterior': 3.0, 'Posterior': 3.0, 'Right': 3.0, 'Left': 3.0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "CTV54.25+15mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+15mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25+18mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+18mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.8, 'Inferior': 1.8, 'Anterior': 1.8, 'Posterior': 1.8, 'Right': 1.8, 'Left': 1.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25+13mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+13mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.3, 'Inferior': 1.3, 'Anterior': 1.3, 'Posterior': 1.3, 'Right': 1.3, 'Left': 1.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25+8mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+8mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25+5mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+5mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25+3mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+3mm", Color="Red", Type="PTV", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if "NTCP_OARs" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"NTCP_OARs", Color="SaddleBrown", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"OralCavity", r"PharConsInf", r"PharConsMid", r"PharConsSup", r"Parotid_L", r"Parotid_R", r"Submandibular_L", r"Submandibular_R"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={
                                  'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "NTCP_OARs+3mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"NTCP_OARs+3mm", Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"NTCP_OARs"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "OtherOARs" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"OtherOARs", Color="SaddleBrown", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': other_oars_selected, 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "OtherOARs+3mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"OtherOARs+3mm", Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"OtherOARs"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "PCMs" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"PCMs", Color="SaddleBrown", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"PharConsInf", r"PharConsMid", r"PharConsSup"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "PCMs+3mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"PCMs+3mm", Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"PCMs"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "SpinalCord+5mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"SpinalCord+5mm", Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"PCMs"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
    ], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="None", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "OtherNotSerialOARs+3mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"OtherNotSerialOARs+3mm", Color="Pink", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"OtherOARs+3mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [r"Brainstem", r"SpinalCord"], 'MarginSettings': {
                                  'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25-CTV70+6mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25-CTV70+6mm", Color="Orange", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {
                                  'Type': "Expand", 'Superior': 0.6, 'Inferior': 0.6, 'Anterior': 0.6, 'Posterior': 0.6, 'Right': 0.6, 'Left': 0.6}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25-CTV70+10mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25-CTV70+10mm", Color="Orange", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [r"CTV_7000"], 'MarginSettings': {
                                  'Type': "Expand", 'Superior': 1.0, 'Inferior': 1.0, 'Anterior': 1.0, 'Posterior': 1.0, 'Right': 1.0, 'Left': 1.0}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "CTV54.25+1mm-CTV70+4mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name=r"CTV54.25+1mm-CTV70+4mm", Color="Orange", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': [r"CTV_5425"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': [
                                  r"CTV_7000"], 'MarginSettings': {'Type': "Expand", 'Superior': 0.4, 'Inferior': 0.4, 'Anterior': 0.4, 'Posterior': 0.4, 'Right': 0.4, 'Left': 0.4}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "Skinring_15mm" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name="Skinring_15mm", Color="Green", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["BODY"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ExpressionB={'Operation': "Union", 'SourceRoiNames': ["BODY"], 'MarginSettings': {
                                  'Type': "Contract", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ResultOperation="Subtraction", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "Parotid_Entrance" not in roi_names:
    retval_0 = case.PatientModel.CreateRoi(
        Name="Parotid_Entrance", Color="SaddleBrown", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': ["Parotid_L", "Parotid_R"], 'MarginSettings': {'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5}}, ExpressionB={'Operation': "Intersection", 'SourceRoiNames': [
                                  "Skinring_15mm"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

if "Brain" not in roi_names:

    if "aux_Brain" not in roi_names:
        create_roi("aux_Brain", "Red", "Organ")
        algebra_several_rois(case.PatientModel.RegionsOfInterest["aux_Brain"], case.Examinations["pCT"], [
                         "Brainstem"], 0, [], 0, "None", 0)
    
    if "aux_Brains" not in roi_names:
        with CompositeAction('Expand (aux_Brains, Image set: pCT)'):

            retval_0 = case.PatientModel.CreateRoi(Name="aux_Brains", Color="Yellow", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            retval_0.CreateMarginGeometry(Examination=examination, SourceRoiName="Brainstem", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })


patientmodel = case.PatientModel
rois = patientmodel.RegionsOfInterest
patient_db = get_current("PatientDB")
template_materials = patient_db.GetTemplateMaterials()
for mat in template_materials:
    if mat.Material.Name == "Water":
        water_material = mat.Material

    if mat.Material.Name == "Muscle":
        muscle_material = mat.Material

for ROI in rois:
    if (ROI.OrganData.OrganType != 'Target' and ROI.Name not in oars):
        ROI.OrganData.OrganType = 'Other'

    if ROI.Name == "CouchSurface":
        case.PatientModel.RegionsOfInterest[ROI.Name].Type = "Control"
        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(Material=None)
    
    if ROI.Name == "CouchInterior":
        case.PatientModel.RegionsOfInterest[ROI.Name].Type = "Control"
        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(Material=None)
    
    if "artifact" == ROI.Name or "artefact" == ROI.Name:

        case.PatientModel.RegionsOfInterest['NS_Contrast'].SetRoiMaterial(Material=muscle_material)
    
    if "Contrast" in ROI.Name or "contrast" in ROI.Name:
        
        case.PatientModel.RegionsOfInterest[ROI.Name].SetRoiMaterial(Material=water_material)

patient.Save()