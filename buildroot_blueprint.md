# Blueprint: Synapta OS (Buildroot Appliance)

Este documento detalla la configuración técnica para crear una imagen de sistema (`.img`) booteable, minimalista y autoejecutable para Synapta OS usando Buildroot.

## 1. Arquitectura de Construcción

*   **Host de Compilación**: Linux (Debian/Ubuntu) con `build-essential`, `libncurses-dev`, `python3`, `unzip`, `bc`.
*   **Target**: x86_64 (Intel/AMD 64-bit).
*   **Salida**: `synapta-os.img` (Híbrida BIOS/UEFI).

## 2. Configuración de Buildroot (`make menuconfig`)

### Target Options
- **Target Architecture**: `x86_64`
- **Target Architecture Variant**: `automaton` (o genérico para máxima compatibilidad)

### Toolchain
- **C library**: `glibc` (Indispensable para compatibilidad con binarios de IA como Ollama y bibliotecas Python complejas).
- **C++**: Enabled (Requerido por muchos módulos Python).
- **OpenMP**: Enabled (Para aceleración de IA en CPU).

### System Configuration
- **Init System**: `BusyBox` (Más ligero) + `mdev` (Device manager).
- **Enable Root Login**: `yes` (con password o key para debug).
- **Run a getty (login prompt) after boot**: `yes`.
- **Root FS Overlay Directories**: `$(BR2_EXTERNAL_SYNAPTA_PATH)/board/synapta/overlay`.

### Kernel
- **Kernel Version**: `Latest LTS` (ej. 6.6.x).
- **Defconfig**: `x86_64_defconfig`.
- **Kernel Binary Format**: `bzImage`.

### Bootloaders
- **GRUB2**:
    - **Platform**: `i386-pc` (BIOS Legacy).
    - **Platform**: `x86_64-efi` (UEFI).
    - **Install tools**: `yes` (para generar la imagen).

### Target Packages (Networking & Utilities)
- **Networking**: `dhcpcd` (Cliente DHCP simple) o `ifupdown-scripts`.
- **Filesystem**: `ntfs-3g`, `e2fsprogs` (para redimensionar particiones).
- **SSH**: `dropbear` (Ligero) o `openssh`.

### Target Packages (Python & App)
- **Interpreter**: `python3`.
- **Modules**:
    - `python-fastapi`
    - `python-uvicorn`
    - `python-pydantic`
    - `python-requests`
    - `python-jinja2`
    - `python-mysql-connector` (o `mariadb-connector-c` + binding).

## 3. Estructura de Proyecto (BR2_EXTERNAL)

Crear una carpeta `synapta-os` al mismo nivel que `buildroot`.

```bash
synapta-os/
├── Config.in
├── external.lib.mk
├── external.mk
├── board/
│   └── synapta/
│       ├── genimage.cfg         # Partition layout
│       ├── grub.cfg             # Boot configuration
│       ├── post-build.sh        # Cleanup/copy scripts
│       ├── overlay/             # Files copied to rootfs
│       │   ├── etc/
│       │   │   ├── init.d/
│       │   │   │   └── S99parrot # Auto-start script
│       │   │   ├── network/
│       │   │   │   └── interfaces # DHCP configuration
│       │   │   └── fstab         # Mounts
│       │   └── opt/
│       │       └── parrot/       # Source code of your app
└── configs/
    └── synapta_defconfig        # Saved Buildroot configuration
```

## 4. Archivos Clave

### A. Auto-arranque de Parrot (`board/synapta/overlay/etc/init.d/S99parrot`)
```bash
#!/bin/sh

case "$1" in
  start)
    echo "Starting Synapta Parrot..."
    # Assume code is in /opt/parrot
    cd /opt/parrot
    # Run uvicorn in background
    # --host 0.0.0.0 allows LAN access
    start-stop-daemon -S -b -x /usr/bin/uvicorn -- parrot:app --host 0.0.0.0 --port 8000 --reload
    ;;
  stop)
    echo "Stopping Synapta Parrot..."
    start-stop-daemon -K -x /usr/bin/uvicorn
    ;;
  restart|reload)
    "$0" stop
    "$0" start
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
esac

exit $?
```

### B. Configuración de Red DHCP (`board/synapta/overlay/etc/network/interfaces`)
```text
auto lo
iface lo inet loopback

# Detect and bring up eth0 automatically
auto eth0
iface eth0 inet dhcp
```

### C. Layout de Imagen (`board/synapta/genimage.cfg`)
Define una imagen híbrida válida para UEFI y BIOS.

```ini
image efi-part.vfat {
    vfat {
        file EFI {
            image = "efi-part/EFI"
        }
    }
    size = 32M
}

image synapta-os.img {
    hdimage {
        partition-table-type = "gpt"
    }

    partition boot {
        image = "efi-part.vfat"
        partition-type-uuid = c12a7328-f81f-11d2-ba4b-00a0c93ec93b
        offset = 32K
        bootable = true
    }

    partition root {
        image = "rootfs.ext4" # Or SquashFS for read-only
        partition-type-uuid = 4f68bce3-e8cd-4db1-96e7-fbc68e749c09
    }
    
    # Optional data partition
    partition data {
        size = 512M
        partition-type-uuid = 0fc63daf-8483-4772-8e79-3d69d8477de4
    }
}
```

## 5. Pasos de Construcción (Reproducibles)

1.  **Clonar Buildroot**:
    ```bash
    git clone https://git.buildroot.net/buildroot
    cd buildroot
    git checkout 2024.02.x # Usar una rama estable
    ```

2.  **Preparar External Tree**:
    Copiar la estructura definida en el punto 3 a `../synapta-os`.

3.  **Configurar**:
    ```bash
    make BR2_EXTERNAL=../synapta-os synapta_defconfig
    ```

4.  **Compilar**:
    ```bash
    make
    ```

5.  **Output**:
    La imagen final estará en `output/images/synapta-os.img`.
    Flashear con Rufus (Windows) o `dd` (Linux).

---
**Resultado**: Al bootear, el sistema obtendrá IP por DHCP y `S99parrot` levantará la API. Podrás acceder desde otro PC en la red a `http://<IP_SYNAPTA>:8000/docs`.
