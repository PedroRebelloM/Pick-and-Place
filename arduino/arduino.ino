#include <AccelStepper.h>
#include <string.h>
#include <Servo.h>
#include <Adafruit_NeoPixel.h>

/*** Definição dos pinos padrão da CNC Shield V3.0 ***/
// Pino que liga/desliga a energia de todos os drivers
#define EN_PIN 8 

#define MOTOR_X_STEP 2
#define MOTOR_X_DIR 5

#define MOTOR_Y_STEP 3
#define MOTOR_Y_DIR 6

//#define MOTOR_Z_STEP 4
//#define MOTOR_Z_DIR 7

#define INICIO_CURSO_X 9
#define INICIO_CURSO_Y 11

#define RELE_IMA 12
#define MOTOR_IMA 13

#define SERVO_POS_INI 0

//#define MOTOR_A_STEP 12
//#define MOTOR_A_DIR 13

// Pino da fita de LED
#define PIN_LED 7 
// Quantidade de LEDs na fita/anel
#define NUM_LEDS 60

Adafruit_NeoPixel pixels(NUM_LEDS, PIN_LED, NEO_GRB + NEO_KHZ800);

Servo motor_ima;

int POS_X = 0;
int POS_Y = 0;

int JANELA_X = 1150;
int JANELA_Y = 1200;

float velocidade = 150;
float aceleracao = 100;

bool em_movimento = false;

float velo_homing = -300;

unsigned long contagem_tempo = 0;

/*** Instanciação dos motores usando a biblioteca ***/
// Primeiro parâmetro indica que será utilizado um driver exclusivo, no caso, o ... 
AccelStepper motor_x(1, MOTOR_X_STEP, MOTOR_X_DIR);
AccelStepper motor_y(1, MOTOR_Y_STEP, MOTOR_Y_DIR);


void setup() {
  Serial.begin(9600);

  // Habilita os drivers dos motores
  // ATENÇÃO: Se definir no código, não colocar jumper na placa
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, HIGH);

  // HIGH -> Chave aberta
  // LOW -> Chave fechada
  // Conexão no projeto -> Normalmente fechada
  pinMode(INICIO_CURSO_X, INPUT_PULLUP);
  pinMode(INICIO_CURSO_Y, INPUT_PULLUP);

  pinMode(RELE_IMA, OUTPUT);
  digitalWrite(RELE_IMA, HIGH);
  motor_ima.attach(MOTOR_IMA);
  motor_ima.write(SERVO_POS_INI);

  // Velocidade máxima no eixo x
  motor_x.setMaxSpeed(velocidade);
  // Aceleração no eixo x
  motor_x.setAcceleration(aceleracao);

  // Velocidade máxima no eixo y
  motor_y.setMaxSpeed(velocidade);
  // Aceleração no eixo y
  motor_y.setAcceleration(aceleracao);

  fita_led();

  homing ();

} // setup


void loop() {

  if (Serial.available() > 0) {
    // texto.trim(); // remove quebra de linha

    String comando = Serial.readStringUntil('\n');

    // MOVE X100 Y200
    // STOP
    // HOME
    // IMA DESCE
    // IMA SOBE
    // IMA LIGA
    // IMA DESLIGA
    // ESPALHA

    if (comando.startsWith("STOP") ) {
      motor_x.stop();
      motor_y.stop();
      digitalWrite(EN_PIN, HIGH);
    }
    else
    if(comando.startsWith("ESPALHA") ) {
      espalha_parafusos(velocidade, aceleracao);
    }
    if (comando.startsWith("MOVE")) {
      digitalWrite(EN_PIN, LOW);
      //Serial.print("Motores ligados");
      
      // Leitura da posição X e Y
      int index_X = comando.indexOf("X");
      int index_Y = comando.indexOf("Y");

      if (index_X != -1){
        POS_X = (comando.substring(index_X+1)).toInt();
      }
      if (index_Y != -1){
        POS_Y = (comando.substring(index_Y+1)).toInt();
      }

          // Define uma posição especifica de descolamento
      motor_x.moveTo(POS_X);
      motor_y.moveTo(POS_Y);

      // Avisa o sistema que um movimento acabou de começar
      em_movimento = true;
    } // MOVE
    else
    if (comando.startsWith("HOME")){
      homing ();
    }
    else
    if (comando.startsWith("IMA")){
      if (comando.substring(4) == "DESCE"){
        for (int angulo = 0; angulo <= 180; angulo++) {
          motor_ima.write(angulo);
          delay(15);
        }
        Serial.println("DESCI");
      } 
      else
      if (comando.substring(4) == "SOBE"){
        for (int angulo = 180; angulo >= 0; angulo--) {
          motor_ima.write(angulo);
          delay(15);
        }
        Serial.println("SUBI");
      }
      else
      if (comando.substring(4) == "LIGA"){
        digitalWrite(RELE_IMA, LOW);
        Serial.println("LIGUEI");
      }
      else
      if (comando.substring(4) == "DESLIGA"){
        digitalWrite(RELE_IMA, HIGH);
        Serial.println("DESLIGUEI");
      }
    }
    else{
      Serial.println("Comando inválido!");  
    }

    //Serial.print("Posições X e Y: ");
    //Serial.print(POS_X);
    //Serial.print(" ");
    //Serial.println(POS_Y);
  
  } // leitura serial

  // Verifica se o motor x e o motor y chegarram a posição definada anteriormente
  // Se verdadeiro, desliga a alimentação do motores
  if (em_movimento && motor_x.distanceToGo() == 0 && motor_y.distanceToGo() == 0){
    digitalWrite(EN_PIN, HIGH);

    Serial.println("CHEGUEI");
    em_movimento = false;
  } 

  motor_x.run();
  motor_y.run();

  // Impressão de teste
  if (millis() > contagem_tempo + 1000) {
    // Retorna a velocidade do motor em dado instante
    //float vel_x = motor_x.speed();
    //Serial.print("Velocidade x: ");
    //Serial.println(vel_x);
    
    //float vel_y = motor_y.speed();
    //Serial.print("Velocidade y: ");
    //Serial.println(vel_y);

    contagem_tempo = millis();
  } // millis

} // loop
