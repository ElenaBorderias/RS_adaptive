from connect import get_current

patient_db = get_current('PatientDB')


anon1_ct = {'PatientID': 'ANON1', 'StudyInstanceUID': '1.2.840.114350.2.539.2.798268.2.45009536.1', 'SeriesInstanceUID': '1.2.392.200036.9116.2.6.1.48.1221399529.1620785285.110244'}
patient_db.ImportPatientFromPath(Path = r"c:/Patients/ANON1/CT", SeriesOrInstances = [anon1_ct])