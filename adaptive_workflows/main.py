import create_virtual_ct_from_cbct
from connect import get_current

pct_name="pCT"
cbct_names_list=['CBCT 02']
oars_model=[r"Brainstem", r"SpinalCord",
            r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
            r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
            r"Esophagus", r"BODY"]

targets_model=[r"CTV_5425", r"CTV_7000", r"CTV_all",
                r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

model_rois=targets_model + oars_model
case = get_current("Case")
for cbct_name in cbct_names_list:
    converter = create_virtual_ct_from_cbct.CreateConvertedImage(pct_name, cbct_name, model_rois)
    vct_name = converter.create_vct()
    #case.PatientModel.RegionsOfInterest['BODY'].CreateExternalGeometry(Examination=case.Examinations[vct_name], ThresholdLevel=-250)