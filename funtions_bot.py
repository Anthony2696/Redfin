from selenium import webdriver
from selenium_stealth import stealth
from os import listdir
from scrapy import Selector
from dictionary_filters import time_sold as ts
from dictionary_filters import for_sale
import re
import os
import time
import shutil
import datetime
import random
import pandas as pd
import sys
from subprocess import TimeoutExpired,Popen

def process_redfin(zip_code,filter_status_aux,filter_sold_aux,filter_timeRedfin_aux,state_current,driver,
                   part_name,indx,attemps,part,time_init,row,debug,debug_zip_no_download,retry_c=0):
    link = generate_link_redfin(str(zip_code),str(filter_status_aux),str(filter_sold_aux),str(filter_timeRedfin_aux))
    print('\n\nconsulting link -> ',link,'\nfor state ->',state_current,'\n')
    try:
        driver.get(link)
        time.sleep(1)
        html = driver.page_source
        respObj = Selector(text=html)
        link_resp = driver.current_url
        ip_current = get_ip()
        response = ''
        link_gen = ''                       

        download_url = respObj.xpath("//a[@id='download-and-save']/@href").get()                        
        homes = respObj.xpath('//div[@data-rf-test-id="homes-description"]//text()').extract()
        homes = [clean(e).lower() for e in homes]
        if link_resp != link:
            print('Links not equal!')
            retry_c+=1
            response = link_resp
            link_gen = link

        if 'homes' in homes or 'home' in homes:
            if 'homes' in homes:
                idx = homes.index('homes')
                homes = homes[idx-2]
            elif 'home' in homes:
                idx = homes.index('home')
                homes = homes[idx-2]
            else: homes = ''
        else:
            for item in homes:
                regex1 = re.findall(r'\d+\sof\s(\d+)\shomes',item)
                if len(regex1)>0:
                    homes = regex1[0]
                    break
                else:
                    regex2 = re.findall(r'(\d+)\s?homes|(\d+)\s?home',item)
                    if len(regex2) > 0:
                        if clean(item).find('homes') != -1:
                            homes = regex2[0][0]
                        elif clean(item).find('home') != -1:
                            homes = regex2[0][1]
                        break
            if homes == list(): homes = ''                                    

        if download_url != None:
            driver.get(f"https://www.redfin.com{download_url.replace('&num_homes=350','&num_homes=9999')}")
            time.sleep(random.randint(5,10))
            _,filename = get_df('./downloads')

            if filename != '':
                shutil.move(f"{os.getcwd()}/downloads/{filename}",f"{os.getcwd()}/files_csv_{part_name}/results_{zip_code}_{indx}.csv")
                df_zip_current = pd.read_csv(f'./files_csv_{part_name}/results_{zip_code}_{indx}.csv',dtype=str,keep_default_na=False)

                num_match_zip = df_zip_current.shape[0]
                try:
                    homes = int(homes)
                except: 
                    num_match_zip = 0
                #DEBUG
                debug = debug.append({
                        "zip_code":zip_code,
                        "files_urls":[{"url":f"https://www.redfin.com{download_url.replace('&num_homes=350','&num_homes=9999')}",
                                    "name":f"results_{zip_code}_{indx}.csv"
                                    }],
                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                        "numhomes":homes,
                        "num_match":num_match_zip/int(homes),
                        "reason":'good',
                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                        "ip_request":ip_current,
                        'LINK_GENERATE': link_gen,
                        'RESPONSE_LINK': response,
                        "index":indx
                    },ignore_index=True)
                debug.to_csv(f'results_redfin{attemps}_{part}',index=False)
            else:
                #DEBUG
                debug = debug.append({
                    "zip_code":zip_code,
                    "files_urls":[{"url":f"https://www.redfin.com{download_url.replace('&num_homes=350','&num_homes=9999')}",
                                "name":f"results_{zip_code}_{indx}.csv"
                                }],
                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                    "numhomes":homes,
                    "num_match":'',
                    "reason":'Zip not downloaded',
                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                    "ip_request":ip_current,
                    'LINK_GENERATE': link_gen,
                    'RESPONSE_LINK': response,
                    "index":indx
                },ignore_index=True)
                debug.to_csv(f'results_redfin{attemps}_{part}',index=False) 
        else:
            #DEBUG
            if link_resp.lower().find('sitemap') != -1 or link_resp.lower().find('404') != -1:
                debug = debug.append({
                        "zip_code":zip_code,
                        "files_urls":'',
                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                        "numhomes":homes,
                        "reason":'no results for zip code, code 404',
                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                        "ip_request":ip_current,
                        'LINK_GENERATE': link_gen,
                        'RESPONSE_LINK': response,
                        "index":indx
                    },ignore_index=True)
                debug.to_csv(f'results_redfin{attemps}_{part}',index=False)
                retry_c=0
            else:
                try:
                    homes = int(homes)
                    if homes > 0:
                        addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url = extract_info_properties(respObj,driver,homes)
                        debug = debug.append({
                                "zip_code":zip_code,
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                "index":indx
                            },ignore_index=True)
                        debug_zip_no_download = debug_zip_no_download.append({
                                                "ADDRESS":addr,
                                                "CITY":row["city_name"],
                                                "STATE OR PROVINCE":row["state_name"],
                                                "ZIP OR POSTAL CODE":zip_code,
                                                "PRICE":price,
                                                "BEDS":beds,
                                                "BATHS":baths,
                                                "LOCATION":loc,
                                                "SQUARE FEET":size_sqft,
                                                "DAYS ON MARKET":on_redfin,
                                                "DOLLAR SQUARE FEET":price_sqft,
                                                "URL":url
                        },ignore_index=True)
                        debug.to_csv(f'results_redfin{attemps}_{part}',index=False)
                        debug_zip_no_download.to_csv(f"zip_no_download{attemps}_{part}",index=False)
                    else:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":homes,
                                "reason":'no results for zip code, num_homes less than or equal to 0',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                'LINK_GENERATE': link_gen,
                                'RESPONSE_LINK': response,
                                "index":indx
                            },ignore_index=True)
                        debug.to_csv(f'results_redfin{attemps}_{part}',index=False)
                except:
                    block1 = respObj.xpath('//form[@id="rf_unblock"]//div[@id="captcha"]').get()
                    block2 = respObj.xpath('//div[@id="txt"]//p[2]//text()').get()
                    if block1 != None:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":homes,
                                "reason":'locked',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                'LINK_GENERATE': link_gen,
                                'RESPONSE_LINK': response,
                                "index":indx
                            },ignore_index=True)
                    elif block2 != None:
                        if block2.lower().find('complete the captcha') != -1:
                            debug = debug.append({
                                    "zip_code":zip_code,
                                    "files_urls":'',
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "numhomes":homes,
                                    "reason":'locked',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "ip_request":ip_current,
                                    'LINK_GENERATE': link_gen,
                                    'RESPONSE_LINK': response,
                                    "index":indx
                                },ignore_index=True)
                    else:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":homes,
                                "reason":'no results for zip code, num_homes not found',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                'LINK_GENERATE': link_gen,
                                'RESPONSE_LINK': response,
                                "index":indx
                            },ignore_index=True)

                    debug.to_csv(f'results_redfin{attemps}_{part}',index=False)
                    retry_c=0
    except Exception as e:
        print('***Error Execute***:',e)
        debug = debug.append({
                "zip_code":zip_code,
                "files_urls":'',
                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                "numhomes":'',
                "reason":'Error during execute',
                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                "ip_request":'',
                'LINK_GENERATE': '',
                'RESPONSE_LINK': '',
                "index":indx
            },ignore_index=True)
        debug.to_csv(f'results_redfin{attemps}_{part}',index=False)
    return retry_c,debug,debug_zip_no_download

