🦜 Parrot IA Interface

Parrot IA Interface is a Python + Uvicorn application that serves as a smart communication layer between users and Ollama AI models.
Developed as an integral component of Synapta OS, it provides a fast, secure, and low-latency way to interact with local or remote AI models through a clean, web-based interface.

Built with FastAPI and designed for modularity, Parrot IA enables seamless integration with Synapta OS Server and other Linux-based environments used in education, research, and edge computing. It allows users to deploy and interact with Ollama models—such as Tiny, LLaMA, or Mistral—without relying on external cloud infrastructure.

🚀 Key Features

Native integration with Synapta OS.

Direct and optimized connection with Ollama AI models (local or remote).

Asynchronous and scalable architecture supporting multiple concurrent sessions.

Minimalist web interface compatible with modern browsers.

Built-in security: token validation and IP-based access control.

Real-time streaming responses for natural interaction.

Deployable as a Uvicorn service on Linux, Windows, or Docker.

⚙️ Technology Stack

Backend: Python 3.11+, FastAPI, Uvicorn

Frontend: HTML, JavaScript, native CSS (no external dependencies)

AI Core: Ollama (Tiny, LLaMA, Mistral, etc.)

Platform Integration: Synapta OS Server, Debian, Ubuntu, AlmaLinux