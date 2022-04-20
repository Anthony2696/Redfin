#cd /home/ubuntu/Redfin/insert_original_redfin/ #ruta para servidor 52.52.75.149
cd /home/ubuntu/Redfin/Redfin_csv/insert_original_redfin/ #ruta para servidor  13.57.62.82
#source /home/anthony/kukun/bin/activate
#source /home/kukuno1/Desktop/Redfin_CSV/redfin/bin/activate

cd $1
dayinit=$(date +%A)
horainit=$(date +%H)
mininit=$(date +%M)
nohup echo $"Day Init $dayinit a las $horainit:$mininit" > timeInit_insertOri.txt
cd ..
python3 split_csv.py "$1"

directorio_files_csv="$1"/input_data/divisions
#directorio_files_input=$1/input_data/divisions/part*.csv

if [ -d $directorio_files_csv ];then
	if [ "$(ls $directorio_files_csv)" ]; then
		for file in "$1"/input_data/divisions/part*.csv; do
			./init.sh;
            ./run.sh "$1" "$file";
            sudo docker rm $(sudo docker ps -a -f status=exited -f name=insert-redfin-original -q);
		done
	else
		echo "¡¡El directorio: $directorio_files_csv, esta vacio!!"
	fi
else
	echo "¡¡El directorio: $directorio_files_csv, no existe!!"
fi
cd $1
dayinit=$(date +%A)
horainit=$(date +%H)
mininit=$(date +%M)
nohup echo $"Day End $dayinit a las $horainit:$mininit" > timeEnd_insertOri.txt
cd ..