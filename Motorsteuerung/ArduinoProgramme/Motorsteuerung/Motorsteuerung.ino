#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <math.h>

// Setup des Motorshields und LCDs
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
LiquidCrystal_I2C lcd(0x20, 16, 2);

// neue Motoren hinzufuegen
Adafruit_DCMotor *Motor1 = AFMS.getMotor(1);
Adafruit_DCMotor *Motor2 = AFMS.getMotor(2);
Adafruit_DCMotor *Motor3 = AFMS.getMotor(3);
Adafruit_DCMotor *Motor4 = AFMS.getMotor(4);

//US Bibliothek
#include <NewPing.h>

#define SONAR_NUM     4 // Anzahl der Sensoren
#define MAX_DISTANCE 40 // Maximalze Distanz (in cm) fuer US-Sensoren
#define PING_INTERVAL 60 // Millisekunden zwischen Pings (29 ms ist Minimum wegen Crosstalk)

unsigned long pingTimer[SONAR_NUM]; // Array mit den Zeiten fuer die Pings der Sensoren
unsigned int cm[SONAR_NUM];         // Array mit gemessenen Distanzen
uint8_t currentSensor = 0;          // zeigt an, welcher US-Sensor aktiv ist 
unsigned long uszeitaktuell=0;
unsigned long uszeit1=0;

NewPing sonar[SONAR_NUM] = {     // Sensor Objekt Array
// von jedem Sensor trigger pin, echo pin, and maximale Distanz
  NewPing(2, 3, MAX_DISTANCE), // rechts
  NewPing(8, 9, MAX_DISTANCE), //vorne
  NewPing(6, 7, MAX_DISTANCE), //links
  NewPing(4, 5, MAX_DISTANCE), //hinten
};



//Variablen fuer Motorsteuerung
int M[4] = {0, 0, 0, 0}; //enthaelt die Geschwindigkeitswerte fuer Motoren
bool D = true;       // bestimmt Richtung der Motoren, D=true ist vorwaerts
bool R = false;      //Statusvariable fuer Reset
bool Z = false;      //Statusvariable fuer Nulldurchgang
String C=String("CM M0:000 M1:000 M2:000 M3:000"); //Anfangsstring, wird spaeter durch empfangenen String ueberschrieben
int i;

//Pins des Motorumdrehungen-Decoders
#define LEFT 20
#define RIGHT 21
 
//Array der Umdrehungswerte (aufsummiert)
long coder[2] = {
  0,0};
 //Array der letzten Geschwindigkeitswerte
 int lastSpeed[2] = {
  0,0};  
 
// Variablen fuer Dimmer
int SensorWert = 0;
int Pwm = 0;
//Werte fuer Sendeschleife
long intervall2 = 1000; //Zeit für Senden, aendern!
long zeit2 = 0;          //letzter Zeitpunkt in Sendeschleife
//Werte fuer Blinker
unsigned long zeitaktuell = 0; 
long intervall = 100;
long zeit1 = 0;          
int ledstatus = LOW;


//Setup wird am Anfang ausgefuehrt
void setup() {
  Serial.begin(57600); //Baud-Rate, aendern falls nur Gruetze ueber Serial-Monitor angezeigt wird
  AFMS.begin(); //Motorschield 

  //Pins initialisieren
  pinMode(9, INPUT); //Decoder
  pinMode(10,INPUT); //Decoder
  pinMode(8, OUTPUT); //Tagfahrlicht
  pinMode(7,OUTPUT); //Bremslicht
  pinMode(0,OUTPUT); //Piezolautsprecher
  pinMode(13,OUTPUT); //Testled
  
  //US-Sensoren Pings initialisieren
  pingTimer[0] = millis() + 75;           // Erster Ping nach 75ms, etwas Puffer lassen, ggf. erhoehen
  for (uint8_t i = 1; i < SONAR_NUM; i++) // Startpunkt der anderen Sensoren
  pingTimer[i] = pingTimer[i - 1] + PING_INTERVAL;

  //Initialisiert Unterbruchung fuer die Decoder, wird nur aktiviert falls eine Aenderung an dem Pin dedektiert wird
  attachInterrupt(LEFT, LwheelSpeed, CHANGE);    
  attachInterrupt(RIGHT, RwheelSpeed, CHANGE);   
  
  //LCD-Display (das mit I2C-Backpack)
  lcd.init();
  lcd.backlight();
  lcd.print("Startup...");
  delay(1000);
}

//Funktion, die Wert iterieren falls Aenderung am Decoder-Pin dedektiert werde (siehe setup())
void LwheelSpeed()
{
  coder[LEFT] ++;  
}
void RwheelSpeed()
{
  coder[RIGHT] ++; 
}

