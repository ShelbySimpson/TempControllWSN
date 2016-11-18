#include <QueueArray.h>//data structure to hanlde data packets
#include <Streaming.h>//Makes output formatting easy
#include <MsTimer2.h>//handles interrupts
#include "Thermometer.h"//convert temp data readings 

//vars====================================================
//id for node
#define ID 1
//num of nodes in network
#define num_nodes 1

#define light_pin A0
#define therm_pin A1
#define led_pin 13

//This array will hold all packets
//For each packet there will be three elements: [id, time, value]
QueueArray <unsigned short> queue;
Thermometer therm = Thermometer();
boolean output = HIGH; //Track if LED should be on or off
unsigned short tm; //Timer
//=========================================================

//Helper functions ========================================
void sample();
void transmit();
void stop_sampling();
//=========================================================

//run program ===============================================
void setup() {
  Serial.begin(9600);//baud
  pinMode(led_pin, OUTPUT); //sync led
  pinMode(A1, INPUT); //temp sensor
  tm = 0;//init time
  // set the printer of the queue.
  queue.setPrinter(Serial);
}

void loop() {
  //init char with a dummy value
  char cmd = '0';
  //Get byte off of serial buffer
  cmd = Serial.read();

  //If R then begin sampling
  //If S then re-sync
  //If T then terminate sampling
  if (cmd == 'R') {
    //start sampling
    MsTimer2::set(1800000, sample); //Sample rate
    MsTimer2::start();
  }else if (cmd == 'T') {
    //Stop sampling
    MsTimer2::stop();
    stop_sampling();
  }else if(cmd == 'X'){
    //used for demo only.
    //start sampling
    MsTimer2::set(1000, sample); //Sample rate
    MsTimer2::start();
  }
}
//===================================================================

//Helper Functions===================================================
//samples and toggles led in unison.
void sample() {
  //Toggle light D13 LED--------------------
  digitalWrite(led_pin, output);
  output = !output;
  //----------------------------------------
  //create data packet
  queue.push(tm);
  queue.push(analogRead(light_pin));  
  queue.push(therm.getFahrenheit());


  //We add 1 to the number of nodes so that we don't get a 0 value on the mod
  //operation for the last node in the set of nodes
  if (tm % num_nodes + 1 == ID) { //node's turn to transmit
    transmit();
  }

  tm++;//increment the time counter
}

void stop_sampling() {

  //Allow the node to transmit info
  delay((ID - 1) * 1000);
  transmit();

  digitalWrite(led_pin, LOW); //ensure that light is of when iterrupt is stopped
  tm = 0; //Reset the timer
}

//Transmit all packets in the buffer and empty it as you go
void transmit(){
    unsigned short count = 0; //Used to track if an entire packet has Tx


  while (!queue.isEmpty()) {
    //This will remove the front element in the buffer and pass it to the Serial port
    Serial << queue.dequeue();

    //Inc counter
    count++;
    //If count is 3 then an entire packet has been sent
    //Reset count, send a new line, and continue
    //Else add a comma
    if (count == 3) {
      count = 0;
      Serial << endl;
    }else {
      Serial << ",";
    }
  }

}
//=============================================================================
