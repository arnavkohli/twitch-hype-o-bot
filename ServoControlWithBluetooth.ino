#include <Servo.h>
#include <SoftwareSerial.h> //TX RX lib

int bluetoothTx = 10;
int bluetoothRx = 11;

SoftwareSerial bluetooth(bluetoothTx, bluetoothRx);

Servo myServo;

int multiplier = 0;

void setup() {
  // put your setup code here, to run once:
  myServo.attach(9);
  Serial.begin(9600);
  bluetooth.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (bluetooth.available() > 0){
    multiplier = bluetooth.read();
    Serial.println(multiplier);
  }
  myServo.write(0);
  delay(2000 / (multiplier + 1));
  myServo.write(180);
  delay(2000 / (multiplier + 1));

}
