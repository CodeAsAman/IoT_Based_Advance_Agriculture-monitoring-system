# delay - Time in sconds after which each value to be send 
# minimum -> 10 seconds (arduino reads / send value after each 5 seconds))
wait_4=10    # must be less than arduino delay 

# send at 

#####################################################################################
# install serial module -> python3 -m pip install pyserial
# all-ready install 
import serial 
# serial port - "/dev/ttyUSB0" or "/dev/ttyACM0"
# Check by (in terminal)-> $ ls /dev/tty*
# NOTE - Activate Serial Communication by -> 
##  $ sudo raspi-config
## Select - 5 Interfacing options -> P6 Serial Port. 

#######################################################################################
# load DHT11 sensor value; install -> python3 -m pip install Adafruit-DHT
import Adafruit_DHT
# Set sensor type : Options are DHT11,DHT22 or AM2302
sensor=Adafruit_DHT.DHT22
# at pin 
gpio=4

#######################################################################################
# install -> python3 -m pip install pyrebase
import pyrebase 

config = {
  "apiKey": "AIzaSyAdZpi9epC2hNLjDefiuEDqLSmfthwV_B4",
  "authDomain": "iotdata-efa90.firebaseapp.com",
  "databaseURL": "https://iotdata-efa90-default-rtdb.firebaseio.com",
  "projectId": "iotdata-efa90",
  "storageBucket": "iotdata-efa90.appspot.com",
  "messagingSenderId": "1090215176549",
  "appId": "1:1090215176549:web:4055e982881136a12c598c"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#######################################################################################

import numpy as np  # for numerical calculation 
import time         # to make program wait 

while True:
    try: 
        # read value of "CAPACITIVE_SOIL_SENSOR_VALUE" (raw) and DS18B20_THERMOMETER values from 
        # serial like -> b'590,20.94,;\r\n' 
        serial_connection=serial.Serial('/dev/ttyUSB0',9600)
        # read line form connection 
        raw_data=serial_connection.readline()
        # change byte object to string object 
        raw_data=raw_data.decode('utf-8')
        # split data 
        raw_data=raw_data.split(';')[0].split(',')[:-1]   # list of data 
        # CAPACITIVE_SOIL_SENSOR_VALUE - 'maximum_raw':595 to 'minimum_raw':233; map values to percentage
        # np.interp(value,[min-value,max-value],[to-min,to-max])
        raw_data[0]=round(np.interp(int(float(raw_data[0])),[233,595],[100,0]),2)
        # convert soil temperature to float
        raw_data[1]=float(raw_data[1])
        # read data from dht11 sensor
        raw_data.extend(np.round(Adafruit_DHT.read(sensor,gpio),2))
        if not len(raw_data)==5:
            raw_data=[0,0,0,0,0]
            print('[INFO]: Error! can get all values')
    except Exception as e:
        print('[INFO]: Error ->',e)
        raw_data=[0,0,0,0,0]
    #print(raw_data)
    db.child("node_3").child("view").set(raw_data)
    time.sleep(wait_4)