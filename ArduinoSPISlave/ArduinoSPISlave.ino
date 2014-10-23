/*

Arduino SPI Slave for Playstation 2

Based on busslave's work form 2012
 
Arduino pin |  AVR pin | PSX pin

9 PB1       |    15    | 9 ACK     (green)
10 -SS      |    16    | 6 ATT     (yellow)
11 MOSI     |    17    | 2 COMMAND (orange)
12 MISO     |    18    | 1 DATA    (brown)
13 SCK      |    19    | 7 CLOCK   (blue)
                       | 4 GND

*/

#include "Arduino.h"
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#define F_CPU 16000000
#define ARDUINO 101

#define SPI_PORT PORTB
#define SPI_PINS PINB
#define SPI_DDR  DDRB
#define SPI_PINS  PINB

#define ACK_PIN   1 //PB1
#define ATT_PIN   2 //~SS
#define CMD_PIN   3 //MOSI
#define DATA_PIN  4 //MISO
#define CLK_PIN   5 //SCK

#define DATA_LEN 5

#define LED_PIN 7

#define _DEBUG 0

char control_data[2] = {0xFF,0xFF};

volatile uint8_t data_buff[DATA_LEN]={0x41,0x5A,0xFF,0xFF,0xFF}; // Reply: nothing pressed.
volatile uint8_t command_buff[DATA_LEN]={0x01,0x42,0x00,0x00,0x00};
    
volatile uint8_t curr_byte=0;
volatile uint8_t next_byte=0;

void setup();
void loop();

void setup() {
  
  // Begin Serial communication with Pi
  Serial.begin(115200);
    
  //SPI_PORT setup. 
  SPI_DDR |= (1<<ACK_PIN); // output
  SPI_PORT |= (1<<ACK_PIN); // set HIGH
  SPI_DDR |= (1<<DATA_PIN); // output
  SPI_PORT |= (1<<DATA_PIN); // set HIGH  
  
  //SPI setup.
  PRR &= ~(1<<PRSPI);  // Set to 0 to ensure power to SPI module.
  SPSR|=(1<<SPI2X);    // Fosc/32. @16MHz==500KHz.
  //SPCR|=(1<<SPR1);   // Fosc/64. @16MHz==250KHz.
  SPCR|=(1<<CPHA);     // Setup @ leading edge, sample @ falling edge.
  SPCR|=(1<<CPOL);     // Leading edge is falling edge, trailing edge is rising edge.
  SPCR &= ~(1<<MSTR);  // MSTR bit is zero, SPI is slave.
  SPCR|=(1<<DORD);     // Byte is transmitted LSB first, MSB last.
  SPCR|=(1<<SPE);      // Enable SPI.
  SPCR|=(1<<SPIE);     // Enable Serial Transfer Complete (STC) interrupt.
  SPDR=0xFF;
  
  sei(); // Enable global interrupts.

  // Indicate Reset
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(70);
  digitalWrite(LED_PIN, HIGH);
  delay(70);
  digitalWrite(LED_PIN, LOW);
  delay(70);
  digitalWrite(LED_PIN, HIGH);
  delay(70);
  digitalWrite(LED_PIN, LOW);
  delay(70);
  digitalWrite(LED_PIN, HIGH);
  delay(70);
  digitalWrite(LED_PIN, LOW);

  if (_DEBUG) {
    Serial.println("");
    Serial.println("-----------------------------------");
    Serial.println("Playstation 2 Protocol initialized.");
    Serial.println("-----------------------------------");
  }

}

/* SPI interrupt */
ISR(SPI_STC_vect) { 

  // Byte received from the master
  uint8_t inbyte = SPDR;
  
  // FIX ME : Manage other cases ? (other commands from the master?)
  if (inbyte == command_buff[curr_byte]) {

    // We put the next byte in the buffer, to be send along the next clock cycle
    SPDR = data_buff[curr_byte];
    curr_byte++;
    
    // We need to ACK (PS2 Protocol)
    if (curr_byte < DATA_LEN) { // ACK goes low.
      SPI_PORT &= ~(1<<PORTB1);
      _delay_us(10); // For 10µseconds
      SPI_PORT |= (1<<PORTB1);
    } else { // Except for the last packet
      SPDR = 0xFF;
      curr_byte = 0;
    }

  } else {
    
    SPDR = 0xFF;
    curr_byte = 0;
  
  }
  
}

void loop() {

  /* Reads input from Serial connection */
  /*
    We're going to read 2 characters = 2 x 1 byte
    It's going to be read as a char but then translated
    to HEX, taking only the lower byte
  */

  if (Serial.available() >= 2) {
    
    Serial.readBytes(control_data, 2); // Read 16 bits

    // DEBUG 
    if (_DEBUG) {
      Serial.print("Command : 0x");
      Serial.print(lowByte(control_data[0]), HEX);
      Serial.print(" 0x");
      Serial.print(lowByte(control_data[1]), HEX);
      Serial.println("");
    }
    
    // We store the new commands in the data_buff buffer
    data_buff[2] = lowByte(control_data[0]);
    data_buff[3] = lowByte(control_data[1]);

    // Led
    if (lowByte(control_data[0]) != 255 || lowByte(control_data[1]) != 255){
      digitalWrite(LED_PIN, HIGH);
    } else {
      digitalWrite(LED_PIN, LOW);
    }
    
  }

}
