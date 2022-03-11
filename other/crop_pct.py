# Script recorded 03 Mar 2022, 12:47:57

#   RayStation version: 12.0.110.55
#   Selected patient: ...

from connect import *

patient = get_current("Patient")
case = get_current("Case")
examination = case.Examinations["pCT"]

bounding_box_cbct = case.Examinations["CBCT 01"].Series[0].ImageStack.GetBoundingBox()

boundin_box_max = bounding_box_cbct[0]
boundin_box_min = bounding_box_cbct[1]

bounding_box_pct = case.Examinations["pCT"].Series[0].ImageStack.GetBoundingBox()

print("boundin_box_CBCT")
print(boundin_box_max)
print(boundin_box_min)

print("boundin_box_pCT")
print(bounding_box_pct[0])
print(bounding_box_pct[1])


new_bounding_box_min = {'x':bounding_box_pct[0].x,'y':bounding_box_pct[0].y,'z':bounding_box_cbct[0].z - 10}

print(new_bounding_box_min)

examination.CropImageStackAndStoreAsNewExamination(MinCorner=new_bounding_box_min,MaxCorner=bounding_box_pct[1])
