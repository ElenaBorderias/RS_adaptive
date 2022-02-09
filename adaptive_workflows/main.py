
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage


def main():

    pct_name = "pCT"
    cbct_names_list = ['CBCT 02']

    oars_model = [r"Brainstem", r"SpinalCord",
                  r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
                  r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
                  r"Esophagus", r"BODY"]

    targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all", r"CTVp_7000", r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

    model_rois = targets_model + oars_model
    case = get_current("Case")

    for cbct_name in cbct_names_list:
        converter = CreateConvertedImage(pct_name, cbct_name, model_rois)
        exam_names = [ex.Name for ex in case.Examinations]

        if "Corrected CBCT 02" not in exam_names:
            cbct_name = converter.create_corrected_cbct()
        
        adapt_pct_name = "Corrected CBCT 02"
        
        """
        auto_plan_name = "1_Auto_" + cbct_names_list[0]
        auto_planning = CreateIMPTPlan(adapt_pct_name, auto_plan_name, "RSL_IMPT_conv_img", "IMPT Demo", "Default", False)
        auto_planning.create_run_and_approve_IMPT_plan()
		"""
        mimick_plan_name = "1_Mim_" + cbct_names_list[0]
        mimicking_from_clinical = CreateIMPTPlan(adapt_pct_name, mimick_plan_name, "Only_mimicking_conv_img", "IMPT Demo", "Copy_from_plan", True)
        mimicking_from_clinical.create_run_and_approve_IMPT_plan()

if __name__ == "__main__":
    main()
