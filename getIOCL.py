import csv
import requests
from datetime import datetime
import shutil
import os
import logging
import logging.handlers

def getCurrentTimeStamp():
    current_datetime = datetime.now()
    date_string = current_datetime.strftime('%Y_%m_%d_%H%M%S')
    return date_string

def writeData(data, path):
    with open(path, 'w', newline='\n', encoding='UTF-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='|')
        for row in data:
            csvwriter.writerow(row)

def processResponse(text):
    output = []
    if(text is None or len(text)==0):
        return []
    #split the text into rows
    rows = text.split('|')
    for r in rows:
        parts = r.split(',')
        if(len(parts)>40):
            obj = []
            # RO Code
            obj.append(parts[37])
            # Petrol Pump Name
            obj.append(parts[0])
            # Address
            obj.append(parts[3])
            # Dealer/Partner/Operator/Contact Person Name
            obj.append(parts[30])
            # Contact No
            obj.append(parts[36])
            # Petrol Price
            obj.append(parts[25])
            # Diesel Price
            obj.append(parts[26])
            # XTRAPREMIUM Price
            obj.append(parts[27])
            # XTRAMILE Price
            obj.append(parts[28])
            # XP100 Price
            obj.append(parts[41])
            # XP95 Price
            obj.append(parts[42])
            # XG Price
            obj.append(parts[43])
            # E100 Price
            obj.append(parts[44])
            # District
            obj.append(parts[34])
            # State
            obj.append(parts[35])
            # State Office
            obj.append(parts[31])
            # Divisional Office
            obj.append(parts[32])
            # Sales Area
            obj.append(parts[33])
            # Sales Officer Contact No
            obj.append(parts[29])
            # Latitude
            obj.append(parts[1])
            # Longitude
            obj.append(parts[2])
            #add to result
            output.append(obj)

    return output

def getDataForDistrict(id):
    #make request
    URL = 'https://associates.indianoil.co.in/PumpLocator/DistrictWiseLocator'
    payload = 'district={0}'.format(id)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    req = requests.post(URL, data=payload, headers=headers)
    if(req.status_code==200):
        #process the data
        data = processResponse(req.text)
        return data 
    else:
        return None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)
if __name__ == "__main__":

    #Get the list of the Districts from the CSV file
    Districts = []
    with open('input.csv', 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter='|')
        for row in csvreader:
            Districts.append(row)
    headers = ["RO Code","Petrol Pump Name","Address","Dealer/Partner/Operator/Contact Person Name","Contact No",
                "Petrol Price","Diesel Price","XTRAPREMIUM Price","XTRAMILE Price","XP100 Price",
                "XP95 Price","XG Price","E100 Price","District","State","State Office","Divisional Office",
                "Sales Area","Sales Officer Contact No", "Latitude", "Longitude"]
        
    idx = 0
    recordCount = 0
    tempPath = 'IOCL.csv'
    with open(tempPath, 'w', newline='\n', encoding='UTF-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='|')
        csvwriter.writerow(headers)

        #for each district
        for d in Districts:
            id = d['id']
            name = d['district']
            logger.info('Processing {0} ({1})'.format(name, idx))
            #need to get the data
            data = getDataForDistrict(id)
            recordCount += len(data)
            #write the data
            if(data is not None):
                #write this data
                csvwriter.writerows(data)
            idx = idx + 1

    if(recordCount>0):
        logger.info('Total Records: {0}'.format(recordCount))
        #Move the IOCL file to the archive folder
        destination_path = os.path.join('archive', 'IOCL_{0}.csv'.format(getCurrentTimeStamp()))
        shutil.move(tempPath, destination_path)
    else:
        #delete this file
        os.remove(tempPath)
