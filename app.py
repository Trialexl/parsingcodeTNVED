import requests
import time
import pandas as pd
import os
from bs4 import BeautifulSoup





def SavePage_on_Code(code, pagecount):
    """
    Сохраняет указанное кол-во страниц с сайта по указанному коду 

    Parameters
    ----------
    :code: Код ТНВЭД
    :pagecount: Кол-во необходимых страниц
    
    """
    url = "https://www.ifcg.ru/kb/tnved/search/"
    directory = 'Files'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for pagenumber in range(pagecount):
        filename =f'{directory}/{code}_{pagenumber+1}.html'
        params = {
                'q':code,
                'sp': pagenumber+1,
                's': 'stat'
                }
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, params=params)
        time.sleep(5)
        src = response.text
        # src = 'test'

        
        with open(filename,'w') as file:
            file.write(src)
        print(filename)

def CreateDictBadCodes(endinterval, startinterval = 0):
    """
    Создает Dataframe  с кодами, которые плохо представлены в датасете
    (меньше 10 записей).
    

    Parameters
    ----------
    startinterval : с какой записи возвращать данные
    endinterval : по какую запись возвращать данные

    
    """
    df = pd.read_csv('tnveds_sort.csv',sep=';',names=['id', 'label'], dtype = {'id': str, 'label': int})
    dfBadCodes = df[df['label']<10][startinterval:endinterval]
    return dfBadCodes

def ParsingHTMLFile(code,dfproduct,pagecount = 1):
    """
    Парсит страницу и заполняент данные в Dataframe
    
    Parameters
    ----------
    code : Код ТНВЭД
    dfproduct : Dataframe для заполнения данных в процессе парсинга

    """
    
    for pagenumber in range(pagecount):
        with open(f'Files/{code}_{pagenumber+1}.html') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')   
        products =soup.findAll(class_ = 'col-xs-12 col-md-8 col-lg-10 mt10')
        
        for item in products:
            text = item.text.replace('\n','').replace('\t','')
            dfproduct.loc[len(dfproduct.index)] = [code, text] 

    
def CheckExistFileName(filename,number_of_occurrences = 0):
    
    if os.path.exists(filename):
        splitfilename, file_extension =  os.path.splitext(filename)
        number_of_occurrences += 1
        number_of_occurrences_str = f'({str(number_of_occurrences)})'
        splitfilename = str.split(splitfilename,sep='(')[0]+number_of_occurrences_str+file_extension
        
        filename = CheckExistFileName(filename=splitfilename,number_of_occurrences=number_of_occurrences)
        return filename
    else:
        
        return filename
    
    
def FixBadCode():
    pagecount = 2
    dfproduct = pd.DataFrame(columns=['Code', 'label'])
    dfBadCodes = CreateDictBadCodes(startinterval= 0, endinterval= 300)
    for badcode in dfBadCodes.itertuples():
        # SavePage_on_Code(code=badcode.id, pagecount=pagecount)
        ParsingHTMLFile(code=badcode.id, dfproduct=dfproduct, pagecount=pagecount)
    
    # SavePage_on_Code(code='0802320000',pagecount=5)
    ParsingHTMLFile(code='0802320000', dfproduct=dfproduct, pagecount=5)
    # SavePage_on_Code(code='0802310000',pagecount=5)
    ParsingHTMLFile(code='0802310000', dfproduct=dfproduct, pagecount=5)
    
    filename = 'ParsedData.csv'
    filename = CheckExistFileName(filename)
    dfproduct.to_csv(filename,sep=';',index=False,header=False)


# FixBadCode()
SavePage_on_Code(code='5208330000', pagecount=2)
        
print('done')

