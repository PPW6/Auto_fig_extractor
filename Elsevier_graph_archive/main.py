# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 20:16:00 2023

@author: PPW
"""

import urllib.parse 
import urllib3
import urllib.request
import json 
import requests 
import jsonpath
import ssl
from bs4 import BeautifulSoup
import time
import os
import xlrd
import re 

#ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings() #移除警告
#url = 'https://api.elsevier.com/content/article/doi/10.1016/j.msea.2020.140413?APIKey=9bfd8f6b6724d99bc749612f43a7c9a4&httpAccept=text/xml'
#url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0921509320314775-gr2.jpg'

class Graph_Download:
    def __init__(self, api_path, dois, corpus_type, output_path):
        self.api_path = api_path
        self.dois = dois
        self.corpus_type = corpus_type
        self.output_path = output_path
        self.headers = {
                'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36'
                    }
        self.imgae_down_url_1 = 'https://ars.els-cdn.com/content/image/'
        
    def getHTMLUrl(self, key_id, k):# 获得首页url
        with open(self.api_path, "r", encoding="utf-8") as api_f:
            apikeys = api_f.readlines()
        key = apikeys[key_id]
        key = key.replace("\n","")
        APIKey = "APIKey=" + key
        doi = str(self.dois[k])
        doi_ =  doi.replace("/", "-")
        arformat = "text/xml"  # text/xml,text/plain
        url = "https://api.elsevier.com/content/" + self.corpus_type + "/doi/" + doi_ + "?" + APIKey + "&httpAccept=" + arformat
        return url, doi_
    
    def getHTMLText(self, url, headers):# 访问网页并返回HTML相关的信息
        # 向目标服务器发起请求并返回响应
        try:
            r = requests.get(url, verify=False, headers=self.headers)
#            print(r)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "html.parser")
            return soup
        except:
            return ""

    def CreateFolder(self, doi_):# 创建文件夹
        if doi_ != 0: 
            file = self.output_path + '\\' + doi_  # 如果文件夹不存在，则创建文件夹
        else:
            print(file, "******不存在！")
        if not os.path.exists(file):
            os.mkdir(file)
        path = os.path.abspath(file) + '\\'
        return path


    def DownloadPicture(self, url, path, doi_):# 下载图片
        # 访问目标网址
        soup = self.getHTMLText(url, headers = self.headers)
        # 解析网址，提取目标图片相关信息，注：这里的解析方法是不固定的，可以根据实际的情况灵活使用
        figure = soup.find_all('ce:figure')
        id1 = soup.find_all('coredata')
        id_ = id1[0].find_all("eid")
        id_ = id_[0].text
        # 下载图片
        name = []
        for i in range(0, len(figure)):
            l1 = figure[i].find_all("ce:label")
            if len(l1) != 0:
                name = l1[0].text
                name_ = [word for word in name if word in re.findall('[0-9]*', word)]
                name_ = ''.join(name_)
                p1 = figure[i].find_all("ce:simple-para")
                if p1:
                    para = p1[0].text
                else:
                    continue
            # 解析网址，得到目标图片的下载地址
            imgae_down_url_2 = id_ + '-gr'+ name_ +'_lrg.jpg'  # 获取目标图片下载地址的后半部分
            imgae_url = self.imgae_down_url_1 + imgae_down_url_2  # 把目标图片地址的前后两部分拼接起来，得到完整的下载地址
#            print("imgae_url: ", imgae_url)
            # 给图片命名
            img_name = doi_ + '-' + name_ + ".jpg" # 获取img标签的alt属性，用来给保存的图片命名，图片格式为jpg       
            para_name = doi_ + '-' + name_ + ".txt"
            # 下载图片
            img_data = requests.get(url=imgae_url, headers=self.headers)
            para_path = path + para_name
            with open(para_path, 'w', encoding = 'utf-8' ) as fb:
                fb.write(para) 
                fb.close()
            if "NOT FOUND" not in img_data.text:            
            # 保存图片
                try:
#                   print(imgae_url)
                    img_path = path + img_name                
#                   print(img_path)
                    with open(img_path, 'wb') as fp:
                        fp.write(img_data.content)              
#                   with open(r'C:\Users\PPW\Desktop\tupian\{}.jpg'.format(num),'wb') as f:
#                       f.write(r.content) # 二进制
                    print(img_name, "******1下载完成！")
                except:
                    print(img_name, "******下载失败！")
            else:
                imgae_down_url_2 = id_ + '-gr'+ name_ +'.jpg'  # 获取目标图片下载地址的后半部分
                imgae_url = self.imgae_down_url_1 + imgae_down_url_2
#                print(imgae_url)
                img_name = doi_ + '-' + name_ + ".jpg"
                img_data = requests.get(url=imgae_url, headers = self.headers)
                if "NOT FOUND" not in img_data.text:  
                    try:
                        img_path = path + img_name
#                       print(img_path)
                        with open(img_path, 'wb') as fp:
                            fp.write(img_data.content) 
                        print(img_name, "******2下载完成！")
                    except:
                        print(img_name, "******下载失败！")    
                else:
                    imgae_down_url_2 = id_ + '-gr'+ name_ +'.gif'  # 获取目标图片下载地址的后半部分
                    imgae_url = self.imgae_down_url_1 + imgae_down_url_2
#                    print(imgae_url)
                    img_name = doi_ + '-' + name_ + ".gif"
                    img_data = requests.get(url=imgae_url, headers = self.headers)
                    try:
                        img_path = path + img_name
#                        print(img_path)
                        with open(img_path, 'wb') as fp:
                            fp.write(img_data.content) 
                        print(img_name, "******3下载完成！")
                    except:
                        print(img_name, "******下载失败！") 
        if name == []:
            return print(doi_, "no figure")
        return name, para

# 主函数
if __name__ == "__main__":
    Path = os.getcwd()    
    start = time.time() # 记录下载时间  
    xls = xlrd.open_workbook(r".\infos.xlsx")
    sht = xls.sheet_by_index(0)#sheet索引
    dois = sht.col_values(0)#column索引
    api_path = r".\APIkeys.txt"#保存APIkey的文本，APIkey从https://dev.elsevier.com/进行申请
    arformat = "text/xml"  # text/xml,text/plain
    corpus_type = "article" # article/abstract
    output_path = os.path.join(Path,"graph")
    
    count = len(dois)
    articles = []
    doi_error = dict()
    start_id = dois.index('10.1016/j.jallcom.2018.04.159')#为了防止网络问题断开下载，可以从这个DOI开始继续往下下载
    batch_id = 1
    key_id = 0
    fd = Graph_Download(api_path, dois, corpus_type, output_path)
    
    for i in range(0, count):# 当代码终止，将最新生成的doi所在dois中的索引（start_id）换掉这里的0
        url, doi_ = fd.getHTMLUrl(key_id, i)
        print(url)    
   
        # 创建保存数据的文件夹
        path = fd.CreateFolder(doi_)
#        print("创建文件夹成功: ", path)
        name, para = fd.DownloadPicture(url, path, doi_)
#        print("描述: ",name, para)
        print("第" + str(i) + "下载完成！", "共" + str(len(os.listdir(path))/2) + "张图片")
    # 打印下载总耗时
    end = time.time()
    print("共耗时" + str(end - start) + "秒")   