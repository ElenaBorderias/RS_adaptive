import json
from os import listdir
from os.path import isdir, join

from numpy import imag

from connect import get_current, CompositeAction

patients_path = "C:\\Patients"
patient_list = ["ANON6"]
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
        patient_db.ImportPatientFromPath(
            Path=join(patients_path, patient, "CT"), SeriesOrInstances=[import_info.get('ct')[0]])

        db_patient = get_current('Patient')
        case = get_current('Case')

        case.Examinations['CT 1'].Name = 'pCT'
        pct = case.Examinations['pCT']
        pct.EquipmentInfo.SetImagingSystemReference(
            ImagingSystemName=imaging_system)
        pct.DeleteLaserExportReferencePoint()

        db_patient.Save()

        db_patient.ImportDataFromPath(Path=join(patients_path, patient), CaseName='Case 1',
                                      SeriesOrInstances=[import_info.get('rt_struct'), import_info.get('rt_dose')])

        # cbct
        i = 1
        for cbct in import_info.get('cbct'):

            db_patient.ImportDataFromPath(Path=join(patients_path, patient, "CBCT", cbct.get('SeriesInstanceUID')), CaseName='Case 1',
                                          SeriesOrInstances=[cbct])

            examination_index = case.Examinations.Count - 1
            case.Examinations[examination_index].Name = "CBCT " + \
                str(i).zfill(2)
            case.Examinations[examination_index].EquipmentInfo.SetImagingSystemReference(
                ImagingSystemName=imaging_system)
            case.Examinations[examination_index].DeleteLaserExportReferencePoint()

            db_patient.Save()
            i = i+1
