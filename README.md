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

## 🖨️ Peças 3D

Todos os componentes 3D personalizados foram projetados para otimizar a precisão, estabilidade e eficiência da máquina CNC. Abaixo estão os arquivos disponíveis:

| Peça | Descrição | Arquivo |
|------|-----------|---------|
| **Cabeça CNC** | Componente principal de montagem e estrutura | [`cabeça_CNC.stl`](peças3D/cabeça_CNC.stl) |
| **Pinhão 17mm** | Pinhão para transmissão de movimento dos motores NEMA 17 | [`pinhao17mm.stl`](peças3D/pinhao17mm.stl) |
| **Cremalheira** | Cremalheira de transmissão linear para os eixos | [`cremalheira.stl`](peças3D/cremalheira.stl) |
| **Suporte Cremalheira** | Suporte estrutural para fixação da cremalheira | [`suporte_cremalheira.stl`](peças3D/suporte_cremalheira.stl) |
| **Suporte Câmera** | Suporte principal para montagem da câmera de visão | [`suporte_camera.stl`](peças3D/suporte_camera.stl) |
| **Suporte Câmera 2** | Suporte adicional/complementar para câmera | [`suporte_camera2.stl`](peças3D/suporte_camera2.stl) |
| **Calço Motor NEMA17** | Calço de alinhamento para os motores NEMA 17 | [`calço_motor_nema17.stl`](peças3D/calço_motor_nema17.stl) |
| **Fixador Motor** | Peça de fixação dos motores na estrutura | [`fixador_motor.stl`](peças3D/fixador_motor.stl) |

**Montagem das peças** :  [`montagem_cabeçaCNC.zip`](montagem_cabeçaCNC.zip)

### 📥 Como Usar as Peças 3D

1. **Visualizar:** Acesse a pasta [`peças3D/`](peças3D) e abra os arquivos `.stl` em um visualizador 3D (ex: [Thingiverse Customizer](https://www.thingiverse.com/customizer), Fusion 360, FreeCAD).
2. **Imprimir:** Use um software de fatiamento (ex: Cura, PrusaSlicer) para preparar os arquivos `.stl` para sua impressora 3D.
3. **Modificar:** Os arquivos no formato `.x_t` podem ser editados em softwares de CAD como Fusion 360, SolidWorks ou FreeCAD.

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
│   ├── cabeça_CNC.x_t
│   ├── pinhao17mm.stl
│   ├── cremalheira.stl
│   ├── suporte_cremalheira.stl
│   ├── suporte_camera.stl
│   ├── suporte_camera2.stl
│   ├── calço_motor_nema17.stl
│   └── fixador_motor.stl
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

### Pré-requisitos
- [Arduino IDE](https://docs.arduino.cc/software/ide/) instalado para compilar o firmware.
- Python 3.12.10 instalado.
- Bibliotecas Python: opencv-python, pyserial, flet, numpy, scikit-learn.

### Instalação e Execução (Resumo)
- Faça o upload dos arquivos da pasta arduino/ para o seu Arduino Uno.
- Certifique-se de que a CNC Shield está devidamente alimentada.
- No terminal, navegue até a pasta backend/ e instale as dependências:
  - `pip install -r requirements.txt`
- Inicie o servidor flet: `flet run main.py`
- Acesse o Dashboard pelo seu navegador para controlar a máquina.

## 👤 Autores

- **Cris Guimarães**
- **Pedro Rebello M**
- **Pedro Ribeiro**

## 📞 Suporte e Contato

---

**Status**: Em desenvolvimento 🚧
