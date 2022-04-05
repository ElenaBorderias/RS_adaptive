import json
from os import listdir
from os.path import isdir, join

from numpy import imag

from connect import get_current, CompositeAction

patients_path = "C:\\Patients"
patient_list = ["ANON38"]
imaging_system = "Generic CT"

patient_db = get_current('PatientDB')


def getPatientImportData(path):
    study_uid_data = {}
    with open(join(path, 'import_info.json')) as json_file:
        study_uid_data = json.load(json_file)
    return study_uid_data


for patient in listdir(patients_path):
    if (isdir(join(patients_path, patient)) and patient in patient_list):
        print(patient)
        import_info = getPatientImportData(join(patients_path, patient))
        print(join(patients_path, patient, "CT"))


        db_patient = get_current('Patient')
        case = get_current('Case')

        pct = case.Examinations['pCT']
        pct.EquipmentInfo.SetImagingSystemReference(
                ImagingSystemName=imaging_system)

        db_patient.Save()
        
        # cbct
        i = 1
        for cbct in import_info.get('cbct'):
            try:
                db_patient.ImportDataFromPath(Path=join(patients_path, patient, "CBCT", cbct.get('SeriesInstanceUID')), CaseName='Case 1',
                                          SeriesOrInstances=[cbct])
            except:
                print("I coulndt import CBCT" + str(i).zfill(2))

            examination_index = case.Examinations.Count - 1
            case.Examinations[examination_index].Name = "CBCT " + \
                str(i).zfill(2)
            case.Examinations[examination_index].EquipmentInfo.SetImagingSystemReference(
                ImagingSystemName=imaging_system)

            db_patient.Save()
            i = i+1
