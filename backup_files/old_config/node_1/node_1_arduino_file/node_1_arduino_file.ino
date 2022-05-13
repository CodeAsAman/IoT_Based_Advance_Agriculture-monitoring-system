// send next/each value after/with delay of 
int const delay_4=1000;  // milliseconds 

// load header files for DS18B20 thermometer sensor 
#include <OneWire.h> 
#include <DallasTemperature.h>

// Data (signal) wire is plugged into pin 2 (digital) on the Arduino 
#define ONE_WIRE_BUS 2 
// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs) 
OneWire oneWire(ONE_WIRE_BUS); 
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature ds18b20_sensor(&oneWire);

//##########################################################################################################

// Set values for capacitive soil sensor at pin A0 -----
//const int maxC=595;  // maximum capacitor value (3.3VDC)
//const int minC=233;  // minimum capacitor value (3.3VDC)
int current_capacitor_value=0;
//int soil_moisture_percentage=0;

//#########################################################################################################

// Set values for soil PH sensor at A1
// initial sensor value   
int ph_sensor_value=0;


void setup() {
  // open serial port, set the baud rate to 9600 bps
  Serial.begin(9600); 
  // start communication with DS18B20 thermometer sensor
  ds18b20_sensor.begin(); 
  }

void loop() {
  // read soil moisture capacitive value by capacitive soil sensor 
  current_capacitor_value=analogRead(A0);
  Serial.print(current_capacitor_value);Serial.print(",");
  // read soil temperature value by DS18B20 thermometer sensor 
  ds18b20_sensor.requestTemperatures();
  Serial.print(ds18b20_sensor.getTempCByIndex(0));Serial.print(",");
  // read multiple times value from ph sensor at A1
  ph_sensor_value=int((float)analogRead(A1)*(14.0/1023.0));
  Serial.print(ph_sensor_value);Serial.print(",");
  // End of line / read
  Serial.println(";");
  // make await before next value
  delay(delay_4);
  }
