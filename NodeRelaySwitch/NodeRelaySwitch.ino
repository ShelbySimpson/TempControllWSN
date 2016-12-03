

void setup(){
	Serial.begin(9600);
}

void loop(){
    char cmd = 'z';
    pinMode(13,OUTPUT);
    digitalWrite(13,HIGH)
  //Get byte off of serial buffer
  cmd = Serial.read();

  if (cmd == 'O') {
      digitalWrite(13,LOW);
  }else if(cmd == 'F'){
     digitalWrite(13,HIGH) 
  }
}