def worker_retry(zip_code,filter_status_aux,filter_sold_aux,filter_timeRedfin_aux,state_current,driver,
                 part_name,indx,attemps,part,time_init,row,dir_name_download):
    debug = pd.DataFrame(columns=['zip_code','files_urls','date_create_source','numhomes','num_match','reason',
                                  'TIME_DOWNLOAD_IN_SECONDS','LINK_GENERATE','RESPONSE_LINK','ip_request',"index"
    ])
    debug_zip_no_download = pd.DataFrame(columns=["SALE TYPE","SOLD DATE","PROPERTY TYPE","ADDRESS","CITY","STATE OR PROVINCE",
                                                  "ZIP OR POSTAL CODE","PRICE","BEDS","BATHS","LOCATION","SQUARE FEET","LOT SIZE",
                                                  "YEAR BUILT","DAYS ON MARKET","DOLLAR SQUARE FEET","HOA/MONTH","STATUS",
                                                  "NEXT OPEN HOUSE START TIME","NEXT OPEN HOUSE END TIME","URL","SOURCE",
                                                  "MLS NUMBER","FAVORITE","INTERESTED","LATITUDE","LONGITUDE"
    ])
    link = generate_link_redfin(str(zip_code),str(filter_status_aux),str(filter_sold_aux),str(filter_timeRedfin_aux))
    print('\n\nconsulting link -> ',link,'\nfor state ->',state_current,'\n')
    file_name_debug = f'./files_retry_results_redfin_{part_name}/results_redfin{attemps}_retry_{zip_code}-{indx}.csv'
    file_name_notD = f'./files_retry_results_redfin_{part_name}/zip_no_download{attemps}_retry_{zip_code}-{indx}.csv'
    try:
        driver.get(link)
        time.sleep(1)
        html = driver.page_source
        respObj = Selector(text=html)
        link_resp = driver.current_url
        ip_current = get_ip()
        response = ''
        link_gen = ''                    

        download_url = respObj.xpath("//a[@id='download-and-save']/@href").get()                        
        homes = respObj.xpath('//div[@data-rf-test-id="homes-description"]//text()').extract()
        homes = [clean(e).lower() for e in homes]
        if link_resp != link:
            print('Links not equal. Nothing to Do!')
            response = link_resp
            link_gen = link

        if 'homes' in homes or 'home' in homes:
            if 'homes' in homes:
                idx = homes.index('homes')
                homes = homes[idx-2]
            elif 'home' in homes:
                idx = homes.index('home')
                homes = homes[idx-2]
            else: homes = ''
        else:
            for item in homes:
                regex1 = re.findall(r'\d+\sof\s(\d+)\shomes',item)
                if len(regex1)>0:
                    homes = regex1[0]
                    break
                else:
                    regex2 = re.findall(r'(\d+)\s?homes|(\d+)\s?home',item)
                    if len(regex2) > 0:
                        if clean(item).find('homes') != -1:
                            homes = regex2[0][0]
                        elif clean(item).find('home') != -1:
                            homes = regex2[0][1]
                        break
            if homes == list(): homes = ''                                    

        if download_url != None:
            driver.get(f"https://www.redfin.com{download_url.replace('&num_homes=350','&num_homes=9999')}")
            time.sleep(random.randint(5,10))
            _,filename = get_df(f'./{dir_name_download}')

            if filename != '':
                shutil.move(f"{os.getcwd()}/{dir_name_download}/{filename}",f"{os.getcwd()}/files_csv_{part_name}/results_{zip_code}_{indx}-2.csv")
                df_zip_current = pd.read_csv(f'./files_csv_{part_name}/results_{zip_code}_{indx}.csv',dtype=str,keep_default_na=False)

                num_match_zip = df_zip_current.shape[0]
                try:
                    homes = int(homes)
                except: 
                    num_match_zip = 0
                #DEBUG
                debug = debug.append({
                        "zip_code":zip_code,
                        "files_urls":[{"url":f"https://www.redfin.com{download_url.replace('&num_homes=350','&num_homes=9999')}",
                                    "name":f"results_{zip_code}_{indx}-2.csv"
                                    }],
                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                        "numhomes":homes,
                        "num_match":num_match_zip/int(homes),
                        "reason":'good',
                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                        "ip_request":ip_current,
                        'LINK_GENERATE': link_gen,
                        'RESPONSE_LINK': response,
                        "index":indx
                    },ignore_index=True)
                debug.to_csv(file_name_debug,index=False)
            else:
                #DEBUG
                debug = debug.append({
                    "zip_code":zip_code,
                    "files_urls":[{"url":f"https://www.redfin.com{download_url.replace('&num_homes=350','&num_homes=9999')}",
                                "name":f"results_{zip_code}_{indx}-2.csv"
                                }],
                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                    "numhomes":homes,
                    "num_match":'',
                    "reason":'Zip not downloaded',
                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                    "ip_request":ip_current,
                    'LINK_GENERATE': link_gen,
                    'RESPONSE_LINK': response,
                    "index":indx
                },ignore_index=True)
                debug.to_csv(file_name_debug,index=False)
        else:
            #DEBUG
            if link_resp.lower().find('sitemap') != -1 or link_resp.lower().find('404') != -1:
                debug = debug.append({
                        "zip_code":zip_code,
                        "files_urls":'',
                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                        "numhomes":homes,
                        "reason":'no results for zip code, code 404',
                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                        "ip_request":ip_current,
                        'LINK_GENERATE': link_gen,
                        'RESPONSE_LINK': response,
                        "index":indx
                    },ignore_index=True)
                debug.to_csv(file_name_debug,index=False)
            else:
                try:
                    homes = int(homes)
                    if homes > 0:
                        addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url = extract_info_properties(respObj,driver,homes)
                        debug = debug.append({
                                "zip_code":zip_code,
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                "index":indx
                            },ignore_index=True)
                        debug_zip_no_download = debug_zip_no_download.append({
                                                "ADDRESS":addr,
                                                "CITY":row["city_name"],
                                                "STATE OR PROVINCE":row["state_name"],
                                                "ZIP OR POSTAL CODE":zip_code,
                                                "PRICE":price,
                                                "BEDS":beds,
                                                "BATHS":baths,
                                                "LOCATION":loc,
                                                "SQUARE FEET":size_sqft,
                                                "DAYS ON MARKET":on_redfin,
                                                "DOLLAR SQUARE FEET":price_sqft,
                                                "URL":url
                        },ignore_index=True)
                        debug.to_csv(file_name_debug,index=False)
                        debug_zip_no_download.to_csv(file_name_notD,index=False)
                    else:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":homes,
                                "reason":'no results for zip code, num_homes less than or equal to 0',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                'LINK_GENERATE': link_gen,
                                'RESPONSE_LINK': response,
                                "index":indx
                            },ignore_index=True)
                        debug.to_csv(file_name_debug,index=False)
                except:
                    block1 = respObj.xpath('//form[@id="rf_unblock"]//div[@id="captcha"]').get()
                    block2 = respObj.xpath('//div[@id="txt"]//p[2]//text()').get()
                    if block1 != None:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":homes,
                                "reason":'locked',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                'LINK_GENERATE': link_gen,
                                'RESPONSE_LINK': response,
                                "index":indx
                            },ignore_index=True)
                    elif block2 != None:
                        if block2.lower().find('complete the captcha') != -1:
                            debug = debug.append({
                                    "zip_code":zip_code,
                                    "files_urls":'',
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "numhomes":homes,
                                    "reason":'locked',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "ip_request":ip_current,
                                    'LINK_GENERATE': link_gen,
                                    'RESPONSE_LINK': response,
                                    "index":indx
                                },ignore_index=True)
                    else:
                        debug = debug.append({
                                "zip_code":zip_code,
                                "files_urls":'',
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "numhomes":homes,
                                "reason":'no results for zip code, num_homes not found',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "ip_request":ip_current,
                                'LINK_GENERATE': link_gen,
                                'RESPONSE_LINK': response,
                                "index":indx
                            },ignore_index=True)

                    debug.to_csv(file_name_debug,index=False)
    except Exception as e:
        print('***Error Execute***:',e)
        debug = debug.append({
                "zip_code":zip_code,
                "files_urls":'',
                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                "numhomes":'',
                "reason":'Error during execute',
                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                "ip_request":'',
                'LINK_GENERATE': '',
                'RESPONSE_LINK': '',
                "index":indx
            },ignore_index=True)
        debug.to_csv(file_name_debug,index=False)
    
    driver.quit()
    folderExists = os.path.isdir(f"./{dir_name_download}")
    if folderExists:
        shutil.rmtree(f"{os.getcwd()}/{dir_name_download}")


