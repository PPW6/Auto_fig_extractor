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
requests.packages.urllib3.disable_warnings() #Remove warning
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
        
    def getHTMLUrl(self, key_id, k):# Get the homepage url
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
    
    def getHTMLText(self, url, headers):# Access a web page and return HTML related information
        # Make a request to the target server and return a response
        try:
            r = requests.get(url, verify=False, headers=self.headers)
#            print(r)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "html.parser")
            return soup
        except:
            return ""

    def CreateFolder(self, doi_):
        if doi_ != 0: 
            file = self.output_path + '\\' + doi_
        else:
            print(file, "******NOT Exist！")
        if not os.path.exists(file):
            os.mkdir(file)
        path = os.path.abspath(file) + '\\'
        return path


    def DownloadPicture(self, url, path, doi_):# download figures
        # Visit the target URL
        soup = self.getHTMLText(url, headers = self.headers)
        # Parse the URL and extract relevant information of the target image. Note: The parsing method here is not fixed and can be used flexibly according to the actual situation.
        figure = soup.find_all('ce:figure')
        id1 = soup.find_all('coredata')
        id_ = id1[0].find_all("eid")
        id_ = id_[0].text

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
            # Parse the URL to get the download address of the target image
            imgae_down_url_2 = id_ + '-gr'+ name_ +'_lrg.jpg'
            imgae_url = self.imgae_down_url_1 + imgae_down_url_2
#            print("imgae_url: ", imgae_url)

            img_name = doi_ + '-' + name_ + ".jpg"
            para_name = doi_ + '-' + name_ + ".txt"

            img_data = requests.get(url=imgae_url, headers=self.headers)
            para_path = path + para_name
            with open(para_path, 'w', encoding = 'utf-8' ) as fb:
                fb.write(para) 
                fb.close()
            if "NOT FOUND" not in img_data.text:            
                try:
#                   print(imgae_url)
                    img_path = path + img_name                
#                   print(img_path)
                    with open(img_path, 'wb') as fp:
                        fp.write(img_data.content)              
#                   with open(r'C:\Users\PPW\Desktop\tupian\{}.jpg'.format(num),'wb') as f:
#                       f.write(r.content) #
                    print(img_name, "******Successful download 1！")
                except:
                    print(img_name, "******Failed download！")
            else:
                imgae_down_url_2 = id_ + '-gr'+ name_ +'.jpg'
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
                        print(img_name, "******Successful download 2！")
                    except:
                        print(img_name, "******Failed download！")
                else:
                    imgae_down_url_2 = id_ + '-gr'+ name_ +'.gif'
                    imgae_url = self.imgae_down_url_1 + imgae_down_url_2
#                    print(imgae_url)
                    img_name = doi_ + '-' + name_ + ".gif"
                    img_data = requests.get(url=imgae_url, headers = self.headers)
                    try:
                        img_path = path + img_name
#                        print(img_path)
                        with open(img_path, 'wb') as fp:
                            fp.write(img_data.content) 
                        print(img_name, "******Successful download 3！")
                    except:
                        print(img_name, "******Failed download！")
        if name == []:
            return print(doi_, "no figure")
        return name, para


if __name__ == "__main__":
    Path = os.getcwd()    
    start = time.time()
    xls = xlrd.open_workbook(r".\infos.xlsx")
    sht = xls.sheet_by_index(0)
    dois = sht.col_values(0)
    api_path = r".\APIkeys.txt"#Save the text of APIkey, which can be applied from https://dev.elsevier.com/
    arformat = "text/xml"  # text/xml,text/plain
    corpus_type = "article" # article/abstract
    output_path = os.path.join(Path,"graph")
    
    count = len(dois)
    articles = []
    doi_error = dict()
    start_id = dois.index('10.1016/j.jallcom.2018.04.159')
    batch_id = 1
    key_id = 0
    fd = Graph_Download(api_path, dois, corpus_type, output_path)
    
    for i in range(0, count):
        url, doi_ = fd.getHTMLUrl(key_id, i)
        print(url)    
   

        path = fd.CreateFolder(doi_)
#        print("Folder created successfully: ", path)
        name, para = fd.DownloadPicture(url, path, doi_)
#        print("description: ",name, para)
        print("No." + str(i) + "Successful download！", "Sum" + str(len(os.listdir(path))/2) + "figures")
    #Print download total time
    end = time.time()
    print("total time" + str(end - start) + "s")