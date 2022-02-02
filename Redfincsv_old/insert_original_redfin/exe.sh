#cd /home/ubuntu//Redfin/insert_original_redfin/
cd $(pwd)
source /home/anthony/kukun/bin/activate
#source /home/kukuno1/Desktop/Redfin_CSV/redfin/bin/activate


python split_csv.py "$1"

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