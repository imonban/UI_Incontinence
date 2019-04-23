# UI_Incontinence

To run this code, please follow the following steps. 

This code corresponds to the reference - Banerjee, Imon, Kevin Li, Martin Seneviratne, Michelle Ferrari, Tina Seto, James D. Brooks, Daniel L. Rubin, and Tina Hernandez-Boussard. "Weakly supervised natural language processing for assessing patient-centered outcome following prostate cancer treatment." JAMIA Open 2, no. 1 (2019): 150-159.
https://doi.org/10.1093/jamiaopen/ooy057

1. run the Main.py file.
2. Pass the csv file containing the notes which should have the following columns - 
PAT_DEID	NOTE_DEID	NOTE_DATE	NOTE

3. After, the code will ask you to pass another csv file with surgery dates with the following columns -  
PAT_DEID	SURGERY_DATE

4. Once the code run successfully, it will create a file (UI_assessment.csv) with the following fields:
BASELINE	PAT_DEID	UI_12MONTHS	UI_15MONTHS	UI_18MONTHS	UI_21MONTHS	UI_24MONTHS	UI_3MONTHS	UI_6MONTHS	UI_9MONTHS

 	





