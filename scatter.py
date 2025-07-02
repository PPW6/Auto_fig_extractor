# -*- coding: utf-8 -*-
"""
Created on Thu May 25 15:16:45 2023

@author: PPW
"""

import os
import numpy as np
import orjson as json
import orjson
import shutil
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('agg')
print(matplotlib.get_backend())
from collections import defaultdict
from sklearn.cluster import KMeans, DBSCAN
import time
from sklearn import metrics
#path = os.getcwd()
#pre_text_path = ".\scatter"

def read_record(image_path):
    length = os.listdir(image_path)     
    JSONname = []
    json_record_path = []
    filename = []
    for file in length: 
        if file.endswith(".json"):             
            JSONname.append(os.path.splitext(file)[0])
#            print(JSONname)
    for name in JSONname:
        if 'record' in name and 'cluster_0' not in name:
           record_path = os.path.join(image_path,name)
           json_record_path.append(record_path)
           filename.append(name)
    return json_record_path, filename

class Data_extra: 
    def __init__(self, img_path_png, json_data, filename, scatter_path):
        self.img_path_png = img_path_png
        self.json_data = json_data
        self.filename = filename
        self.scatter_path = scatter_path
        
    def scatter_extra(self):        
        json_data = self.json_data
        origin_data = []
        for j in json_data:
            origin_data.append(json_data[j])
        t = origin_data[4]
        title = origin_data[3]
        #Get the original axis data
        x_data = []
        y_data = []
        u = []
        for n in range(0,len(t)):
            x_data.append(t[n][0])
            y_data.append(t[n][1])
        #frequency = defaultdict(int)
        #Setting the Threshold
        if len(x_data) > 30000:
            u1 = 50
            u2 = 70
        elif 10000 < len(x_data) <= 30000:
            u1 = 10
            u2 = 50
        elif 6000 < len(x_data) <= 10000:
            u1 = 8
            u2 = 40
        elif 5000 < len(x_data) <= 6000:
            u1 = 7
            u2 = 18
        elif 3500 < len(x_data) <= 5000:
            u1 = 5
            u2 = 19
        elif 1500 < len(x_data) <= 3500:
            u1 = 5
            u2 = 12 
        elif len(x_data) <= 1500:
            u1 = 3
            u2 = 5
        u.append(u1)
        u.append(u2)
        
#        elif len(x_data) <= 400:
#            u = 1
        return x_data,y_data,title,u
    
    def clear_line(self, u, x_data, y_data):#Clear lines information
        x_dup = []
        y_dup = []
        frequency = defaultdict(int)
        for m in range(0,len(x_data)):
            x_mean = x_data[m]            
            frequency[str(x_mean)] += 1
            if frequency[str(x_mean)] > u:
                y_mean = y_data[x_data.index(x_mean)]
                x_dup.append(x_mean)
                y_dup.append(y_mean)             
        #print("x_dup:",x_dup,"y_dup:",y_dup)
        return x_dup, y_dup
     
    def clear_dup(self, x_data, y_data, x_dup, y_dup):#Delete Duplicate Points
        x_del = []
        y_del = []
        if x_dup == []:
            x_del = x_data
            y_del = y_data
            #print(self.filename)
        elif x_dup != []:
            for i in x_dup:
                if i not in x_del:
            #        print(i,x_dup.index(i))        
                    x_del.append(i)
                    y_del.append(y_dup[x_dup.index(i)])
            #print(self.filename)
        #print("x_del:",x_del,"y_del:",y_del)
        return x_del, y_del
        
               
    def clear_lin(self, x_data, y_data, x_del, y_del):#Find the average of adjacent points
        x_lin = [x_del[-1]]
        y_lin = [y_del[-1]]
        for k in range(len(x_del)-1,0,-1):
            if x_del[k] >= 300:
                dis = 20
            elif 200 < x_del[k] < 300:
                dis = 10
            elif 70 < x_del[k] < 200:
                dis = 8
            elif 30 < x_del[k] < 70:
                dis = 5
            elif 18 < x_del[k] <= 30:
                dis = 1
            elif 5 < x_del[k] <= 18:
                dis = 0.3
            elif  x_del[k] <= 5:
                dis = 0.1
        #    print(k,x_del[k],x_del[k-1],abs(x_del[k-1]-x_del[k]))
            if abs(x_del[k-1]-x_del[k]) > dis:
                #print(k,x_del[k],x_del[k-1],abs(x_del[k-1]-x_del[k]))         
                x_lin.append(x_del[k])
                x_lin.append(x_del[k-1])
                y_lin.append(y_del[k])
                y_lin.append(y_del[k-1])
        x_lin.append(x_del[0])
        y_lin.append(y_del[0])
        return x_lin, y_lin
    
    def mean_line(self, x_dup, y_dup, x_lin, y_lin):
        x = list()
        y = list()
        for o in range(len(x_lin)-1, 0, -2):
