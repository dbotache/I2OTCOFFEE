/**
 * Before Flashing Put GPIO0 to Low (Flashing mode) - >>>> Jumper below the ESP8266 Board
 * Disconnect Serial wires from Level converter (Answer from Coffemaker generates error on flashing) Jumpers down the arduino board
 * Disconnect Arduino Board 
 * Now Connect USB Port to computer
 * Press reset button before firmware upload
 * 
 * When Firmware uploaded, release push button and switch GPIO to HIGH (Normal operation mode)
 * 
 * Zum auslesen von Nachrichten Arduino Nano Anschliessen. (siehe "Receiving with Arduino" Folder)
 * 
 * TODO: Internal Power supply without coffemaker. >>>>>> (New Board design)
 */

#include "Arduino.h"
#include "ESP8266WiFi.h"

void TranslateToJura(String c);
void toCoffeemaker(String outputString);

const char* ssid = "Diego-wlan";
const char* password = "11a22b33c44d";

WiFiServer wifiServer(8585);

byte z[4];
String msg;
byte d0; byte d1; byte d2; byte d3;

void setup()
{
  // initialize LED digital pin as an output.
  Serial.begin(9600);

  WiFi.begin(ssid, password);

  pinMode(LED_BUILTIN, OUTPUT);
  delay(1000);

  while (WiFi.status() != WL_CONNECTED) 
  {
    //Connecting...
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
  }

  //Connected to WiFi.
  wifiServer.begin();
  // Serial.print(WiFi.localIP());
}

void loop()
{

  while (WiFi.status() == WL_CONNECTED)
  {
    digitalWrite(LED_BUILTIN, LOW);
  
    WiFiClient client = wifiServer.available();

    if (client) {
      while (client.connected()) {
        while(client.available()){
          msg = client.readStringUntil('\r');
          TranslateToJura(msg);
          // if(Serial.available())
          // {       
          //   delay (1); byte d0 = Serial.read();
          //   delay (1); byte d1 = Serial.read();
          //   delay (1); byte d2 = Serial.read();
          //   delay (1); byte d3 = Serial.read();
          //   delay (1);

          //   client.print("\n");
          //   client.print(d0, DEC); client.print(" ");
          //   client.print(d1, DEC); client.print(" ");
          //   client.print(d2, DEC); client.print(" ");
          //   client.print(d3, DEC); client.print(" ");
          //   client.print("\n");

          //   delay(100);
          //   digitalWrite(LED_BUILTIN, HIGH);
          //   delay(100);
          //   digitalWrite(LED_BUILTIN, LOW);

          // }
          delay(100);
          digitalWrite(LED_BUILTIN, HIGH);
          delay(100);
          digitalWrite(LED_BUILTIN, LOW);
        }
      }
      client.stop();
    }
  }

  if (WiFi.status() == WL_DISCONNECTED)
  {
    for(int i=0; i<4; i++)
    {
      delay(100);
      digitalWrite(LED_BUILTIN, HIGH);
      delay(100);
      digitalWrite(LED_BUILTIN, LOW);
    } 
  }

    if (WiFi.status() == WL_NO_SSID_AVAIL)
  {
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
  }

}

// TODO: Weitere If-cases für verschiedene Getränke:
void TranslateToJura(String c){
  if (c == "KAFFEE_1"){
    // Nachricht an Coffeemaker:
    toCoffeemaker("FA:04\r\n"); delay(7);
  } 
  if (c == "KAFFEE_2"){
    // Nachricht an Coffeemaker:
    toCoffeemaker("FA:04\r\n"); delay(100);
    toCoffeemaker("FA:04\r\n"); delay(7);
  } 
}

void toCoffeemaker(String outputString)
{
  for (byte a = 0; a < outputString.length(); a++) {
    z[0] = 255;
    z[1] = 255;
    z[2] = 255;
    z[3] = 255;

    int var = 0;
    for (int i=0;i<4;i++){
      bitWrite(z[i], 2, bitRead(outputString.charAt(a),var));
      bitWrite(z[i], 5, bitRead(outputString.charAt(a),var+1));
      var += 2;
    }

    for (int i = 0; i < 4; i++){
      delay (1); 
      Serial.write(z[i]); 
    }
    delay(7); 
  }
}

// TODO: Lese Funktion für die Antwort der Kaffeemaschine!

// void loop() {
//   byte d0; byte d1; byte d2; byte d3;
//   if(mySerial.available())
//   {       
//     delay (1); byte d0 = mySerial.read();
//     delay (1); byte d1 = mySerial.read();
//     delay (1); byte d2 = mySerial.read();
//     delay (1); byte d3 = mySerial.read();
//     delay (1);

//     Serial.print(d0, BIN); Serial.print(" ");
//     Serial.print(d1, BIN); Serial.print(" ");
//     Serial.print(d2, BIN); Serial.print(" ");
//     Serial.print(d3, BIN); Serial.print("\t");

//     Serial.print(d0, HEX); Serial.print(" ");
//     Serial.print(d1, HEX); Serial.print(" ");
//     Serial.print(d2, HEX); Serial.print(" ");
//     Serial.print(d3, HEX); Serial.print("\t");

//     Serial.print(d0, DEC); Serial.print(" ");
//     Serial.print(d1, DEC); Serial.print(" ");
//     Serial.print(d2, DEC); Serial.print(" ");
//     Serial.print(d3, DEC); Serial.print("\t");
//     Serial.print("\n");
//   }
// }