def exec_cyberghost(cmd,country,stop=None):
    try:
        if stop == None:
            cmd = cmd.replace('codecountry',str(country))
            cmd = cmd.split(' ')
            proc = Popen(cmd)
            print('Execute command: ',cmd)
        else:
            proc = Popen(['sudo','cyberghostvpn','--stop'])
        try:            
            proc.wait(60)
        except TimeoutExpired as e:
            print('TimeoutExpired Execute cyberghost',e)
            os.kill(proc.pid,15)

    except Exception as e:
        print('Error Exception: ',e)

def extract_info_properties(response,dr,homes):
    addr = ''
    loc = ''
    price = ''
    beds = ''
    baths = ''
    size_sqft = ''
    price_sqft = ''
    on_redfin = ''
    url = ''

    if response != '':
        button_table = dr.find_elements_by_xpath("//button[contains(span,'Table')]")
        button_table2 = dr.find_elements_by_xpath("//li[contains(span,'Table')]")
        if len(button_table)>0:
            button_table[0].click()
            html = dr.page_source
            response = Selector(text=html)
            table_properties = response.xpath('//tbody[@class="tableList"]//tr')
            table_properties = table_properties[:homes]
            addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url = process_extract(table_properties)
            return addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url
            
        elif len(button_table2)>0:
            button_table2[0].click()
            html = dr.page_source
            response = Selector(text=html)
            table_properties = response.xpath('//tbody[@class="tableList"]//tr')
            table_properties = table_properties[:homes]
            addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url = process_extract(table_properties)
            return addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url

        else:
            return '','','','','','','','',''
    else:
        return addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url

