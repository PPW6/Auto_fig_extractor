# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 10:40:20 2023

@author: PPW
"""

import cv2
import os
import re
import math
import numpy as np
from PIL import Image
import colorspacious
import pandas as pd
import sys
import nltk
sys.path.append("..")
from dictionary.dictionary import Dictionary
from paddle_ocr.ocr import img_match
from object_detection.posterization import read_image, detect_colors, hex2rgb


def euclidean_distance(lab_color1, lab_color2):
    # Calculate the Euclidean distance between two colors in Lab space
    distance = np.linalg.norm(lab_color1 - lab_color2)
    normalized_distance = distance / math.sqrt(3 * (255**2))
    return distance


# Calculate Euclidean distance
def is_color_close(lab_color1, lab_color2, threshold):
    # Determine the proximity of two colors
    distance = euclidean_distance(lab_color1, lab_color2)
    print(lab_color1, lab_color2,distance)
    if distance < threshold:
        return True
    else:
        return False

# Convert RGB values to Lab values
def rgb2lab(colorsrgb):
    [r,g,b] = colorsrgb
    rgb = (int(np.round(255*r)), int(np.round(255*g)), int(np.round(255*b)))
#    print(rgb)
    lab_color = colorspacious.cspace_convert(rgb, "sRGB255", "CAM02-UCS")
    return lab_color

def preprocess(image_filename, legend_filenames, x_names, y_names):
    """cuts legend and all b/w objects"""
    img0 = read_image(image_filename)
    hsv0 = cv2.cvtColor(img0,cv2.COLOR_RGB2HSV)
    hsv = hsv0
    rows, cols, channels = hsv.shape
#    print(rows, cols)
    for i in range(len(hsv0)):
        for j in range(len(hsv0[0])):
            if hsv0[i,j,1] < 43 and  hsv0[i,j,2] > 130:
                hsv[i,j] = [0, 0 , 255]
            if 90 <hsv0[i,j,1] < 130 and hsv0[i,j,2] > 170:
                    hsv[i,j] = [0, 0 , 255]
            if 10 < hsv0[i,j,1] < 60 and 90 > hsv0[i,j,2] > 30:
                    hsv[i,j] = [0, 0 , 255]
            if 60 < hsv0[i,j,1] < 80 and hsv0[i,j,2] > 200:
                    hsv[i,j] = [0, 0 , 255]
    img = cv2.cvtColor(hsv,cv2.COLOR_HSV2RGB)
    return img

def get_color_text(filename, path_img, path_save, path_model, curve_color, c_path):
    boxes, txts = img_match(filename, path_img, path_save, path_model)
    print(txts)
    legend_names = []
    x_names = []
    y_names = []
    dic_col_txt = []
    [r,g,b] = hex2rgb(curve_color)
    rgb = (int(np.round(255*r)), int(np.round(255*g)), int(np.round(255*b)))
    lab_color1 = rgb2lab([r,g,b])
    legend_name = filename.split('final_record')[0]
    cv_image = preprocess(os.path.join(path_model, path_save, legend_name+'_legend.png'), legend_names, x_names, y_names)

    y_name, y_unit = y_key(txts, c_path) 
    x_name, x_unit = x_key(txts, c_path) 
    legend_names = legend_txts(txts, c_path) 
    if (cv_image<255).any():
        if len(legend_names) != 0:
            for i in range(0, len(legend_names)):   
                box = boxes[txts.index(legend_names[i])] 
                print(legend_names[i])
                # Get the selection rectangle
                x_left = int(box[0][0])  # x coordinate of the upper left corner
                x_right = int(box[1][0]) # x coordinate of the upper right corner
                y_top = int(box[0][1]) # Top y coordinate
                y_bottom = int(box[2][1]) # Bottom y coordinate
                width = x_right-x_left # Area Width
                height = y_bottom-y_top  # Area Height
                #roi = cv_image[y:y+height, x:x+width]
                if y_top<y_bottom:
                    if 3*height < x_left:
                        roi = cv_image[y_top:y_bottom, x_left-3*height:x_left]
                    else:
                        roi = cv_image[y_top:y_bottom, x_left-80:x_left]
                    image_roi = Image.fromarray(roi)
                    colorsrgb = detect_colors(roi)
                    for n in range(0,len(colorsrgb)):
                        [rn,gn,bn] = colorsrgb[n]
                        rgbn = (int(np.round(255*rn)), int(np.round(255*gn)), int(np.round(255*bn)))
                        print('1:',rgb,'2:',rgbn)
                        lab_color2 = rgb2lab(colorsrgb[n])
                        if is_color_close(lab_color1, lab_color2, threshold = 19):
                             image_roi.save(os.path.join(path_model, path_save, legend_name+'_roi_'+legend_names[i]+'.png'))
                             dic_col_txt = {'legend_name':legend_names[i], 'color':curve_color, 'x_name':x_name, 'x_unit':x_unit, 'y_name':y_name, 'y_unit':y_unit}
                             return dic_col_txt
                        else:
                            dic_col_txt = {'legend_name':None, 'color':None, 'x_name':None, 'x_unit':None, 'y_name':None, 'y_unit':None}
        if len(legend_names) == 0:
            dic_col_txt = {'legend_name':None, 'color':None, 'x_name':None, 'x_unit':None, 'y_name':None, 'y_unit':None}
    return dic_col_txt


def process(c_path, key):
    dict_info = Dictionary(c_path)
    replace_word = dict_info.replace_word
    paras_to_replace = dict_info.paras_to_replace
    for para_model, change_place in paras_to_replace.items():
            paras_all = re.findall(para_model, key)
            for para in paras_all:
                find_word = re.findall(change_place[0], para)
                para_out = para.replace(find_word[0], change_place[1])
                name = key.replace(para, para_out)
                print(key,change_place[0],para, para_out)
                key = name
    for old_word, new_word in replace_word.items():
        if old_word in key:
            name = key.replace(old_word, new_word)
            key = name
    return key

def legend_txts(txts, c_path):
    prop_name = ['alloy', 'condition']
    dict_info = Dictionary(c_path)
    legend_writing_type = dict_info.legend_writing_type
    legend_txts = []
    for i in range(0, len(txts)):
        txts[i] = process(c_path, txts[i])
    for i in range(0, len(txts)):
        for n in range(0, len(prop_name)):
            for element in legend_writing_type[prop_name[n]]:
                search = re.findall(element, txts[i])
#                
                if search:
                    print(search,element, txts[i])
                    if element == '\\W+[3-6][0-9]{2}$':
                        txts[i] = txts[i]+'°C'
                    txts[i] = txts[i].replace('/','_')
                    txts[i] = txts[i].replace(':','_')
                    legend_txts.append(txts[i])
#    print(legend_txts)
    return legend_txts
    
def y_key(txts, c_path):
    prop_name = ['conductivity', 'UTS', 'hardness']
    dict_info = Dictionary(c_path)
    prop_writing_type = dict_info.prop_writing_type
    unit_y = ['%IACS', 'MPa', 'Hv', 'GPa', 'HBW', 'MS.M-1']
    for i in range(0, len(txts)):
        for n in range(0, len(prop_name)):
            for element in prop_writing_type[prop_name[n]]:
                search = re.findall(element, txts[i])
#                print(search,element, txts[i])
                if search:
                    y_key = txts[i]
                    y_name, y_unit = xy_unit(txts, c_path, unit_y, y_key, prop_name[n])
                    return y_name, y_unit
                else:
                    y_key = None
                    y_name = None
                    y_unit = None
    return y_name, y_unit

def x_key(txts, c_path):
    process_name = ['strain','reduction', 'temperature', 'time']
    dict_info = Dictionary(c_path)
    process_writing_type = dict_info.process_writing_type
    unit_x = ['°C', 'K', '%', 'h\\s?\\W?$', 'min', 's\\s?\\W?$']
    for i in range(len(txts)-1, -1, -1):
        for n in range(0, len(process_name)):
            for element in process_writing_type[process_name[n]]:
                search = re.findall(element, txts[i])
#                print('x',process_name[n],search,element, txts[i])
                if search:
                    x_key = txts[i]
                    x_name, x_unit = xy_unit(txts, c_path, unit_x, x_key, process_name[n])
                    return x_name, x_unit
            if search == []:
                x_key = txts[-1]
                if all([re.findall('\\d+', num) for num in x_key]):
                    x_name = None
                    x_unit = None
                    continue
                x_name, x_unit = xy_unit(txts, c_path, unit_x, x_key, process_name[n])
    return x_name, x_unit

def xy_unit(txts, c_path, units, key, element):
    if any([re.findall(x, key) for x in ['t\\s?\\W+','T\\s?\\W+']]):
        element =  t_T(key, element)
    key = process(c_path, key)
    for word in units:
        search_unit = re.findall(word, key)
        if search_unit:
            unit = word
            name = element
            if any([x == word for x in ['h\\s?\\W?$','s\\s?\\W?$']]):
                unit = word[0]
            print('1',element,search_unit,word, key)
            return name, unit
    if search_unit == []:
        for u in units:
            if any([re.findall(u, process(c_path, txt)) for txt in txts]):
                unit = u
                name = element
                print('2',element,u)
                return name, unit 
        print('3', key)
        unit = None
        name = key
    return name, unit  

def t_T(x_key,element):
    if any([re.findall(x, x_key) for x in ['°C', 'K']]):
        x_key = 'temperature'
    elif any([re.findall(x, x_key) for x in ['h', 'min', 's']]):
        x_key = 'time'
    else:
        x_key = element
    return x_key

# Display color information
if __name__ == '__main__':
    PATH_TO_DIR = '..\object_detection\images'
    filename = '10.1016-j.jallcom.2020.155762-4-e.png'
    path_img = os.path.join(PATH_TO_DIR,filename)
    path_model = '..\paddle_ocr'
    path_save = 'legends'
    color1 = '#eb1013'
    c_path = "..\dictionary\dictionary.ini"
    # Open the image

    #image = Image.open('0.png') #PIL.PngImagePlugin.PngImageFile cannot be sliced, but can get point pigments
    #color = image.getpixel((10, 20))
#    cv_image = cv2.imread(path) #numpy.ndarray can be sliced
    txt = get_color_text(filename, path_img, path_save, path_model, color1, c_path)
    print(txt)
