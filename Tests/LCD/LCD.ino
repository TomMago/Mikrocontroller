#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

//Initialisierung des Displays
LiquidCrystal_I2C lcd(0x20,16,2);
int i=0;

void setup()
{
  lcd.init();                      
  lcd.backlight();
  lcd.print("Hello, world!");
  delay(1000);
}

void loop()
{
  
  lcd.clear();
  lcd.setCursor(0,(i%2));  //Wechselt Zeilen nach jedem Durchgang
  lcd.print("Arduino");
  
  delay(200);
  i++;
}