def process_extract(table):
    addr = ''
    loc = ''
    price = ''
    beds = ''
    baths = ''
    size_sqft = ''
    price_sqft = ''
    on_redfin = ''
    url = ''

    for i,item in enumerate(table):
        addr_c = item.xpath('td[2]//a//@title').extract_first()
        url_c = item.xpath('td[2]//a//@href').extract_first()
        loc_c = item.xpath('td[3]//div[@class="location"]//text()').extract_first()
        price_c = item.xpath('td[4]//text()').extract_first()
        beds_c = item.xpath('td[5]//text()').extract_first()
        baths_c = item.xpath('td[6]//text()').extract_first()
        size_sqft_c = item.xpath('td[7]//text()').extract_first()
        price_sqft_c = item.xpath('td[8]//text()').extract_first()
        on_redfin_c = item.xpath('td[9]//span//text()').extract_first()

        if i == 0:
            if addr_c != None:
                addr = clean(addr_c)
            else: addr = ''
            
            if loc_c != None:
                loc = clean(loc_c)
            else: loc = ''
            
            if price_c != None:
                price = clean(price_c)
            else: price = ''
            
            if beds_c != None:
                beds = clean(beds_c)
            else: beds = ''
            
            if baths_c != None:
                baths = clean(baths_c)
            else: baths = ''

            if size_sqft_c != None:
                size_sqft = clean(size_sqft_c)
            else: size_sqft = ''

            if price_sqft_c != None:
                price_sqft = clean(price_sqft_c)
            else: price_sqft = ''

            if on_redfin_c != None:
                on_redfin = clean(on_redfin_c)
            else: on_redfin = ''

            if url_c != None:
                url = 'https://www.redfin.com'+url_c
            else: url= ''
        else:
            if addr_c != None:
                addr += '|'+clean(addr_c)
            else: addr += '|'+''
            
            if loc_c != None:
                loc += '|'+clean(loc_c)
            else: loc += '|'+''
            
            if price_c != None:
                price += '|'+clean(price_c)
            else: price += '|'+''
            
            if beds_c != None:
                beds += '|'+clean(beds_c)
            else: beds += '|'+''
            
            if baths_c != None:
                baths += '|'+clean(baths_c)
            else: baths += '|'+''

            if size_sqft_c != None:
                size_sqft += '|'+clean(size_sqft_c)
            else: size_sqft += '|'+''

            if price_sqft_c != None:
                price_sqft += '|'+clean(price_sqft_c)
            else: price_sqft += '|'+''

            if on_redfin_c != None:
                on_redfin += '|'+clean(on_redfin_c)
            else: on_redfin += '|'+''

            if url_c != None:
                url += '|'+'https://www.redfin.com'+url_c
            else: url += '|'+''
    
    return addr,loc,price,beds,baths,size_sqft,price_sqft,on_redfin,url

