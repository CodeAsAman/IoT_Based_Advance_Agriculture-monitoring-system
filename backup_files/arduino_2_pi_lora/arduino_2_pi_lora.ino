//#include <SPI.h>
#include <RH_RF95.h>

RH_RF95 rf95;

void setup() 
{
  Serial.begin(9600);
  if (!rf95.init())
    Serial.println("init failed");
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

}

void loop()
{
  //String humidity = String(12.345); //int to String
  //String temperature = String(23.2887);
  String info ="";
  info += String(45.365268)+";";
  info += "Okay:"+String(18.8)+";";
  //String info="Hello !@#$%^&*()";
  Serial.print(info);
  char d[info.length()+1];
  info.toCharArray(d,info.length()+1); //String to char array
  Serial.print(" :->: ");
  Serial.print(d);
  Serial.println("    -> Sending to rf95_server");
  rf95.send(d,sizeof(d));
  rf95.waitPacketSent();
  delay(400);
}
