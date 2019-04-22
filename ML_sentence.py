import nltk
import pandas as pd
from random import shuffle
import re #regexes
import sys #command line arguments
import os, os.path
import numpy as np
import string
from nltk.corpus import stopwords


#text pre-processing and tagging
from IPython.display import HTML as html_print
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


## Dictionary reading

df_dic = pd.ExcelFile( './dic/terms_dictionary.xls')
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

date_input = "" #global for date input (can be removed if we use lambdas later)
pairs = {} #global variable to count common pairs
exclude_list =  set(stopwords.words('english'))

re1='((?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'	# MMDDYYYY 1

date = re.compile(re1,re.IGNORECASE|re.DOTALL)

def concatenate_into_string(infile):
    total_text = ""
    for line in infile:
        line = line.replace('\n', ' ')
        total_text += line
    return total_text

def remove_forbidden_tokens(output, exclude_list):
    for item in exclude_list:
        output = re.sub(r""+re.escape(item)+r"", " ", output)
    return output


'''
The primary method. Takes input as a string and an exclusion list of strings and outputs a string.
'''
def preprocess(inputstr):
    output = inputstr.lower() #tolowercase
    output = re.sub(date, ' ', inputstr) #processes dates of the form MM/DD/YYYY
    
    output = re.sub(r'([+-]?\\d*\\.\\d+)(?![-+0-9\\.])', ' ', output) #remove special characters
    #output = re.sub('['+string.punctuation+']', ' ', output)
    #words = output.split(' ')
    #words = [str(convert2int(word)) for word in words]
    #output = ' '.join(words)
   #num = filter(str.isdigit, output)
 
    #output = output.replace(i,' ') #try without the number
    #output = remove_forbidden_tokens(output, exclude_list)
    output = re.sub(r" +", " ", output) #remove extraneous whitespace
    return output

def dateprocess(date):
    string = str(date)
    splitdate = string.split()[0].split('-')
    newformatted = splitdate[2] +'/'+ splitdate[1]+'/'+splitdate[0]
    return newformatted 



def cstr(s, color='black'):
    return "<text style=color:{}>{}</text>".format(color, s)

   
   
def UIsentence_extraction(df_relevant):
    Dt = 'pads pad leakage'
    try:
        rawnote = str(df_relevant['NOTE'])
    except:
        rawnote = ' '
    
    rawnote = rawnote.split('PLAN:')[0]       
    
    #content  = rawnote.lower();
    str1 = rawnote
    str1 = ' '+str1+' '
    sentences = []
    str1 = re.sub(r'[^\x00-\x7f]',r' ', str1)
    re1='(\\d+)'	# Integer Number 1
    re2='(\\.)'	# Any Single Character 1
    re3='( )'	# White Space 1
    re4='((?:[a-z][a-z]+))'	# Word 1

    rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
    str1 = re.sub(rg,r'\n', str1)
    re1='((?:[a-z][a-z]+))'	# Word 1
    re2='(:)'	# Any Single Character 1
    re3='(\\s+)'	# White Space 1
    re4 = ';'
    rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
    m = rg.search(str1)
    if m:
        str1 = re.sub(rg,'\n'+m.group(1)+':', str1)
    str1 = re.sub('\s\s\s+','\n',str1)
    str1 = str1.replace('\r', '\n')
    str1 = str1.replace('--', '\n')
    str1 = str1.replace('#', '\n')
    str1 = str1.replace('?', '\n')
    str1 = str1.replace(';', '\n')
    str1 = str1.replace(':', '\n')
    paragraphs = [p for p in str1.split('\n') if p]
    #paragraphs = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', str1)
    #paragraphs = filter(None, re.split("([A-Z][^A-Z]*)", str1))
    for paragraph in paragraphs:
        temp_sentences = sent_tokenize(paragraph)
        for term in Uterms:
            for i in range(len(temp_sentences)):
                temp_sentences[i] = temp_sentences[i].lower()
                #if term in temp_sentences[i]: ## Alternative approach: more flexible
                if re.search(r'\b' + term + r'\b', temp_sentences[i]):
                    if (term in Dt):
                      if('eye' not in temp_sentences[i]) and ('cold' not in temp_sentences[i]) and ('heating' not in temp_sentences[i]):
                        sentences.append(temp_sentences[i])
                    elif (term not in Dt):
                        sentences.append(temp_sentences[i])
    return sentences
    
