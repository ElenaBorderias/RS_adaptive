import json
import shutil
from os import chdir, listdir
from os.path import isdir, join

from pydicom import read_file
from pydicom.dataset import Dataset

patients_path = '/Users/comas/develop/elena/dicom_samples'
chdir(patients_path)

patient_config = {}
for patient in listdir():
    if (isdir(patient) and '1' in patient):
        patient_config[patient] = {}
        for file in listdir(patient):
            if "RTSTRUCT" in file:
                rt_struct = read_file(join(patient, file), force=True)
                patient_config[patient]['StudyInstanceUID'] = rt_struct.StudyInstanceUID

with open("patient_study_uid.json", "w") as outfile:
    json.dump(patient_config, outfile)
