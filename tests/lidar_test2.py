from sick_scan_tcp import SickScan
from time import sleep
from datetime import datetime

if __name__ == "__main__":


    start_time = datetime.now()

    i = 0

    while True:
        if (datetime.now() - start_time).seconds == 30:
            break
        else:
            print(i)
            sleep(1)
        i+=1
            


    