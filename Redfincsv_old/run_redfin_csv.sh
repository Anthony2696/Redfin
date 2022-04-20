#!/bin/bash
#########################################################################################################
#Script Bash para el automatizado de scrapy, normalizado y insercion de datos desde la pagina Redfin.com
#Anthony Briceño Fecha de realizacion: 2021-08-04, correo anthony.briceno@mykukun.com
#########################################################################################################

cd $(pwd)
#source /home/ubuntu/Redfin/redfin/bin/activate #COLOCAR RUTA ESPECIFICA DONDE SE ENCUENTRE EL PROYECTO
source /home/kukuno1/Desktop/Redfin_CSV/redfin/bin/activate
#source /home/anthony/kukun/bin/activate
######################ENTER FILTERS REDFIN########################
while :
do
	echo -e "\t\t\t***ENTER REDFIN FILTERS***\n";
	echo -e "\t\t\t\tTIME ON REDFIN\n";
	echo -e "\tPRESS 1, NEW LISTINGS\t\tPRESS 2, LESS THAN 3 DAYS";
	echo -e "\tPRESS 3, LESS THAN 7 DAYS\tPRESS 4, LESS THAN 14 DAYS";
	echo -e "\tPRESS 5, LESS THAN 30 DAYS\tPRESS 6, MORE THAN 7 DAYS";
	echo -e "\tPRESS 7, MORE THAN 14 DAYS\tPRESS 8, MORE THAN 30 DAYS";
	echo -e "\tPRESS 9, MORE THAN 45 DAYS\tPRESS 10, MORE THAN 60 DAYS";
	echo -e "\tPRESS 11, MORE THAN 90 DAYS\tPRESS 12, MORE THAN 180 DAYS";
	echo -e "\tPRESS 13, NO MAX\n";

	read -p "ENTER FILTER TIME ON REDFIN: " opt_timeonredfin

	echo -e "\n\t\t\t\tFILTER PROPERTIES SOLD\n";
	echo -e "\t\tPRESS 1, LAST 1 WEEK\tPRESS 2, LAST 1 MONTH";
	echo -e "\t\tPRESS 3, LAST 3 MONTH\tPRESS 4, LAST 6 MONTH";
	echo -e "\t\tPRESS 5, LAST 1 YEAR\tPRESS 6, LAST 2 YEAR";
	echo -e "\t\tPRESS 7, LAST 3 YEAR\tPRESS 8, LAST 5 YEAR";
	echo -e "\t\tPRESS 9, NOTHING\n";

	read -p "ENTER FILTER PROPERTIES SOLD: " opt_sold

	echo -e "\n\t\t\t\tSTATUS\n";
	echo -e "PRESS 1, ACTIVE LISTINGS\tPRESS 2, COMING SOON LISTINGS";
	echo -e "PRESS 3, ACTIVE+COMING SOON LISTINGS\tPRESS 4, ACTIVE+UNDER CONTRACT/PENDING";
	echo -e "PRESS 5, ONLY UNDER CONTRACT/PENDING\tPRESS 6, NOTHING\n";

	read -p "ENTER FILTER STATUS: " opt_status

	############################INPUT GEOGRAPHIC AREA##############################
	echo -e "\n\t\t*** INPUT GEOGRAPHIC AREA ***\n"
	read -p "ENTER STATE FILTER (PRESS ENTER TO SKIP FILTER): " stateOpt
	format_state='^[a-zA-Z]{2}$'

	read -p "ENTER CITY O COUNTY FILTER (PRESS ENTER TO SKIP FILTER): " locationOpt
	format_loc='^[a-zA-Z]+(\_[a-zA-Z]+)*?$'

	############################VALIDATE INSERT REDFIN##############################
	echo -e "\n\t\t*** INPUT VALIDATE INSERT REDFIN ***\n"
	read -p "DO YOU WANT TO INSERT INTO THE DATABASE, PRESS Y OR N: " validateinsert
	
	validateinsert="${validateinsert,,}"
	if [ "$validateinsert" = '' ]; then
		validateinsert='n'
	elif [[ "$validateinsert" != 'y' && "$validateinsert" != 'n' ]]; then
		echo -e "Wrong format !,\nHELP: RESPOND WITH THE LETTERS Y OR N, TO INSERT INTO THE ORIGINALDATA DATABASE."
		continue
	fi

	if [ "$locationOpt" = '' ]; then
		locationOpt=0
	elif [[ ! $locationOpt =~ $format_loc ]]; then
		echo -e "Wrong format !,\nHELP: Make sure the name does not have any special characters EXCEPT '_'. BLANKS SHOULD BE REPLACED BY THE '_' CHARACTER, FOR EXAMPLE: LOS_ANGELES, COLLIN_COUNTY."
		continue
	fi

	if [ "$stateOpt" = '' ]; then
		stateOpt=0
	elif [[ ! $stateOpt =~ $format_state ]]; then
		echo -e "Wrong format !,\nHELP: Enter a state in its abbreviated form, The format for states is two uppercase or lowercase letters. for example: OH."
		continue
	fi

	if [ "$opt_status" = "" ]; then
		echo -e "\n¡Filter status cannot be empty!.\nHELP: Enter a property status in redfin, choosing an option from 1 to 5.\nIf you do not want this filter, press option 6.\n"
		continue
	elif [[ $opt_status -gt 6 || $opt_status -lt 1 ]]; then
		echo -e "\n¡Invalid option, out of range!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 6.\n"
		continue
	fi

	if [ "$opt_sold" = "" ]; then
		echo -e "\n¡Filter properties sold cannot be empty!.\nHELP: Enter a period of time for properties sold in redfin, choosing an option from 1 to 8.\nIf you do not want this filter, press option 9.\n"
		continue
	elif [[ $opt_sold -gt 9 || $opt_sold -lt 1 ]]; then
		echo -e "\n¡Invalid option, out of range!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 9.\n"
		continue
	fi

	if [ "$opt_timeonredfin" = "" ]; then
		echo -e "\n¡Time on Redfin cannot be empty!.\nHELP: Enter a period of time for properties in redfin, choosing an option from 1 to 12.\nIf you do not want this filter, press option 13.\n"
		continue
	elif [[ $opt_timeonredfin -gt 13 || $opt_timeonredfin -lt 1 ]]; then
		echo -e "\n¡Invalid option, out of range!.\nHELP: Enter one of the options displayed. The accepted options are from 1 to 13.\n"
		continue
	fi

	break
done

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
			python redfinBot.py $stateOpt $locationOpt $opt_status $opt_sold $opt_timeonredfin "$file"
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
python merge.py results_redfin $stateOpt $locationOpt #results_redfin es el nombre del archivo que generara el merge.py
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
namefolder="$stateOpt[$locationOpt]-$fecha-$dayinit[$horainit:$mininit]"
#./prepare_input.sh $namefolder

python clean.py $stateOpt $locationOpt
if [ "$validateinsert" = 'y' ]; then
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
