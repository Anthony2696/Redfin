from os import listdir
import pandas as pd
from sys import argv #importar argumentos desde la terminal
import time
from tqdm import tqdm

script, file_name,state,loc = argv

if state == '0':
	state = ''
if loc == '0':
	loc = ''

count = 0
df_aux = None
list_files = [file for file in listdir('./input') if not '.~' in file and '.csv' in file ]

for file in tqdm(list_files, desc=f"Join Files",total=len(list_files)):
	try:
		df_file = pd.read_csv('./input/{}'.format(file),dtype=str,keep_default_na=False)
		if count == 0:
			df_aux = df_file
		else:
			df_aux = pd.concat([df_aux,df_file])
		count += 1
	except: print('Archivo defectuoso',file)
if file_name == 'results_redfin':
	namefile = '{}_{}-{}_{}.csv'.format(file_name,state,loc,str(time.strftime("%Y-%m-%d-%H:%M")))
else:
	namefile = '{}.csv'.format(file_name)

if count > 0:
	df_aux.to_csv(namefile,index=False,encoding='utf-8')
	print('Fusionado con exito! en {}.csv'.format(file_name))
else: print('\t¡¡¡No generado archivo {}!!!'.format(namefile))