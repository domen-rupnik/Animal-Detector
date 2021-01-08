const int PIR1 = 9;
const int PIR2 = 10;
const int KAMERA_PIN = 4;
const int SNEMAJ_PIN = 2;
#define DELAY_UGAS 4000
const int DELAY_PREKLOP = 1300;
int gibanje = millis();
bool kamera = true;
bool snemaj = false;
int now = millis();

void setup() {
  Serial.begin(9600);
  delay(15000);
  pinMode(13, OUTPUT);
  pinMode(PIR1, INPUT_PULLUP);
  pinMode(PIR2, INPUT_PULLUP);
  pinMode(KAMERA_PIN, OUTPUT);
  pinMode(SNEMAJ_PIN, OUTPUT);
  digitalWrite(KAMERA_PIN, HIGH);
  digitalWrite(SNEMAJ_PIN, HIGH);
  on(KAMERA_PIN);
  kamera = false;
  delay(2000);
}
void loop() {
  bool sensorVal = digitalRead(PIR1);
  bool sensorVal2 = digitalRead(PIR2);

  if (sensorVal == 0 || sensorVal2 == 0) {
    gibanje = millis();
    snemaj = true;
  }
  if(snemaj == true && kamera == false){
    //Kamera
    on(KAMERA_PIN);
    
    on(SNEMAJ_PIN);
    kamera = true;
  }
  now = millis();
  if(snemaj == true && (now - gibanje) > 30000){
    //Konec snemanja
    on(SNEMAJ_PIN);
    //Off fotoaparat
    on(KAMERA_PIN);
    snemaj = false;
    kamera = false;
    delay(DELAY_UGAS);
  }
}
void on(int pinn){
  digitalWrite(pinn, LOW);
  delay(DELAY_PREKLOP);
  digitalWrite(pinn, HIGH);
}
