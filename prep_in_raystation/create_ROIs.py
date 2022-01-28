

#CTVp_High, CTVnR_Low, CTVnL_Low, CTVp_Low

with CompositeAction('ROI algebra (CTV_54.25)'):

    retval_0 = case.PatientModel.CreateRoi(
        Name="CTV_54.25", Color="Blue", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

    retval_0.CreateAlgebraGeometry(Examination=examination, 
                        Algorithm="Auto", 
                        ExpressionA={'Operation': "Union", 'SourceRoiNames': ["CTVnL_Low"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, 
                        ExpressionB={'Operation': "Union", 'SourceRoiNames': ["CTVnR_Low", "CTVp_Low"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, 
                        ResultOperation="Union", 
                        ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})

    # CompositeAction ends
with CompositeAction('ROI algebra (CTV_7000)'):

  retval_0 = case.PatientModel.CreateRoi(Name="CTV_7000", Color="255, 128, 0", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

  retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["CTVnR_High"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["CTVp_High"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

  retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

with CompositeAction('Expand (CTV_7000+10mm)'):

  retval_0 = case.PatientModel.CreateRoi(Name="CTV_7000+10mm", Color="Red", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

  retval_0.CreateMarginGeometry(Examination=examination, SourceRoiName="CTV_7000", MarginSettings={ 'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 1, 'Posterior': 1, 'Right': 1, 'Left': 1 })

  # CompositeAction ends 


with CompositeAction('ROI algebra (CTV_5425-CTV_7000+10mm)'):

  retval_1 = case.PatientModel.CreateRoi(Name="CTV_5425-CTV_7000+10mm", Color="Red", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

  retval_1.CreateAlgebraGeometry(Examination=examination, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["CTV_54.25"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["CTV_7000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 1, 'Posterior': 1, 'Right': 1, 'Left': 1 })

  # CompositeAction ends 

with CompositeAction('ROI algebra (CTV_all)'):

  retval_0 = case.PatientModel.CreateRoi(Name="CTV_all", Color="Yellow", Type="Ctv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

  retval_0.CreateAlgebraGeometry(Examination=examination, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["CTV_5425"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["CTV_7000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
