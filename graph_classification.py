# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:30:15 2023

@author: PPW
"""

import os
import re
import shutil
from PIL import Image
from nltk.tokenize import WhitespaceTokenizer
from dictionary.dictionary import Dictionary

def graph_sure(graph_path, prop_name, scatter_path, c_path):
    word_path = get_txt(graph_path, prop_name, c_path)
    for i in range(0, len(word_path)):
        target_format = 'png'
        path_1 = os.path.join(word_path[i]+'.txt')        
        shutil.copy(path_1, scatter_path)
        path_2 = os.path.join(word_path[i]+'.jpg')
        if os.path.exists(path_2):
            img_path_png = os.path.splitext(path_2)[0] + '.' + target_format
            with Image.open(path_2) as img:
                img.save(img_path_png)
            shutil.copy(img_path_png, scatter_path)
            os.remove(img_path_png)
        path_3 = os.path.join(word_path[i]+'.gif')
        if os.path.exists(path_3):
            img_path_png = os.path.splitext(path_3)[0] + '.' + target_format
            with Image.open(path_3) as img:
                img.save(img_path_png)
            shutil.copy(img_path_png, scatter_path)
            os.remove(img_path_png)
            
def get_txt(graph_path, prop_name, c_path):
    word_path = []
    length = os.listdir(graph_path)
    for i in range(0,len(length)):
        Path = os.path.join(graph_path, length[i])
        count = int(len(os.listdir(Path))/2)
        for n in range(0, count):
            w = n+1        
            with open(os.path.join(Path, length[i]+'-'+str(w)+'.txt') ,'r',encoding='utf-8') as file:
                data = file.read()
                word = txt_sure(data, prop_name, c_path) 
                if word:                    
#                    print(length[i], 'No.', str(w)+'.txt')
                    wordpath = os.path.join(Path, length[i]+'-'+str(w))
                    word_path.append(wordpath)
    return word_path

def txt_sure(data, prop_name, c_path):
    dict_info = Dictionary(c_path)
    prop_writing_type = dict_info.prop_writing_type
    word=WhitespaceTokenizer()
    for element in prop_writing_type[prop_name]:
        data = data.replace(element, prop_name)
    word_list = word.tokenize(data)
    for word in word_list:        
        if word in prop_writing_type[prop_name]:
           return data

if __name__ == "__main__":
    PATH = os.getcwd()
    graph_path = ".\input_graph"
    c_path = r".\dictionary\dictionary.ini"
    scatter_path = ".\output_graph"
    prop_name = 'conductivity'
    fd = graph_sure(graph_path, prop_name, scatter_path, c_path)
