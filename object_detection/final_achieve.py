import easyocr
import cv2
from easyocr import Reader
import json
import numpy as np
import pandas as pd
import re
from os import walk
import os
import argparse
from object_detection.final_record_func import get_scaling, save_json

class Origin_data_achieve:
    def __init__(self, img_path, dirname):
        self.img_path = img_path
        self.dirname = dirname
      
    def origin_data(self):
        img_path = os.path.join(self.dirname, self.img_path)
        parser = argparse.ArgumentParser()
        parser.add_argument('-ax','--axscale', default='xy', type=str, help='Axes to rescale. Options: x, y, xy')
        args = parser.parse_args()
        scale_mode = args.axscale
        
        reader = easyocr.Reader(['en'], gpu=True)
        allowlist = '0123456789.-'
        PATH_TO_DIR = os.getcwd()
        print(PATH_TO_DIR)
        
        fnames = []
        for (dirpath, dirnames, filenames) in walk(os.path.join(PATH_TO_DIR, img_path)):
            fnames.extend(filenames)
            break
        #print(anames)
        imgnames = [filename for filename in fnames if 'png' in filename and 'axis' not in filename and 'Legend' not in filename and 'colorcut' not in filename]
        #print(imgnames)
        axisnames = [filename for filename in fnames if 'axis' in filename and 'json' in filename]
        #print(axisnames)
        clusternames = [filename for filename in fnames if 'cluster' in filename and 'json' in filename]
        #print(clusternames)
        
        
        for i,clustername in enumerate(clusternames):
        	FILE = clustername[:-24]
        	print('FILE:',FILE)
        	f = open(os.path.join(img_path,clustername))  
        	cluster = json.load(f)
        	f.close()
        	XAXIS = [xname for xname in axisnames if re.match(FILE+'_X_axis', xname)][0]
        	YAXIS = [xname for xname in axisnames if re.match(FILE+'_Y_axis', xname)][0]
        	print(XAXIS,YAXIS)
        	f = open(os.path.join(img_path,XAXIS))
#        	print(os.path.join(img_path,XAXIS))
        	x_axis_json = json.load(f)
        	f.close()
        	x_axis_img = cv2.imread(os.path.join(img_path,XAXIS[:-4]+'png'))
#        	print(os.path.join(img_path,XAXIS[:-4]+'png'))
        	[confidence, x_a1, x_box] = get_scaling(x_axis_json, x_axis_img, reader, allowlist, 'x')
        	if confidence == 'unconfident':
        		print(i, clustername, FILE, confidence)
        		continue
        	else:
        		f = open(os.path.join(img_path,YAXIS))
#        		print(os.path.join(img_path,YAXIS))
        		y_axis_json = json.load(f)
        		f.close()
        		y_axis_img = cv2.imread(os.path.join(img_path,YAXIS[:-4]+'png'))
#        		print(os.path.join(img_path,YAXIS[:-4]+'png'))
        		[confidence, y_a1, y_box] = get_scaling(y_axis_json, y_axis_img, reader, allowlist, 'y')
			if confidence == 'unconfident':
				print(i, clustername, FILE, confidence)
				continue
			else:
				save_json(img_path, FILE, clustername, cluster, x_box, x_a1, y_box, y_a1)
				print(i, clustername, FILE, confidence)