#            print(o,x_lin[o],x_lin[o-1])
            if len(x_dup) > 200 and x_lin[o] != x_lin[o-1]:
                mean_x = (x_lin[o]+x_lin[o-1])/2
                mean_y = (y_lin[o]+y_lin[o-1])/2
                x.append(mean_x)
                y.append(mean_y)  
            elif len(x_dup) < 200 :
                #print(o,x_lin[o],x_lin[o-1])
                mean_x = (x_lin[o]+x_lin[o-1])/2
                mean_y = (y_lin[o]+y_lin[o-1])/2
                x.append(mean_x)
                y.append(mean_y)
        return x, y
    
    def test_Kmeans(self, X_Y):#Find the most suitable K-means
        nums = range(3, 10) #The minimum k cannot be less than 2
        # ARI Index
        SILs = []
        Distances = []
        for num in nums:
            cls = KMeans(n_clusters=num, init='k-means++')
            cls.fit(X_Y)
            predicted_labels = cls.labels_
            #Calinski-Harabaz indicator
#            CH = metrics.calinski_harabasz_score(X_Y, predicted_labels)
            #Silhouette indicator
            count = list(set(predicted_labels))
            if len(count) == len(X_Y):
                SILs.append(num)
                break
            sil = metrics.silhouette_score(X_Y, predicted_labels, metric='euclidean')
            SILs.append(sil)
            # Find the sum of the distances between each sample and the nearest cluster center
            Distances.append(cls.inertia_)
        num = nums[SILs.index(max(SILs))]
        return num
    
    def K_means(self, x_K, y_K):
        X_Y = []
        for i in range(len(x_K)):
            X_Y.append((x_K[i],  y_K[i]))
        if len(x_K) < 8:
            model = KMeans(n_clusters = len(x_K))
        elif 8 <= len(x_K):
            num= self.test_Kmeans(X_Y)    
            model = KMeans(n_clusters = num)
        model.fit(X_Y)
        pred_label = model.labels_
        centers = model.cluster_centers_
        centers = centers[np.lexsort(centers[:,::-1].T)]
        x_cent = []
        y_cent = []
        for i in range(len(centers)):
            x_cent.append(float(centers[i][0]))
            y_cent.append(float(centers[i][1]))
        return x_cent, y_cent, pred_label

    def bar_xlin(self, x_del, y_del, x_lin, y_lin):
        x, y = [], []
        x_index = []
        for n in range(0,len(x_lin),2):   
            x_index.append(x_del.index(x_lin[n]))
            x_index.append(x_del.index(x_lin[n+1]))
            x_mean = (x_lin[n]+x_lin[n+1])/2
            x.append(x_mean)
        y_label = []
        for k in range(len(x_del),0,-1):
            for n in range(0,len(x_index),2):
                if x_index[n] > k >= x_index[n+1]:
                    y_label.append({'y':y_del[k],'label':int(n/2)})
        for n in range(0, len(x)) :
            y_max = []
            for m in range (0,len(y_label)):
                if n == y_label[m]['label']:
                    y_max.append(y_label[m]['y'])
            yy_max = max(y_max)
            y.append(yy_max)
        return x, y

    def less_zero_translation(self, x, y, num):
        x = [ i - num for i in x]
        return x, y
    
    def unpack_list(self, u, x_data, y_data):
        id_ = []
        len_l = 85
        len_b = 98
        len_del = 98
        for x in range(len(x_data)):
            if x_data[x] < 70:
                id_.append(x)
        if len(id_) != 0 and x_data[0]<=15:
            id_ = id_[-1]
            x_data_l, y_data_l = x_data[:id_], y_data[:id_]
            x_data_b, y_data_b = x_data[id_:], y_data[id_:]
            x_dup_l, y_dup_l, x_del_l, y_del_l, x_lin_l, y_lin_l, x_l, y_l = self.line_data_extra(len_l, u, x_data_l, y_data_l)
            print('x_del_70:',len(x_del_l))
            if len_l >= len(x_del_l) > 40:
                x_dup_b, y_dup_b, x_del_b, y_del_b, x_lin_b, y_lin_b, x_b, y_b = self.line_data_extra(len_b, u, x_data_b, y_data_b)
                print('x_del_70_:',len(x_del_b))
                x_l, y_l, label_l = self.K_means(x_del_l, y_del_l)
                plt.scatter(x_del_l, y_del_l, c = label_l)
                x_dup, y_dup = self.splice_list(x_dup_l, y_dup_l, x_dup_b, y_dup_b)
                x_del, y_del = self.splice_list(x_del_l, y_del_l, x_del_b, y_del_b)
                x_lin, y_lin = x_lin_b, y_lin_b
                x, y = self.splice_list(x_l, y_l, x_b, y_b) 
            else:
                x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y = self.line_data_extra(len_del, u, x_data, y_data)
                print('x_del:',len(x_del))
        else:
            x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y = self.line_data_extra(len_del, u, x_data, y_data)
            print('x_del:',len(x_del))
        return x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y
    
    def splice_list(self, x_l, y_l, x_b, y_b):
        x_all = x_l + x_b
        y_all = y_l+ y_b
        return x_all, y_all
    
    def line_data_extra(self, len_, u, x_data, y_data):
        for yu in range(int(u[0]),int(u[1])):
            x_dup, y_dup = self.clear_line(yu, x_data, y_data)
            x_del, y_del = self.clear_dup(x_data, y_data, x_dup, y_dup)
            if len(x_dup) <= len(x_del):
                x_dup, y_dup = self.clear_line(yu-1, x_data, y_data)
                x_del, y_del = self.clear_dup(x_data, y_data, x_dup, y_dup)
                print('len(x_dup) <= len(x_del)',yu-1,len(x_del))
                break
            if len(x_del)<20:
                x_dup, y_dup = self.clear_line(yu-1, x_data, y_data)
                x_del, y_del = self.clear_dup(x_data, y_data, x_dup, y_dup)
                print('x_del too few',yu-1,len(x_del))
                break
            if len_ == 98:
                if len(x_del)<90:
                    x_dup, y_dup = self.clear_line(yu-1, x_data, y_data)
                    x_del, y_del = self.clear_dup(x_data, y_data, x_dup, y_dup)
                    x_lin, y_lin = self.clear_lin(x_data, y_data, x_del, y_del)
                    if any([x_lin[i-1]-x_lin[i] > 20 for i in range(len(x_lin)-1, 0, -2)])==True:
                        x_dup, y_dup = self.clear_line(yu, x_data, y_data)
                        x_del, y_del = self.clear_dup(x_data, y_data, x_dup, y_dup)
                        print('x_lin too much',yu,len(x_del))
                        break
                    if len(x_del)<120:
                        print('x_del too much',yu-1,len(x_del))
                        break
            if len(x_del)<len_:
                print('correct',yu,len_)
                break
        x_lin, y_lin = self.clear_lin(x_data, y_data, x_del, y_del)
        x, y = self.mean_line(x_dup, y_dup, x_lin, y_lin)
        return x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y
                        
    def save_line(self): #plot
        x_data,y_data,title,u= self.scatter_extra()
        if 18 < x_data[-1] <= 70:
            x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y = self.unpack_list(u, x_data, y_data)
            x, y, label = self.K_means(x_del, y_del)
        elif x_data[-1] <= 18:
            len_del = 98
            x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y = self.line_data_extra(len_del, u, x_data, y_data)
        elif x_data[-1] > 70:
            x_dup, y_dup, x_del, y_del, x_lin, y_lin, x, y = self.unpack_list(u, x_data, y_data)
        if x[0] < 0:
            num = x[0]
            x_data, y_data = self.less_zero_translation(x_data, y_data, num)
            x_dup, y_dup = self.less_zero_translation(x_dup, y_dup, num)
            x_del, y_del = self.less_zero_translation(x_del, y_del, num)
            x_lin, y_lin = self.less_zero_translation(x_lin, y_lin, num)
            x, y = self.less_zero_translation(x, y, num)
