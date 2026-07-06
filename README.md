# Máquina CNC Pick-and-Place (Separação Automática)

Uma máquina CNC (Controle Numérico Computadorizado) projetada para separar e organizar automaticamente parafusos e porcas de acordo com seus tipos, utilizando visão computacional e precisão robótica.

## 🎯 Visão Geral do Projeto

Este projeto visa desenvolver um sistema automatizado de *pick-and-place* (pegar e colocar) que:
- **Identifica** diferentes tipos de parafusos e porcas usando visão computacional.
- **Classifica** os fixadores por suas características (tamanho, tipo, formato).
- **Separa e Organiza** os componentes em recipientes ou compartimentos designados.
- **Otimiza** os movimentos de deslocamento e captura (eixos X e Y) para maior velocidade e precisão.

## 📋 Funcionalidades (Roadmap)

- [ ] Sistema de visão computacional para detecção e classificação de peças.
- [ ] Atuador magnético (Eletroímã controlado por Servo Motor) para captura precisa.
- [ ] Sistema de controle de movimento CNC (Arduino + CNC Shield).
- [ ] Separação e organização em tempo real.
- [ ] Regras de classificação personalizáveis.
- [ ] Interface de usuário (Dashboard) para monitoramento de estatísticas.

## 🏗️ Arquitetura do Sistema

### Componentes de Hardware
- Sistema de Movimento CNC:
  - 1 Arduino Uno
  - 1 CNC Shield V3.0
  - 3 Módulos de Driver A4988
  - 3 Motores NEMA 17
- Ferramenta de Captura:
  - Eletroímã
  - Servo Motor MG90S
  - Módulo Relé 
- Câmera para visão computacional.
- Recipientes de separação para os componentes classificados.

![Circuito CNC](https://github.com/PedroRebelloM/Pick-and-Place/blob/e6c53de7f7e20458a12f1c13ce07474f8cb05818/img/Circuito.png)

### Componentes de Software
- **Visão Computacional:** Algoritmo de detecção e classificação (Raspberry Pi / PC com Python e OpenCV).
- **Firmware de Controle de Movimento:** Lógica em C++ utilizando a [Biblioteca AccelStepper](https://github.com/adafruit/AccelStepper/blob/master/AccelStepper.h#L154) (Arduino).
- **Comunicação e Backend:** Processamento de dados em tempo real via porta Serial e servidor web (Python + flet).
- **Interface/Dashboard:** UI para monitoramento e configuração da máquina (Web/Flask).

---

## 📁 Estrutura de Diretórios

A estrutura atual do repositório é a seguinte:

```text
Pick-and-Place/
├── arduino/                 # Arquivos de firmware para o Arduino
│   ├── arduino.ino
│   └── funcoes.ino
├── img/                     # Imagens e materiais visuais do projeto
├── peças3D/                 # Arquivos 3D das peças da máquina
├── src/                     # Código principal em Python
│   ├── binarizacao.py
│   ├── classe.py
│   ├── main.py
│   ├── video.py
│   └── images/              # Imagens usadas pelos scripts
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação do projeto
```

## 🚀 Como Começar

Pré-requisitos
- [Arduino IDE](https://docs.arduino.cc/software/ide/) instalado para compilar o firmware.
- Python 3.12.10 instalado.
- Bibliotecas Python: opencv-python, pyserial, flet, numpy, scikit-learn.

Instalação e Execução (Resumo)
- Faça o upload dos arquivos da pasta arduino/ para o seu Arduino Uno.
- Certifique-se de que a CNC Shield está devidamente alimentada.
- No terminal, navegue até a pasta backend/ e instale as dependências:
  - pip install -r requirements.txt.
- Inicie o servidor flet: flet run main.py
- Acesse o Dashboard pelo seu navegador para controlar a máquina.


## 👤 Autores

- **Cris Guimarães**

- **Pedro Rebello M**

- **Pedro Ribeiro**


## 📞 Suporte e Contato

Email: pribeirofernande@gmail
---

**Status**: Em desenvolvimento 🚧
