
import os
import shutil

import pydicom
from pydicom.dataset import Dataset

runDicomRead = True
runDicomWrite = False

studyID = 'CBCT 1'
seriesNumber = '1'

os.chdir('/Users/comas/develop/elena/dicom_samples/AnonExample/CBCT/01_1.2.246.352.62.2.4727064650066947855.2549107407885888896')

for file in os.listdir():
    print(file)
    if (runDicomRead) and 'trial' in file:
        dcm_header = pydicom.read_file(file, force=True)
        print(dcm_header.StudyID)
        print(dcm_header.SeriesNumber)
        if (runDicomWrite):
            dcm_header.StudyID = studyID
            dcm_header.SeriesNumber = seriesNumber
            dcm_header.save_as('trial_' + file)
