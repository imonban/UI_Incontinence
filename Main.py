import nltk
import pandas as pd
from random import shuffle
import re #regexes
import sys #command line arguments
import os, os.path
from ML_sentence import UIsentence_extraction
from Sentence_processing import sentence_preprocess
from Text_vectorization import text_vector
from Ui_eval import processing_notes
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
name = input("Enter file path + file name ")







def word_steming(sent):
    stemmer = SnowballStemmer("english")
    #print(outputstr)
    #print exclude_list         
    words = sent.split(' ')
    words = [stemmer.stem(str(word)) for word in words]
    newContent = ' '.join([word for word in words])
    return newContent





# ## read notes

try: 
    df_relevant = pd.read_csv(name, encoding='latin1')
    print('File read')
        
except:
    print('Please give a valid corpus: single CSV file with NOTE column')
    sys.exit() 

df_relevant = df_relevant.reset_index(drop = True)

#extract sentence from the text
for i in (range(df_relevant.shape[0])):
    sentences = UIsentence_extraction(df_relevant.iloc[i])
    print(sentences)
    PAT_DEID = []
    NOTE_DEID = []
    NOTE_DATE = []
    for j in range(len(sentences)):
        PAT_DEID.append(df_relevant.iloc[i]['PAT_DEID'])
        NOTE_DEID.append(df_relevant.iloc[i]['NOTE_DEID'])
        NOTE_DATE.append(df_relevant.iloc[i]['NOTE_DATE'])
    df_frame_temp = pd.DataFrame({'PAT_DEID':PAT_DEID,'NOTE_DEID':NOTE_DEID,'NOTE_DATE':NOTE_DATE,'TEXT_SNIPPET':sentences})
    if (i>0):
        data_frame = data_frame.append(df_frame_temp, ignore_index=True)
    else:
        data_frame = df_frame_temp


## modify the sentences
data_sen_filter = sentence_preprocess(data_frame)

## vectorization of the text
X_test_word_average = text_vector(data_sen_filter)
## Load the classifier
classifier = pickle.load(open('./models/finalized_model_4.sav', 'rb'))

## Classify - sentences
p = classifier.predict(X_test_word_average)
testSentiment_2 = []



for i in range(len(p)):
    if p[i] == 1:
        testSentiment_2.append('Incontinence')
    if p[i] == 3:
        testSentiment_2.append('Negated Incontinence')   
    if p[i] == 2:
        testSentiment_2.append('Risk Incontinence')

data_sen_filter['UI Neural Label'] = testSentiment_2
annotation = []
for i in range(data_sen_filter.shape[0]):
    text = data_sen_filter.iloc[i]['TEXT_SNIPPET']
    if 'this is normal' in text:
        annotation.append('Risk Incontinence')
    elif 'incontinence is relatively uncommon' in text:
        annotation.append('Risk Incontinence')
    elif 'denies' in text:
        annotation.append('Negated Incontinence')
    elif 'no urgency, frequency' in text:
        annotation.append('Negated Incontinence')
    elif 'no leakage' in text:
        annotation.append('Negated Incontinence')  
    else:
        annotation.append(data_sen_filter.iloc[i]['UI Neural Label'])

data_sen_filter['UI Neural Label'] = annotation

data_sen_filter.to_csv('./outcome/Sentence_level_outcome.csv')

## Note level annotation


PAT_DEID = []
NOTE_DEID = []
ENCOUNTER_DATE = []
MODIFIED = []
UI_LABEL_IMPUTED = []
TEXT_SNIPPET = []
patient_id = data_sen_filter['PAT_DEID'].unique()
for patid in patient_id:
    df_patient = data_sen_filter[data_sen_filter['PAT_DEID'] == patid]
    note_id = df_patient['NOTE_DEID'].unique()
    for note in note_id:
        temp = ' '
        temp_mod = ' '
        df_note = df_patient[df_patient['NOTE_DEID']== note]
        PAT_DEID.append(patid)
        NOTE_DEID.append(note)
        ENCOUNTER_DATE.append(df_note.iloc[0]['NOTE_DATE'])
        Y_s = 0
        N_s = 0
        R_s = 0
        df_note = df_note.reset_index(drop = True)
        for i in range(df_note.shape[0]):
            if df_note.iloc[i]['TEXT_SNIPPET'] != ' ':
                temp =  temp+' '+ df_note.iloc[i]['TEXT_SNIPPET']
                temp_mod = temp_mod + ' '+ df_note.iloc[i]['MOD_SNIPPET'] 
                if(df_note.iloc[i]['UI Neural Label'] == 'Incontinence'):
                    Y_s = Y_s +1
                if(df_note.iloc[i]['UI Neural Label'] == 'Negated Incontinence'):
                    N_s = N_s +1
                if(df_note.iloc[i]['UI Neural Label'] == 'Risk Incontinence'):
                    R_s = R_s +1
        TEXT_SNIPPET.append(temp)
        MODIFIED.append(temp_mod)
        # Rule1: highest priority to incontinence
        if Y_s >= N_s and TEXT_SNIPPET !=' ':
            if Y_s >= R_s:
                UI_LABEL_IMPUTED.append('Incontinence')
            else:
                UI_LABEL_IMPUTED.append('Risk Incontinence')
        else:
            if N_s >= R_s:
                UI_LABEL_IMPUTED.append('Negated Incontinence')
            else:
                UI_LABEL_IMPUTED.append('Risk Incontinence')

df_patient_annotation = pd.DataFrame({'PAT_DEID':PAT_DEID, 'NOTE_DEID':NOTE_DEID,'ENCOUNTER_DATE':ENCOUNTER_DATE, 'MOD_SNIPPET':MODIFIED, 'TEXT_SNIPPET':TEXT_SNIPPET, 'UI_LABEL_IMPUTED':UI_LABEL_IMPUTED})

df_patient_annotation.to_csv('./outcome/Note_level_outcome.csv')

print('Saved the note level outcome!')
      
## Do the UI evaluation after treatment
response = input("Do you want to evaluate the UI rates after prostectomy? If yes, press 'Y'")

if response == 'Y':
      name_treatment = input("Enter file path + file name which stores the prostectomy dates from each patients")
      try:
          df_surgery = pd.read_csv(name_treatment)
      except:
        print('Please give a valid file: single CSV file with PAT_DEID and SURGERY_DATE column')
        sys.exit()

      df_UI = processing_notes(df_patient_annotation, df_surgery)
      df_UI.to_csv('./outcome/UI_assessment.csv')
else:
      sys.exit()
