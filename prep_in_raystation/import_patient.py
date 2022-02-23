from connect import get_current

patient_db = get_current('PatientDB')


anon1_ct = {'PatientID': 'ANON1', 'StudyInstanceUID': '1.2.840.114350.2.539.2.798268.2.45009536.1', 'SeriesInstanceUID': '1.2.392.200036.9116.2.6.1.48.1221399529.1620785285.110244'}
anon1_rtstruct = {'PatientID': 'ANON1', 'StudyInstanceUID': '1.2.840.114350.2.539.2.798268.2.45009536.1', 'SeriesInstanceUID': '1.2.246.352.71.2.398328564559.181210.20210520181917'}
anon1_rtdose = {'PatientID': 'ANON1', 'StudyInstanceUID': '1.2.840.114350.2.539.2.798268.2.45009536.1', 'SeriesInstanceUID': '1.2.246.352.71.2.398328564559.179786.20210519092134'}

patient_db.ImportPatientFromPath(Path = r"c:/Patients/ANON1/CT", SeriesOrInstances = [anon1_ct])

patient = get_current('Patient')
patient.ImportDataFromPath(Path = r"c:/Patients/ANON1", CaseName = 'Case 1', SeriesOrInstances = [anon1_rtstruct,anon1_rtdose])

case = get_current('Case')
case.Examinations['CT 1'].Name = 'pCT' 






