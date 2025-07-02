# -*- coding: utf-8 -*-
"""
Created on Mon May 15 15:45:29 2023

@author: PPW
"""


import xlrd
import os
import pandas as pd
#######################################################Part 1 Obtain requests from Elsevier and Springer########################################
from Elsevier_articles_archive.main import File_Download
from Elsevier_graph_archive.main import Graph_Download
from other_articles_archive.html_download import *
PATH = os.getcwd()
xls = pd.read_excel('CuCr_2025.xlsx', engine='openpyxl')
dois = xls['DOI'].tolist()
User_Agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36'
doi_s=[]#Springer publisher
doi_e=[] #Elsevier publisher

for i in range(0,len(dois)):     
    url_te = doi_info(dois[i]) 
#    print(i,'publisher database:',url_te[1])
#    if url_te[1]!="other database" and url_te[1]!= "Elsevier":
#        doif=dois[i]
#        doi_fe.append(doif) 
#        url_te=url_te
    if url_te[1] == "Springer":
        doisp=dois[i]
        doi_s.append(doisp)
    elif url_te[1] == "Elsevier":
        doie=dois[i]
        doi_e.append(doie)
print('Springer database',len(doi_s))
print('Elsevier database',len(doi_e))
#######################################################Part 2 Save the file########################################
#start_id_s = dois.index('10.1016/S1001-0521(07)60171-5')#In order to prevent network problems from interrupting the download, you can continue downloading from this DOI
#for j in range(0,len(doi_s)):# When the code terminates, replace the index (start_id) in doi_s where the latest generated DOI is located with 0 here
#    url_te = doi_info(doi_s[j])
#    print(j,url_te[1],'publisher database:',url_te[0])
#    output_path = r"./input_html"
#    html = getHtml(url_te,User_Agent)
#    name = doi_s[j].replace("/","-")
#    saveHtml(os.path.join(output_path,str(name)), html)
#    print(doi_s)
    
start_id_e = dois.index('10.1016/j.jmrt.2025.04.309')
for k in range(0, len(doi_e)):
    url_te = doi_info(doi_e[k])
    if url_te[1] == "Elsevier":
        doie=doi_e[k]
        doi_e.append(doie)  
        url_te=url_te
        print(k,'Elsevier数据库:',url_te[0]) 
        arformat = "text/xml"  # text/xml is in XML file format; text/plain is in plain text txt format
#        arformat = "text/plain"
        api_path = os.path.join(PATH,"./Elsevier_articles_archive/apikeys.txt")
        corpus_type = "article" # article/abstract
        key_id = 0
        output_path = os.path.join(PATH,"input_xml")
#        output_path = os.path.join(PATH,"input_txt")
        fd = File_Download(api_path, doi_e, arformat, corpus_type, output_path)
        count = len(doi_e)
        doi = fd.run(key_id,doi_e,k)
        graph_path = os.path.join(PATH,"25input_graph")
        fb = Graph_Download(api_path, doi_e, corpus_type, graph_path)
        url, doi_ = fb.getHTMLUrl(key_id, k)
        path = fb.CreateFolder(doi_)
        fb.DownloadPicture(url, path, doi_)