def get_ip():
    version = sys.version[0]

    if version == '2':
        import urllib2 as urllib
    else:
        import urllib.request as urllib

    url1 = None
    url2 = None
    servidor1 = 'http://www.soporteweb.com'
    servidor2 = 'http://www.ifconfig.me/ip'

    consulta1 = urllib.build_opener()
    consulta1.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0')] 
    consulta2=consulta1

    try:
        url1 = consulta1.open(servidor1, timeout=17)
        respuesta1 = url1.read()
        if version == '3':
            try:
                respuesta1 = respuesta1.decode('UTF-8')
            except UnicodeDecodeError:
                respuesta1 = respuesta1.decode('ISO-8859-1')

        url1.close()
        #print('Servidor1:'+respuesta1)
        return respuesta1
    
    except:
        print('Falló la consulta ip a '+servidor1)
        try:
            url2 = consulta2.open(servidor2, timeout=17)
            respuesta2 = url2.read()
            if version == '3':
                try:
                    respuesta2 = respuesta2.decode('UTF-8')
                except UnicodeDecodeError:
                    respuesta2 = respuesta2.decode('ISO-8859-1')

            url2.close()
            #print('Servidor2:'+respuesta2)
            return respuesta2
        except:
            #print('Falló la consulta ip a '+servidor2)
            return ''

