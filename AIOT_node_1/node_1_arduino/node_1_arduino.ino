/*#######################################################CONNECTIONS#######################################################
 * NOTE: Do not use Pins: DIGITAL 2,9,10,11,12, and 13 as they are used by LoRa shield. 
 * AM2105A :-: Air temperature and humidity 
 * AM2105A :: BY DHT Header, Pins - 3.3VDC:RED, GND:BLACK, YELLOW:DIGITAL4 
 *            10K resistor from pin DIGITAL4 (data) to pin 3.3VDC (power)
 * CAPACITIVE_SOIL_SENSOR :-: Soil humidity            
 * CAPACITIVE_SOIL_SENSOR :: NO HEADER, Pins - 3.3VDC:RED, GND:BLACK, YELLOW:ANALOG0
 * DS18B20 :-: Soil temperature (thermometer sensor)
 * DS18B20 :: BY OneWire and DallasTemperature Header, Pins - 5VDC:RED, GND:BLACK, YELLOW:DIGITAL3 
 *            4K7 (4.7K) resistor from pin DIGITAL3 (data) to pin 3.3VDC (power)
 * SOIL PH SENSOR :-: Soil PH sensor
 * SOIL PH SENSOR :: NO HEADER, Pins - 5VDC:V+, GND:G, ANALOG1:P0
 */

// ----------------------------------------------------------------------------------------------------------------------

// send next/each value after/with delay of 1 second 
int const DELAY4=30000;                             // milliseconds  (NOTE: Cn't be less than 2000 milliseconds)
int timeGap=250;                                    // gap for time between readings (most time takking)
char const NODENAME='2';                            // node name  

// -----------------------------------------------------------------------------------------------------------------------

// load header files
#include<DHT.h>                                     // for AM2105A (Temperature and Humidity)
#include<OneWire.h>                                 // for DS18B20 soil thermometer sensor (soil temperature)
#include<DallasTemperature.h>                       // for DS18B20 soil thermometer sensor (soil temperature) 
#include<RH_RF95.h>                                 // for LoRa sending and reciving  

// ------------------------------------------------------------------------------------------------------------------------

// PIN DEFINATIONS
#define AM2105APIN 4                                // of AM2105A (as AM2105A)
#define SOILCAPPIN A0                               // of capacitive soil sensor
#define SOILTHMPIN 3                                // of soil thermometer sensor
#define SOILPHPIN A1                                // of soil PH sensor 

// -------------------------------------------------------------------------------------------------------------------------

// other definations 
#define AM2105ATYPE DHT22                           // AM2105A (DHT) sensor type 

// -------------------------------------------------------------------------------------------------------------------------

// Initialize sensor
DHT AM2105ASENSOR(AM2105APIN,AM2105ATYPE);          // setup AM2105A (AM2105A) sensor 
// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs) 
OneWire oneWire(SOILTHMPIN);                        // for soil thermometer sensor (soil temperature)
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature DS18B20(&oneWire);                // for soil thermometer sensor (soil temperature)
// make LoRa connection object 
RH_RF95 LoRaConnection;                             // for send data by LoRa module 

// ------------------------------------------------------------------------------------------------------------------------

// variable to controll detailed printing on serial monitor 
bool detailed=false;
// variables to store sensor values ------------------------------
// AM2105A (as AM2105A) sensor 
int AM2105A_ARRAY_SIZE=5;
float AM2105A_VALUES[]={-1.0,-1.0,-1.0,-1.0,-1.0};  // to store humidity, temperature(°C), temperature(°F), heat index (°C and °F)
// set values for capacitive soil sensor at pin A0 ---------------
const int max_CAPACITOR_VALUE=590;                  // maximum capacitor value (3.3VDC) (in dry air)
const int min_CAPACITOR_VALUE=265;                  // minimum capacitor value (3.3VDC) (in water)
int CURRENT_CAPACITOR_VALUE=0;                      // capacitor value (soil humidity)
// soil thermometer sensor (soil temperature) --------------------
float CURRENT_SOIL_TEM_VALUE=0;                     // soil temperature value 
// Soil PH sensor at A1 (SOil PH Value) --------------------------
float CURRENT_SOIL_PH_VALUE=0;                      // soil PH value 

// -------------------------------------------------------------------------------------------------------------------------

// setup function 
void setup() {
  // open serial port, set the baud rate to 9600 bps
  Serial.begin(9600); 
  // start communication with AM2105A temperature and humidity sensor
  AM2105ASENSOR.begin();
  // start communication with DS18B20 thermometer sensor
  DS18B20.begin(); 
  // Wait a few seconds before starting measurements.
  delay(2000);
  }

// ---------------------------------------------------------------------------------------------------------------------------

// loop function 
void loop(){
  // read temeperature and humidity 
  callAM2105A(detailed=false);
  // read soil moisture capacitive value by capacitive soil sensor 
  callSOILCAP(detailed=false);
  // read soil temeperature by DS18B20 
  callDS18B20(detailed=false);
  // read PH value 
  callPHSENSOR(detailed=false);
  // make wait for a while before start sending 
  delay(timeGap*2);
  // make send message 
  callLoRaSender(detailed=true);                      
  // make await before next value
  delay(DELAY4-(timeGap*2));
}

