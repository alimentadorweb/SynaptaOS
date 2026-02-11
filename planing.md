# Esquema del Proyecto Synapta OS (Buildroot Edition)

## 📌 Descripción General
**Synapta OS** evoluciona hacia un "AI Appliance" minimalista, construido desde cero usando **Buildroot**. El objetivo es crear un sistema embebido Linux extremadamente ligero, reproducible y optimizado para ejecutar modelos de IA local (Small Language Models) en hardware modesto, eliminando todo el "bloatware" de una distribución tradicional.

## 🏗️ Arquitectura del Sistema (Appliance)

```mermaid
graph TD
    User[Usuario] -->|Navegador Web| UI[Parrot UI]
    UI -->|HTTP/WebSocket| PythonApp[Parrot Backend (FastAPI)]
    PythonApp -->|Inferencia| Ollama[Motor Ollama (Go)]
    Ollama -->|Carga| Models[Modelos GGUF (en partición de datos)]
    
    subgraph "Buildroot System Image"
        Kernel[Linux Kernel (Custom)]
        Init[Init System (BusyBox/SysV)]
        Libs[LibC (glibc/musl) + Python3 + Drivers]
        Binaries[Ollama Binary + App Dependencies]
    end

    Boot[Bootloader (Syslinux/GRUB)] --> Kernel
```

## 🧩 Componentes Principales

### 1. **Buildroot Core**
- **Sistema Base**: Generado completamente desde código fuente.
- **Init System**: BusyBox init o SysVinit (arranque en < 5 segundos).
- **C Library**: glibc (para compatibilidad máxima con binarios de IA) o musl (para tamaño mínimo).
- **Tamaño Esperado**: < 300MB (sin modelos).

### 2. **Capa de Aplicación (Parrot)**
- **Integración**: Python 3.x compilado dentro de la imagen.
- **Dependencias**: Módulos Python (FastAPI, Uvicorn, MariaDB connector) integrados como paquetes de Buildroot (`python-fastapi`, etc.).
- **Backend**: `parrot.py` ejecutado como servicio de sistema (`/etc/init.d/S99parrot`).

### 3. **Motor de IA (Ollama)**
- **Desafío**: Ollama está escrito en Go.
- **Estrategia**:
    - Opción A: Compilar Ollama dentro de Buildroot (requiere paquete `golang`).
    - Opción B: Usar binario precompilado estático (amd64/arm64) y copiarlo vía `rootfs overlay`.
- **Modelos**: Almacenados en una partición persistente separada para no inflar la imagen raíz.

### 4. **Hardware Support**
- **Kernel**: Linux Mainline o LTS, configurado solo con los drivers necesarios (USB, Audio, Ethernet, WiFi, Video simple).
- **Firmware**: `linux-firmware` reducido (solo lo esencial).

## 🔄 Flujo de Desarrollo (Workflow)
1.  `make menuconfig`: Seleccionar arquitectura, kernel, paquetes (Python, SSL, etc.).
2.  `make`: Buildroot descarga fuentes, compila toolchain, kernel y rootfs.
3.  `output/images/sdcard.img`: Imagen lista para flashear ("quemar") en USB/SD/SSD.

## 🛠️ Stack Tecnológico Refactorizado

| Componente | Tecnología | Notas |
| :--- | :--- | :--- |
| **Build System** | **Buildroot** | Generación de OS completo y reproducible. |
| **Kernel** | Linux (LTS) | Optimizado para tamaño y boot rápido. |
| **Userland** | BusyBox | Utilities estándar (ls, cp, sh) en un solo binario. |
| **App Runtime** | Python 3 + Go | Entorno para Parrot y Ollama. |
| **UI** | HTML5/JS | Servido por FastAPI (sin X11/Wayland pesado si es headless, o con Kiosk mode). |

## 🚀 Estado Actual
Transición de prototipo basado en Debian a arquitectura Buildroot. Se requiere portar la aplicación `Parrot` y sus dependencias a paquetes `.mk` de Buildroot o entornos virtuales portables.
