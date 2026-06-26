# Pick-and-Place CNC Machine

A Computer Numeric Control (CNC) machine designed to automatically sort and organize screws and nuts by their types using machine vision and precision robotics.

## 🎯 Project Overview

This project aims to develop an automated pick-and-place system that:
- **Identifies** different types of screws and nuts using computer vision
- **Classifies** fasteners by their characteristics (size, type, thread pattern)
- **Sorts** components into designated bins or containers
- **Optimizes** pick-and-place movements for speed and accuracy

## 📋 Features

- [ ] Computer vision system for fastener detection and classification
- [ ] Robotic arm for precise picking and placement
- [ ] CNC motion control system
- [ ] Real-time sorting and organization
- [ ] Customizable classification rules
- [ ] Performance monitoring and statistics

## 🏗️ System Architecture

### Hardware Components
- CNC Motion Control System (X, Y, Z axes)
- Eletromagnet
- Computer vision camera system
- Sorting bins/containers for classified components

### Software Components
- Machine vision algorithm (object detection & classification) (Raspbarry py with Open CV)
- Motion control firmware (Arduino)
- Real-time web data processing (Serial + Flask) 
- UI/Dashboard for monitoring and configuration (Flask)

## 🚀 Getting Started

### Prerequisites
- [List hardware requirements]
- [List software dependencies]

### Installation
```bash
# Clone the repository
git clone https://github.com/PedroRebelloM/Pick-and-Place.git

# Navigate to project directory
cd Pick-and-Place

# Install dependencies
[Installation instructions]
```

### Quick Start
```bash
# Run the system
[Execution command]
```

## 📁 Project Structure

```
Pick-and-Place/
├── firmware/           # CNC control firmware
├── vision/             # Computer vision algorithms
├── motion/             # Motion control system
├── hardware/           # Hardware schematics and designs
├── ui/                 # User interface/dashboard
├── docs/               # Documentation
└── tests/              # Test suite
```

## 🔍 How It Works

1. **Input**: Raw mix of screws and nuts fed into the system
2. **Detection**: Computer vision identifies each component
3. **Classification**: Machine learning model classifies by type
4. **Picking**: Robotic arm picks the classified component
5. **Placement**: Component is placed in its designated bin
6. **Repeat**: Process continues automatically

## 🛠️ Development Status

- [ ] System design and CAD models
- [ ] Hardware assembly
- [ ] Vision system development
- [ ] Motion control implementation
- [ ] Integration and testing
- [ ] Performance optimization

## 📚 Documentation

- [Hardware Setup Guide](docs/hardware-setup.md)
- [Software Installation](docs/software-setup.md)
- [Configuration Guide](docs/configuration.md)
- [API Reference](docs/api.md)


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Pedro Rebello M**
- GitHub: [@PedroRebelloM](https://github.com/PedroRebelloM)

## 📞 Contact & Support

For questions or support regarding this project, please open an issue on the GitHub repository.

---

**Status**: Under Development 🚧
