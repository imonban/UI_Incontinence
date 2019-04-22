
import pandas as pd
from random import shuffle
import re #regexes
import sys #command line arguments
import os, os.path
import numpy as np
import string
from nltk.corpus import stopwords



#compute the word map based on common-term dictionary
GeneralwordMap = {}
Gterms = []
with open('./dic/clever_base_terminologyv3.txt', 'r') as termFile:
    for line in termFile:
        words = line.split('|')
        GeneralwordMap[' ' + words[1].lstrip(' ').rstrip(' ') + ' '] = ' ' + words[2].replace('\n', '').lstrip(' ').rstrip(' ') + ' '
        Gterms.append(' ' + words[1].lstrip(' ').rstrip(' ') + ' ')
Gterms.sort(key = len)
Gterms.reverse()

df_dic = pd.ExcelFile('./dic/terms_dictionary.xls')
df_dic= df_dic.parse(u'terms_dictionary')
df_dic = df_dic.fillna('N/A')
#Urinary_Incontinence mapping
UIworldMap = {}
Uterms = []
UIdic = df_dic[df_dic['Type']=='Urinary_Incontinence']
Terms = UIdic['Term'].unique()
for i in Terms:
    UIworldMap[' ' + str(i).lower() + ' '] = ' ' + str(i).replace(' ', '_') + '|Urinary_Incontinence'+' '
    Uterms.append(' ' + str(i).lower() + ' ')
    #UIworldMap[' ' + str(i).lower()] = ' ' + str(i).replace(' ', '_') + '|Urinary_Incontinence'+' '
    #Uterms.append(' ' + str(i).lower())
    #UIworldMap[str(i).lower() + ' '] = ' ' + str(i).replace(' ', '_') + '|Urinary_Incontinence'+' '
    #Uterms.append( str(i).lower() + ' ')
    #UIworldMap[str(i).lower()] = ' ' + str(i).replace(' ', '_') + '|Urinary_Incontinence'+' '
    #Uterms.append(str(i).lower())
Uterms.sort(key = len)
Uterms.reverse()

def noteUIprocessing(rawnote):
    
    content  = rawnote.lower();
    str1 = content
    str1 = re.sub(r'[^\w\s]','',str1)
    
    words = str1.split(' ')
    str1 = ' '.join(words)
    str1 = ' '+str1+' '
    
    for term in Gterms:
        #str1 = str1.replace(term, cstr(GeneralwordMap[term].rstrip() +'|CLEVER ', color='red'))
        #str1 = re.sub(r'\b' + term + r'\b', GeneralwordMap[term].rstrip() +'|CLEVER ', str1)
        str1 = str1.replace(term, GeneralwordMap[term].rstrip() +'|CLEVER ')
        
    #str1 =  str1.replace(' no ', cstr('NEGEX|CLEVER ', color='red'))  
    re1='(\\s+)'	# White Space 1
    re2='(no)'	# Word 1
    re3='(\\s+)'	# White Space 2
    
    rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)

    replaced = re.sub(rg, ' NEGEX|CLEVER ', str1)
    pattern = re.compile(r'\b(' + r'|'.join(stopwords.words('english')) + r')\b\s*')
    str1 = pattern.sub(' ', replaced)
   
    
    str1 = str1.replace('\n', '<br/> ')
    
    return str1



