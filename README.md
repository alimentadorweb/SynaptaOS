🌐 Synapta OS

Synapta OS is an educational Linux distribution preconfigured with **local Artificial Intelligence (AI)** capabilities.  
It is designed for **schools and remote areas** where Internet connectivity is limited or unavailable, offering access to AI-based learning and digital tools offline.

---

🎯 Mission

To **reduce the digital divide** by delivering a complete, privacy-respectful AI environment that empowers teachers and students in rural and under-connected regions.

---

🧠 Core Features

- 🦙 **Built-in Ollama + TinyLlama Models**  
  Runs lightweight language models locally for educational assistance, translation, and creative writing — no Internet required.

- 🧩 **Modular and Open Design**  
  Based on standard Linux packages and open frameworks, allowing easy customization and community contributions.

- 💻 **Low Hardware Requirements**  
  Optimized for low-resource environments: 2 GB RAM, dual-core CPU, and 20 GB disk space are sufficient.

- 🔐 **Privacy-Focused**  
  All data and AI interactions are processed locally — no cloud dependency.

- 🏫 **Education-Ready Tools**  
  Pre-installed applications for science, math, reading, and coding education.

---

🧩 Editions

| Edition | Description | License |
|----------|--------------|----------|
| **Synapta OS Community** | Open version for schools, NGOs, and volunteers | MPL-2.0 |
| **Synapta OS Server / Education Pack** | Preconfigured image with full AI setup, support, and training material | Commercial EULA |

---

⚙️ Technical Overview

Synapta OS combines:

- **Ubuntu/Debian-based** system optimized for educational environments.  
- **Ollama framework** to run local AI models.  
- **TinyLlama regional models**, supporting multilingual and culturally adapted learning.  
- **Offline-ready configuration** for use in remote classrooms or local networks.  

installer/
├── post_install.sh      # Automatic setup for Synapta OS
├── setup_ollama.sh      # Ollama installation and model loading
├── setup_network.sh     # Optional LAN configuration

💻 Hardware Requirements

Synapta OS is designed to operate efficiently on modest or legacy hardware,  
making it ideal for schools and community centers with limited resources.

🖥️ Minimum Requirements
| Component | Specification |
|------------|----------------|
| **Processor (CPU)** | Dual-core 1.6 GHz or higher (x86_64 / ARM64) |
| **Memory (RAM)** | 2 GB |
| **Storage** | 20 GB of free disk space |
| **Display** | 1024×768 resolution |
| **Connectivity** | Optional Internet access for updates (not required for local AI) |
| **Power** | 25 W average consumption (optimized for low-energy environments) |

⚙️ Recommended Requirements
| Component | Specification |
|------------|----------------|
| **Processor (CPU)** | Quad-core 2.0 GHz or higher |
| **Memory (RAM)** | 8 GB or more |
| **Storage** | 40 GB SSD |
| **GPU (optional)** | CUDA-compatible or OpenCL-capable GPU for AI acceleration |
| **Network** | Ethernet or Wi-Fi for LAN classroom mode |
| **Extras** | Microphone and camera for voice or vision AI modules |

---
🚀 Project Stage

Synapta OS is currently in **active development**, moving through the following phases:

🧩 Current Phase: Prototype & Packaging
- ✅ Core system base and installer scripts completed.  
- ✅ Ollama integration with TinyLlama models tested successfully.  
- 🧠 Local AI assistant prototype operational in offline mode.  
- 🧰 Post-installation scripts under refinement for automated setup.  
- 🖥️ Preparing ISO image for testing in rural education environments.

📅 Next Milestones
| Phase | Description | Estimated Date |
|--------|--------------|----------------|
| **Beta Release** | Public test version with preinstalled AI modules | 2023 |
| **Pilot Deployment** | Field testing in 10 rural schools (Latin America) | 2024 |
| **Educational Content Pack** | Integration of open learning materials (science, math, reading) | 2025 |
| **Stable Release 1.0** | Official release with multilingual support |  2025 |

🧭 Long-Term Vision
To establish **Synapta OS** as a globally recognized open educational platform powered by local AI,  
supporting teachers and students in every region — regardless of connectivity or infrastructure.

---
🛠️ *Community contributions, partnerships, and testing feedback are welcome  
to accelerate the development of Synapta OS and expand its reach.*


