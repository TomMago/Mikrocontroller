/*
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2
---->	http://www.adafruit.com/products/1438
*/

#include <Wire.h>
#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *motor1 = AFMS.getMotor(1);
Adafruit_DCMotor *motor2 = AFMS.getMotor(2);
Adafruit_DCMotor *motor3 = AFMS.getMotor(3);
Adafruit_DCMotor *motor4 = AFMS.getMotor(4);

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  Serial.println("Adafruit Motorshield v2 - DC Motor test!");

  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz

  // Set the speed to start, from 0 (off) to 255 (max speed)
  //myMotor->setSpeed(150);
  //myMotor->run(FORWARD);
  // turn on motor
  //myMotor->run(RELEASE);
	  }

void loop() {
  uint8_t i;

  delay(3000);

  // 1. Motor
  Serial.println("Motor 1 Test:");
  Serial.println("Vorwaerts");

  delay(500);

  motor1->run(FORWARD);
  motor1->setSpeed(50);
  delay(500);
  motor1->setSpeed(0);
  delay(500);

  Serial.println("Rueckwaerts");

  motor1->run(BACKWARD);
  motor1->setSpeed(50);
  delay(500);
  motor1->setSpeed(0);
  delay(50);


  motor1->run(RELEASE);
  delay(3000);





  // 2. Motor
  Serial.println("Motor 2 Test:");
  Serial.println("Vorwaerts");

  delay(500);

  motor2->run(FORWARD);
  motor2->setSpeed(50);
  delay(500);
  motor2->setSpeed(0);
  delay(500);

  Serial.println("Rueckwaerts");

  motor2->run(BACKWARD);
  motor2->setSpeed(50);
  delay(500);
  motor2->setSpeed(0);
  delay(50);


  motor2->run(RELEASE);
  delay(3000);





  // 3. Motor
  Serial.println("Motor 3 Test:");
  Serial.println("Vorwaerts");

  delay(500);

  motor3->run(FORWARD);
  motor3->setSpeed(50);
  delay(500);
  motor3->setSpeed(0);
  delay(500);

  Serial.println("Rueckwaerts");

  motor3->run(BACKWARD);
  motor3->setSpeed(50);
  delay(500);
  motor3->setSpeed(0);
  delay(50);

  motor3->run(RELEASE);
  delay(3000);






  // 4. Motor
  Serial.println("Motor 4 Test:");
  Serial.println("Vorwaerts");

  delay(500);

  motor4->run(FORWARD);
  motor4->setSpeed(50);
  delay(500);
  motor4->setSpeed(0);
  delay(500);

  Serial.println("Rueckwaerts");

  motor4->run(BACKWARD);
  motor4->setSpeed(50);
  delay(500);
  motor4->setSpeed(0);
  delay(50);


  motor4->run(RELEASE);
  delay(3000);

  Serial.println("Motortest abgeschlossen!");
  delay(100000);

//
//  // 2. Motor
//  Serial.println("Motor 2 Test:");
//  Serial.println("Vorwärts");
//
//  motor2->run(FORWARD);
//  for (i=0; i<200; i++) {
//    motor2->setSpeed(i);
//    delay(7);
//  }
//  for (i=200; i!=0; i--) {
//    motor2->setSpeed(i);
//    delay(7);
//  }
//
//  Serial.println("Rückwärts");
//
//  motor2->run(BACKWARD);
//  for (i=0; i<200; i++) {
//    motor2->setSpeed(i);
//    delay(7);
//  }
//  for (i=200; i!=0; i--) {
//    motor2->setSpeed(i);
//    delay(7);
//  }
//
//  motor2->run(RELEASE);
//  delay(10000);
//
//
//
//  // 3. Motor
//  Serial.println("Motor 3 Test:");
//  Serial.println("Vorwärts");
//
//  motor3->run(FORWARD);
//  for (i=0; i<255; i++) {
//    motor3->setSpeed(i);
//    delay(5);
//  }
//  for (i=255; i!=0; i--) {
//    motor3->setSpeed(i);
//    delay(5);
//  }
//
//  Serial.println("Rückwärts");
//
//  motor3->run(BACKWARD);
//  for (i=0; i<255; i++) {
//    motor3->setSpeed(i);
//    delay(5);
//  }
//  for (i=255; i!=0; i--) {
//    motor3->setSpeed(i);
//    delay(5);
//  }
//
//  motor3->run(RELEASE);
//  delay(1000);
//
//
//
//  // 4. Motor
//  Serial.println("Motor 4 Test:");
//  Serial.println("Vorwärts");
//
//  motor4->run(FORWARD);
//  for (i=0; i<255; i++) {
//    motor4->setSpeed(i);
//    delay(5);
//  }
//  for (i=255; i!=0; i--) {
//    motor4->setSpeed(i);
//    delay(5);
//  }
//
//  Serial.println("Rückwärts");
//
//  motor4->run(BACKWARD);
//  for (i=0; i<255; i++) {
//    motor4->setSpeed(i);
//    delay(5);
//  }
//  for (i=255; i!=0; i--) {
//    motor4->setSpeed(i);
//    delay(5);
//  }
//
//  motor4->run(RELEASE);
//  delay(1000);
//
//  Serial.println("Motortest abgeschlossen!");
}