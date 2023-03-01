
import imp
from os import read
from connect import get_current
from Patients import Patient
import pandas as pd
from os.path import join
import json

def read_patient_ct_list(patient_name):
    path =  'C:\\Elena\\results_NTCP\\treatment_schedules'
    patient_path = join(path,patient_name+'_ttmt_schedule.xlsx')
    patient_info = pd.read_excel(patient_path)
    repeated_images_list = patient_info['CBCT_name']
    return repeated_images_list

def read_volume(roi_name,adaptation_image):
    case = get_current("Case")
    roi_vol = case.PatientModel.StructureSets[adaptation_image].RoiGeometries[roi_name].GetRoiVolume()
    return roi_vol

def main():
    try:
        patient = get_current("Patient")
        patient.Save()
    except:
        print("No patient loaded")

    patient_list = ["ANON6","ANON12","ANON16","ANON18","ANON26","ANON29","ANON34","ANON37","ANON38","ANON43"]
    #patient_list = ["ANON6"]
    stats_folder = "C:\\Elena\\results_NTCP\\volume_statistics"
    all_patient_results = pd.DataFrame(columns=["Patient", "Image","CTV54.25vol", "CTV70vol", "BODYvol"])

    for patient_name in patient_list:

        pat = Patient(patient_name)
        RS_Patient = pat.loadPatient()

        RS_Patient.Cases[0].SetCurrent()

        case = get_current("Case")
        patient = get_current("Patient")
        repeate_images = read_patient_ct_list(patient.Name).to_list()
        ct_list = ["pCT"] + repeate_images
        print(ct_list)
          
        #dataframe initialisations
        df_results = pd.DataFrame(columns=["Patient", "Image","CTV54.25vol", "CTV70vol", "BODYvol"])

        for i in range(len(ct_list)):

            ct = ct_list[i]
            df_results = df_results.append({'Patient' : patient.Name, 
                                'Image': ct_list[i],
                                'CTV54.25vol': read_volume("CTV_5425",ct),
                                'CTV70vol' : read_volume("CTV_7000",ct), 
                                'BODYvol': read_volume("BODY",ct)
                                },ignore_index = True)
        print(df_results)

        patient.Save()
        
        #write results
        results_file = join(stats_folder, patient.Name + "_volumes" + ".xlsx")
        df_results.to_excel(results_file, engine='openpyxl')

    all_patient_results = all_patient_results.append(df_results)

    #export results for all patients, all strategies and sum over fractions
    all_patient_results_file = join(stats_folder,"results_all_patients" + ".xlsx")
    all_patient_results.to_excel(all_patient_results_file, engine='openpyxl')

if __name__ == "__main__":
    main()
