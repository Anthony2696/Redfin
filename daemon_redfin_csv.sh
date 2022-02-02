#!/bin/bash
#########################################################################################################
#Script automatizado del demonio, para la descarga e insercion de datos desde la pagina Redfin.com
#Anthony Briceño Fecha de realizacion: 2021-12-15, correo anthony.briceno@mykukun.com
#########################################################################################################
##SIGNIFICADO PARAMETROS##
# $1-> STATE
# $2-> CITY O COUNTY
# $3-> FILTER STATUS
# $4-> FILTER SOLD
# $5-> FILTER TIME ON REDFIN
# $6-> VALIDATION INSERT INTO BD

#COLOCAR RUTA ESPECIFICA DONDE SE ENCUENTRE EL PROYECTO
#source /home/ubuntu/Redfin/redfin/bin/activate 
source /home/kukuno1/Desktop/Redfin_CSV/redfin/bin/activate #Ruta del entorno virtual del proyecto
#source /home/anthony/kukun/bin/activate
cd /home/kukuno1/Desktop/Redfin_CSV/redfin_csv_daemonExec/ #Ruta de la carpeta donde se ejecuta el demonio
#cd /home/anthony/Documentos/workKukun/Redfin/Redfin_CSV/download_process_new/Test3_vpncyberghost

#######################################
python redfinBot.py $1 $2 $3 $4 $5

##############FUSION DE ARCHIVOS DESCARGADOS DE REDFIN.COM#############
fichero_downloaded=merge/downloaded.csv
if [ -f $fichero_downloaded ];then
	rm merge/downloaded.csv
fi
fichero_no_download=merge/zip_no_download.csv
if [ -f $fichero_no_download ];then
	rm merge/zip_no_download.csv
fi

directorio_files_csv=files_csv
if [ -d $directorio_files_csv ];then
	if [ "$(ls $directorio_files_csv)" ]; then
		for file in files_csv/results_*.csv; do
			cp "$file" ./merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
		done
		#rm -r files_csv
		cd merge/
		python merge.py downloaded 0 0 #downloaded es el nombre del archivo que generara el merge.py
		for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
		cd ../ #Salir de la carpeta merge
	else
		echo "¡¡El directorio: $directorio_files_csv, esta vacio!!"
	fi
else
	echo "¡¡El directorio: $directorio_files_csv, no existe!!"
fi
##########################################################
fichero_results_redfin=results_redfin1.csv
if [ -f $fichero_results_redfin ]; then
	for file in results_redfin*.csv; do
		mv "$file" ./merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
	done
	cd merge/
	python merge.py results_redfin $1 $2 #results_redfin es el nombre del archivo que generara el merge.py
	for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
	cd ../ #Salir de la carpeta merge
else
	echo "¡¡El fichero: $fichero_results_redfin, no existe!!"
fi

#######################################################
fichero_no_download=zip_no_download1.csv
if [ -f $fichero_no_download ]; then
	for file in zip_no_download*.csv; do
		mv "$file" ./merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
	done
	cd merge/
	python merge.py zip_no_download 0 0 #results_redfin es el nombre del archivo que generara el merge.py
	for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
	cd ../ #Salir de la carpeta merge
	#######################################################
else
	echo "¡¡El fichero: $fichero_no_download, no existe!!"
fi

cd send_fileRemote
if [ -d $"input_file" ]; then 
	echo $"Limpiando carpeta input_file para nueva ejecucion"; 
	rm -r input_file;
	mkdir input_file;
else
	echo $"Creando carpeta input_file para la ejecucion";
	mkdir input_file;
fi
cd ../

dayinit=$(date +%A)
horainit=$(date +%H)
mininit=$(date +%M)
year=$(date +%Y)
month=$(date +%m)
namefolder="$1[$2]-$year-$month-$dayinit[$horainit:$mininit]"

#./prepare_input.sh $namefolder

python clean.py $1 $2 $namefolder
if [ "$6" = 'y' ]; then
	#echo "$namefolder"
	#sudo ssh ubuntu@52.52.75.149 -i ./insert_original_redfin/TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < prepare_input.sh $namefolder
	sudo ssh ubuntu@13.57.62.82 -i ./insert_original_redfin/TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < prepare_input.sh $namefolder	
	
	cd send_fileRemote
	python send_file_remote.py $namefolder #Envia downloaded.csv a servidor remoto 50.18.238.132
	cd ../

	cd insert_original_redfin
	######################################################
	#cp results_redfin.csv ./merge/output_scrapy.csv

	#python worker.py get_zips

	######################################################

	#sudo ssh ubuntu@52.52.75.149 -i ./TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < exe.sh $namefolder
	sudo ssh ubuntu@13.57.62.82 -i ./TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < exe.sh $namefolder	
	#./exe.sh $namefolder
	cd ..
fi