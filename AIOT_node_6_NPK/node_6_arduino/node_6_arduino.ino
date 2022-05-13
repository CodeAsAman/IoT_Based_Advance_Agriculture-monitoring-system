/*#######################################################CONNECTIONS#######################################################
 * NOTE: Do not use Pins: DIGITAL 2,9,10,11,12, and 13 as they are used by LoRa shield. 
 * NPK SENSOR :-: N(nitrogen), P(phosphorus), and K(potassium) in soil 
 * NPK SENSOR :: NO HEADER, 12VDC:BROWN, 0VDC:BLACK, B:BLUE, A:YELLOW (MAIN SENSOR TO BOARD)
 *               DRIVER PIN: 5VDC:VCC, 0VDC:GND, B:BLUE, A:YELLOW, R0:DIGITAL3, RE:DIGITAL4, DE:DIGITAL5, DI:DIGITAL6
 */

// ----------------------------------------------------------------------------------------------------------------------

// send next/each value after/with delay of 1 second 
int const DELAY4=30000;                             // milliseconds  (NOTE: Cn't be less than 2000 milliseconds)
int timeGap=250;                                    // gap for time between readings (most time takking)
char const NODENAME='6';      
// node name  

// -----------------------------------------------------------------------------------------------------------------------

// load header files
#include<SoftwareSerial.h>                          // for npk sensor 
#include<RH_RF95.h>                                 // for LoRa sending and reciving  

// ------------------------------------------------------------------------------------------------------------------------

// PIN DEFINATIONS
#define SOILNPKRO 5                                // for npk driver. Receiver Output. Connects to a serial RX pin on 
                                                    // the microcontroller 
#define SOILNPKRE 6                                 // for npk driver. Receiver Enable. Active LOW. Connects to a 
                                                    // digital output pin on a microcontroller. Drive LOW to enable receiver,
                                                    // HIGH to enable Driver 
#define SOILNPKDE 7                                 // for npk driver. Driver Enable. Active HIGH. Typically jumpered to RE Pin. 
#define SOILNPKDI 8                                 // for npk driver. Driver Input. Connects to serial TX pin on the 
                                                    // microcontroller 

// -------------------------------------------------------------------------------------------------------------------------

// other definations 

// -------------------------------------------------------------------------------------------------------------------------

// NPK sensor object 
SoftwareSerial NPKREADER(SOILNPKRO,SOILNPKDI);      // to read data from NPK
// make LoRa connection object 
RH_RF95 LoRaConnection;                             // for send data by LoRa module 

// ------------------------------------------------------------------------------------------------------------------------

// variable to controll detailed printing on serial monitor 
bool detailed=false;
// variables to store sensor values ------------------------------
// define resistor value to read from NPK 
//const byte code[]={0x01,0x03,0x00,0x1e,0x00,0x03,0x65,0xCD};
const byte nitroNPK[]={0x01,0x03,0x00,0x1e,0x00,0x01,0xe4,0x0c};
const byte phosNPK[]={0x01,0x03,0x00,0x1f,0x00,0x01,0xb5,0xcc};
const byte potaNPK[]={0x01,0x03,0x00,0x20,0x00,0x01,0x85,0xc0};
// variable to store raw values readed from resisitors 
byte NPKRawValues[11];
// Store value readed from NPK sensor 
byte CURRENT_NPK_VALUES[]={byte(-1),byte(-1),byte(-1)};
// NPK array size 
int NPK_ARRAY_SIZE=3;

// -------------------------------------------------------------------------------------------------------------------------

// setup function 
void setup() {
  // open serial port, set the baud rate to 9600 bps
  Serial.begin(9600); 
  // start communication with NPK sensor 
  NPKREADER.begin(9600);
  // define pinmode of NPK sensor 
  pinMode(SOILNPKRE,OUTPUT);                                      // Receiver Enable.Active LOW. 
                                                                  // Connects to a digital output pin on a microcontroller. 
                                                                  // Drive LOW to enable receiver, HIGH to enable Driver
  pinMode(SOILNPKDE,OUTPUT);                                      // Driver Enable. Active HIGH. Typically jumpered to RE Pin.
  // start connection with LoRa 
  while (!LoRaConnection.init()) {
    Serial.println("LoRa initialization failed!");
    delay(500);
  }
  // Wait a few seconds before starting measurements.
  delay(2000);
  }

// ---------------------------------------------------------------------------------------------------------------------------

