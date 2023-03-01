import json
import os
from os import mkdir
from os.path import join
from Patients import Patient

from connect import get_current
import System

export_path = "C:\\Documents\\dcm_backup_adaptive"
#patient_list = ["ANON12","ANON6","ANON16","ANON18","ANON26","ANON29","ANON34","ANON37","ANON38","ANON43"]
patient_list = ["ANON12"]

#############################################################################
############################### functions ###################################
#############################################################################

# Example on how to read the JSON error string.
def LogWarning(error):
    try:
        jsonWarnings = json.loads(str(error))
        # If the json.loads() works then the script was stopped due to
        # a non-blocking warning.
        print ("WARNING! Export Aborted!")
        print ("Comment:")
        print (jsonWarnings["Comment"])
        print ("Warnings:")

        # Here the user can handle the warnings. Continue on known warnings,
        # stop on unknown warnings.
        for w in jsonWarnings["Warnings"]:
            print (w)
    except ValueError as error:
        print ("Error occurred. Could not export.")

# The error was likely due to a blocking warning, and the details should be stated
# in the execution log.
# This prints the successful result log in an ordered way.
def LogCompleted(result):
    try:
        jsonWarnings = json.loads(str(result))
        print ("Completed!")
        print ("Comment:")
        print (jsonWarnings["Comment"])
        print ("Warnings:")
        for w in jsonWarnings["Warnings"]:
            print (w)
        print ("Export notifications:")
        # Export notifications is a list of notifications that the user should read.
        for w in jsonWarnings["Notifications"]:
            print (w)
    except ValueError as error:
        print ("Error reading completion messages.")

def ExportDCM_ct_and_RTStruct(path,examination):
    try:
        # It is not necessary to assign all of the parameters, you only need to assign the
        # desired export items. In this example we try to export with
        # IgnorePreConditionWarnings=False. This is an option to handle possible warnings.      

        result = case.ScriptableDicomExport(ExportFolderPath = path,
                                            Examinations = [examination.Name],
                                            RtStructureSetsForExaminations = [examination.Name],
                                            DicomFilter = "",
                                            IgnorePreConditionWarnings = False)

        # It is important to read the result event if the script was successful.
        # This gives the user a chance to see possible warnings that were ignored, if for
        # example the IgnorePreConditionWarnings was set to True by mistake. The result
        # also contains other notifications the user should read.
        LogCompleted(result)

    except System.InvalidOperationException as error:
        # The script failed due to warnings or errors.
        LogWarning(error)
        print ("\nTrying to export again with IgnorePreConditionWarnings=True\n")

        result = case.ScriptableDicomExport(ExportFolderPath = path,
                                            Examinations = [examination.Name],
                                            RtStructureSetsForExaminations = [examination.Name],
                                            DicomFilter = "",
                                            IgnorePreConditionWarnings = True)

        # It is very important to read the result event if the script was successful.
        # This gives the user a chance to see any warnings that have been ignored.
        LogCompleted(result)
    except Exception as e:
        print ('Except %s' % e)


def ExportDCM_plan_and_dose(path,beam_set):
    try:
        # It is not necessary to assign all of the parameters, you only need to assign the
        # desired export items. In this example we try to export with
        # IgnorePreConditionWarnings=False. This is an option to handle possible warnings.      

        result = case.ScriptableDicomExport(ExportFolderPath = path,
                                            BeamSets = beam_set_to_export,
                                            EffectiveBeamSetDoseForBeamSets = beam_set_to_export,
                                            EffectiveBeamDosesForBeamSets = beam_set_to_export,
                                            DicomFilter = "",
                                            IgnorePreConditionWarnings = False)

        # It is important to read the result event if the script was successful.
        # This gives the user a chance to see possible warnings that were ignored, if for
        # example the IgnorePreConditionWarnings was set to True by mistake. The result
        # also contains other notifications the user should read.
        LogCompleted(result)

    except System.InvalidOperationException as error:
        # The script failed due to warnings or errors.
        LogWarning(error)
        print ("\nTrying to export again with IgnorePreConditionWarnings=True\n")

        result = case.ScriptableDicomExport(ExportFolderPath = path,
                                            BeamSets = [beam_set.BeamSetIdentifier()],
                                            EffectiveBeamSetDoseForBeamSets = [beam_set.BeamSetIdentifier()],
                                            EffectiveBeamDosesForBeamSets = [beam_set.BeamSetIdentifier()],
                                            DicomFilter = "",
                                            IgnorePreConditionWarnings = True)

        # It is very important to read the result event if the script was successful.
        # This gives the user a chance to see any warnings that have been ignored.
        LogCompleted(result)
    except Exception as e:
        print ('Except %s' % e)
    

#############################################################################
############################### main ########################################
#############################################################################

for patient in patient_list:
    
    pat = Patient(patient)
    RS_Patient = pat.loadPatient()

    RS_Patient.Cases[0].SetCurrent()

    case = get_current("Case")
    patient = get_current("Patient")

    ct_names = [exam.Name for exam in case.Examinations] 
    plan_names = [plan.Name for plan in case.TreatmentPlans]
    patient_folder = join(export_path,patient)
    if not os.path.exists(patient_folder):
        mkdir(patient_folder)

    for ct in ct_names:
        #export ct_and_rt_struct in folder
        path_to_export_ct = join(patient_folder,'ct')
        if not os.path.exists(path_to_export_ct):
            mkdir(path_to_export_ct)

        ct_to_export_with_structures = patient.Examinations[ct]
        ExportDCM_ct_and_RTStruct(path_to_export_ct,ct_to_export_with_structures,"")

        if ct.startswith('corr'):
            original_cbct_name = ct[10:]
            for plan in plan_names:
                if original_cbct_name in plan:
                    path_to_export_plan = join(path_to_export_ct,plan)
                    
                    if not os.path.exists(path_to_export_plan):
                        mkdir(path_to_export_plan)
                    
                    beam_set_to_export = case.TreatmentPlans[plan].BeamSets[0]
                    ExportDCM_plan_and_dose(path_to_export_plan,"",beam_set_to_export)


        elif ct == 'pCT':
            reference_plan_name = "ML_IMPT_plan"
            path_to_export_plan = join(path_to_export_ct,reference_plan_name)
            beam_set_to_export = case.TreatmentPlans[reference_plan_name].BeamSets[0]
                    
            if not os.path.exists(path_to_export_plan):
                mkdir(path_to_export_plan)

            ExportDCM_plan_and_dose(path_to_export_plan,beam_set_to_export)

        elif ct.startswith('CBCT'):
            print("Nothing to export")
        
        else:
            print("Invalid CT name")