def sentence_preprocess(data_frame_sen):
    test_snippet2 = []
    test_label = []
    for i in range(data_frame_sen.shape[0]):
        text = data_frame_sen.iloc[i]['TEXT_SNIPPET']
        if len(text.split(' '))>30:
            temp = re.split(r'\s{3,}', text)
            text_mod = ' '
            for term in Uterms:
                for i in range(len(temp)):
                    if term in temp[i] and temp[i] not in text_mod:
                        if i > 0:
                            before =temp[i-1]+' '
                        else:
                            before =' '
                        if i < len(temp)-1:
                            after =' '+temp[i+1]
                        else:
                            after =' '
                        T =  before+temp[i]+after
                        text_mod = text_mod + ' ' +T
            str1 = noteUIprocessing(text_mod)
        else:
            str1 = noteUIprocessing(text)
        str1 = str1.replace(' na ', ' NEGEX|CLEVER ')
        str1 = str1.replace(' none ', ' NEGEX|CLEVER ')
        re1='((?:[a-z][a-z]+))'	# Word 1
        re2='(\\s+)'	# White Space 1
        re3='(0|zero|Zero)'	# Integer Number 1
        re4='(\\s+)'	# White Space 2
        re5='((?:[a-z][a-z]+))'	# Word 2
        rg = re.compile(re2+re3+re4,re.IGNORECASE|re.DOTALL)
        str1 = re.sub(rg,' NEGEX|CLEVER ', str1)
        str1 = re.sub('none', ' NEGEX|CLEVER ', str1)
        str1 = re.sub('denies', ' NEGEX|CLEVER ', str1)
        str1 = re.sub('risks', ' RISK|CLEVER ', str1)
        list_str = str1.split()
        new_list = []
        for i in list_str:
            temp_list = i.split('|')
            if len(temp_list) >2:
                new_list.append(temp_list[0]+'|'+temp_list[-1])
            else:
                new_list.append(i)
        str1 = ' '.join(new_list)
        #newContent = re.sub('risk', 'RISK|CLEVER', newContent)
        
        test_snippet2.append(str1)
    
    data_frame_sen['MOD_SNIPPET'] = test_snippet2

    #clearning sentence frame
    unique_note = data_frame_sen['NOTE_DEID'].unique()

    #for each unique note find unique sentence
    for i in range(len(unique_note)):
        df_temp = data_frame_sen[data_frame_sen['NOTE_DEID']==unique_note[i]]
        df_temp = df_temp.drop_duplicates(['TEXT_SNIPPET'])
        if (i>0):
            data_frame = data_frame.append(df_temp, ignore_index=True)
        else:
            data_frame = df_temp

    data_sen_filter = data_frame[~data_frame['MOD_SNIPPET'].str.contains("eye")]
    data_sen_filter = data_sen_filter[~data_sen_filter['MOD_SNIPPET'].str.contains("colorectal")]


    ## Join condition

    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('wound') & data_sen_filter['MOD_SNIPPET'].str.contains('leakage'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('nasal'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('pen'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('cold'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('hot'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('fat'))]
    data_sen_filter =data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('toe'))]
    data_sen_filter =data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('heel'))]
    data_sen_filter =data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('leg'))]
    data_sen_filter =data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('bony'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('wound') & data_sen_filter['MOD_SNIPPET'].str.contains('pad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('wound') & data_sen_filter['MOD_SNIPPET'].str.contains('leak'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('wound') & data_sen_filter['MOD_SNIPPET'].str.contains('leakage'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('leakage') & data_sen_filter['MOD_SNIPPET'].str.contains('macula'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('leakage') & data_sen_filter['MOD_SNIPPET'].str.contains('catheter'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('crest'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('leakage') & data_sen_filter['MOD_SNIPPET'].str.contains('shoulder'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pad') & data_sen_filter['MOD_SNIPPET'].str.contains('fat'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('skin') & data_sen_filter['MOD_SNIPPET'].str.contains('incontin'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('stool') & data_sen_filter['MOD_SNIPPET'].str.contains('incontin'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('rectal') & data_sen_filter['MOD_SNIPPET'].str.contains('incontin'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('fecal incontin'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('baby') & data_sen_filter['MOD_SNIPPET'].str.contains('diaper'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('padda, suki'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('padda'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('salicylic pad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('abd pad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('metatarsal'))]
    data_sen_filter = data_sen_filter[data_sen_filter['TEXT_SNIPPET']!='#NAME?']
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('defibrillation pad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('heating pads'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('gauze pad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('adhesive pad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('ipad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('paddila'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('peripad'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('dressing'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('anastomosis'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('these include but are not limited'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('wound'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('catheter'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('defibrillator'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['MOD_SNIPPET'].str.contains('pacer pads'))]
    data_sen_filter = data_sen_filter[~(data_sen_filter['TEXT_SNIPPET'].str.contains('history and physical'))]
    data_sen_filter = data_sen_filter.reset_index(drop = True)
    return data_sen_filter
