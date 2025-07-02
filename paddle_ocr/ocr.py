# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 17:28:15 2023

@author: PPW
"""


import cv2
import os
from math import *
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR, draw_ocr
import math
import sys
sys.path.append("..")

def img_match(filename, img_address, path_save, path_model):
    # The multiple languages ​​currently supported by Paddleocr can be switched by modifying the lang parameter
    # ex: `ch`, `en`, `ml`, `fr`, `german`, `korean`, `japan`
    # Here use_angle_cls=False means not using a custom training set
#    ocr = PaddleOCR(use_angle_cls=False, lang="ch", use_gpu=False)
#     use_angle_cls=TrueUse the training model, the model is placed in the models directory
    ocr = PaddleOCR(use_angle_cls=True,lang="ch",
                     rec_model_dir = os.path.join(path_model,'models\ch_PP-OCRv3_rec_slim_infer'),
                     cls_model_dir = os.path.join(path_model,'models\ch_ppocr_mobile_v2.0_rec_slim_infer'),
                     det_model_dir = os.path.join(path_model,'models\ch_PP-OCRv3_det_slim_infer'), 
                     use_gpu=False)
    src_img = cv2.imread(img_address)
    if src_img is None:
        raise ValueError('Failed to read image.')
    h, w = src_img.shape[:2]
    big = int(math.sqrt(h * h + w * w))
    big_img = np.empty((big, big, src_img.ndim), np.uint8)
    yoff = round((big - h) / 2)
    xoff = round((big - w) / 2)
    big_img[yoff:yoff + h, xoff:xoff + w] = src_img
    # Text Recognition
    matRotate = cv2.getRotationMatrix2D((big * 0.5, big * 0.5), 0, 1)
    dst = cv2.warpAffine(big_img, matRotate, (big, big))
#    cv2.imshow('big_img', big_img)
    result = ocr.ocr(dst, cls=True) #dst
#    print(result)
    boxes = [[word[0] for word in line]
                for line in result][0]
    txts = [[word[1][0] for word in line]
                for line in result] [0]       
    scores = [[word[1][1] for word in line]
                for line in result][0]    
    # simsun.ttc is a very common and practical computer font, which is used as a template for recognition.
    # We use this template for text recognition
    im_show = draw_ocr(dst, boxes, txts, scores, font_path='./fonts/simsun.ttc')#dst
    im_show = Image.fromarray(im_show)
    img = np.asarray(im_show)

    # Display results
#    cv2.imshow('img', img)
    cv2.waitKey(0)
    # The image recognition results are saved in the same directory as the code
    legend_name = filename.split('final_record')[0]
#    legend_name = filename[0]
    cv2.imwrite(os.path.join(path_model, path_save, legend_name+'_result.png'), img)#img
    cv2.imwrite(os.path.join(path_model, path_save, legend_name+'_legend.png'), dst)#src_img
    # close images
    cv2.destroyAllWindows()
    pass
    return boxes, txts
 
if __name__ == '__main__':
    print("———————————————————— start ————————————————————\n")
    #Set the image path yourself. The following is my local path. Remember to replace it!!!
    path_model = '..\paddle_ocr'
    path_image = r"..\object_detection\images3\10.1016-j.msea.2017.05.114-4-a.png"
    path_save = 'legends'
    filename = '10.1016-j.msea.2017.05.114-4-a_ocr.png'
    result = img_match(filename, path_image, path_save, path_model)
    print("———————————————————— end ————————————————————\n")
