import paramiko
from os import listdir
from tqdm import tqdm
import pandas as pd
from sys import argv #importar argumentos desde la terminal

def sftp_connect_put(localfile,remotefile):
    """
        envia archivo desde ruta local
        hasta ruta remota.
    """
    try:
        mypkey = paramiko.RSAKey.from_private_key_file('./TunelSsh(NOBORRAR)/KUKUN_DATA_TEAM_NOV_2020.pem')

        #pt = paramiko.Transport('52.52.75.149',22) #Cambiar ip del servidor
        pt = paramiko.Transport('13.57.62.82',22) #Cambiar ip del servidor        
        
        pt.connect(username='ubuntu',pkey=mypkey)
        sftp = paramiko.SFTPClient.from_transport(pt)
        sftp.put(localfile,remotefile)
        pt.close()
        print('Archivo enviado exitosamente!')
    except Exception as e:
        print('Error: ',e)

def sftp_connect_get(localfile,remotefile):
    """
        descarga archivo desde ruta remota 
        a ruta local.
    """
    try:
        t = paramiko.Transport('13.57.62.82', 22) #Cambiar ip del servidor 
        t.connect(username='admin', password='Admin@123')
        #
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remotefile, localfile)
        t.close()
    except Exception as e:
        print('Error: ',e)

if __name__ == '__main__':
    list_files = [file for file in listdir('./input_file') if not '.~' in file and '.csv' in file ]
    script, folder_name = argv

    for file in tqdm(list_files, desc=f"Transfer file",total=len(list_files)):
        try:
            sftp_connect_put('./input_file/{}'.format(file),'/home/ubuntu/Redfin/Redfin_csv/insert_original_redfin/{}/input_data/{}'.format(folder_name,file))

        except: print('Archivo defectuoso',file)

