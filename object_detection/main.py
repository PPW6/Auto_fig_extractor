# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 18:01:54 2023

@author: PPW
"""

import sys
sys.path.append("..")

def run():
    PATH_TO_DIR = 'images'#Target detection image folder name
    dirname = '.\object_detection'#Current folder

    from object_detection.object_detection_curve import Save_boxes_json
    ff = Save_boxes_json(PATH_TO_DIR, dirname)
    ff.boxes_and_write_json()
    
    print('-----------color decomposition-----------')
    from object_detection.color_decomposition_ import Color_decomposition
    fb = Color_decomposition(PATH_TO_DIR, dirname)
    fb.decomposition()
    print('-----------get record-----------')
    
    from object_detection.final_achieve import Origin_data_achieve
    fd = Origin_data_achieve(PATH_TO_DIR, dirname)
    fd.origin_data()

