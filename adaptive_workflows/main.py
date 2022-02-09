
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage


def main():

    pct_name = "pCT"
    adapt_pct_name = "vCT 01"
    cbct_names_list = ['CBCT 02']
    oars_model = [r"Brainstem", r"SpinalCord",
                  r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
                  r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
                  r"Esophagus", r"BODY"]

    targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all", r"CTVp_7000", r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

    create_corrected_cbct = True

    model_rois = targets_model + oars_model
    case = get_current("Case")

    for cbct_name in cbct_names_list:
        converter = CreateConvertedImage(pct_name, cbct_name, model_rois)
        if create_corrected_cbct:
            cbct_name = converter.create_corrected_cbct()
            
            adapt_pct_name = "Corrected CBCT 02"
            cbct_names_list = ['CBCT 02']
            auto_plan_name = "Adapt_" + cbct_names_list[0]
            converter_plan = CreateIMPTPlan(adapt_pct_name, auto_plan_name, "try_1_vct", "IMPT Demo", "Default")
            converter_plan.create_run_and_approve_IMPT_plan()


if __name__ == "__main__":
    main()
