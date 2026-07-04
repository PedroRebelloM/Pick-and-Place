// FUNÇÃO DE REFERENCIAMENTO - HOMING

void homing () {
  digitalWrite(EN_PIN, LOW);

  // EIXO X
  Serial.println("Voltando para o início do Eixo X");
  motor_x.setSpeed(velo_homing); 
  
  // Enquando não chegou na chave de fim de curso
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
  motor_y.setSpeed(velo_homing); 
  
  while (digitalRead(INICIO_CURSO_Y) == LOW) {
    motor_y.runSpeed();
  }
  
  motor_y.stop();
  motor_y.setCurrentPosition(0);
  Serial.println("Eixo Y zerado!");

  // Posição inicial do servo imã
  int angulo_atual = motor_ima.read();

  // Retorna o eletrima para posição inicial
  if (angulo_atual > 0){
    for (int angulo = angulo_atual; angulo >= angulo_atual; angulo--) {
      motor_ima.write(angulo);
      delay(15);
    }
  }

  // Desliga a alimentação dos motores
  digitalWrite(EN_PIN, HIGH);
} // homing



// FUNÇÃO PARA ESPALHAR PARAFUSOS

# define AMPLITUDE_ONDA 50
# define COMPRIMENTO_PERCURSO_X 800 
# define PASSO_X 20
# define PERIODO_ONDA 200


void espalha_parafusos() {
  Serial.println("Iniciando espalhamento de parafusos...");

  // Desativa o ima, caso ele esteja ativado
  digitalWrite(RELE_IMA, LOW);

  // Move o servo do imã para baixo
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
      comando_stop.trim(); // Limpa espaços invisíveis ou quebras de linha extras

      if (comando_stop.startsWith("STOP")) {
        Serial.println("Espalhamento interrompido!");
        //homing();
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

  Serial.println("Espalhamento de parafusos concluído!");

  // Mantém POS_X / POS_Y coerentes com o restante do código
  POS_X = motor_x.currentPosition();
  POS_Y = motor_y.currentPosition();

} // espalha_parafusos