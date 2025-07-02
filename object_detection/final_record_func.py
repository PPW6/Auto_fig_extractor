import easyocr
import cv2
from easyocr import Reader
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import math
import re
from os import walk
import os
'''
def rgb_to_hex(color):
    [r,g,b] = color
    rgb = (int(np.round(255*r)), int(np.round(255*g)), int(np.round(255*b)))
    return '#%02x%02x%02x' % rgb
'''

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_scaling(axis_json, axis_img, reader, allowlist, axis):
    box = axis_json['detected_box'][0]
    x_left = box['xmin']  
    x_right = box['xmax'] 
    y_top = box['ymin'] 
    y_bottom = box['ymax'] 
    width = box['xmax']-box['xmin']
    height = box['ymax']-box['ymin']
    
#    axis_img = cv2.copyMakeBorder(axis_img, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
    axis_img = cv2.copyMakeBorder(axis_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT,value=(255,255,255))
    
    # cv2.imshow('axis_img', axis_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    results = reader.readtext(axis_img, min_size = 5,  width_ths=0.1, mag_ratio=20, allowlist=allowlist)
    a = clean_array(results, axis)

    #visualize easyocr
    a_clean = {t[-1] for t in a}
    filtered_b = [
                    item for item in results
                    if item[1] not in ('', '-')
                    and is_float(item[1])
                    and float(item[1]) in a_clean
                ]
    img = axis_img
    for area in filtered_b:
        top_left = area[0][0]
        bottom_right = area[0][2]
        top_left = (int(top_left[0]), int(top_left[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
        img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),5)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # cv2.imwrite(os.path.join('.\images', axis_json['image_name'].split('\\')[-1][:-4] + '_see_x.png'), img, [int(cv2.IMWRITE_JPEG_QUALITY),100])

    print('axis',a,a['value'],a[axis],axis)
    if len(a) < 3 and axis == 'y':
        original_img = cv2.imread(axis_json['image_name'])
        axis_new = original_img[y_top:y_bottom,0:x_right]
        a = enlage_image(axis_new, reader, allowlist, axis)
        a = remove_arr_abnormal_data(a,axis)
        print('new_axis',a,a['value'],a[axis],axis)
    if len(a) > 2:
        a = remove_arr_abnormal_data(a,axis)
        print('remov_axis',a,a['value'],a[axis],axis)
    [a1, confidence] = well_approximated(a, axis)
    return [confidence, a1, box]

def clean_array(results, axis):
    a = np.array([])
    record = []
    m_height_box = 10
    m_width_box = 5
    for (bbox, text, prob) in results:
        if prob < 0.5:
            continue
        if text =='' or text == '.' or text == '-':
            continue
        else:
            try:
                float(text)
            except ValueError:
                continue
            (tl, tr, br, bl) = bbox
            width_box = br[0]-tl[0]
            height_box = br[1]-tl[1]
            y = tl[1]+int(height_box/2)
            x = tl[0]+int(width_box/2)
            record.append((x,y,float(text)))
            m_height_box = min(height_box, 10)
            m_width_box = min(width_box,5)
#    print(record)
    if len(record)>0:
        dtype = [('x', int), ('y', int), ('value', float)]
        a = np.array(record, dtype=dtype)
        a = np.sort(a, order=axis)
        axis2 = 'xy'.replace(axis,'')
        param_box = {'x':max(int(m_height_box/2),6), 'y':max(int(m_width_box/2),40)}
        if stats.mode(a[axis2])[1]>1:
            A_bool = [[math.isclose(i,j, abs_tol=param_box[axis]) for i in a[axis2]] for j in a[axis2]]
            rows = [stats.mode(j)[0][0] for j in A_bool]
            a = a[rows]
    return a

def lin_approx(a,axis):
    linear_model=np.polyfit(a[axis],a['value'],1)
    linear_model_fn=np.poly1d(linear_model)
    return linear_model_fn(a[axis])

def enlage_image(axis_img, reader, allowlist, axis):
    results = reader.readtext(axis_img, min_size = 5,  width_ths=0.1, mag_ratio=2, allowlist=allowlist)
    a = clean_array(results, axis)
    return a

def remove_arr_abnormal_data(arr,axis):
    """Remove the 0 point on the x-axis and the incorrectly identified points above 1000 on the y-axis."""
    if axis == 'x':
        search = []
        for n in range(0, len(arr)-1):
            if arr['value'][n-1] < arr['value'][n] > arr['value'][n+1]:
                search.append(n)    
        if len(search) != 0:
            x_arr = np.delete(arr, search[0])
        else:
            x_arr = arr 
        search_ = []
        for n in range(0, len(x_arr)-1):
            if  x_arr['value'][n] > x_arr['value'][n+1] and x_arr['value'][n-1] > x_arr['value'][n+1]:
                search_.append(n+1)    
        if len(search_) != 0:
                xx_arr = np.delete(x_arr, search_[0])
        else:
            xx_arr = x_arr
        if xx_arr['value'][0] == 0:
            new_arr = xx_arr[1:]
        else:
            new_arr = xx_arr 
    elif axis == 'y':
        if arr['value'][0] == 0:
            y_arr = arr[1:]
        else:
            y_arr = arr
        if y_arr['value'][-1] == 0:
            yy_arr = y_arr[:-1]
        else:
            yy_arr = y_arr
        search_ = []
        for n in range(1, len(yy_arr)-1):
            if yy_arr['value'][n-1] < yy_arr['value'][n] > yy_arr['value'][n+1] and yy_arr['value'][n-1] > yy_arr['value'][n+1]:
                print(n)
                search_.append(n)    
        if len(search_) != 0:
            yy_arr = np.delete(yy_arr, search_[0])
        else:
            yy_arr = yy_arr
        search = []
        for n in range(1, len(yy_arr)-1):
            if yy_arr['value'][n-1] > yy_arr['value'][n] < yy_arr['value'][n+1] and yy_arr['value'][n-1] > yy_arr['value'][n+1]:
                search.append(n)    
        if len(search) != 0:
            new_arr = np.delete(yy_arr, search[0])
        else:
            new_arr = yy_arr
    return new_arr
    
# want error of approximation for every dot to be less than 5%
def big_rel_error(arr1, arr2, axis, threshold = 0.05):
    err = np.absolute(1 - arr1/arr2) > threshold
    print('err',err)
    return err.any()

def drop_outlier(a,axis):
    err = lin_approx(a,axis) - a['value']
    a1 =  a[err**2 < max(err**2)]
    return a1

def well_approximated(a, axis):
    a1=a
    while True:
        if len(a1)>2:
            #print('long enough')
            a1 = remove_arr_abnormal_data(a1,axis)
            print('predit',lin_approx(a1,axis), a1['value'])
            if big_rel_error(lin_approx(a1,axis),a1['value'],axis):
                a1 = drop_outlier(a1,axis)
                #print('drop')
            else:
                confidence = 'confident'
                break
        else:
            confidence = 'unconfident'
            break
    return [a1, confidence]

def intersect(x1,v1,x2,v2):
    return v1-x1*(v2-v1)/(x2-x1)

def axis_rec(axis_arr, a1, box, axis):
    pix1 = a1[len(a1)//2-1][axis]
    val1 = a1[len(a1)//2-1]['value']
    pix2 = a1[len(a1)//2][axis]
    val2 = a1[len(a1)//2]['value']
    starting_pix = box[axis+'min']
    return (val2-val1)/(pix2-pix1)*axis_arr + intersect(pix1+starting_pix,val1,pix2+starting_pix,val2)

def recalc(x_a1,x_box,y_a1,y_box,cluster):
    X = np.array(cluster['coordinates'])[:,0]
    Y = np.array(cluster['coordinates'])[:,1]
    X_rec = axis_rec(X, x_a1, x_box, 'x')
    #print('X data type ', type(X_rec))
    Y_rec = axis_rec(Y, y_a1, y_box, 'y')
    #print('Y data type ', type(Y_rec))
    cluster = np.array([(float(x),float(y)) for (x,y) in zip(X_rec,Y_rec)])
    result = cluster[cluster[:, 0].argsort()].tolist()
    #print('result type', type(result))
    return result

def save_json(name, cluster_name, cluster, x_box, x_a1, y_box, y_a1):
    record = {}
    record['file_name']=name
    record['cluster_name'] = cluster_name[:-5]
    record['axes_units'] = "na"
    record['color'] = cluster['color']
    record['data'] = recalc(x_a1,x_box,y_a1,y_box,cluster)
    #print(record)
    cluster_name_out = cluster_name[:-5]+'final_record.json'
    with open(os.path.join('images',cluster_name_out), 'w') as outfile:
        json.dump(record, outfile)
    X = np.array(record['data'])[:,0]
    Y = np.array(record['data'])[:,1]
    fig = plt.figure(figsize=(8,6))
    plt.plot(X,Y,color = record['color'])
    fig.savefig(os.path.join('images',cluster_name_out)[:-4]+'png')
    plt.close('all')
