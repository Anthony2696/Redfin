from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from scrapy import Selector
from sys import argv #importar argumentos desde la terminal
from dictionary_filters import time_sold as ts
from dictionary_filters import for_sale
from funtions_bot import clean, worker_retry
from funtions_bot import get_df
from funtions_bot import get_ip
from multiprocessing import Process
from funtions_bot import initChromeDriver
from funtions_bot import process_redfin
from funtions_bot import exec_cyberghost
import os
import shutil
import time
import random
import pandas as pd
import datetime
import re

script, state, location, filter_status, filter_sold, filter_timeRedfin,file = argv

match_city_county = [False,False]

df,part = get_df(file)

list_scrape = pd.DataFrame(columns=[
    'zip_code',
    'state_name',
    'city_name',
    'county_name'
])
dr = ChromeDriverManager().install()

def errors_in_inputs(fstate,flocation,fstatus,fsold,ftimeredfin):
    global df
    opt_status = """
        PRESS 1, ACTIVE LISTINGS\tPRESS 2, COMING SOON LISTINGS
        PRESS 3, ACTIVE+COMING SOON LISTINGS\tPRESS 4, ACTIVE+UNDER CONTRACT/PENDING
        PRESS 5, ONLY UNDER CONTRACT/PENDING\tPRESS 6, NOTHING
    """
    opt_timeonredfin = """
        PRESS 1, NEW LISTINGS\t\tPRESS 2, LESS THAN 3 DAYS
        PRESS 3, LESS THAN 7 DAYS\tPRESS 4, LESS THAN 14 DAYS
        PRESS 5, LESS THAN 30 DAYS\tPRESS 6, MORE THAN 7 DAYS
        PRESS 7, MORE THAN 14 DAYS\tPRESS 8, MORE THAN 30 DAYS
        PRESS 9, MORE THAN 45 DAYS\tPRESS 10, MORE THAN 60 DAYS
        PRESS 11, MORE THAN 90 DAYS\tPRESS 12, MORE THAN 180 DAYS
        PRESS 13, NO MAX
    """
    opt_sold = """
        PRESS 1, LAST 1 WEEK\tPRESS 2, LAST 1 MONTH
        PRESS 3, LAST 3 MONTH\tPRESS 4, LAST 6 MONTH
        PRESS 5, LAST 1 YEAR\tPRESS 6, LAST 2 YEAR
        PRESS 7, LAST 3 YEAR\tPRESS 8, LAST 5 YEAR
        PRESS 9, NOTHING
    """
    if fstate != '0':
        if len(fstate) != 2:
            print('¡Wrong format!.\nHELP: Enter a state in its abbreviated form, The format for states is two uppercase or lowercase letters. for example: OH.')
            return True
        else:
            try:
                read_state = [clean(e) for e in df["STATE"] if fstate.lower() == clean(e).lower()]
                df["ZIP_CODE"]
                if len(read_state)==0:
                    print('¡NOT FOUND STATE INSIDE CSV INPUT!.\nHELP:PLEASE CHECK STATES IN THE CSV INPUT AND TRY AGAIN.')
                    return True
            except Exception as e:
                print('***WARNING***: ',e,'.\nHELP:PLEASE CHECK THE NAME OF THE COLUMN WHERE THE STATES ARE CONSULTED. THE COLUMN MUST BE CALLED "STATE".')
                return True

    if flocation != '0':
        if fstate == '0':
            print('¡INPUT ERROR!.\nHELP: YOU MUST ENTER THE STATE FOR THIS LOCATION. IF YOU ONLY WANT TO CONSULT BY STATE, ENTER "0" FOR THE LOCATION.')
            return True

        format_loc= r'^[a-zA-Z]+(\_[a-zA-Z]+)*?$'
        if not re.search(format_loc,flocation):
            print('¡Wrong format!.\nHELP: Make sure the name does not have any special characters EXCEPT "_". BLANKS SHOULD BE REPLACED BY THE "_" CHARACTER, FOR EXAMPLE: LOS_ANGELES, COLLIN_COUNTY.')
            return True
        else:
            try:
                try:
                    read_loc = [ clean(e) for e in df["city_name"] if clean(flocation).replace('_',' ').lower() == clean(e).lower() ]
                    if len(read_loc)==0:
                        try:
                            read_loc = [ clean(e) for e in df["county_name"] if clean(flocation).replace('_',' ').lower() == clean(e).lower() ]
                            if len(read_loc)==0:
                                print('¡NOT FOUND LOCALITY INSIDE CSV INPUT!.\nHELP:PLEASE CHECK LOCATIONS IN THE CSV INPUT AND TRY AGAIN.')
                                return True
                            else: match_city_county[1] = True

                        except Exception as excepcionName:
                            print('WARNING: LOCATION NOT FOUND IN COL city_name AND COLUMN NAME county_name WRONG WRITTEN.\nHELP:PLEASE CHECK THE NAME OF THE COLUMN WHERE THE LOCATIONS ARE CONSULTED. THE COLUMN MUST BE CALLED "city_name" OR "county_name", AND THERE SHOULD BE AT LEAST ONE OF THEM.')
                            return True
                    else: match_city_county[0] = True
                except:
                    read_loc = [ clean(e) for e in df["county_name"] if clean(flocation).replace('_',' ').lower() == clean(e).lower() ]
                    if len(read_loc)==0:
                        print('WARNING: COLUMN NAME city_name WRONG WRITTEN AND ¡NOT FOUND LOCALITY INSIDE CSV INPUT IN COL county_name!.\nHELP:PLEASE CHECK LOCATIONS IN THE CSV INPUT AND TRY AGAIN.')
                        return True
                    else: match_city_county[1] = True

            except Exception as excepcionName:
                print('WARNING: BOTH POORLY WRITTEN COLUMNS.\nHELP:PLEASE CHECK THE NAME OF THE COLUMN WHERE THE LOCATIONS ARE CONSULTED. THE COLUMN MUST BE CALLED "city_name" OR "county_name", AND THERE SHOULD BE AT LEAST ONE OF THEM.')
                return True
                    
    if fsold == '0':
        print('\n¡Filter properties sold cannot be empty!.\nHELP: Enter a period of time for properties sold in redfin, choosing an option from 1 to 8.\nIf you do not want this filter, press option 9.\n')
        print('VALID OPTIONS FOR PROPERTIES SOLD ARE:\n',opt_sold)
        return True
    elif fsold not in ts.keys():
        print('\n¡Invalid option, out of range!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 9.\n')
        print('VALID OPTIONS FOR PROPERTIES SOLD ARE:\n',opt_sold)
        return True
    else:
        try:
            int(fsold)
        except:
            print('\n¡Error in format filter input sold!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 9.\n')
            print('VALID OPTIONS FOR PROPERTIES SOLD ARE:\n',opt_sold)
            return True
    
    tr = for_sale["time_on_redfin"]

    if ftimeredfin == '0':
        print('\n¡Time on Redfin cannot be empty!.\nHELP: Enter a period of time for properties in redfin, choosing an option from 1 to 12.\nIf you do not want this filter, press option 13.\n')
        print('VALID OPTIONS FOR TIME ON REDFIN ARE:\n',opt_timeonredfin)
        return True
    elif ftimeredfin not in tr.keys():
        print('\n¡Invalid option, out of range!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 13.\n')
        print('VALID OPTIONS FOR TIME ON REDFIN ARE:\n',opt_timeonredfin)
        return True
    
    st = for_sale["status"]

    if fstatus == '0':
        print('\n¡Filter status cannot be empty!.\nHELP: Enter a property status in redfin, choosing an option from 1 to 5.\nIf you do not want this filter, press option 6.\n')
        print('VALID OPTIONS FOR STATUS ARE:\n',opt_status)
        return True
    elif fstatus not in st.keys():
        print('\n¡Invalid option, out of range!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 6.\n')
        print('VALID OPTIONS FOR STATUS ARE:\n',opt_status)
        return True
        
    return False