#        print(self.filename)
        print('x_data:',len(x_data),'x_dup:',len(x_dup),'x_del:',len(x_del),'x_lin:',len(x_lin),'x:',len(x))
        plt.scatter(x_data, y_data, s=0.1, c = title)
#        plt.scatter(x_dup,y_dup)
#         plt.scatter(x_del,y_del)#c ='forestgreen')
        plt.scatter(x_lin,y_lin)#c ='hotpink')
        plt.scatter(x, y, c = '#FF8C00')
        plt.title(title)
        plt.savefig(os.path.join(self.img_path_png, '{}.png'.format(self.filename)), dpi=300)
        shutil.copy(os.path.join(self.img_path_png, '{}.png'.format(self.filename)), self.scatter_path)
        key_data = {'curve_color':title,'x_data':x,'y_data':y}
        with open(os.path.join(self.img_path_png, '{}.json'.format(self.filename)), 'wb' ) as fb:
            fb.write(orjson.dumps(key_data))
#        plt.clf()#When the plt kernel is agg
        plt.show(block = False)#When the plt kernel is backend_inline
        return x, y, title

    def save_curve(self):
        json_data = self.json_data
        img_scatter_png = self.img_path_png
        name = self.filename
        origin_data = json_data['data']
        xy = sorted(origin_data, key=lambda x: x[1])
        title = json_data['color']
        x = xy[-1][0]
        y = xy[-1][1]
        # Get the original axis data
        x_data = []
        y_data = []
        for n in range(0, len(origin_data)):
            x_data.append(origin_data[n][0])
            y_data.append(origin_data[n][1])
        plt.scatter(x_data, y_data, s=0.1, c=title)
        #        plt.scatter(x_dup,y_dup)
        #        plt.scatter(x_del,y_del)#c ='forestgreen')
        #    plt.scatter(x_lin,y_lin)#c ='hotpink')
        plt.scatter(x, y, c='#FF8C00')
        plt.title(title)
        plt.savefig(os.path.join(img_scatter_png, '{}.png'.format(name)), dpi=300)
        shutil.copy(os.path.join(img_scatter_png, '{}.png'.format(name)), ".\output_graph")
        key_data = {'curve_color': title, 'x_data': x, 'y_data': y}
        with open(os.path.join(img_scatter_png, '{}.json'.format(name)), 'wb') as fb:
            fb.write(orjson.dumps(key_data))
        #        plt.clf()#When the plt kernel is agg
        plt.show(block=False)  # When the plt kernel is backend_inline
        return x, y, title
    def save_bar(self):#plot
        x_data,y_data,title,u= self.scatter_extra()
