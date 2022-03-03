# Script recorded 03 Mar 2022, 12:47:57

#   RayStation version: 12.0.110.55
#   Selected patient: ...

from connect import *

case = get_current("Case")
examination = get_current("Examination")



bounding_box = examination.Series[0].ImageStack.GetBoundingBox()

boundin_box_max = bounding_box[0]
boundin_box_min = bounding_box[1]

size = { 'x': abs(bounding_box[0].x - bounding_box[1].x), 'y': abs(bounding_box[0].y - bounding_box[1].y), 'z': abs(bounding_box[0]. - bounding_box[1].z) }


retval_0 = case.PatientModel.CreateRoi(Name="aux_FOV_CBCT", Color="Green", Type="FieldOfView", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
retval_0.CreateBoxGeometry(Size= size, Examination=examination, Center={ 'x': 0.0824999999999996, 'y': 7.6175, 'z': -1.1977288531834 }, Representation="TriangleMesh", VoxelSize=None)
