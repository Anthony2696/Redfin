#####################################################################################################
# Inserta registros en la tabla Redin de la BD OriginalData suministrados en un archivo .csv almacenado 
# en la carpeta <input_data>
# La Entrada es un archivo .csv almacenado en la carpeta <input_data> 
# La Salida es un archivo .csv con los errores que arroja Mysql si los hubiere. Esta salida se almacena 
# en la carpeta <output>
#####################################################################################################
# Nahir Barrios  Fecha de realizacion: 2021-08-25, correo nahir.barrios@mykukun.com
#
#####################################################################################################

import pandas as pd
from pandas import DataFrame, read_csv, read_sql
from os import listdir
from os.path import join
import string
import datetime 
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm
from sshtunnel import SSHTunnelForwarder
import sshtunnel
import paramiko
import logging
import time
import os

def isNaN(num):
    return num != num
def is_null(v):
    if (isNaN(v) or v=='' or v=='nan'):
        return None
    else:
        return v


tqdm.pandas()

date_now = datetime.datetime.now()
date_now = datetime.datetime.strftime(date_now,'%Y-%m-%d')

def open_ssh_tunnel(verbose=False):
    """Abrir un tunel usando  username y pem.
       Asignar de forma correcta la locaclizacion y nombre del archivo pem
    
    :param verbose: Set to True to show logging
    :return tunnel: Global SSH tunnel connection
    """
    
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG
    
    global tunnel
    #mypkey = paramiko.RSAKey.from_private_key_file('../../pem/13.57.62.82_DB/' + 'Kukun_data_team.pem')
    mypkey = paramiko.RSAKey.from_private_key_file('./TunelSsh(NOBORRAR)/KUKUN_DATA_TEAM_NOV_2020.pem')

    tunnel = SSHTunnelForwarder(
        ('13.57.62.82', 22),
        ssh_username = 'ubuntu',
        ssh_pkey=mypkey,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    
    tunnel.start()

def close_ssh_tunnel():
    """Closes the SSH tunnel connection.
    """
    
    tunnel.close

def db_connection(db):
    open_ssh_tunnel()

    if (db == 'property_db'):
        mySQLconnection_Contractor = mysql.connector.connect(host='127.0.0.1',
                        database='OriginalData',
                        user='user_insert',
                        password='kl4v3.1ns3rt',
                        port=tunnel.local_bind_port)
        """
        user='root',
        password='mysql')                        
        user='user_insert',
        password='kl4v3.1ns3rt')
        """
        print("conexion")
        return(mySQLconnection_Contractor)
    close_ssh_tunnel()


df_report = pd.DataFrame(columns=['file_name','street_address', 'error'])
df_output = pd.DataFrame(columns=['redfin_original_id', 'SALE TYPE', 'SOLD DATE', 'PROPERTY TYPE', 'ADDRESS', 'CITY', 'STATE OR PROVINCE',
    'ZIP OR POSTAL CODE', 'PRICE', 'BEDS', 'BATHS', 'LOCATION', 'SQUARE FEET', 'LOT SIZE', 'YEAR BUILT', 'DAYS ON MARKET', '$/SQUARE FEET',
    'HOA/MONTH', 'STATUS', 'URL', 'SOURCE', 'MLS#', 'LATITUDE', 'LONGITUDE'])

def consult_redfin(addr,city,zip,sale_type,sold_date,price,sqft,lot_size,dollar_sqft,hoa,status,cursor):
    """
        Return 1 -> duplicate entry
        Return 2 -> Error Ocurred
        Return 3 -> No duplicate 
    """
    data = ''
    if addr == None: addr = 'is NULL'
    else: addr = """= '%s'""" % (addr)

    if city == None: city = 'is NULL'
    else: city = """= '%s'""" % (city)

    if sale_type == None: sale_type = 'is NULL'
    else: sale_type = """= '%s'""" % (sale_type)

    if sold_date == None: sold_date = 'is NULL'
    else: sold_date = """= '%s'""" % (sold_date)

    if price == None: price = 'is NULL'
    else: price = """= '%s'""" % (price)

    if sqft == None: sqft = 'is NULL'
    else: sqft = """= '%s'""" % (sqft)

    if lot_size == None: lot_size = 'is NULL'
    else: lot_size = """= '%s'""" % (lot_size)

    if dollar_sqft == None: dollar_sqft = 'is NULL'
    else: dollar_sqft = """= '%s'""" % (dollar_sqft)

    if hoa == None: hoa = 'is NULL'
    else: hoa = """= '%s'""" % (hoa)

    if status == None: status = 'is NULL'
    else: status = """= '%s'""" % (status)
    try:
        query = """SELECT zip_code FROM OriginalData.Redfin where (street_address %s and city %s 
                and zip_code = %s and sale_type %s and sold_date %s and price %s 
                and square_feet %s and lot_size %s and dollar_for_square_feet %s and hoa_for_month %s 
                and status %s);""" % (addr,city,zip,sale_type,sold_date,price,sqft,lot_size,dollar_sqft,hoa,status)
        cursor.execute(query)
        data = cursor.fetchall()

        if len(data) > 0: return 1

    except Error as e:
        print ("REPORT ERROR MYSQL CONSULT ORIGINAL REDFIN", e)
        return 2
    
    return 3

def process_insert(row,mySQLconnection_Property,cursor,file_name):
    global df_output,df_report

    try:
        #N = is_null(row['N'])
        sale_type = is_null(row['SALE TYPE'])
        sold_date = is_null(row['SOLD DATE'])
        building_category =  is_null(row['PROPERTY TYPE']) 
        #building_sub_category_code = is_null(row['BUILDING_SUB_CATEGORY_CODE'])
        street_address = is_null(row['ADDRESS']) 	
        city = is_null(row['CITY']) 	
        state_code =  is_null(row['STATE OR PROVINCE']) 
        zip_code =  is_null(row['ZIP OR POSTAL CODE']) 
        price =  is_null(row['PRICE'])
        beds = 	is_null(row['BEDS'])
        baths = is_null(row['BATHS'])
        location = 	is_null(row['LOCATION']) 
        square_feet =  is_null(row['SQUARE FEET']) 
        lot_size = is_null(row['LOT SIZE']) 	
        year_built = is_null(row['YEAR BUILT']) 
        days_on_market =  is_null(row['DAYS ON MARKET']) 
        dollar_for_square_feet =  is_null(row['DOLLAR SQUARE FEET']) 
        hoa_for_month = is_null(row['HOA/MONTH'])
        status = is_null(row['STATUS'])
        #next_open_house_start_time =  is_null(row['NEXT OPEN HOUSE START TIME'])
        #next_open_house_end_time =  is_null(row['NEXT OPEN HOUSE END TIME'])
        url = is_null(row['URL'])
        source = is_null(row['SOURCE'])
        mls = is_null(row['MLS NUMBER']) 	
        #favorite =	is_null(row['FAVORITE'])
        #interested = is_null(row['INTERESTED'])
        latitude =	is_null(row['LATITUDE'])
        longitude =	is_null(row['LONGITUDE'])
        
        if zip_code != None:
            cursor = mySQLconnection_Property.cursor()
            consult_val = consult_redfin(street_address,city,zip_code,sale_type,sold_date,price,square_feet,lot_size,dollar_for_square_feet,hoa_for_month,status,cursor)
            if  consult_val == 1:
                print ("REPORT DUPLICATE INSERT ORIGINAL REDFIN", street_address, file_name)
                df_report = df_report.append({'file_name':file_name, 'street_address': street_address, 'error':'DUPLICATE ENTRY'}, ignore_index=True)
            
            elif consult_val == 2:
                print ("REPORT ERROR CONSULT ORIGINAL REDFIN", street_address, file_name)
                df_report = df_report.append({'file_name':file_name, 'street_address': street_address, 'error':'ERROR CONSULT ORIGINAL REDFIN'}, ignore_index=True)
            else:
                sql_insert_query = "INSERT INTO Redfin \
                                (sale_type, sold_date, building_category, street_address, city, \
                                state_code, zip_code, price, beds, baths, location, square_feet, lot_size, \
                                year_built, days_on_market, dollar_for_square_feet, hoa_for_month, status,  url, source, mls, \
                                latitude, longitude) \
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute (sql_insert_query, (sale_type, sold_date, building_category, street_address, city, 
                                state_code, zip_code,  price, beds, baths, location, square_feet, lot_size, 
                                year_built, days_on_market, dollar_for_square_feet, hoa_for_month, status, 
                                url, source, mls,  latitude, longitude) )
                
                sql_last_record = "SELECT MAX(redfin_original_id) as redfin_original_id  FROM Redfin"
                df = pd.read_sql(sql_last_record,mySQLconnection_Property)
                #print("df", df)
                
                redfin_original_id = df.iloc[0].loc['redfin_original_id']
                
                df_output = df_output.append({'redfin_original_id':redfin_original_id, 'SALE TYPE':sale_type, 'SOLD DATE':sold_date, 
                'PROPERTY TYPE':building_category, 'ADDRESS':street_address, 'CITY': city, 'STATE OR PROVINCE':state_code,
                'ZIP OR POSTAL CODE':zip_code, 'PRICE':price, 'BEDS':beds, 'BATHS':baths, 'LOCATION':location, 'SQUARE FEET':square_feet, 
                'LOT SIZE':lot_size, 'YEAR BUILT':year_built, 'DAYS ON MARKET':days_on_market, '$/SQUARE FEET':dollar_for_square_feet,
                'HOA/MONTH':hoa_for_month, 'STATUS':status, 'URL':url, 'SOURCE':source, 'MLS#':mls, 'LATITUDE':latitude, 'LONGITUDE':longitude}, ignore_index=True)
        
    except Error as e :
        print ("REPORT ERROR MYSQL INSERT ORIGINAL REDFIN", e, street_address, file_name)
        df_report = df_report.append({'file_name':file_name, 'street_address': street_address, 'error':e}, ignore_index=True)