//Dimmer in Abhaengigkeit des Helligkeits-Sensors
void dimmer(int Wert) {
  Pwm = 0.6 * (Wert) - 195;
  if (Pwm > 255) {
    Pwm = 255;
  }
  else if (Pwm < 0) {
    Pwm = 0;
  }
  analogWrite(8, Pwm);
}


//frueher wurde hier der Motorwert berechnet, jetzt alles im Python programm
//die Einparkautomatik koennte hier eingebaut werden
void MotorWert() {
  
}

//Ausgabe an LCD Display und ueber Serial-Display
void ausgabe(){
//  zeitaktuell = millis();
//  if (zeitaktuell - zeit1 > 1000){
//    zeit1=zeitaktuell;
//    lcd.clear();
//  }
  lcd.home();
  lcd.print("Char=");
  lcd.print(C);
  lcd.setCursor(0,1); //setzt Cursor dorthin, wo der Motorwert stehen soll
  lcd.print(M[0]);
  //lcd.print(" ");
  lcd.setCursor(4,1);
  lcd.print(M[1]);
  //lcd.print(" ");
  lcd.setCursor(8,1);
  lcd.print(M[2]);
  //lcd.print(" ");
  lcd.setCursor(12,1);
  lcd.print(M[3]);
  //lcd.print(" ");
  
  //misst Zeit und aktiviert ggf. Uebertragung ueber Serial-Schnittstelle
  //Achtung: muss kompatibel bleiben mit Python Programm!
  zeitaktuell = millis();
  if (zeitaktuell - zeit2 > intervall2){
    zeit2=zeitaktuell;
    //letzte Motorwerte
    Serial.print("AM ");
    for (int i = 0; i < 2; i++) {
       Serial.print(lastSpeed[i]);
       Serial.print(" ");
    }
    Serial.print("\n");
    
    //letzte US-Sensorwerte
    Serial.print("AU ");
    for (uint8_t i = 0; i < SONAR_NUM; i++) {
       Serial.print(cm[i]);
       Serial.print(" ");
    }
    Serial.print("\n");
  }
}
//Uebergabe der Werte an Motor
void fahr() {
  //Vorwaerts
  if (D) {
    Motor1->run(FORWARD); 
    Motor2->run(FORWARD);
    Motor3->run(FORWARD);
    Motor4->run(FORWARD);
  }
  //Rueckwaerts
  else {
    Motor1->run(BACKWARD);
    Motor2->run(BACKWARD);
    Motor3->run(BACKWARD);
    Motor4->run(BACKWARD);
  }
  Motor1->setSpeed(M[0]);
  Motor2->setSpeed(M[1]);
  Motor3->setSpeed(M[2]);
  Motor4->setSpeed(M[3]);
}


//Blinker in Abhaengigkeit von letztem Buchstaben, muesste also umgeschrieben werden

//void blinker(char H) {
//  zeitaktuell = millis();
//  if (H == 'a') {
//    digitalWrite(10,LOW);
//    if (zeitaktuell - zeit1 > intervall){
//    zeit1=zeitaktuell; 
//    if (ledstatus == LOW)
//      ledstatus = HIGH;
//    else 
//      ledstatus = LOW;
//    digitalWrite(9,ledstatus);
//    }
//  }
//  else if (H == 'd') {
//    digitalWrite(9,LOW);
//    if (zeitaktuell - zeit1 > intervall){
//    zeit1=zeitaktuell; 
//    if (ledstatus == LOW)
//      ledstatus = HIGH;
//    else 
//      ledstatus = LOW;
//    digitalWrite(10,ledstatus);
//  }
//  }
//  else if ((H != 'd')&&(H != 'a')&&(ledstatus == HIGH)){
//  ledstatus = LOW;
//  digitalWrite(9,ledstatus);
//  digitalWrite(10,ledstatus);
//  }
//}


