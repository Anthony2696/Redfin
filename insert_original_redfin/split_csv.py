from sys import argv #importar argumentos desde la terminal
from os import listdir
from os.path import join
import pandas as pd

df_empty = pd.DataFrame(columns=[
                    "SALE TYPE",
                    "SOLD DATE",
                    "PROPERTY TYPE",
                    "ADDRESS",
                    "CITY",
                    "STATE OR PROVINCE",
                    "ZIP OR POSTAL CODE",
                    "PRICE",
                    "BEDS",
                    "BATHS",
                    "LOCATION",
                    "SQUARE FEET",
                    "LOT SIZE",
                    "YEAR BUILT",
                    "DAYS ON MARKET",
                    "DOLLAR SQUARE FEET",
                    "HOA/MONTH",
                    "STATUS",
                    "NEXT OPEN HOUSE START TIME",
                    "NEXT OPEN HOUSE END TIME",
                    "URL",
                    "SOURCE",
                    "MLS NUMBER",
                    "FAVORITE",
                    "INTERESTED",
                    "LATITUDE",
                    "LONGITUDE"
                ])

def split(df,file_name,folder_name,divisor=50000):
    if df.shape[0] <= 0:
        print('dataframe empty, nothing to do!.')
    else:
        file_name = file_name.replace('.csv','')
        lower_limit = 0
        upper_limit = divisor
        n_div = df.shape[0]//divisor
        for i in range(0,n_div+1):
            print('Ciclo:',i,lower_limit,'-',upper_limit)
            file_name_o = 'part'+str(i+1)
            if df.shape[0] <= upper_limit:
                df_aux = df[lower_limit:]
            else: df_aux = df[lower_limit:upper_limit]
            df_aux.to_csv(f'./{folder_name}/input_data/divisions/{file_name_o}.csv', index=False)

            lower_limit += divisor
            upper_limit += divisor

if __name__ == '__main__':
    script,folder = argv
    files = f'./{folder}/input_data/'
    df = df_empty
    for file_name in sorted(listdir(files)):
        if '.~lock' in file_name:
                continue 
        if ( '.csv' in file_name):           
            print("File: ", file_name)
            df = pd.read_csv(join(files,file_name),dtype=str,keep_default_na=False)
            split(df,file_name,folder)
            break
    