def insert_redfin(df, file_name):
    print("Start insert redfin for", file_name, "size_df", len(df))
    mySQLconnection_Property = db_connection('property_db')
    cursor = mySQLconnection_Property.cursor()
    print("File: ", file_name) 
    df.progress_apply(lambda row: process_insert(row,mySQLconnection_Property,cursor,file_name),axis=1)
    mySQLconnection_Property.commit()
    mySQLconnection_Property.close()
    cursor.close()
    print("End Insert ", file_name)

def delete_all_redfin():
    """
        NO USAR, BORRA TODo EL CONTENIDO
        DE LA TABLA REDFIN EN LA BD ORIGINALDATA
    """
    print('Start Delete Redfin from OriginalData')
    mySQLconnection_Property = db_connection('property_db')
    cursor = mySQLconnection_Property.cursor()
    sql_insert_query = "DELETE FROM OriginalData.Redfin"
    cursor.execute (sql_insert_query)

    mySQLconnection_Property.commit()
    mySQLconnection_Property.close()
    cursor.close()
    print("End ")

if __name__ == '__main__':
    """
    folder_name = os.environ.get("FOLDER_NAME")
    files = f'./{folder_name}/input_data/divisions'
    print("START")
    for file_name in tqdm(sorted(listdir(files))):
        if '.~lock' in file_name:
                continue 
        if ( '.csv' in file_name):           
            print("File: ", file_name) 
            input_data_frame = pd.read_csv(join(files, file_name), dtype=str, keep_default_na=False,low_memory=True, encoding="ISO-8859-1")    
            print ("Antes del llamado, para procesar: ", file_name)
            insert_redfin(input_data_frame, file_name)

            df_output = df_output.drop_duplicates()
            if not df_output.empty:
                file_name = file_name.replace('.csv','')
                df_output.to_csv(join(f'./{folder_name}/output/output_'+ file_name+'.csv'), index=0)
                df_output.to_csv(join(f'./{folder_name}/output_'+ file_name+'_'+str(time.strftime("%Y-%m-%d-%H:%M"))+'.csv'), index=0)
            
    if not df_report.empty:
        df_report.to_csv(join(f'./{folder_name}/output/df_report_'+ str(time.strftime("%Y-%m-%d-%H:%M"))+ '.csv'), index=0)
        df_report.to_csv(join(f'./{folder_name}/df_report_'+ str(time.strftime("%Y-%m-%d-%H:%M"))+ '.csv'), index=0)
    """
    file_name = os.environ.get("FILE_NAME")
    folder_name = os.environ.get("FOLDER_NAME")
    dir_files = f'{folder_name}/input_data/divisions/'

    print(file_name)
    print(folder_name)
    print(dir_files)
    
    if '.~lock' in file_name:
            pass 
    elif ( '.csv' in file_name):
        input_data_frame = pd.read_csv(f'./{file_name}', dtype=str, keep_default_na=False,low_memory=True, encoding="ISO-8859-1")    
        print ("Antes del llamado, para procesar: ", file_name)
        insert_redfin(input_data_frame, file_name)

        df_output = df_output.drop_duplicates()
        file_name = file_name.replace('.csv','').replace(dir_files,'')
        if not df_output.empty:
            df_output.to_csv(join(f'./{folder_name}/output/output_'+ file_name+'.csv'), index=0)
            df_output.to_csv(join(f'./{folder_name}/output_'+ file_name+'_'+str(time.strftime("%Y-%m-%d-%H:%M"))+'.csv'), index=0)
            
        if not df_report.empty:
            df_report.to_csv(join(f'./{folder_name}/output/df_report_'+ file_name+str(time.strftime("%Y-%m-%d-%H:%M"))+ '.csv'), index=0)
            df_report.to_csv(join(f'./{folder_name}/df_report_'+ file_name+str(time.strftime("%Y-%m-%d-%H:%M"))+ '.csv'), index=0)
    
    print("END")  

