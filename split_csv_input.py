from os import listdir
from os.path import join
import pandas as pd

df_empty = pd.DataFrame(columns=[
                    "ZIP_CODE",
                    "city_name",
                    "city_code",
                    "STATE",
                    "state_code",
                    "county_name",
                    "state_county_fips_code",
                    "cbsa_name",
                    "cbsa_code"
            ])

def split(df,file_name,divisor=5000):
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
            df_aux.to_csv(f'./input_divisions/{file_name_o}.csv', index=False)

            lower_limit += divisor
            upper_limit += divisor

if __name__ == '__main__':
    files = 'input/'
    df = df_empty
    for file_name in sorted(listdir(files)):
        if '.~lock' in file_name:
                continue 
        if ( '.csv' in file_name):           
            print("File: ", file_name)
            df = pd.read_csv(join(files,file_name),dtype=str,keep_default_na=False)
            split(df,file_name)
            break
    