//Empfaengt Daten,
void serialEvent() {
    //Serial.print("test ");

    //Pruefen, ob serieller Monitor erkennbar
    if (Serial.available() > 0)
    {
    String C = "";
    char character;
    //Chars einlesen und aneinanderreihen
    while(Serial.available()) {
      character = Serial.read();
      C.concat(character);
    }
    //bemerkbar machen durch Test-LED auf Board 
    digitalWrite(13,HIGH);
    delay(10);
    digitalWrite(13,LOW);
    //Pruefen, ob Codewort richtig ist 
    int ifrom;
      int ito=26;
      String substr;
      String teststring=String("CM");
      //String Cb=String("CM M0:000 M1:000 M2:000 M3:000\n");
      //C=Serial.readString();
      
      //String separieren und in Integer konvertieren
      if (C.startsWith(teststring)){
        ifrom=C.indexOf("M3:");
        //Serial.print(ifrom);
        substr=C.substring(ifrom+3,31);
        M[3]=substr.toInt();
        Serial.print(substr);
        ito=ifrom-1;
        ifrom=C.indexOf("M2:");
        substr=C.substring(ifrom+3,ito);
        M[2]=substr.toInt();
        ito=ifrom-1;
        ifrom=C.indexOf("M1:");
        substr=C.substring(ifrom+3,ito);
        M[1]=substr.toInt();
        ito=ifrom-1;
        ifrom=C.indexOf("M0:");
        substr=C.substring(ifrom+3,ito);
        M[0]=substr.toInt();
        D=true;
         //Serial.print("Motorwerte: ");
         //for (int i = 0; i < 4; i++) {
         //  Serial.print(M[i]);
         //  Serial.print(" ");
         //}
         //Serial.print("\n");
         //delay(1000);
        
        //negative Werte in positive Werte umwandeln (Motorshield nimmt nur positive Werte an)
        if (M[0]<0){
          M[0]=-M[0];
          M[1]=-M[1];
          M[2]=-M[2];
          M[3]=-M[3];
          D=false;
        }
    
    }
  //wenn Verbindung unterbrochen oder kein Befehl gesendet wird
  //ggf. Aenderung, zB vorletzten Motorwert speichern und auf diesen zurueck gehen
  else 
  {
//    
//    M[0]=0;
//    M[1]=0;
//    M[2]=0;
//    M[3]=0;
    //Serial.print("No Input!");
  }
}
}

void us() {
  // Loop durch alle Sensoren
  for (uint8_t i = 0; i < SONAR_NUM; i++) { 
    if (millis() >= pingTimer[i]) {         // Pruefen, ob dieser Sensor gepingt werden soll
      pingTimer[i] += PING_INTERVAL * SONAR_NUM;  // naechsten Zeitpunkt setzen2
      if (i == 0 && currentSensor == SONAR_NUM - 1) oneSensorCycle(); //alle Sensoren abgeklappert, Auswertungsfunktion
      sonar[currentSensor].timer_stop();          // Absicherung, dass keine zwei Timer gesetzt werden.
      currentSensor = i;                          // aktueller Sensor
      cm[currentSensor] = 100;                      // grosse Distanz, falls kein Wert empfangen
      sonar[currentSensor].ping_timer(echoCheck); // startet ping und wartet auf Aenderung am Pin, Programme werden weiter ausgefuehrt
      //Piezolautsprecher 
      if (cm[currentSensor]<3){
        digitalWrite(0,HIGH);
      }
      digitalWrite(0,LOW);
    }
  }
  
  
}

//wird aufgerufen, falls Ping empfangen
void echoCheck() { 
  if (sonar[currentSensor].check_timer())
    //empfangener Wert wird umgerechnet und in Array geschrieben
    cm[currentSensor] = sonar[currentSensor].ping_result / US_ROUNDTRIP_CM;
//    if (cm[currentSensor]!=100){
//    Serial.println(cm[currentSensor]);
//    }
    //Serial.println("Echo");
    //Serial.println(cm[currentSensor]);
}

void oneSensorCycle() { // alle Sensoren gemessen, Auswertung
  //schaut, ob eine der Sensoren sehr nah an Hindernis ist -> Stop der Motoren
  bool check=false;
  uszeitaktuell=millis();
  for (uint8_t i = 0; i < SONAR_NUM; i++) {
    if (cm[i]<10)
      check=true;
  }
  if ((check)&&(uszeitaktuell-uszeit1>2000)){
    for (int i = 0; i < 4; i++) {
        M[i] = 0;
    }
  uszeit1=uszeitaktuell;
  }
}


//Decoder funktion, berechnet Geschwindigkeit aus Umdrehungen 
void decoder(){
   
  static unsigned long timer = 0;               
   
  if(millis() - timer > 100){    
       
   // Serial.print("Coder value: ");
   // Serial.print(coder[LEFT]);
    //Serial.print("[Left Wheel] ");
    //Serial.print(coder[RIGHT]);
    //Serial.println("[Right Wheel]");
    timer = millis();
    lastSpeed[LEFT] = coder[LEFT]/timer*100;   //Geschwindigkeit berechnen
    lastSpeed[RIGHT] = coder[RIGHT]/timer*100;
    coder[LEFT] = 0;                 //letzte Werte loeschen
    coder[RIGHT] = 0;

  }
   
}


//eigentliche Funktion, wird dauerhaft ausgefuehrt und klappert Unterfunktionen ab
void loop() {
  MotorWert();
  us();
  fahr();
  ausgabe();
  //blinker(C);
  decoder();
  SensorWert = analogRead(A0);
  dimmer(SensorWert);
  //delay(20);
}
