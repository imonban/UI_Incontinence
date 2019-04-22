import nltk
import pandas as pd
from random import shuffle
import re #regexes
import sys #command line arguments
import os, os.path
import numpy as np
import string
import datetime 


# ## READ NLP generated annotations

# In[206]:

baseline_formatted = 0    

def Ui_annotation(list_UI, flag):
    Y_s = 0
    N_s = 0
    R_s = 0
    if (len(list_UI)>0):
        for i in range(len(list_UI)):
            if(list_UI[i] == 'Incontinence'):
                Y_s = Y_s +1
            if(list_UI[i] =='Negated Incontinence'):
                N_s = N_s +1
            if(list_UI[i] == 'Risk Incontinence'):
                R_s = R_s +1
    # Rule1: highest priority to incontinence
        if Y_s >= N_s:
            if Y_s >= R_s:
                UI_LABEL_IMPUTED = 'Incontinence'
            else:
                UI_LABEL_IMPUTED = 'Risk Incontinence'
        else:
            if N_s >= R_s:
                UI_LABEL_IMPUTED ='Negated Incontinence'
            else:
                UI_LABEL_IMPUTED= 'Risk Incontinence' 
    else:
        UI_LABEL_IMPUTED = 'N/A'
    
    return UI_LABEL_IMPUTED

