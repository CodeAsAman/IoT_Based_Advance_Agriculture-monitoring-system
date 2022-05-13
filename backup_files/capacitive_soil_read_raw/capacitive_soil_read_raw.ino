/*Program to get capacitive soil sensor 
minimum and maximum value*/
int capacitive_value=0;

void setup() {Serial.begin(9600);}

void loop() {
  capacitive_value = analogRead(A0); // read capistor value
  Serial.println(capacitive_value);

}
