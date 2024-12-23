#include <Keypad.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <Preferences.h>
#include <HTTPClient.h>

void fetchData();
int postData(String data);
void setupWIFIConnection();
void check_humidity();
Preferences preferences;

#define ROW_NUM     4 // three rows
#define COLUMN_NUM  3 // three columns

char keys[ROW_NUM][COLUMN_NUM] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};

byte pin_rows[ROW_NUM]      = {12, 14, 27, 26}; // GPIO19, GPIO18, GPIO5, GPIO17 connect to the row pins
byte pin_column[COLUMN_NUM] = {25, 33, 32};   // GPIO16, GPIO4, GPIO0, GPIO2 connect to the column pins

Keypad keypad = Keypad(makeKeymap(keys), pin_rows, pin_column, ROW_NUM, COLUMN_NUM );
LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address 0x27, 16 column and 2 rows

int cursorColumn = 0;
String inputString = ""; // To hold the input string

void setup(){
  lcd.init(); // initialize the lcd
  lcd.backlight();
  Serial.begin(115200);
  randomSeed(analogRead(A0));
  setupWIFIConnection();

  preferences.begin("settings", false);
}

void loop() {
  // Check humidity every 10 seconds (10000 ms)
  static unsigned long lastHumidityCheck = 0;
  if (millis() - lastHumidityCheck >= 10000) {
    check_humidity();
    lastHumidityCheck = millis();  // Update the last humidity check time
  }

  // Handle keypad input
  char key = keypad.getKey();
  if (key) {
    if (key == '*') { // If '*' key is pressed, erase the input
      lcd.clear();
      int result = postData(inputString); // Call the function and store the result
      if (result == 1) {
        lcd.print("Lock opened!");
      } else if (result == 0) {
        lcd.print("Incorrect key.");
      } else {
        lcd.print("Unexpected response");
      }

      delay(2000); // Wait before the next operation
      inputString = ""; // Clear the input string
      cursorColumn = 0;
      lcd.setCursor(cursorColumn, 0);
      lcd.clear();
    } else if (key == '#') { // If '#' key is pressed, erase last digit
      if (inputString.length() > 0) {
        inputString.remove(inputString.length() - 1); // Remove last character from inputString
        cursorColumn--; // Move cursor back one position
        lcd.setCursor(cursorColumn, 0); // Update cursor position
        lcd.print(" "); // Print a blank space to erase the last character on the screen
        lcd.setCursor(cursorColumn, 0); // Reset cursor after clearing
      }
    }else {
      lcd.setCursor(cursorColumn, 0); // Move cursor to (cursorColumn, 0)
      lcd.print(key);                 // Print key at (cursorColumn, 0)
      inputString += key;             // Append the key to inputString
      cursorColumn++;                 // Move cursor to next position
      if (cursorColumn == 16) {        // If reaching limit, clear LCD
        lcd.clear();
        cursorColumn = 0;
      }
    }
  }

}
