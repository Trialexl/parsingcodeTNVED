import requests
import time
import pandas as pd
import os
from bs4 import BeautifulSoup
import json





def GetDescrFromTnved_Info(Code): 
    """
    По API api.tnved.info получаем json и сохраняем в файл 
    
    Parameters
    ----------
    code : Код ТНВЭД

    """
    url = "https://api.tnved.info/api/Search/Search"

    payload = json.dumps({
    "query": Code
    })
    headers = {
    'Content-Type': 'application/json'
    }

    directory = 'FilesJson'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename =f'{directory}/{Code}.json'
    if os.path.isfile(filename):
        return
    time.sleep(3)
    
    response = requests.request("POST", url, headers=headers, data=payload)
    src = response.text
    with open(filename,'w',encoding="utf-8") as file:
        file.write(src)
    print(filename)

def GetInfoFromJSONFile(code,dfproduct):
    """
    После сохранения json файлов через GetDescrFromTnved_Info(), 
    заполняет dfproduct
    
    Parameters
    ----------
    code : Код ТНВЭД
    dfproduct : Dataframe для заполнения данных 

    """
    filename = f'FilesJson/{code}.json'
    print(filename)
    
    if not os.path.exists(filename):
        print(f'{code}  файл не найден')
        return
        
    with open(filename,encoding='windows-1251') as file:
        src = json.load(file)
     
    if src['similar'] == None:
        print(f'{code}  нет данных')
        return
    
    for children in src['similar']: 
        dfproduct.loc[len(dfproduct.index)] = [code, children]   

        
    # codeobj = src['resultWithDescription'] [0]
    # dfproduct.loc[len(dfproduct.index)] = [code, codeobj['description'],codeobj['endDate']]   


def SavePage_on_Code(code, pagecount):
    """
    Сохраняет указанное кол-во страниц с сайта ifcg.ru по указанному коду 

    Parameters
    ----------
    :code: Код ТНВЭД
    :pagecount: Кол-во необходимых страниц
    
    """
    shiftindex = 1
    url = "https://www.ifcg.ru/kb/tnved/search/"
    directory = 'Files'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for pagenumber in range(pagecount):
        filename =f'{directory}/{code}_{pagenumber+shiftindex}.html'
        params = {
                'q':code,
                'sp': pagenumber+shiftindex,
                's': 'stat'
                }
        payload = {}
        headers = {}
        if os.path.isfile(filename):
            return
        time.sleep(3)
        response = requests.request("GET", url, headers=headers, params=params)
        src = response.text
        # src = 'test'

        
        with open(filename,'w') as file:
            file.write(src)
        print(filename)

def CreateDictBadCodes(endinterval, startinterval = 0):
    """
    Создает Dataframe  с кодами, которые плохо представлены в датасете
    

    Parameters
    ----------
    startinterval : с какой записи возвращать данные
    endinterval : по какую запись возвращать данные

    
    """
    df = pd.read_csv('tnveds_sort.csv',sep=';',names=['id', 'label'], dtype = {'id': str, 'label': int})
    dfBadCodes = df[startinterval:endinterval]
    return dfBadCodes

def ParsingHTMLFile(code,dfproduct,pagecount = 1):
    """
    После SavePage_on_Code(), парсит сохраненные в файл страницу,
    с сайта ifcg.ru и заполняент данные в Dataframe.
    
    Parameters
    ----------
    code : Код ТНВЭД
    dfproduct : Dataframe для заполнения данных в процессе парсинга

    """
    
    for pagenumber in range(pagecount):
        filename = f'Files/{code}_{pagenumber+1}.html'
        if not os.path.exists(filename):
            print(f'{code}  файл не найден')
            return
            # SavePage_on_Code(code=code, pagecount=pagecount)
            # ParsingHTMLFile(code,dfproduct,pagecount)           
        with open(filename) as file:
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
    startinterval = 0
    endinterval= 2648
    dfBadCodes = CreateDictBadCodes(startinterval= startinterval, endinterval= endinterval)
    count = startinterval
    for badcode in dfBadCodes.itertuples():
        count += 1
        print (count)
        # GetDescrFromTnved_Info(badcode.id)
        GetInfoFromJSONFile(code=badcode.id, dfproduct=dfproduct)
        # SavePage_on_Code(code=badcode.id, pagecount=pagecount)
        # ParsingHTMLFile(code=badcode.id, dfproduct=dfproduct, pagecount=pagecount)
    
    # SavePage_on_Code(code='0802320000',pagecount=5)
    # ParsingHTMLFile(code='0802320000', dfproduct=dfproduct, pagecount=5)
    # SavePage_on_Code(code='0802310000',pagecount=5)
    # ParsingHTMLFile(code='0802310000', dfproduct=dfproduct, pagecount=5)
    
    filename = 'Similar.csv'
    filename = CheckExistFileName(filename)
    dfproduct.to_csv(filename,sep=';',index=False,header=False)


FixBadCode()
# SavePage_on_Code(code='9102110000', pagecount=2)

print('done')

