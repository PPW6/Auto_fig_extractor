from __future__ import division
from matplotlib.image import imread
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import json
import cv2
from PIL import Image, ImageDraw
from PIL.Image import Image as Image_type
from sklearn.metrics import silhouette_score

def read_image(image):
    if type(image) is not Image_type:
        img = Image.open(image)
    else:
        img = image
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    im = np.asarray(img)
    im = im[:, :, :3]
    return im

def remove_legend(img, legend_filename):
    """given image and path to legend json record; open json record, find box with coordinates, return image without legend + 5 pixels padding"""

    f = open(legend_filename)
    data = json.load(f)
    legend_box = data['detected_box'][0]

    return cv2.rectangle(img, (legend_box['xmin']-5,legend_box['ymin']-5), (legend_box['xmax']+5,legend_box['ymax']+5), (255, 255, 255), -1)

def remove_grey(x_names, y_names):
    """given image and path to axis json record; open json record, find box with coordinates, the coordinates of the top left and bottom right of the figure panel box"""
    f_x = open(x_names[0])
    f_y = open(y_names[0])
    data_x = json.load(f_x)
    data_y = json.load(f_y)
    x_left = data_y['detected_box'][0]['xmax']
    x_right = data_x['detected_box'][0]['xmax']
    y_top = data_y['detected_box'][0]['ymin']
    y_bottom = data_x['detected_box'][0]['ymin']
    return x_left, x_right, y_top, y_bottom

def preprocess(image_filename, legend_filenames, x_names, y_names):
    """cuts legend and all b/w objects"""
    img0 = read_image(image_filename)
    hsv0 = cv2.cvtColor(img0,cv2.COLOR_RGB2HSV)
    hsv = hsv0
    rows, cols, channels = hsv.shape
    x_left, x_right, y_top, y_bottom = remove_grey(x_names, y_names)
#    print(rows, cols)
    for i in range(len(hsv0)):
        for j in range(len(hsv0[0])):
            if y_top+10 <= i <= y_bottom-5 and x_left+5 <= j <= x_right-10:
                if hsv0[i,j,1] < 43 and  hsv0[i,j,2] > 130:
                    hsv[i,j] = [0, 0 , 255]
                if 100 <hsv0[i,j,1] < 130 and hsv0[i,j,2] > 170:
                        hsv[i,j] = [0, 0 , 255]
                if 10 < hsv0[i,j,1] < 60 and 90 > hsv0[i,j,2] > 30:
                        hsv[i,j] = [0, 0 , 255]
                if 60 < hsv0[i,j,1] < 80 and hsv0[i,j,2] > 200:
                        hsv[i,j] = [0, 0 , 255]
            else:
                if hsv0[i,j,1] < 124 or hsv0[i,j,2] < 124: #S or V is close to grey or black 124
                    hsv[i,j] = [0, 0 , 255]
    img = cv2.cvtColor(hsv,cv2.COLOR_HSV2RGB)
    if len(legend_filenames)>0:
        for legend_filename in legend_filenames:
            img = remove_legend(img, legend_filename)
    return img

def test_eps(cluster):
    nums = range(33, 25, -1) 
    SILs = []
    for num in nums:
        cls = DBSCAN(eps = num, min_samples=5)
        cls.fit(cluster)
        predicted_labels = cls.labels_
        predicted_num = list(set(predicted_labels))
        print(predicted_num)
        if len(predicted_num) < 2:
            eps = 33
            return eps 
        else:
            sil = silhouette_score(cluster, predicted_labels, metric='euclidean')
            SILs.append(sil)
    max_score_index = SILs.index(max(SILs))
    eps = nums[max_score_index]
    return eps

def remove_cluster_abnormal_data(cluster, color, index, filename):
    """Remove noise from clusters"""
    eps = test_eps(cluster)
    min_samples = 5
    model = DBSCAN(eps = eps,min_samples=min_samples)
    model.fit(cluster)
    pred_label = model.labels_
    pred_label= pred_label.tolist()
    pred_label_num = list(set(pred_label))
