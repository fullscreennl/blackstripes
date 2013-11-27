#define encoder0PinA 2
#define encoder0PinB 3

#define L_MOTOR_PULSE 5
#define L_MOTOR_DIR 4

#define R_MOTOR_PULSE 6
#define R_MOTOR_DIR 7

#define LED_PIN 13

volatile int DIR = LOW;
int ENA= HIGH;
int LARGESTEPS = LOW;
int LEFTENGINE= LOW;
int lastBstate = LOW;
unsigned long currentTime;
unsigned long loopTime;

void setup() {

  pinMode(encoder0PinA, INPUT); 
  pinMode(encoder0PinB, INPUT); 

  digitalWrite(encoder0PinA, HIGH);       // turn on pullup resistor
  digitalWrite(encoder0PinB, HIGH);       // turn on pullup resistor
  pinMode(L_MOTOR_PULSE, OUTPUT);
  pinMode(L_MOTOR_DIR, OUTPUT);
  pinMode(R_MOTOR_PULSE, OUTPUT);
  pinMode(R_MOTOR_DIR, OUTPUT);
  pinMode(LED_PIN,OUTPUT);                  // built-in led pin
  digitalWrite(LED_PIN,LOW);
  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoderA, FALLING);
  //
  //Serial.begin (9600);
  currentTime = millis();
  loopTime = currentTime; 
}

void loop(){ //Do stuff here
  currentTime = millis();
  if(currentTime >= (loopTime + 20)){  //50 Hz sample freq for switches
    int switchState1 = analogRead(A0);
    if(switchState1 > 500){
      LARGESTEPS = HIGH;
    }else{
      LARGESTEPS = LOW;
    }
    int switchState2 = analogRead(A1);
    if(switchState2 > 500){
      LEFTENGINE = HIGH;
     // Serial.println ("left engine"); 
    }else{
      LEFTENGINE = LOW;
     // Serial.println ("rightt engine"); 
    }
  } 
}

void setEngineDirs(){
  if(LEFTENGINE){
      digitalWrite(L_MOTOR_DIR,DIR);
   }else{
      digitalWrite(R_MOTOR_DIR,DIR);
   }
}

void doStep(){
  setEngineDirs();
  int i=0;
  int count =1;
  if(LARGESTEPS){
    count = 1000;
  }
  for(i=0;i<count;i++){
    if(LEFTENGINE){
      digitalWrite(L_MOTOR_PULSE,HIGH);
      digitalWrite(L_MOTOR_PULSE,LOW);
    }
    else{
      digitalWrite(R_MOTOR_PULSE,HIGH);
      digitalWrite(R_MOTOR_PULSE,LOW);
    }
    delay(1); 
    ENA=LOW; 
  }
  ENA=HIGH;
}

void doEncoderA(){
  if(!ENA){
    return;
  }
  // high to low edge on channel A
  // check channel B to see which way encoder is turning
  int bState = digitalRead(encoder0PinB);
  if (bState == LOW && lastBstate == LOW) {  
    // CW
    DIR= HIGH;
    digitalWrite(LED_PIN,HIGH);
  }else if (bState == HIGH && lastBstate == HIGH) {
    // CCW
    DIR= LOW;
    digitalWrite(LED_PIN,LOW);
  }
 
  if(bState == lastBstate){
    doStep();
  }
  lastBstate = bState;
}
