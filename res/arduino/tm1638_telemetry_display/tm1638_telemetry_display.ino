/*
TM1638 Sim Racing Telemetry Display Controller

Copyright (C) 2017 Cyril Bosselut <bossone0013 at gmail dot com>

This program is free software: you can redistribute it and/or modify
it under the terms of the version 3 GNU General Public License as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <TM1638.h>

// define a module on data pin 8, clock pin 9 and strobe pin 7
TM1638 module(7, 8, 9);
#define serialRate 115200

long readVcc() { 
  long result; // Read 1.1V reference against AVcc 
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1); 
  delay(2); // Wait for Vref to settle 
  ADCSRA |= _BV(ADSC); // Convert 
  while (bit_is_set(ADCSRA,ADSC)); 
  result = ADCL; 
  result |= ADCH<<8; 
  result = 1126400L / result; // Back-calculate AVcc in mV 
  return result; 
}

void setup() {
  delay(1500);
  Serial.begin(serialRate);
  module.setupDisplay(true, 2);
  module.clearDisplay();
  module.setDisplayToString("Lights");
  delay(1000);
  module.clearDisplay();
  module.setDisplayToString("ON");
  delay(1000);
  module.clearDisplay();
}

char header = 0;
char opt;
byte prev_keys = 0;

void loop() {
  if(prev_keys == 128) {
    module.setDisplayToDecNumber(readVcc(), 8, false);
    //delay(500);
  }
  else {
    if(Serial.available() >= 1) {
      header = Serial.read();
      if(header == 0) {
        opt = Serial.read();
        if(opt == '0') {
          int intensity = Serial.read() - '0';
          module.setupDisplay(true, intensity);
        }
        else if(opt == '1') {
          displayData();
        }
        else if(opt == '2') {
          printString();
        }
        else if(opt == '3') {
          displaySpeedGear();
        }
        else if(opt == '4') {
          displayLapInfo();
        }
      }
    }
  }

  byte keys = module.getButtons();
  
  if(keys > 0 && keys != prev_keys) {
    module.setLEDs(keys);
    Serial.write(keys + '0');
    delay(5);
    module.setLEDs(0);
    prev_keys = keys;
  }
  //delay(5);
}

void printString() {
  //module.clearDisplay();
  //char c = Serial.read();
  String msg = Serial.readString();
  /*String msg = "";
  while(c != '\n') {
    msg.concat(c);
    c = Serial.read();
  }*/
  msg.replace("\n", "");
  module.setDisplayToString(msg);
}
  
void displayLapInfo() {
  module.clearDisplay();
  int l1 = Serial.read() - '0';
  int l2 = Serial.read() - '0';
  int l = l1*10 + l2;
  int t1 = Serial.read() - '0';
  int t2 = Serial.read() - '0';
  int t = t1*10 + t2;
  String lap_info = "  ";
  if(l < 10) {
    lap_info.concat(" ");
  }
  lap_info.concat(String(l));
  lap_info.concat("  ");
  if(t < 10) {
    lap_info.concat(" ");
  }
  lap_info.concat(String(t));
  module.setDisplayToString(lap_info);
  setLeds();
}

void displaySpeedGear() {
  module.clearDisplay();
  char gear = Serial.read();
  for(int i = 0; i < 5; i++) {
    Serial.read();
  }
  int s1 = Serial.read() - '0';
  if(s1 < 0) {
    s1 = 0;
  }
  int s2 = Serial.read() - '0';
  if(s2 < 0) {
    s2 = 0;
  }
  int s3 = Serial.read() - '0';
  int spd = s1*100 + s2*10 + s3;
  String gs = " ";
  if(spd < 100) {
    gs.concat(" ");
  }
  if(spd < 10) {
    gs.concat(" ");
  }
  gs.concat(String(spd));
  gs.concat("   ");
  gs.concat(String(gear));
  module.setDisplayToString(gs);
  setLeds();
}

void setLeds() {
  int n = 0;
  int leds = 0;
  while(n < 8) {
    char led_state = Serial.read();
    if(led_state == 'G') {
      leds += round(pow(2, n));
    }
    n++;
  }
  module.setLEDs(leds);
}

void displayData() {
  module.clearDisplay();
  byte data[8];
  Serial.readBytesUntil('\n', data, 9);
  module.setDisplay(data, sizeof(data));
  //Serial.write(data, 8);
}

