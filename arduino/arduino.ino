#include <AccelStepper.h>
#include <string.h>
#include <Servo.h>

/*** Definição dos pinos padrão da CNC Shield V3.0 ***/
// Pino que liga/desliga a energia de todos os drivers
#define EN_PIN 8 

#define MOTOR_X_STEP 2
#define MOTOR_X_DIR 5

#define MOTOR_Y_STEP 3
#define MOTOR_Y_DIR 6

#define MOTOR_Z_STEP 4
#define MOTOR_Z_DIR 7

#define INICIO_CURSO_X 9
#define INICIO_CURSO_Y 10

#define RELE_IMA 12
#define MOTOR_IMA 13

#define SERVO_POS_INI 0

//#define MOTOR_A_STEP 12
//#define MOTOR_A_DIR 13

// Parâmetros do movimento ondulatório - ajuste conforme a bancada/curso da CNC
#define AMPLITUDE_ONDA 50           // amplitude do "vai e vem" no eixo Y (em passos)
#define COMPRIMENTO_PERCURSO_X 800  // distância total a percorrer no eixo X (em passos)
#define PASSO_X 20                  // incremento de X entre cada ponto calculado da onda
#define PERIODO_ONDA 200            // "período" da senoide em passos de X (controla a frequência das ondulações)

Servo motor_ima;

int POS_X = 0;
int POS_Y = 0;

float velocidade = 150;
float aceleracao = 100;

float velo_home = -200;

unsigned long contagem_tempo = 0;

/*** Instanciação dos motores usando a biblioteca ***/
// Primeiro parâmetro indica que será utilizado um driver exclusivo, no caso, o ... 
AccelStepper motor_x(1, MOTOR_X_STEP, MOTOR_X_DIR);
AccelStepper motor_y(1, MOTOR_Y_STEP, MOTOR_Y_DIR);
AccelStepper motor_z(1, MOTOR_Z_STEP, MOTOR_Z_DIR);
//AccelStepper motor_a(1, MOTOR_A_STEP, MOTOR_A_DIR);


void setup() {
  Serial.begin(9600);

  // Habilita os drivers dos motores
  // ATENÇÃO: Se definir no código, não colocar jumper na placa
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, HIGH);

  // HIGH -> Chave aberta
  // LOW -> Chave fechada
  // Conexão do projeto -> Normalmente fechada
  pinMode(INICIO_CURSO_X, LOW);
  pinMode(INICIO_CURSO_Y, LOW);

  pinMode(RELE_IMA, OUTPUT);
  digitalWrite(RELE_IMA, LOW);
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

  // Velocidade máxima no eixo z
  motor_z.setMaxSpeed(velocidade);      
  // Aceleração no eixo z
  motor_z.setAcceleration(aceleracao);

  // Velocidade máxima no eixo a
  //motor_a.setMaxSpeed(velocidade);
  // Aceleração no eixo a      
  //motor_a.setAcceleration(aceleracao);

  retorno_inicio ();

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

    if (comando.startsWith("STOP") ) {
      digitalWrite(EN_PIN, HIGH);
    }
    else
    if (comando.startsWith("MOVE")) {
      digitalWrite(EN_PIN, LOW);
      Serial.print("Motores ligados");
   
      //int espaco;
      //espaco = texto.lastIndexOf(" "); 
      
      // Leitura da posição X e Y
      int index_X = comando.indexOf("X");
      int index_Y = comando.indexOf("Y");

      if (index_X != -1){
        POS_X = (comando.substring(index_X+1)).toInt();
      }
      if (index_Y != -1){
        POS_Y = (comando.substring(index_Y+1)).toInt();
      }
    } // MOVE
    else
    if (comando.startsWith("HOME")){
      retorno_inicio ();
    }
    else
    if (comando.startsWith("IMA")){
      if (comando.substring(4) == "DESCE"){
        for (int angulo = 0; angulo <= 180; angulo++) {
          motor_ima.write(angulo);
          delay(15);
        }
        //motor_ima.write(180);
      } 
      else
      if (comando.substring(4) == "SOBE"){
        for (int angulo = 180; angulo >= 180; angulo--) {
          motor_ima.write(angulo);
          delay(15);
        }
        //motor_ima.write(SERVO_POS_INI);
      }
      else
      if (comando.substring(4) == "LIGA"){
        digitalWrite(RELE_IMA, HIGH);
      }
      else
      if (comando.substring(4) == "DESLIGA"){
        digitalWrite(RELE_IMA, LOW); 
      }
      else
      if (comando.startsWith("ESPALHA")){
        espalha_parafusos();
      }
    }
    else{
      Serial.print("Comando inválido!");  
    }

    Serial.print("Posições X e Y: ");
    Serial.print(POS_X);
    Serial.print(" ");
    Serial.println(POS_Y);

    // define uma posição especifica
    motor_x.move(POS_X);
    motor_y.move(POS_Y);
  }

  //Serial.println("Movendo motor X");
  motor_x.run();

  //Serial.println("Movendo motor Y");
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