def processing_notes(df_patient_annotation, Epic26_data):
    #Epic26_data = Epic26_data.fillna('N/A')
    #Epic26_data = Epic26_data[Epic26_data['PAT_DEID'] != 'N/A']
    #Epic26_data['PAT_DEID'] = Epic26_data['PAT_DEID'].astype('string')
    #df_patient_annotation['PAT_DEID'] = df_patient_annotation['PAT_DEID'].astype('string')
    df_patient_annotation['ENCOUNTER_DATE'] = pd.to_datetime(df_patient_annotation['ENCOUNTER_DATE'])
    MRN = []
    BASELINE = []
    UI_3MONTHS = []
    UI_6MONTHS = []
    UI_9MONTHS = []
    UI_12MONTHS = []
    UI_15MONTHS =[]
    UI_18MONTHS =[]
    UI_21MONTHS = []
    UI_24MONTHS = []
    no = 0
    uni_mrn = Epic26_data['PAT_DEID'].unique()
    diff_surdate = []
    labels = []
    surd_date = []
    note_date = []
    no_MRN =[]
    note_text = []
    mrn = []
    uni_mrn = list(Epic26_data['PAT_DEID'].unique())
    for i in uni_mrn:
        MRN.append(i)
        BASELINE.append(np.nan)
        UI_3MONTHS.append(np.nan)
        UI_6MONTHS.append(np.nan)
        UI_9MONTHS.append(np.nan)
        UI_12MONTHS.append(np.nan)
        UI_15MONTHS.append(np.nan)
        UI_18MONTHS.append(np.nan)
        UI_21MONTHS.append(np.nan)
        UI_24MONTHS.append(np.nan)
    
    for i in range(len(uni_mrn)):
        print(i)
        temp = df_patient_annotation[df_patient_annotation['PAT_DEID']==uni_mrn[i]]
        temp_EPIC = Epic26_data[Epic26_data['PAT_DEID']==uni_mrn[i]]
        if temp.shape[0] > 1:
            baseline = temp_EPIC.iloc[0]['SURGERY_DATE']
            date_format = '%Y-%m-%d'
        t = str(pd.to_datetime(baseline).isoformat())
        baseline_formatted = datetime.datetime.strptime(t.split('T')[0], date_format)
        def compare_dates(date):
            #global baseline_formatted
            t = str(pd.to_datetime(date).isoformat())
            current_date = datetime.datetime.strptime(t.split('T')[0], date_format)
            diff = current_date - baseline_formatted 
            return diff.days
        temp['no_days_after_sur'] = temp['ENCOUNTER_DATE'].apply(compare_dates)
        temp = temp.sort_values('no_days_after_sur')
        t_b = []
        t_3 =[]
        t_6 = []
        t_9 = []
        t_12 = []
        t_15 = []
        t_18 = []
        t_21 = []
        t_24 = []
        off_mon = 45
        T = ' '
        for j in range(temp.shape[0]):
            
            if temp.iloc[j]['TEXT_SNIPPET'] not in T:
                mrn.append(uni_mrn[i])
                diff_surdate.append(temp.iloc[j]['no_days_after_sur'])
                labels.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                note_text.append(temp.iloc[j]['TEXT_SNIPPET'])
                T = T + ' ' + temp.iloc[j]['TEXT_SNIPPET']
                note_date.append( temp.iloc[j]['ENCOUNTER_DATE'])
            ## Baseline 
                if(temp.iloc[j]['no_days_after_sur']<0 and temp.iloc[j]['no_days_after_sur']>-120): ## surg closest day days before and after
                    t_b.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']<90+30 and temp.iloc[j]['no_days_after_sur']>90-30): ## 
                    t_3.append(temp.iloc[j]['UI_LABEL_IMPUTED']) 
                if(temp.iloc[j]['no_days_after_sur']<180+45 and temp.iloc[j]['no_days_after_sur']>180-45):
                    t_6.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']<270+off_mon and temp.iloc[j]['no_days_after_sur']>270-off_mon):
                    t_9.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']<365+60 and temp.iloc[j]['no_days_after_sur']>365-60):
                    t_12.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']<450+off_mon and temp.iloc[j]['no_days_after_sur']>450-off_mon):
                    t_15.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']<540+off_mon and temp.iloc[j]['no_days_after_sur']>540-off_mon):
                    t_18.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']<630+off_mon and temp.iloc[j]['no_days_after_sur']>630-off_mon):
                    t_21.append(temp.iloc[j]['UI_LABEL_IMPUTED'])
                if(temp.iloc[j]['no_days_after_sur']>730 - 180 and temp.iloc[j]['no_days_after_sur']<810+180):
                    t_24.append(temp.iloc[j]['UI_LABEL_IMPUTED'])

                BASELINE[i] =  Ui_annotation(t_b,0)
                UI_3MONTHS[i] =  Ui_annotation(t_3, 1)
                UI_6MONTHS[i] =  Ui_annotation(t_6,1)
                if UI_6MONTHS[i]=='N/A': 
                    if UI_3MONTHS[i]== 'Negated Incontinence':
                        UI_6MONTHS[i] = 'Negated Incontinence'
                UI_9MONTHS[i] =  Ui_annotation(t_9,1)
                if UI_9MONTHS[i]=='N/A': 
                    if UI_6MONTHS[i]== 'Negated Incontinence':
                        UI_9MONTHS[i] = 'Negated Incontinence'
                UI_12MONTHS[i] =  Ui_annotation(t_12,1)
                if UI_12MONTHS[i]=='N/A': 
                    if UI_9MONTHS[i]== 'Negated Incontinence':
                        UI_12MONTHS[i] = 'Negated Incontinence' 
                UI_15MONTHS[i] =  Ui_annotation(t_15,1)
                if UI_15MONTHS[i]=='N/A': 
                    if UI_12MONTHS[i]== 'Negated Incontinence':
                        UI_15MONTHS[i] = 'Negated Incontinence'
                UI_18MONTHS[i] =  Ui_annotation(t_18,1)
                if UI_18MONTHS[i]=='N/A': 
                    if UI_15MONTHS[i]== 'Negated Incontinence':
                        UI_18MONTHS[i] = 'Negated Incontinence'
                UI_21MONTHS[i] =  Ui_annotation(t_21,1)
                if UI_21MONTHS[i]=='N/A': 
                    if UI_18MONTHS[i]== 'Negated Incontinence':
                        UI_21MONTHS[i] = 'Negated Incontinence'
                UI_24MONTHS[i] =  Ui_annotation(t_24,1)
                if UI_24MONTHS[i]=='N/A': 
                    if UI_21MONTHS[i]== 'Negated Incontinence':
                        UI_24MONTHS[i] = 'Negated Incontinence'
            else:
                no_MRN.append(uni_mrn[i])


    df_longitudinal_label = pd.DataFrame({'PAT_DEID':MRN, 'BASELINE': BASELINE, 'UI_3MONTHS':UI_3MONTHS, 'UI_6MONTHS':UI_6MONTHS, 'UI_9MONTHS':UI_9MONTHS, 'UI_12MONTHS':UI_12MONTHS, 'UI_15MONTHS':UI_15MONTHS, 'UI_15MONTHS':UI_15MONTHS, 'UI_18MONTHS':UI_18MONTHS, 'UI_21MONTHS': UI_21MONTHS, 'UI_24MONTHS':UI_24MONTHS})
    df_longitudinal_label = df_longitudinal_label.fillna('N/A')
    return(df_longitudinal_label)