#        x_dup, y_dup = self.clear_line(u[0], x_data, y_data)
        x_dup, y_dup= [],[]
        x_del, y_del = self.clear_dup(x_data, y_data, x_dup, y_dup)
        x_lin, y_lin = self.clear_lin(x_data, y_data, x_del, y_del)
        x, y = self.bar_xlin(x_del, y_del, x_lin, y_lin)
#        print(self.filename)
        print('x_data',len(x_data),'x_dup',len(x_dup),'x_del',len(x_del))
        plt.scatter(x_data, y_data, s=0.1, c = title)
#        plt.scatter(x_dup,y_dup)
#        plt.scatter(x_del,y_del)
        plt.scatter(x, y, c = '#FF8C00')  
#        plt.title(title)
#        plt.savefig(os.path.join(self.img_path_png, '{}.png'.format(self.filename)), dpi=300)
#        shutil.copy(os.path.join(self.img_path_png, '{}.png'.format(self.filename)), self.scatter_path)
#        key_data = {'curve_color':title,'x_data':x,'y_data':y}
#        with open(os.path.join(self.img_path_png, '{}.json'.format(self.filename)), 'wb' ) as fb:
#            fb.write(orjson.dumps(key_data))
##        plt.clf()#When the plt kernel is agg
#        plt.show(block = False)#When the plt kernel is backend_inline
        return x, y, title
    
if __name__ == "__main__":
    start = time.time()
    PATH = os.getcwd()
    scatter_path = ".\output_graph"
    for n in range(1,5):
        json_record_path = '.\\object_detection\\images_key_data\\images'+str(n)
        print(json_record_path)
        json_record_path, filename = read_record(json_record_path)
        length = len(json_record_path) 
        num = 0
        for l in range(0, length):
            with open(os.path.join(json_record_path[l]+'.json'), 'r', encoding='utf8') as fp:
                json_data = json.loads(fp.read())
                name = filename[l]
                print(name)
            stats = os.stat(os.path.join(json_record_path[l]+'.json'))
            print('file_size:',stats.st_size)
            if stats.st_size < 3000000:
                img_scatter_png = ".\object_detection\scatter"
                fc = Data_extra(img_scatter_png, json_data, name, scatter_path)
                x_data, y_data, title, u = fc.scatter_extra()
                x_dup, y_dup = fc.clear_line(u[0], x_data, y_data)
                x_del, y_del = fc.clear_dup(x_data, y_data, x_dup, y_dup)
                x, y, legend_color = fc.save_line()
            if 3000000 < stats.st_size < 40000000:
                img_scatter_png = ".\object_detection\scatter"
                fc = Data_extra(img_scatter_png, json_data, name, scatter_path)
                x, y, legend_color = fc.save_bar()
            num += len(x)
        print('count:',num)
    end = time.time()
    print(f"耗时为：{end - start} s")