#    print(list(set(pred_label)))
    label_max = []
    label_list =[]
    cluster_new = []

    for m in range(len(pred_label_num)):
        count = []
        for n in range(len(pred_label)):
            if pred_label[n] == pred_label_num[m]:
                count.append(n)
        label_list.append({'label_num':len(count),'label':pred_label_num[m],'index':count})
        label_max.append(len(count))
    label_max = sorted(label_max,reverse=True)
    
    for n in range(0, len(label_max)):
        max_ = label_max[n]
        for i in range(len(pred_label_num)):
            if  max_ == label_list[i]['label_num']:
                label_index = label_list[i]['index']
        cluster_n = []
        for i in range(len(label_index)):    
            cluster_n.append(cluster[label_index[i]])
        if len(cluster_n)>40:
        #Sort cluster by x from small to large
            cluster_l2h = sorted(cluster_n, key=lambda x: x[0])
            cluster_x = [cluster_l2h[x][0] for x in range(0, len(cluster_l2h))]
            cluster_x_l2h = list(set(cluster_x))
            cluster_x_l2h.sort(key=cluster_x.index)
            length = len(cluster_x_l2h)
            if length>20:
                split = 20
                step = round(length/split)
                cluster_split_x = [cluster_x_l2h[s:s+step] for s in range(0, length, step)]
                cluster_index_x = [cluster_x.index(cluster_x_l2h[s]) for s in range(0, length, step)]
                cluster_index_x.append(cluster_x.index(cluster_x_l2h[-1]))
                cluster_split = [cluster_l2h[cluster_index_x[s]:cluster_index_x[s+1]] for s in range(len(cluster_index_x)-1)]
                if [] in cluster_split:
                    cluster_split.remove([])
                cluster_y = [s[1] for s in cluster_l2h]
                high = max(cluster_y) - min(cluster_y)
                print('cluster_high', high)
                count = 0
                for m in range(0,len(cluster_split)-1):
                    H1 = abs(cluster_split[m][-1][1] - cluster_split[m][0][1])
                    H2 = abs(cluster_split[m+1][-1][1] - cluster_split[m+1][0][1])
                    print(H1,H2)
                    if H1 == H2 and H1<10 and H2<10:
                        count +=1
                if count < 10:
                    if high>80:
                        cluster_new = cluster_l2h
                        break
            else:
                high = 'too short'
        else:
                high = 'vertical'
    save_DBSCAN_json(cluster,eps,color,high,index,filename[:-4]+'_DBSCAN_')
    save_DBSCAN(cluster, cluster_new, index,pred_label, filename[:-4]+'_DBSCAN_')
    return cluster_new

def hex2rgb(hex_code):
    h = hex_code.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

def rgb2hex(color):
    [r,g,b] = color
    rgb = (int(np.round(255*r)), int(np.round(255*g)), int(np.round(255*b)))
    return '#%02x%02x%02x' % rgb

def squared_distance(p, q):
    """given points p and q returns the sum of the squares"""   
    return sum((p_i - q_i) ** 2 for p_i, q_i in zip(p, q))

def closest_index(pixels,  colors):
    """given a pixel point and a list of color points, returns the index of the closest color point"""
    return min(range(len(colors)), key=lambda i: squared_distance(pixels, colors[i]))

def get_matrix(image_array, colorsrgb):
    im = image_array[:, :, :3]/255
    return [[closest_index(pixel, colorsrgb) for pixel in row] for row in im]

def get_cluster_data(matrix,index):
    """returns list of (x,y) pixel coordinates of pixels associated with this cluster"""
    return [(j,i) for i,_ in enumerate(matrix) for j,_ in enumerate(matrix[i]) if matrix[i][j]==index]

def mean(ps):
    """given a list of points, check if the cluster is emply, return the single point
    whose first element is the average of all the first elements,
    whose second element is the average of all the second elements, and so on"""   
    n = len(ps)
    if n > 0:
        k = len(ps[0])
        mean = [sum(p[i] for p in ps) / n for i in range(k)]
    else:
        mean = None
    return mean

def average_distance(means, new_mean_set, drop_out):
    """drop out the cluster if needed, calculate the average distance in RGB space between cluster centers"""
    if len(drop_out)>0:
        means = [means[idx] for idx in range(len(means)) if idx not in drop_out]
    distances = [squared_distance(means[i],new_mean_set[i]) for i in range(len(means))]
    return np.mean(np.array([(d)**0.5 for d in distances]))

def new_means(ps, old_means):
    """given a list of points and some cluster means,
    assign each point to its closest cluster,
    and then compute the means of the new clusters and indexes of dropped clusters"""
    positions = list(range(len(old_means)))
    indexes = [closest_index(p, old_means) for p in ps]
    return [mean([p for p, i in zip(ps, indexes) if i == j]) for j in Counter(indexes).keys()], [idx for idx in positions if idx not in Counter(indexes).keys()]

