//Initialiserung einer Variable
char C;

//setup
void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
}

// Loop Funktion die dauerhaft ausgefuehrt wird
void loop() {
  
  //Lesen des Zeichens
  if (Serial.available()>0){
    C=Serial.read();
  }
  
  //Schalten der LED
  if (C=='H'){
   digitalWrite(13, HIGH);
   delay(1000);
   Serial.println("Die Led leuchtet!");
  }
  else if (C=='L'){
   digitalWrite(13, LOW); 
   Serial.println("Die Led leuchtet nicht!");
   delay(1000);
  }
  else {
  digitalWrite(13, HIGH);   
  delay(100);             
  digitalWrite(13, LOW);    
  delay(100);   
  Serial.println("Die Led blinkt!");
  }  

}
