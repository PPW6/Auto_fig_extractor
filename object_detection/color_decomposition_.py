from os import walk
import os
import re
import cv2
import numpy as np
from PIL import Image
from object_detection.posterization import detect_colors
from object_detection.posterization import preprocess, rgb2hex, save_palette, get_matrix, save_cluster, save_json, get_cluster_data, data_score_mult, remove_cluster_abnormal_data

class Color_decomposition:
    def __init__(self, img_path, dirname):
        self.img_path = img_path
        self.dirname = dirname
        
    def decomposition(self):
        img_path = os.path.join(self.dirname, self.img_path)
        fnames = []
        for (dirpath, dirnames, filenames) in walk(img_path):
        	fnames.extend(filenames)
        	break
        
        images = [filename for filename in fnames if 'axis' not in filename and 'Legend' not in filename and 'png' in filename]
        legends = [filename for filename in fnames if 'Legend' in filename and 'json' in filename]
        xs = [filename for filename in fnames if 'X_axis' in filename and 'json' in filename]
        ys = [filename for filename in fnames if 'Y_axis' in filename and 'json' in filename]

        for image_name in images:
        	print(image_name)
        	legend_names = [os.path.join(img_path,legend) for legend in legends if re.match(image_name[:-4]+'_Legend', legend)]
        	x_names = [os.path.join(img_path,x) for x in xs if re.match(image_name[:-4]+'_X_axis', x)]
        	y_names = [os.path.join(img_path,y) for y in ys if re.match(image_name[:-4]+'_Y_axis', y)]
        	image_arr = preprocess(os.path.join(img_path,image_name), legend_names, x_names, y_names)
        	if (image_arr<255).any():
        		image = Image.fromarray(image_arr)
        		image.save(os.path.join(img_path,image_name)[:-4]+'_colorcut.png')
        		colorsrgb = detect_colors(image_arr)
        		print('colors: ',colorsrgb, type(colorsrgb))
        		save_palette([colorsrgb],os.path.join(img_path,image_name))
        		matrix = get_matrix(image_arr,colorsrgb)
        		for i in range(1, len(colorsrgb)): #过滤掉（1,1,1）像素点的计算节约时间
        			cluster = get_cluster_data(matrix,i)
        			cluster = remove_cluster_abnormal_data(cluster)#在这里过滤掉不合适的cluster，再进行data_score
        			if len(cluster)>160:
        				score_m = data_score_mult(cluster)
        				print('Cluster '+str(i)+' score: ', score_m)
        				if score_m > 0.66:
        					save_cluster(cluster,i,rgb2hex(colorsrgb[i]),os.path.join(img_path,image_name))
        					save_json(cluster,rgb2hex(colorsrgb[i]),i,os.path.join(img_path,image_name))
