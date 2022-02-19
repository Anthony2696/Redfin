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
#cd /home/kukuno1/Desktop/Redfin_CSV/redfin_csv_daemonExec/ #Ruta de la carpeta donde se ejecuta el demonio
cd /home/anthony/Documentos/workKukun/Redfin/Redfin_CSV/download_process_new/Test3_vpncyberghost

###############PROCESO DE DESCARGA REDFIN ###############
if [ -d input_divisions ]; then
	
	echo $"Se borrara el directorio input_divisions y se creara de nuevo";
	sudo rm -r input_divisions
	mkdir input_divisions
else
	echo $"Se creara el directorio input_divisions";
	mkdir input_divisions
fi
python split_csv_input.py
dir_divisions_input=input_divisions
if [ -d $dir_divisions_input ];then
	if [ "$(ls $dir_divisions_input)" ]; then
		for file in input_divisions/part*.csv; do
			python redfinBot.py $1 $2 $3 $4 $5 "$file"
		done
	else
		echo "¡¡El directorio: $dir_divisions_input, esta vacio!!"
	fi
else
	echo "¡¡El directorio: $dir_divisions_input, no existe!!"
fi

##############FUSION DE ARCHIVOS DESCARGADOS DE REDFIN.COM#############
fichero_downloaded=merge/downloaded.csv
if [ -f $fichero_downloaded ];then
	rm merge/downloaded.csv
fi
fichero_no_download=merge/zip_no_download.csv
if [ -f $fichero_no_download ];then
	rm merge/zip_no_download.csv
fi

directorio_files_csv=files_csv_*
for d in $directorio_files_csv; do
	if [ -d "$d" ];then
		if [ "$(ls $d)" ]; then
			for file in $d/results_*.csv; do
				cp "$file" ./merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
			done
			rm -r $d
			cd merge/
			python merge.py "$d" 0 0 #downloaded es el nombre del archivo que generara el merge.py
			for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
			cd ../ #Salir de la carpeta merge
		else
			rm -r $d
			echo "¡¡El directorio: $d, esta vacio!!"
		fi
	else
		echo "¡¡El directorio: $d, no existe!!"
	fi
done
files_csv_dir=merge/files_csv*.csv
for fc in $files_csv_dir; do
	if [ -f $fc ]; then
		mv $fc ./merge/input
	fi
done
cd merge
python merge.py downloaded 0 0
for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
cd ..
##########################################################
for file in results_redfin*.csv; do
	if [ -f $file ]; then
		mv "$file" ./merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
	fi
done
cd merge/
python merge.py results_redfin $1 $2 #results_redfin es el nombre del archivo que generara el merge.py
for file in input/*.csv; do 
	if [ -f $file ]; then
		rm "$file";
	fi
done #borrar archivos copiados anteriormente
cd ../ #Salir de la carpeta merge
#######################################################
for file in zip_no_download*.csv; do
	if [ -f $file ]; then
		mv "$file" ./merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
	fi
done
cd merge/
python merge.py zip_no_download 0 0 #results_redfin es el nombre del archivo que generara el merge.py
for file in input/*.csv; do 
	if [ -f $file ]; then
		rm "$file";
	fi
done #borrar archivos copiados anteriormente
cd ../ #Salir de la carpeta merge
#######################################################

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
fecha=$(date +%F)
namefolder="$1[$2]-$fecha-$dayinit[$horainit:$mininit]"

#./prepare_input.sh $namefolder

python clean.py $1 $2 
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