def find_proxie_valid(PROXIES,pxy,link):
    if pxy == None:
        driver = initChromeDriver()
        driver.get(link)
        time.sleep(1)
        html = driver.page_source
        respObj = Selector(text=html)
        link_resp = driver.current_url
        return pxy,PROXIES,respObj,link_resp,driver

    while(True):
        testp = False
        response = ''
        link_resp = ''
        if pxy != '':
            testp,response,link_resp,driver = test_proxie(link,pxy)

        if testp == True:
            print('proxie good!')
            return pxy,PROXIES,response,link_resp,driver

        while(len(PROXIES)>0 and testp == False):
            PROXIES,pxy = rotate_proxie(PROXIES,pxy)
            if len(PROXIES)>0:
                PROXIES.pop(0)
                testp,response,link_resp,driver = test_proxie(link,pxy)

            if testp == True:
                print('good proxie!')
                return pxy,PROXIES,response,link_resp,driver       
        
        if len(PROXIES) == 0:
            print('Generando nueva lista PROXIES')
            PROXIES,pxy = create_list_proxies()

def generate_link_redfin(zipc,fstatus,fsold,ftimeredfin):
    link_base = f'https://www.redfin.com/zipcode/{zipc}'
    if (fsold != '9' or ((fstatus != '3' and fstatus != '6') or ftimeredfin != '13')):
        link_base = link_base+'/filter/'
        if ftimeredfin != '13':
            tr = for_sale["time_on_redfin"]
            link_base += tr[ftimeredfin]
        if fsold != '9':
            if ftimeredfin != '13':
                link_base += ','+ts[fsold]
            else: link_base += ts[fsold]

            if fstatus != '6':
                link_base = link_base.replace('include=','include=forsale+mlsfsbo+construction+fsbo+')
        
        if (fstatus != '3' and fstatus != '6'):
            st = for_sale["status"]
            if ftimeredfin != '13' or fsold != '9':
                link_base += ','+st[fstatus]
            else: link_base += st[fstatus]            
        
    return link_base

