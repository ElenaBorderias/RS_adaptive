import json
from connect import get_current

class Patient:
    def __init__(self, name):
        self.name = name
        self.patientInfo = ''

    def getPatientInfo(self):
        if self.patientInfo == '':
            patient_db = get_current("PatientDB")
            patientInfos = patient_db.QueryPatientInfo(
                Filter={'LastName': '^'+self.name+'$'})
            # Check that info contains exactly one item.
            if len(patientInfos) == 1:
                self.patientInfo = patientInfos[0]
            else:
                # No patient, with last name 'p' found.
                # Raise an exception.
                raise Exception(
                    "No patient or more than one patient with last \   name '{0}' in the database".format(self.name))
        return self.patientInfo

    def loadPatient(self):
        """Sets the patient as the current patient"""
        print("Loading patient: " + self.name)
        patient_db = get_current("PatientDB")
        patient = patient_db.LoadPatient(PatientInfo=self.getPatientInfo())
        return patient