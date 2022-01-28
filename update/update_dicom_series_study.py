
import os
import shutil

import pydicom
from pydicom.dataset import Dataset

runDicomRead = True
runDicomWrite = False

studyID = 'CBCT 2'
seriesNumber = '2'

os.chdir('C:\\Patients\\ANON1\\CBCT\\02_1.2.246.352.62.2.4617570859487105173.2989146184136452022')

for file in os.listdir():
    print(file)
    if (runDicomRead):
        dcm_header = pydicom.read_file(file, force=True)
        print(dcm_header.StudyID)
        print(dcm_header.SeriesNumber)
        if (runDicomWrite):
            dcm_header.StudyID = studyID
            dcm_header.SeriesNumber = seriesNumber
            dcm_header.save_as(file)
