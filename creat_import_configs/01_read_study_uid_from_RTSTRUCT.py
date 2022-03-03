import json
import shutil
from os import chdir, listdir
from os.path import isdir, join

_f = open('creat_import_configs/env.json')

properties = json.load(_f)

_f.close()

from pydicom import read_file

patients_path = properties['patientsFolder']
chdir(patients_path)

patient_config = {}
for patient in listdir(patients_path):
    if (isdir(patient) and patient in properties['patientFilter']):
        patient_config[patient] = {}
        for file in listdir(patient):
            if "RTSTRUCT" in file:
                rt_struct = read_file(join(patient, file), force=True)
                patient_config[patient]['StudyInstanceUID'] = rt_struct.StudyInstanceUID

with open("patient_study_uid.json", "w") as outfile:
    json.dump(patient_config, outfile)
