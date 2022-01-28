import json
import shutil
from os import chdir, listdir
from os.path import isdir, join

#from connect import get_current
from pydicom import read_file
from pydicom.dataset import Dataset

# def importPatient(patient, ct_config, cbct_configs, rt_dose_config, rt_struct_config):
#     patient_db = get_current('PatientDB')
#     patient_db.ImportPatientFromPath(
#         Path=r"c:/Patients/" + patient + r"/CT", SeriesOrInstances=[ct_config])
#     patient_db.ImportPatientFromPath(
#         Path=r"c:/Patients/ANON1/" + patient, SeriesOrInstances=[rt_dose_config, rt_struct_config])
#     patient_db.ImportPatientFromPath(
#         Path=r"c:/Patients/ANON1/CBCT", SeriesOrInstances=[cbct_configs])


patients_path = '/Users/comas/develop/elena/dicom_samples'
chdir(patients_path)

patient_config = {}
for patient in listdir():
    if (isdir(patient) and 'Example' in patient):
        patient_config[patient] = {}
        for file in listdir(patient):
            if (isdir(join(patient, file))):
                patient_folder = join(patient, file)
                if "CBCT" in file:
                    patient_config[patient]['cbct'] = {}
                    for cbct in listdir(patient_folder):
                        cbct_folder = join(patient_folder, cbct)
                        if isdir(cbct_folder):
                            cbct_slice = listdir(cbct_folder)[0]
                            print(cbct_slice)
                            cbct_dcm = read_file(
                                join(cbct_folder, cbct_slice), force=True)
                            patient_config[patient]['cbct'][cbct] = {'PatientID': patient, 'StudyInstanceUID': cbct_dcm.StudyInstanceUID,
                                                                     'SeriesInstanceUID': cbct_dcm.SeriesInstanceUID}
                elif "CT" in file:
                    ct_slice = listdir(patient_folder)[0]
                    print(ct_slice)
                    ct = read_file(join(patient_folder, ct_slice), force=True)
                    patient_config[patient]['ct'] = {'PatientID': patient, 'StudyInstanceUID': ct.StudyInstanceUID,
                                                     'SeriesInstanceUID': ct.SeriesInstanceUID}
                else:
                    print("Not CT or CBCT")
            else:
                if "RTSTRUCT" in file:
                    rt_struct = read_file(join(patient, file), force=True)
                    patient_config[patient]['rt_struct'] = {'PatientID': patient, 'StudyInstanceUID': rt_struct.StudyInstanceUID,
                                                            'SeriesInstanceUID': rt_struct.SeriesInstanceUID}
                elif "RTDOSE" in file:
                    rt_dose = read_file(join(patient, file), force=True)
                    patient_config[patient]['rt_dose'] = {'PatientID': patient, 'StudyInstanceUID': rt_dose.StudyInstanceUID,
                                                          'SeriesInstanceUID': rt_dose.SeriesInstanceUID}

with open("patient_info.json", "w") as outfile:
    json.dump(patient_config, outfile)