// loop function 
void loop(){
  // read data from NPK sensor 
  callNPK(detailed=true,timeGap=250);                   // 3 reading with each of time gap of 250 milliseconds 
  // make wait for a while before start sending 
  delay(timeGap*2);
  // make send message 
  callLoRaSender(detailed=true);                      
  // make await before next value
  delay(DELAY4-(timeGap*4));
}


// ----------------------------------------------------------------------------------------------------------------------------

// function to read data from NPK sensor 
float callNPK(bool detailed, int timeGap){
  byte nitrogen_val,phosphorus_val,potassium_val;
 
  CURRENT_NPK_VALUES[0] = nitrogen();
  delay(timeGap);
  CURRENT_NPK_VALUES[1] = phosphorous();
  delay(timeGap);
  CURRENT_NPK_VALUES[2] = potassium();
  delay(timeGap);
  if (detailed) {
  Serial.print("Nitrogen: ");Serial.print(CURRENT_NPK_VALUES[0]);Serial.println(" mg/kg");
  Serial.print("Phosphorous: ");Serial.print(CURRENT_NPK_VALUES[1]);Serial.println(" mg/kg");
  Serial.print("Potassium: ");Serial.print(CURRENT_NPK_VALUES[2]);Serial.println(" mg/kg");
  }
  delay(2000);} 

// function to read raw data from NPK sensor for nitrogen 
byte nitrogen(){
  digitalWrite(SOILNPKDE,HIGH);
  digitalWrite(SOILNPKRE,HIGH);
  delay(10);
  if(NPKREADER.write(nitroNPK,sizeof(nitroNPK))==8){
    digitalWrite(SOILNPKDE,LOW);
    digitalWrite(SOILNPKRE,LOW);
    // When we send the inquiry frame to the NPK sensor, then it replies with the response frame
    // now we will read the response frame, and store the values in the values[] arrary, we will be using a for loop.
    for(byte i=0;i<7;i++){
      //Serial.print(NPKREADER.read(),HEX);                 // make value print 
      NPKRawValues[i]=NPKREADER.read();
      // Serial.print(values[i],HEX);
    }
  }
  return NPKRawValues[4]; // returns the Nigtrogen value only, which is stored at location 4 in the array
}

// function to read raw data from NPK sensor for phosphorous 
byte phosphorous(){
  digitalWrite(SOILNPKDE,HIGH);
  digitalWrite(SOILNPKRE,HIGH);
  delay(10);
  if(NPKREADER.write(phosNPK,sizeof(phosNPK))==8){
    digitalWrite(SOILNPKDE,LOW);
    digitalWrite(SOILNPKRE,LOW);
    // When we send the inquiry frame to the NPK sensor, then it replies with the response frame
    // now we will read the response frame, and store the values in the values[] arrary, we will be using a for loop.
    for(byte i=0;i<7;i++){
      //Serial.print(NPKREADER.read(),HEX);                 // make value print 
      NPKRawValues[i]=NPKREADER.read();
      // Serial.print(values[i],HEX);
    }
  }
  return NPKRawValues[4];
}

// function to read raw data from NPK sensor for potassium 
byte potassium(){
  digitalWrite(SOILNPKDE,HIGH);
  digitalWrite(SOILNPKRE,HIGH);
  delay(10);
  if(NPKREADER.write(potaNPK,sizeof(potaNPK))==8){
    digitalWrite(SOILNPKDE,LOW);
    digitalWrite(SOILNPKRE,LOW);
    // When we send the inquiry frame to the NPK sensor, then it replies with the response frame
    // now we will read the response frame, and store the values in the values[] arrary, we will be using a for loop.
    for(byte i=0;i<7;i++){
      //Serial.print(NPKREADER.read(),HEX);                 // make value print 
      NPKRawValues[i]=NPKREADER.read();
      // Serial.print(values[i],HEX);
    }
  }
  return NPKRawValues[4];
}

// function to send data to LoRa reciver 
float callLoRaSender(bool detailed){
  // make string to send to reciver 
  String sensorData="Node"+String(NODENAME)+"::";
  // add PNK all values to data
  sensorData+="P,N,K:";                                     // to sending humidity, temperature(°C), temperature(°F), heat index (°C and °F)
  for(int i=0;i<NPK_ARRAY_SIZE;i++){
    // add data
    sensorData+=String(CURRENT_NPK_VALUES[i])+",";
  }
  // mark end of the value for AM2105A
  sensorData+=";";
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
