import json
import shutil
from os import chdir, listdir
from os.path import isdir, join

import env

from pydicom import read_file

patients_path = env.properties['patientsFolder']
chdir(patients_path)

patient_config = {}
for patient in listdir():
    if (isdir(patient) and patient in env.properties['patientFilter']):
        patient_config[patient] = {}
        for file in listdir(patient):
            if "RTSTRUCT" in file:
                rt_struct = read_file(join(patient, file), force=True)
                patient_config[patient]['StudyInstanceUID'] = rt_struct.StudyInstanceUID

with open("patient_study_uid.json", "w") as outfile:
    json.dump(patient_config, outfile)