if __name__ == "__main__":
    
    print('\n**INPUTS**\n\tSTATE:',state,'\n\tLOCATION:',location,'\n\tFILTER_STATUS:',filter_status,'\n\tFILTER_SOLD',filter_sold,'\n\tFILTER_TIME_ON_REDFIN:',filter_timeRedfin,'\n')
    part_name = part.replace('.csv','')
    folderExists = os.path.isdir(f"./files_csv_{part_name}")
    if folderExists:
        shutil.rmtree(f"{os.getcwd()}/files_csv_{part_name}")
    os.mkdir(f"./files_csv_{part_name}")
    folderExists = os.path.isdir(f"./files_retry_results_redfin_{part_name}")
    if folderExists:
        shutil.rmtree(f"{os.getcwd()}/files_retry_results_redfin_{part_name}")
    os.mkdir(f"./files_retry_results_redfin_{part_name}")

    c_state=0
    c_loc = 0
    attemps = 0
    cmd = 'sudo cyberghostvpn --traffic --country-code codecountry --connect'
    d = {1:'BR', #brasil
        2: 'CO', #colombia
        3: 'CL', #chile
        4: 'AR', #Argentina
        5: 'CR' #costa rica
    }

    if errors_in_inputs(str(state),str(location),str(filter_status),str(filter_sold),str(filter_timeRedfin)) != True:
        #GENERATE LIST TO SCRAPE       
        for indx,row in tqdm( df.iterrows(), desc=f"GENERATE LIST TO SCRAPE",total=len(df)):
            zip_code = str(row["ZIP_CODE"])
            state_current = str(row["STATE"])
            city = ''
            county = ''
            if match_city_county[0] == True:
                loc_current = str(row["city_name"])
                city = loc_current
            elif match_city_county[1] == True:
                loc_current = str(row["county_name"])
                county = loc_current
            else:
                loc_current = '0'

            if (str(state) != '0' and str(state).lower() != str(state_current).lower()):
                c_state+=1
                continue
            if (str(location) != '0' and clean(location).replace('_',' ').lower() != clean(loc_current).lower()):
                c_loc+=1
                continue

            list_scrape = list_scrape.append({'zip_code':zip_code,'state_name':state_current,'city_name':city,'county_name':county},ignore_index=True)
        list_scrape.to_csv(f'list_{part}',index=False)
        del df
        if len(list_scrape) >0:
            print('STATES AND LOCATIONS FILTERS: ',list_scrape.shape[0])

        while(attemps < 3 and list_scrape.shape[0] > 0):
            c = d[random.randint(1,5)]
            debug = pd.DataFrame(columns=['zip_code','files_urls','date_create_source','numhomes','num_match','reason',
                                        'TIME_DOWNLOAD_IN_SECONDS','LINK_GENERATE','RESPONSE_LINK','ip_request',"index"
            ])
            debug_zip_no_download = pd.DataFrame(columns=["SALE TYPE","SOLD DATE","PROPERTY TYPE","ADDRESS","CITY",
                                                        "STATE OR PROVINCE","ZIP OR POSTAL CODE","PRICE","BEDS","BATHS","LOCATION",
                                                        "SQUARE FEET","LOT SIZE","YEAR BUILT","DAYS ON MARKET","DOLLAR SQUARE FEET",
                                                        "HOA/MONTH","STATUS","NEXT OPEN HOUSE START TIME","NEXT OPEN HOUSE END TIME",
                                                        "URL","SOURCE","MLS NUMBER","FAVORITE","INTERESTED","LATITUDE","LONGITUDE"
            ])
            attemps += 1
            time_init_cyb = 0
            time_end_cyb = 0
            processes = []

            #-- PROCESS DOWNLOAD CSV --#
            for indx,row in tqdm(list_scrape.iterrows(), desc=f"Download by Zip Codes",total=len(list_scrape)):
                filter_status_aux = filter_status
                filter_sold_aux = filter_sold
                filter_timeRedfin_aux = filter_timeRedfin
                try:
                    if time_init_cyb == 0:
                        time_init_cyb = datetime.datetime.now()
                        exec_cyberghost(cmd,c)
                        print('Time_init cyberghost',time_init_cyb,'Time_end cyberghost',time_end_cyb)

                    time_init = datetime.datetime.now()
                    zip_code = str(row["zip_code"])
                    state_current = str(row["state_name"])

                    if zip_code.isdigit() == True:
                        folderExists = os.path.isdir("./downloads")
                        if folderExists:
                            shutil.rmtree(f"{os.getcwd()}/downloads")
                        os.mkdir("./downloads")
                        driver = initChromeDriver(dr)
                        retry,debug,debug_zip_no_download = process_redfin(zip_code,filter_status_aux,filter_sold_aux,
                                                                           filter_timeRedfin_aux,state_current,driver,part_name,
                                                                           indx,attemps,part,time_init,row,debug,
                                                                           debug_zip_no_download,0)
                        driver.quit()
                    else:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":'',
                                "reason":'Zip not valid',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":'',
                                'LINK_GENERATE': '',
                                'RESPONSE_LINK': '',
                                "index":indx
                            },ignore_index=True)
                        debug.to_csv(f'results_redfin{attemps}_{part}',index=False)

                    folderExists = os.path.isdir("./downloads")
                    if folderExists:
                        shutil.rmtree(f"{os.getcwd()}/downloads")
                    
                    time_end_cyb = datetime.datetime.now()
                    if (time_end_cyb - time_init_cyb).total_seconds() >= 420: # Establecer la frecuencia con que rotara la ip (en segundos)
                        time_init_cyb = 0

                    if retry == 1:
                        print('THE RESPONSE LINK HAS CHANGED. TRYING TO SOLVE...')
                        filter_status_aux = '6'
                        filter_sold_aux = filter_sold
                        filter_timeRedfin_aux = '13'
                        #Execute multiprocessing
                        dir_download = f'downloads{indx}'
                        folderExists = os.path.isdir(f'downloads{indx}')
                        if folderExists:
                            shutil.rmtree(f"{os.getcwd()}/downloads{indx}")
                        os.mkdir(f"./downloads{indx}")
                        driver2 = initChromeDriver(dr,dir_download)
                        p = Process(target=worker_retry,args=(zip_code,filter_status_aux,filter_sold_aux,
                                                                           filter_timeRedfin_aux,state_current,driver2,part_name,
                                                                           indx,attemps,part,time_init,row,
                                                                           dir_download))
                        processes.append(p)
                        p.start()

                except Exception as e:
                    print('***ERROR***: ',e)
                    
            zips_downloaded = [ int(debug["index"][i]) for i in range(len(debug["zip_code"])) if (debug["reason"][i] != 'Zip not downloaded' and debug["reason"][i] != 'Error during execute' and debug["reason"][i] != 'locked') ]
            list_scrape = list_scrape.drop(zips_downloaded,axis=0)
            for pro in processes: pro.join()
            del debug
            del debug_zip_no_download
            del processes

        exec_cyberghost('','','yes')
        del list_scrape                       
    else:
        print('1')