def test_proxie(link,pxy):
    print('Testing proxie: ',pxy)
    #str(input('presione ENTER para continuar'))
    try:
        html = ''
        driver = initChromeDriver(pxy)
        driver.set_page_load_timeout(60)
        driver.get(link)
        time.sleep(1)       
        html = driver.page_source
        xpath = '//div[@class="InputBox"]//input[@id="search-box-input"]'
        respObj = Selector(text=html)
        search_box = respObj.xpath(xpath).extract_first()
        if search_box != None:
            return True,respObj,driver.current_url,driver
        
        driver.quit()
    except Exception as e:
        print('*WARNING* ',e)
        driver.quit()

    return False,'','',''

def rotate_proxie(PROXIES,pxy):
    if str(pxy) == str(PROXIES[0]):
        PROXIES.pop(0)
        if len(PROXIES)>0:
            return PROXIES,PROXIES[0]
        else:
            return [],''
     
    return PROXIES,PROXIES[0]

def create_list_proxies():
    driver = initChromeDriver()
    driver.get("https://free-proxy-list.net/")

    PROXIES = []
    html = driver.page_source
    respObj = Selector(text=html)
    table_proxies = respObj.xpath("//section[@id='list']//table//tbody//tr")

    for row in table_proxies:
        ip_addr = row.xpath('td[1]//text()').extract_first()
        port = row.xpath('td[2]//text()').extract_first()

        if ip_addr != None and port != None:
            ip_addr = clean(ip_addr)
            port = clean(port)
            PROXIES.append(ip_addr+":"+port)

    driver.quit()
    if len(PROXIES)>0:
        return PROXIES,PROXIES[0]
    else:
        return [],''

def clean(cadena):
    cadena = str(cadena)
    cadena = cadena.strip()     
    cadena = cadena.replace(',','')
    cadena = cadena.replace('*','').replace('(','').replace(')','')
    cadena = cadena.replace('\n','')
    cadena = cadena.replace('\r','')
    cadena = cadena.replace('\t','')
    cadena = cadena.replace(';','')
    cadena = cadena.replace('$','')
    cadena = cadena.replace('%','percent')
    cadena = cadena.replace('"','')
    cadena = cadena.replace('\xa0','')
    cadena = cadena.replace('&amp','&')
    
    if cadena.lower() == 'nan':
        cadena = cadena.lower().replace('nan','')
    if cadena.lower() == 'none':
        cadena = cadena.lower().replace('none','')
    if cadena.lower() == 'n/a':
        cadena = ''
    if cadena.lower() == 'unkown':
        cadena = ''
    if cadena.lower() == 'unassigned':
        cadena = ''

    cadena = cadena.strip()
    return cadena

#-- Inicializar chrome driver --#
def initChromeDriver(dr,dir_name_download=None,proxie=None):

    options = webdriver.ChromeOptions()
    #ua = UserAgent()
    #userAgent = ua.random
    # -- Descomentar la siguiente linea, para ocultar el navegador --#
    options.add_argument('--headless')
    #-- Descomentar las siguientes dos lineas en caso de ejecutar en MAC/LINUX  --#
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')
    options.add_argument("--start-maximized")
    options.add_argument('ignore-certificate-errors') #ignore certificate errors for google chrome
    # -- USO DE PROXIES -- #
    if proxie != None:
        options.add_argument(f'--proxy-server={proxie}')
    #options.add_argument(f'user-agent={userAgent}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if dir_name_download == None:
        prefs = {"download.default_directory" : f"{os.getcwd()}/downloads"}
    else:
        prefs = {"download.default_directory" : f"{os.getcwd()}/{dir_name_download}"}
    options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(executable_path=dr, options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    return driver

def get_df(file_path):
    try:
        if '.csv' in file_path:
            if '.csv' in file_path and '.~lock' not in file_path:
                df = pd.read_csv(file_path,dtype=str,keep_default_na=False)
                print('\tAbriendo',file_path)
                file = file_path.replace('input_divisions/','')
                return df,file
        else:
            folder = str(file_path)
            for file in listdir(folder):
                if '.csv' in file and '.~lock' not in file:
                    df = pd.read_csv('{}/{}'.format(folder,file),dtype=str,keep_default_na=False)
                    print('\tAbriendo',file)
                    return df,file
            return [],''            
    except: return [],''