// ----------------------------------------------------------------------------------------------------------------------------

// function to read temeperature and humidity
float callAM2105A(bool detailed){
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  AM2105A_VALUES[0]=AM2105ASENSOR.readHumidity();
  // Read temperature as Celsius (the default)
  AM2105A_VALUES[1]=AM2105ASENSOR.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  AM2105A_VALUES[2]=AM2105ASENSOR.readTemperature(true);
  // Check if any reads failed and exit early (to try again).
  if (isnan(AM2105A_VALUES[0])||isnan(AM2105A_VALUES[2])||isnan(AM2105A_VALUES[3])){
    // print notification if value fail to read 
    Serial.println("Failed to read from AM2105A sensor!");
    // make all values to -1 
    AM2105A_VALUES[0]=-1;
    AM2105A_VALUES[1]=-1;
    AM2105A_VALUES[2]=-1;
    AM2105A_VALUES[3]=-1;
    AM2105A_VALUES[4]=-1;
    // make return that reading failed 
    return -1;
  }
  // Compute heat index in Fahrenheit (the default)
  AM2105A_VALUES[3]=AM2105ASENSOR.computeHeatIndex(AM2105A_VALUES[2],AM2105A_VALUES[0]);
  // Compute heat index in Celsius (isFahreheit = false)
  AM2105A_VALUES[4]=AM2105ASENSOR.computeHeatIndex(AM2105A_VALUES[1],AM2105A_VALUES[0],false);
  // if value have to be printed on serial monitor 
  if (detailed) {
    // make print all values 
    Serial.print("Humidity: ");Serial.print(AM2105A_VALUES[0]);
    Serial.print("%  Temperature: ");Serial.print(AM2105A_VALUES[1]);
    Serial.print("°C ");Serial.print(AM2105A_VALUES[2]);Serial.print("°F  Heat index: ");
    Serial.print(AM2105A_VALUES[4]);Serial.print("°C ");Serial.print(AM2105A_VALUES[3]);Serial.println("°F");
  }
  // make return
  return 0;  
}

// function to read soil moisture capacitive value by capacitive soil sensor 
float callSOILCAP(bool detailed){
  // read soil moisture capacitive value by capacitive soil sensor 
  CURRENT_CAPACITOR_VALUE=map(analogRead(SOILCAPPIN),min_CAPACITOR_VALUE,max_CAPACITOR_VALUE,100,0);
  // if value have to be printed on serial monitor 
  if (detailed) {
    // make print soil capacitor (humidity) value values
    Serial.print("Soil capacitor value (Soil humidity): ");Serial.println(CURRENT_CAPACITOR_VALUE);
  }
  // make return 
  return 0; 
}

// function to read soil temeprature by soil thermometer sensor (soil temperature)
float callDS18B20(bool detailed){
  // read soil temperature value by DS18B20 thermometer sensor 
  DS18B20.requestTemperatures();                                    // call for temperature value
  CURRENT_SOIL_TEM_VALUE=DS18B20.getTempCByIndex(0);
  // if value have to be printed on serial monitor 
  if (detailed) {
    // make print soil temperature value values
    Serial.print("Soil temperature: ");Serial.println(CURRENT_SOIL_TEM_VALUE);
  }
  // make return 
  return 0; 
}

// function to read ph sensor value
float callPHSENSOR(bool detailed){
  // read soil PH by soil PH sensor 
  CURRENT_SOIL_PH_VALUE=(float)analogRead(SOILPHPIN)*(14.0/1023.0);
  // make print soil temperature value values
  if (detailed){
  Serial.print("Soil PH: ");Serial.println(CURRENT_SOIL_PH_VALUE);
  }
  // make return 
  return 0; 
}

// function to send data to LoRa reciver 
float callLoRaSender(bool detailed){
  // make string to send to reciver 
  String sensorData="Node"+String(NODENAME)+"::";
  // add AM2105A all values to data
  sensorData+="H,Tc,Tf,HIc,HIf:";                 // to sending humidity, temperature(°C), temperature(°F), heat index (°C and °F)
  for(int i=0;i<AM2105A_ARRAY_SIZE;i++){
    // add data
    sensorData+=String(AM2105A_VALUES[i])+",";
  }
  // mark end of the value for AM2105A
  sensorData+=";";
  // add values for soil Humidity
  sensorData+="SH:"+String(CURRENT_CAPACITOR_VALUE)+";";
  // add values for soil temperature
  sensorData+="ST:"+String(CURRENT_SOIL_TEM_VALUE)+";";
  // add value for soil PH sensors 
  sensorData+="PH:"+String(CURRENT_SOIL_PH_VALUE)+";";
  // sending data - convert data to character array
  char dataArray[sensorData.length()+1];
  sensorData.toCharArray(dataArray,sensorData.length()+1);
  // if value have to be printed on serial monitor 
  if (detailed) {
    // print array to send 
    Serial.print("Sending: "); Serial.println(dataArray);
  }
  // Sending data to reciver 
  LoRaConnection.send(dataArray,sizeof(dataArray));
  LoRaConnection.waitPacketSent();
}
