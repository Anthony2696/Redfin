from funtions_bot import exec_cyberghost
import time
import datetime

if __name__ == '__main__':
    time_init = 0
    time_end = 0
    cmd = 'sudo cyberghostvpn --traffic --country-code codecountry --connect'
    while True:
        #print('.')
        if time_init == 0:
            time_init = datetime.datetime.now()
            exec_cyberghost(cmd,'AR')
            print('Time_init',time_init,'Time_end',time_end)
        
        time_end = datetime.datetime.now()
        if (time_end - time_init).total_seconds() > 60:
            time_init = 0
