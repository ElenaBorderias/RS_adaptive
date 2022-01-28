import json
from os import listdir
from os.path import isdir, join

from connect import get_current

patients_path = '/Users/comas/develop/elena/dicom_samples'

patient_db = get_current('PatientDB')


def getPatientImportData(path):
    study_uid_data = {}
    with open(join(path, 'import_info.json')) as json_file:
        study_uid_data = json.load(json_file)
    return study_uid_data


for patient in listdir(patients_path):
    if (isdir(patient) and patient in ['']):
        import_info = getPatientImportData(join(patients_path, patient))
        patient_db.ImportPatientFromPath(
            Path=join(patients_path, patient, "CT"), SeriesOrInstances=[import_info.get('ct')])

        patient = get_current('Patient')
        patient.ImportDataFromPath(Path=join(patients_path, patient), CaseName='Case 1',
                                   SeriesOrInstances=[import_info.get('rt_struct'), import_info.get('rt_dose')])
        case = get_current('Case')
        case.Examinations['CT 1'].Name = 'pCT'

        # cbct
        for cbct in import_info.get('cbct'):
            patient.ImportDataFromPath(Path=join(patients_path, patient, cbct.get('SeriesInstanceUID')), CaseName='Case 1',
                                       SeriesOrInstances=[cbct])
