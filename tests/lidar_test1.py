from sick_scan_tcp import SickScan
from time import sleep

if __name__ == "__main__":
    
    sick_scan = SickScan(
        ip = '169.254.241.88',
        port = 2111
    )

    while True:
        telegram = sick_scan.scan()

        angles, values = sick_scan.extract_telegram(telegram=telegram)
        
        for i in range(len(angles)):
            if round(angles[i]) == 90:
                print(str(angles[i]) + " Dist: " + str(values[i]))
                break
        
        sleep(1)