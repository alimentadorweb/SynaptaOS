# Arquitectura de Imagen Synapta OS (Buildroot)

## 1. Concepto: "Appliance Firmware"

En lugar de una ISO híbrida tradicional (Live CD + Installer), Synapta OS se distribuye como una **imagen de disco completa** (`.img`) lista para ser flasheada en el medio de destino (SD Card, USB, SSD).

*   **Filosofía**: "Flash & Run". No hay proceso de instalación. El primer arranque *es* el sistema final.
*   **Actualizaciones**: Sistema A/B (opcional) o reflasheo de la partición de sistema manteniendo la partición de datos.
*   **Persistencia**: Partición dedicada `/mnt/data` o `/overlay` para configuraciones de usuario y historial de chat.

## 2. Herramientas de Construcción

### 🛠️ Core: `Buildroot`
Herramienta que automatiza la generación cruzada de sistemas Linux completos.
*   **Entrada**: Configuración (`.config`) + Parches + Buildroot Makefiles.
*   **Salida**: Kernel image (`bzImage`), Root Filesystem (`rootfs.tar`), Bootloader binaries.

### 🖼️ Generación de Imagen: `genimage`
Herramienta estandar en el ecosistema Buildroot para ensamblar las piezas en un solo archivo binario particionado.
*   **Función**: Toma el bootloader, kernel, y rootfs, y crea las particiones alineadas correctamente (EFI, ext4, swap) en un archivo `sdcard.img`.

## 3. Diagrama de Componentes (Boot & Runtime)

```mermaid
graph TD
    subgraph "Storage Medium (USB/SSD)"
        Part1[Partición 1: BOOT (FAT32)]
        Part2[Partición 2: ROOTFS (SquashFS/Ext4 - Read Only)]
        Part3[Partición 3: DATA (Ext4 - Read Write)]
    end

    Boot[UEFI BIOS] --> Part1
    Part1 -->|EFIStub / Syslinux| Kernel[Linux Kernel]
    Kernel -->|Mount| Part2
    Part2 --> Init[BusyBox Init]
    
    Init -->|Mount| Overlay[OverlayFS]
    Overlay -->|Upper Dir| Part3
    Overlay -->|Lower Dir| Part2
    
    Init --> Services[Systemv / Init Scripts]
    Services --> Python[Python Runtime]
    Services --> Ollama[Ollama Server]
    
    Python --> App[Parrot Web UI]
```

## 4. Estrategia de Implementación (Buildroot)

**Ruta Recomendada: `Buildroot` External Tree**

### Estructura de Proyecto ("BR2_EXTERNAL")
Mantener las personalizaciones de Synapta OS fuera del árbol principal de Buildroot para facilitar actualizaciones de Buildroot.

```text
synapta-os-buildroot/
├── board/
│   └── synapta/
│       ├── genimage.cfg      # Partition layout
│       ├── post-build.sh     # Scripts to copy files before packaging
│       ├── post-image.sh     # Script that calls genimage
│       └── rootfs_overlay/   # Files that overwrite rootfs (etc, init.d)
├── configs/
│   └── synapta_defconfig     # Base configuration (kernel, packages)
├── package/
│   ├── python-parrot/        # Package for Parrot app (Config.in, python-parrot.mk)
│   └── ollama-bin/           # Package for Ollama binary (Config.in, ollama-bin.mk)
└── Config.in                 # Main menu
```

### Pasos Clave:
1.  **Defconfig**: Crear una configuración mínima (`make menuconfig`) seleccionando kernel LTS, glibc, python3, y soporte de hardware genérico (x86_64).
2.  **Paquetes**:
    - Portar las dependencias de Python de Parrot (`requirements.txt`) a paquetes de Buildroot si no existen (muchos ya están en `package/python-*`).
    - Crear un paquete `ollama-bin` que descargue el binario estático de Ollama y lo instale en `/usr/bin`.
3.  **Overlay**: Usar `board/synapta/rootfs_overlay` para configurar la red, usuarios, y scripts de inicio (`S90parrot`).
4.  **Genimage**: Configurar particiones para soportar persistencia de datos (modelos de IA y base de datos) separada del sistema.

---
**Resultado**: Un sistema operativo de < 500MB (sin modelos) que arranca en segundos, es inmutable (robusto ante apagones) y reproducible bit a bit.
