// FUNÇÃO PARA ESPALHAR PARAFUSOS

# define AMPLITUDE_ONDA 300
# define COMPRIMENTO_PERCURSO_X 700
# define PASSO_X 5
# define PERIODO_ONDA 100

// Posição X e Y
// Velocidade do espalhamento
// Aceleração do espalhamento
void espalha_parafusos(int velo_esp, int acel_esp) {

  //Serial.println("Iniciando espalhamento de parafusos...");

  // Desativa o ima
  digitalWrite(RELE_IMA, HIGH);

  // Habilita os drivers dos motores
  digitalWrite(EN_PIN, LOW);

  motor_x.setMaxSpeed(velo_esp);
  motor_x.setAcceleration(acel_esp);
  motor_y.setMaxSpeed(velo_esp);
  motor_y.setAcceleration(acel_esp);

  int posX_inicial = 603;
  int posY_inicial = 769;

  motor_x.moveTo(posX_inicial);
  motor_y.moveTo(posY_inicial);

  while (motor_x.distanceToGo() != 0 || motor_y.distanceToGo() != 0) {
    motor_x.run();
    motor_y.run();
  }

  // Move o servo do imã para baixo
  for (int angulo = motor_ima.read(); angulo <= 180; angulo++) {
    motor_ima.write(angulo);
    delay(15);
  }

  // Percorre o eixo X em pequenos passos, calculando Y = amplitude * sen(x)
  for (long x = 0; x <= COMPRIMENTO_PERCURSO_X; x += PASSO_X) {

    // Permite interromper o movimento enviando STOP durante a execução
    if (Serial.available() > 0) {
      String comando_stop = Serial.readStringUntil('\n');
      comando_stop.trim(); // Limpa espaços invisíveis ou quebras de linha extras

      if (comando_stop.startsWith("STOP")) {
        motor_x.stop();
        motor_y.stop();
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
  } // for

  
  // Eletrimã retorna a posição inicial
  for (int angulo = 180; angulo >= SERVO_POS_INI; angulo--) {
    motor_ima.write(angulo);
    delay(15);
  }

  //Serial.println("Espalhamento de parafusos concluído!");

  // Mantém POS_X / POS_Y coerentes com o restante do código
  POS_X = motor_x.currentPosition();
  POS_Y = motor_y.currentPosition();
  Serial.println("ESPALHEI");

  homing();

} // espalha_parafusos




// FUNÇÃO DE REFERENCIAMENTO - HOMING

void homing () {
  // Habilita os drivers dos motores 
  digitalWrite(EN_PIN, LOW);

  for (int angulo = 180; angulo >= SERVO_POS_INI; angulo--) {
    motor_ima.write(angulo);
    delay(15);
  }

  // EIXO X
  //Serial.println("Voltando para o início do Eixo X");
  motor_x.setSpeed(velo_homing); 
  
  // Enquando não chegou na chave de fim de curso
  while (digitalRead(INICIO_CURSO_X) == LOW) {
    motor_x.runSpeed();
  }
  
  // Chegou na chave
  motor_x.stop();
  // Definie onde é a posição 0
  motor_x.setCurrentPosition(0);
  POS_X = 0;
  //Serial.println("Eixo X zerado!");

  // EIXO Y
  //Serial.println("Voltando para o início do Eixo Y");
  motor_y.setSpeed(velo_homing); 
  
  while (digitalRead(INICIO_CURSO_Y) == LOW) {
    motor_y.runSpeed();
  }
  
  motor_y.stop();
  motor_y.setCurrentPosition(0);
  POS_Y = 0;
  //Serial.println("Eixo Y zerado!");

  // Posição inicial do servo imã
  int angulo_atual = motor_ima.read();

  // Retorna o eletrima para posição inicial
  /*
  if (angulo_atual > 0){
    for (int angulo = angulo_atual; angulo >= angulo_atual; angulo--) {
      motor_ima.write(angulo);
      delay(15);
    }
  }
  */

  Serial.println("PAROU");
  // Desliga a alimentação dos motores
  digitalWrite(EN_PIN, HIGH);
} // homing



void fita_led() {
  pixels.clear(); // Limpa qualquer cor anterior

  // Define a cor de cada LED. O formato é (Número do LED, Vermelho, Verde, Azul)
  // 255, 255, 255 significa luz branca na potência máxima.
  for(int i=0; i<NUM_LEDS; i++) {
    pixels.setPixelColor(i, pixels.Color(255, 255, 255)); 
  }
  
  pixels.show(); // Envia os dados para os LEDs acenderem

  //Serial.println("Leds acesos!");

}
