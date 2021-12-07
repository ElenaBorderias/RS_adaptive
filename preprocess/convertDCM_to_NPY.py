#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 15:02:59 2020

@author: margerie
"""

# import general libraries
import os
import sys
import numpy as np
import pandas as pd
from itertools import compress
from scipy.ndimage.interpolation import zoom

# import custom libraries
from Process.PatientData import *
# define source and destination folders
patient_data_path= r"../NTCP_VMAT/anon2971_added_submax"#r"../NAS_database/train_data/HAN_PT/HAN_PT_db"#DICOM"
dst=r"../NTCP_VMAT/anon2971_out"#r"../HAN_PT_npy" #NPY

# define dictionary to use
# NOTE: the dictionary must contain three columns: col 1 = raw names; 
# col 2 = 1 if the structure is relevant, 0 otherwise; col 3 = standard names
dict_path = r'./HAN_PT_dictionary_not_all_caps.xlsx'
"""
For PT or XT (AAPM challenge): TV_HIGH = ["CTV_7000"] TV_LOW = ["CTVn_5425"]
For VMAT: TV_HIGH = ["PTVp_7000","PTVnL_7000","PTVnR_7000"] TV_LOW = ["PTVnL_crop","PTVnR_crop"]
"""
TV_HIGH = ["CTV_7000"] #["PTVp_7000","PTVnL_7000","PTVnR_7000"]
TV_LOW = ["CTVn_5425"] #["PTVnL_crop","PTVnR_crop"]
value_tv_high = 70.0
value_tv_low = 54.25

def overwrite_ct_threshold(ct_image, body, artefact = None,contrast = None):
    # Change the HU out of the body to air: -1000    
    ct_image[body==0]=-1000
    if not(artefact is None):
        # Change the HU to muscle: 14
        ct_image[artefact==1]=14
    if not(contrast is None):
        # Change the HU to water: 0 Houndsfield Unit: CT unit
        ct_image[contrast==1]=0
    # Threshold above 1560HU
    ct_image[ct_image > 1560] = 1560
    return ct_image

def get_tv(roi, arrayshape):
    tv = np.zeros((arrayshape[0],arrayshape[1],arrayshape[2]))
    for c in TV_LOW:
        if c in roi:
            tv[roi[c]>0]=value_tv_low
    for c in TV_HIGH:
        if c in roi and np.count_nonzero(roi[c])>0:
            print(c)
            print(np.count_nonzero(roi[c]) )
            tv[roi[c]>0]=value_tv_high
    return tv

def get_struct_and_contoursexist(roi,array_shape):
    struct = np.zeros((array_shape[0],array_shape[1],array_shape[2]),dtype=np.int32)
    oar_names = list(roi.keys())
    # Remove the contours not linked to an OAR
    if 'Artefact' in oar_names:
        oar_names.remove('Artefact')
    if "Contrast" in oar_names:
        oar_names.remove('Contrast')
    # Remove tv contours:
    for c in TV_HIGH:
        oar_names.remove(c)
    for c in TV_LOW:      
        oar_names.remove(c)
    contoursexist = np.zeros((len(oar_names),1))
    
    for i in range(len(oar_names)):
        if(not(roi[oar_names[i]] is None)):
            contoursexist[i]=1
            struct += (2**i)*roi[oar_names[i]]
    return struct, contoursexist

def get_sample_probability(ctv):
    # get sample probability for patch-based training
    buffctv=np.zeros_like(ctv)
    buffctv[ctv!=0]=1
    m=buffctv.sum(axis=0).sum(axis=0).sum()/1000
    sample_probability_slc=(buffctv.sum(axis=0).sum(axis=0)+m)/(buffctv.sum(axis=0).sum(axis=0)+m).sum()
    sample_probability_row=(buffctv.sum(axis=1).sum(axis=1)+m)/(buffctv.sum(axis=1).sum(axis=1)+m).sum()
    sample_probability_col=(buffctv.sum(axis=0).sum(axis=-1)+m)/(buffctv.sum(axis=0).sum(axis=-1)+m).sum()
    return sample_probability_row, sample_probability_col, sample_probability_slc

def resize_TV(roi, scale, arrayshape):
    tv_resized = np.zeros((arrayshape[0],arrayshape[1],arrayshape[2]))
    for c in TV_LOW:
        if c in roi and np.count_nonzero(roi[c]):
            tv_resized[zoom(roi[c].astype(float),scale,order=1).round().astype(bool)>0]=value_tv_low
    for c in TV_HIGH:
        if c in roi and np.count_nonzero(roi[c]):
            tv_resized[zoom(roi[c].astype(float),scale,order=1).round().astype(bool)>0]=value_tv_high
    return tv_resized

def resize_STRUCT(roi, scale, arrayshape):
    struct_resized = np.zeros((arrayshape[0],arrayshape[1],arrayshape[2]),dtype=np.int32)
    oar_names = list(roi.keys())
    if 'Artefact' in oar_names:
        oar_names.remove('Artefact')
    if "Contrast" in oar_names:
        oar_names.remove('Contrast')
    # Remove tv contours:
    for c in TV_HIGH:
        oar_names.remove(c)
    for c in TV_LOW:      
        oar_names.remove(c)
    
    contoursexist = np.zeros((len(oar_names),1))
    for i in range(len(oar_names)):
        if(not(roi[oar_names[i]] is None)):
            contoursexist[i]=1
            resized_oar = zoom(roi[oar_names[i]].astype(float),scale,order=1).round().astype(bool)
            struct_resized += (2**i)*resized_oar
    return struct_resized, contoursexist


def save_resized_images(voxelsize, newvoxelsize, innerfile, dose, ct, roi, dst_dir):
    #newvoxelsize = 3
    scale = voxelsize/newvoxelsize
    ct_resized = zoom(ct,scale,order=1)
    arrayshape = ct_resized.shape
    if not os.path.exists(os.path.join(dst_dir,innerfile)):
        os.makedirs(os.path.join(dst_dir,innerfile))
    # Save CT
    np.save(os.path.join(dst_dir,innerfile,'ct.npy'),ct_resized)
    # Save Dose
    np.save(os.path.join(dst_dir,innerfile,'dose.npy'),zoom(dose,scale,order=1))
    # Save CTV
    ctv_resized = resize_TV(roi, scale=scale, arrayshape = arrayshape)
    np.save(os.path.join(dst_dir,innerfile,'ctv.npy'),ctv_resized)
    # Save Struct
    struct_resized, contoursexist = resize_STRUCT(roi, scale, arrayshape)
    np.save(os.path.join(dst_dir,innerfile,'struct.npy'),struct_resized)
    # Save contoursexist
    np.save(os.path.join(dst_dir,innerfile,'contoursexist.npy'),contoursexist)
    # Save voxelsize
    np.save(os.path.join(dst_dir,innerfile,'voxelsize.npy'),[newvoxelsize,newvoxelsize,newvoxelsize])
    # Save arrayshape
    np.save(os.path.join(dst_dir,innerfile,'arrayshape.npy'),arrayshape)
    # Save sampleprobability
    sample_probability_row, sample_probability_col, sample_probability_slc = get_sample_probability(ctv_resized)
    np.save(os.path.join(dst_dir,innerfile,'sample_probability_row.npy'),sample_probability_row)
    np.save(os.path.join(dst_dir,innerfile,'sample_probability_col.npy'),sample_probability_col)
    np.save(os.path.join(dst_dir,innerfile,'sample_probability_slc.npy'),sample_probability_slc)
    #del ct_resized, ctv_resized, struct_resized, contoursexist, sample_probability_col, sample_probability_row, sample_probability_slc 

def save_originalsize_images(voxelsize, dose, ct, roi, dst_dir):
    arrayshape = ct.shape
    if not os.path.exists(os.path.join(dst_dir,'original_ct_size')):
        os.makedirs(os.path.join(dst_dir,'original_ct_size'))
    # Save CT
    np.save(os.path.join(dst_dir,'original_ct_size','ct.npy'),ct)
    # Save Dose
    np.save(os.path.join(dst_dir,'original_ct_size','dose.npy'),dose)
    # Save CTV
    ctv = get_tv(roi,arrayshape)
    np.save(os.path.join(dst_dir,'original_ct_size','ctv.npy'),ctv)
    # Save Struct
    struct, contoursexist = get_struct_and_contoursexist(roi, arrayshape)
    np.save(os.path.join(dst_dir,'original_ct_size','struct.npy'),struct)
    # Save contoursexist
    np.save(os.path.join(dst_dir,'original_ct_size','contoursexist.npy'),contoursexist)
    # Save voxelsize
    np.save(os.path.join(dst_dir,'original_ct_size','voxelsize.npy'),voxelsize)
    # Save arrayshape
    np.save(os.path.join(dst_dir,'original_ct_size','arrayshape.npy'),arrayshape)
    # Save sampleprobability
    sample_probability_row, sample_probability_col, sample_probability_slc = get_sample_probability(ctv)
    np.save(os.path.join(dst_dir,'original_ct_size','sample_probability_row.npy'),sample_probability_row)
    np.save(os.path.join(dst_dir,'original_ct_size','sample_probability_col.npy'),sample_probability_col)
    np.save(os.path.join(dst_dir,'original_ct_size','sample_probability_slc.npy'),sample_probability_slc)
    #del struct, contoursexist, sample_probability_col, sample_probability_row, sample_probability_slc

def save_resized_beam_doses(voxelsize, newvoxelsize, innerfile, bdoses,dst_dir):
    scale = voxelsize/newvoxelsize
    for i in range(len(bdoses)):
        
        
        beam_nb = bdoses[i].beam_number
        np.save(os.path.join(dst_dir,innerfile,'beam_dose'+beam_nb+'.npy'),zoom(bdoses[i].Image,scale,order=1))
    


def get_dict(dict_path):
    """
    get dictionary in NAS/public_info
    :param : dict_path(string) location of the dictionary
    :return: dictionary in pandas format
    """
    if dict_path == 'default':
        dictionary = pd.read_excel(r'/home/ana/NAS_database/public_info/RT_dictionary.xlsx',  engine='openpyxl')
    else:
        dictionary = pd.read_excel(dict_path, engine='openpyxl')
    
    return dictionary

# get content of dictionary
dictionary = get_dict(dict_path)
relevant_struct = dictionary.iloc[:,1].tolist() # relevant structures = 1, otherwise 0 (skip)
struct_names = dictionary.iloc[:,0].tolist() # standard names

# struct_names when corresponding value in relevant_struct is 1
considered_struct = list(compress(struct_names, relevant_struct)) 


# Load patient data
Patients = PatientList() # initialize list of patient data
Patients.list_dicom_files(patient_data_path, 1) # search dicom files in the patient data folder, stores all files in the attributes (all CT images, dose file, struct file)
trainlistpatients = []
#innerfile = "resized_3mm"
for patient in Patients.list:
    roi = dict.fromkeys(considered_struct, None)  
    patient.import_patient_data()
    CT = patient.CTimages[0]
    Dose = None
    voxelsize = np.array(CT.PixelSpacing)
    arrayshape = CT.GridSize
    BDoses = []
    for i in range(len(patient.RTdoses)):
        if patient.RTdoses[i].beam_number == "PLAN":
            Dose = patient.RTdoses[i].Image
        else:
            BDoses.append(patient.RTdoses[i])
    Struct = patient.RTstructs_CT[0]
    trainlistpatients.append(patient.PatientInfo.PatientName)
    print(patient.PatientInfo.PatientName)
    # print("Nb beam doses",len(BDoses))
    if not os.path.exists(os.path.join(dst,patient.PatientInfo.PatientName)):
        os.makedirs(os.path.join(dst,patient.PatientInfo.PatientName))
    if not os.path.exists(os.path.join(dst,patient.PatientInfo.PatientName,'original_ct_size')):
        os.makedirs(os.path.join(dst,patient.PatientInfo.PatientName,'original_ct_size'))
    if not os.path.exists(os.path.join(dst,patient.PatientInfo.PatientName,"resized_1mm")):
        os.makedirs(os.path.join(dst,patient.PatientInfo.PatientName,"resized_1mm"))
    if not os.path.exists(os.path.join(dst,patient.PatientInfo.PatientName,"resized_3mm")):
        os.makedirs(os.path.join(dst,patient.PatientInfo.PatientName,"resized_3mm"))
    # Create a dictionary from 
    for contour_id in range(Struct.NumContours):
        # Deal with the patient having the "Constrast" contour, add it to the "Contrast" ROI
        if Struct.Contours[contour_id].ROIName == "Constrast":
            roi['Contrast'] = Struct.Contours[contour_id].Mask
        elif Struct.Contours[contour_id].ROIName in roi:
            roi[Struct.Contours[contour_id].ROIName] = Struct.Contours[contour_id].Mask 
        # elif Struct.Contours[contour_id].ROIName == "CTVp_7000":
        #     np.save(os.path.join(dst,patient.PatientInfo.PatientName,'original_ct_size','ctvp_7000.npy'),Struct.Contours[contour_id].Mask)
        #     newvoxelsize = 1
        #     scale = voxelsize/newvoxelsize
        #     np.save(os.path.join(dst,patient.PatientInfo.PatientName,"resized_1mm",'ctvp_7000.npy'),zoom(Struct.Contours[contour_id].Mask,scale,order=1))
        #     newvoxelsize = 2
        #     scale = voxelsize/newvoxelsize
        #     np.save(os.path.join(dst,patient.PatientInfo.PatientName,"resized_2mm",'ctvp_7000.npy'),zoom(Struct.Contours[contour_id].Mask,scale,order=1))
    # Overwrite artefact to muscle HU, contrast to water and out of body to air. Also threshold above 1560HU 
    artefact = None
    contrast = None
    if 'Artefact' in roi:
        artefact = roi['Artefact']
    if 'Contrast' in roi:
        artefact = roi['Contrast']
    ct_overwritten = overwrite_ct_threshold(CT.Image, roi['BODY'], artefact,contrast)
    # Save images original size:

    #save_originalsize_images(voxelsize, Dose, ct_overwritten, roi, os.path.join(dst,patient.PatientInfo.PatientName))
    # Save 3mm resized images:
    save_resized_images(voxelsize,3, "resized_3mm",  Dose, ct_overwritten, roi,  os.path.join(dst,patient.PatientInfo.PatientName))
    #save_resized_images(voxelsize,1, "resized_1mm",  Dose, ct_overwritten, roi,  os.path.join(dst,patient.PatientInfo.PatientName))
    #save_resized_beam_doses(voxelsize,1, "resized_1mm",  BDoses, os.path.join(dst,patient.PatientInfo.PatientName))
    for contour in Struct.Contours:
        del contour.Mask
        del contour.ContourMask
    roi.clear()
    
    del CT.Image,  patient.Plans,  roi, Dose, Struct, arrayshape,  patient.CTimages, patient #,ct_overwritten, CT,patient.Plans[0],
np.save(os.path.join(dst,'trainlistpatients.npy'),trainlistpatients)
if 'Artefact' in considered_struct:
    considered_struct.remove('Artefact')
if 'Contrast' in considered_struct:
    considered_struct.remove('Contrast')
for c in TV_HIGH:
    considered_struct.remove(c)
for c in TV_LOW:
    considered_struct.remove(c)
np.save(os.path.join(dst,'trainliststruct.npy'),considered_struct)