def k_means(ps, num_iterations, convergence):
    """given a list of points, start with basic 8 color palette,
    then compute new_means num_iteration times or until convergence criteria is reached,
    returning the final means and convergence path"""
    #white, red, green, blue, yellow, purple, cyan, black
    means = [[0.99, 0.99, 0.99], [0.99, 0.01, 0.01], [0.01, 0.99, 0.01], [0.01, 0.01, 0.99], [0.99, 0.99, 0.01], [0.99, 0.01, 0.99], [0.01, 0.99, 0.99], [0.01, 0.01, 0.01]]
    track_convergence = []
    for i in range(num_iterations):
        drop_out = []
        new_mean_set, drop_out = new_means(ps, means)
#        print (i, new_mean_set)
        track_convergence.append(average_distance(means,new_mean_set,drop_out))
        if len(track_convergence)>2 and track_convergence[-1] < convergence and track_convergence[-2] < convergence:
            break
        else:
            means = new_mean_set
    return new_mean_set


def detect_colors(image_array,num_iterations = 12, convergence = 0.05):
    """returns image palette with cluster centers as a list of hex codes"""
    im = image_array[:, :, :3]/255
    flattened = [pixel for row in im for pixel in row]
    palette = k_means(flattened, num_iterations, convergence)
    return palette

def save_DBSCAN(cluster, cluster_new, index, colorhex, img_filename):
    """save cluster DBSCAN image"""
    fig = plt.figure()
    plt.scatter(np.array(cluster)[:,0],np.array(cluster)[:,1], s = 0.5, c=colorhex)
    if len(cluster_new) != 0:
        plt.scatter(np.array(cluster_new)[:,0],np.array(cluster_new)[:,1], s = 0.5, c='#FF8C00')
    plt.gca().invert_yaxis()
    plt.axis('off')
    fig.savefig(img_filename+str(index)+'.png', dpi=500)
    plt.cla()
    plt.clf()
    plt.close()

def save_DBSCAN_json(cluster,eps,color,high,index,img_filename):
    """write (x,y) in coordinates, palette DBSCAN eps"""
    record = {}
    record['eps'] = eps
    record['color'] = color
    record['high'] = high
    record['count'] = len(cluster)
    record['coordinates'] = cluster
    with open(img_filename+str(index)+'.json', 'w') as outfile:
        json.dump(record, outfile)

def save_cluster(cluster, index, colorhex, img_filename):
    """save cluster image"""

    fig = plt.figure()
    plt.scatter(np.array(cluster)[:,0],np.array(cluster)[:,1],s = 0.5, c=colorhex)
    plt.gca().invert_yaxis()
    plt.axis('off')
    fig.savefig(img_filename[:-4]+'_colorcut_cluster_'+str(index)+'.png')
    plt.cla()
    plt.clf()
    plt.close()

def save_json(cluster,color,index,img_filename):
    """write (x,y) in coordinates, palette colors"""
    record = {}
    record['color'] = color
    record['coordinates'] = cluster
    with open(img_filename[:-4]+'_colorcut_cluster_'+str(index)+'.json', 'w') as outfile:
        json.dump(record, outfile)

def save_palette(pixels, img_filename):
    """save the pixels"""
    plt.imsave(arr=np.array(pixels), fname=img_filename[:-4]+'_colorcut_palette.png')
    plt.cla()
    plt.clf()
    plt.close()

def ygroups(ys):
    ys_ref = range(ys[0],ys[0]+len(ys))
    if sum(np.array(ys)-ys_ref) == 0:
        ys_res = int(np.mean(ys))
        comment = ''
    else:
        dif = list(np.array(ys)-ys_ref)
        classes = list(set(dif))
        ys_res = [int(np.mean([y for i,y in enumerate(ys) if dif[i]==cl])) for cl in classes]
        comment = 'multiple'
    return [ys_res, comment]

def data_structured(cluster):
    structured = []
    Xs = np.array(cluster)[:,0]
    for ind in range(min(Xs),max(Xs)+1):
        ys = sorted([item[1] for item in cluster if item[0]==ind])
        comment = ''
        if len(ys)==0:
            comment = 'gap'
            ys_res = []
        else:
            [ys_res,comment] = ygroups(ys)
        structured.append({'x': ind, 'y': ys_res, 'c': comment})
    return structured

def data_score_mult(cluster):
    structured = data_structured(cluster)
    mults = len([entry for entry in structured if entry['c']=='multiple'])
    gaps = len([entry for entry in structured if entry['c']=='gap'])
    tot = len(structured)
    return 1-mults/(tot-gaps)
