// SPDX-License-Identifier: Apache-2.0
// Copyright 2019-2026 Diego Botache
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// See README.md for hardware setup and flashing instructions.

#include "Arduino.h"
#include "ESP8266WiFi.h"
#include "config.h"

void TranslateToJura(String c);
void toCoffeemaker(String outputString);

WiFiServer wifiServer(COFFEE_TCP_PORT);

void setup()
{
  // initialize LED digital pin as an output.
  Serial.begin(9600);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

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
}

void loop()
{

  while (WiFi.status() == WL_CONNECTED)
  {
    digitalWrite(LED_BUILTIN, LOW);

    WiFiClient client = wifiServer.accept();

    if (client) {
      while (client.connected()) {
        while(client.available()){
          String msg = client.readStringUntil('\r');
          msg.trim();
          TranslateToJura(msg);
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

void TranslateToJura(String c){
  if (c == "KAFFEE_1" || c == "Coffee"){
    toCoffeemaker("FA:04\r\n"); delay(7);
  }
  if (c == "Espresso"){
    toCoffeemaker("FA:03\r\n"); delay(7);
  }
  if (c == "KAFFEE_2"){
    toCoffeemaker("FA:04\r\n"); delay(100);
    toCoffeemaker("FA:04\r\n"); delay(7);
  }
}

void toCoffeemaker(String outputString)
{
  for (byte a = 0; a < outputString.length(); a++) {
    byte z[4] = {255, 255, 255, 255};

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
