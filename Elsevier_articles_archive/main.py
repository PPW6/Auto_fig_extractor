import requests
import xlrd
import pickle
import os

class File_Download:
    def __init__(self, api_path, dois, arformat, corpus_type, output_path):
        """

        :param api_path: r"...\APIkeys.txt"
        :param dois:
        :param arformat: text/xml,text/plain
        :param corpus_type: article/abstract
        :param output_path: r"...\txts"
        """
        with open(api_path, "r", encoding="utf-8") as api_f:
            self.apikeys = api_f.readlines()
        self.dois = dois
        self.arformat = arformat
        self.corpus_type = corpus_type
        self.header = {'Accept': 'text/xml', 'CR-TDM-Rate-Limit': '4000', 'CR-TDM-Rate-Limit-Remaining': '76',
          'CR-TDM-Rate-Limit-Reset': '1378072800'}
        self.url_publisher = "https://api.elsevier.com/content/" + self.corpus_type + "/doi/"

        self.output_path = output_path
        if self.arformat == "text/xml":
            self.end = ".xml"
        elif self.arformat == "text/plain":
            self.end = ".txt"


    def data_totxt(self,sample, path):
        f = open(path, 'w', encoding='utf-8')
        f.write(sample)
        f.close()

    def dois_read(self,path):
        with open(path, "rb") as file:
            dois = file.readlines()
        return dois

    def run(self,key_id,dois,i):
        key = self.apikeys[key_id]
        key = key.replace("\n","")
        APIKey = "APIKey=" + key
        arformat = self.arformat
        doi = str(dois[i])
        doi_ = doi.replace("\n", "")
        url = self.url_publisher + doi_ + "?" + APIKey + "&httpAccept=" + arformat
        r = requests.get(url, verify=False, headers=self.header)
        doi_ = doi_.replace("/", "-")
        print(url)
        path = os.path.join(self.output_path, doi_ + self.end)
        if "RESOURCE_NOT_FOUND" not in r.content.decode()and "AUTHENTICATION_ERROR" not in r.content.decode() and "Bad Request"  not in r.content.decode():#Unable to obtain resource
            try:
                self.data_totxt(r.content.decode(), path)
            except (OSError) as e:
                path = os.path.join(self.output_path, str(i)+ self.end)
                self.data_totxt(r.content.decode(), path)
            size = os.path.getsize(path)
            if size//1024 <3:
                key_id += 1
                doi = self.download(self.apikeys, key_id, dois, i)
        return doi



if __name__ == '__main__':

    xls = xlrd.open_workbook(r".\infos.xlsx")
    sht = xls.sheet_by_index(0)
    dois = sht.col_values(0)
    api_path = r".\APIkeys.txt"#Save the text of APIkey, which can be applied from https://dev.elsevier.com/
    arformat = "text/xml"  # text/xml,text/plain
    corpus_type = "article" # article/abstract
    output_path = r".\xmls"
    fd = File_Download(api_path, dois, arformat, corpus_type, output_path)

    count = len(dois)
    articles = []
    doi_error = dict()
    start_id = dois.index('10.1016/j.ijmachtools.2023.104047')#In order to prevent network problems from interrupting the download, you can continue downloading from this DOI
    batch_id = 1
    key_id = 0
    for i in range(0, count):# When the code terminates, replace the index (start_id) in the DOIS where the newly generated DOI is located with 0 here
        doi = fd.run(key_id,dois,i)
        print(doi)

