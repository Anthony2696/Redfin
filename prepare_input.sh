#cd /home/ubuntu/Redfin/insert_original_redfin/ #Ruta servidor 52.52.75.149
#cd $(pwd)/insert_original_redfin #Ruta para correrlo en computador
cd /home/ubuntu/Redfin/Redfin_csv/insert_original_redfin #Ruta servidor 13.57.62.82
if [ -d $"$1" ]; then
	
	echo $"Se borrara el directorio $1 se creara de nuevo";
	sudo rm -r $1
	mkdir $1
	cd $1
	mkdir input_data;
	mkdir input_data/divisions;
	mkdir output;
else
	echo $"Se creara el directorio $1";
	mkdir $1
	cd $1
	mkdir input_data;
	mkdir input_data/divisions;
	mkdir output;
fi