// FUNÇÃO DE INÍCIO DE PERCURSO

void retorno_inicio () {
  digitalWrite(EN_PIN, LOW);

  // EIXO X
  Serial.println("Voltando para o início do Eixo X");
  motor_x.setSpeed(velo_home); 
  
  // Enquando não chegou na chave
  while (digitalRead(INICIO_CURSO_X) == LOW) {
    motor_x.runSpeed();
  }
  
  // Chegou na chave
  motor_x.stop();
  // Definie onde é a posição 0
  motor_x.setCurrentPosition(0); 
  Serial.println("Eixo X zerado!");

  // EIXO Y
  Serial.println("Voltando para o início do Eixo Y");
  motor_y.setSpeed(velo_home); 
  
  while (digitalRead(INICIO_CURSO_Y) == LOW) {
    motor_y.runSpeed();
  }
  
  motor_y.stop();
  motor_y.setCurrentPosition(0);
  Serial.println("Eixo Y zerado!");

  // Posição inicial do servo imã
  int angulo_atual = motor_ima.read();

  if (angulo_atual > 0){
    for (int angulo = angulo_atual; angulo >= angulo_atual; angulo--) {
      motor_ima.write(angulo);
      delay(15);
    }
  }

  digitalWrite(EN_PIN, HIGH);
} // retorno_inicio


void espalha_parafusos() {
  Serial.println("Iniciando espalhamento de parafusos...");

  // Garante que o imã esteja DESATIVADO, para não prender os parafusos durante o movimento
  digitalWrite(RELE_IMA, LOW);

  // Move o servo do imã para baixo (mesmo padrão usado em IMA DESCE)
  for (int angulo = motor_ima.read(); angulo <= 180; angulo++) {
    motor_ima.write(angulo);
    delay(15);
  }

  // Habilita os drivers dos motores
  digitalWrite(EN_PIN, LOW);

  motor_x.setMaxSpeed(velocidade);
  motor_x.setAcceleration(aceleracao);
  motor_y.setMaxSpeed(velocidade);
  motor_y.setAcceleration(aceleracao);

  long posX_inicial = motor_x.currentPosition();
  long posY_inicial = motor_y.currentPosition();

  // Percorre o eixo X em pequenos passos, calculando Y = amplitude * sen(x)
  for (long x = 0; x <= COMPRIMENTO_PERCURSO_X; x += PASSO_X) {

    // Permite interromper o movimento enviando STOP durante a execução
    if (Serial.available() > 0) {
      String comando_stop = Serial.readStringUntil('\n');
      if (comando_stop.startsWith("STOP")) {
        Serial.println("Espalhamento interrompido!");
        digitalWrite(EN_PIN, HIGH);
        return;
      }
    }

    float angulo_rad = (2.0 * PI * x) / PERIODO_ONDA;
    long y = (long)(AMPLITUDE_ONDA * sin(angulo_rad));

    motor_x.moveTo(posX_inicial + x);
    motor_y.moveTo(posY_inicial + y);

    // Roda os dois motores até alcançarem o ponto calculado
    while (motor_x.distanceToGo() != 0 || motor_y.distanceToGo() != 0) {
      motor_x.run();
      motor_y.run();
    }
  }

  Serial.println("Espalhamento de parafusos concluído!");

  // Mantém POS_X / POS_Y coerentes com o restante do código
  POS_X = motor_x.currentPosition();
  POS_Y = motor_y.currentPosition();

} // espalha_parafusos
