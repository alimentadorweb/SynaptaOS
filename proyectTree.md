# Synapta OS - Project Structure

This document provides a comprehensive overview of the Synapta OS project directory structure.

## Root Structure

```text
SynaptaOS/
├── .git/                       # Git version control
├── .gitignore
├── AboutMe.md                  # Project origin and mission statement (English/Spanish)
├── EULA.txt                    # End User License Agreement
├── LICENSE                     # Project license
├── LICENSE_CHANGE_NOTICE.md    # License change documentation
├── README.md                   # Project overview and getting started
│
├── assets/                     # Project assets
│   ├── logo/                   # Synapta OS logos
│   ├── presentation/           # Presentation materials
│   ├── screenshot/             # Screenshots
│   └── wallpaper/              # Desktop wallpapers
│
├── docs/                       # Documentation
│   ├── SynaptaOS_Server_Manual_en.md
│   ├── SynaptaOS_Server_Manual_es.md
│   ├── impact_plan.md
│   ├── legal/
│   ├── project_overview.md
│   └── roadmap.md
│
├── etc/                        # System configuration overlay (for Buildroot target)
│   ├── init.d/                 # Init scripts
│   │   └── S99parrot           # Parrot service init script
│   └── synapta/
│       └── synapta.env         # Runtime environment variables
│
├── installer/                  # Buildroot overlay and configuration files
│   ├── S01mount_data           # Mount data partition for persistence
│   ├── S40mariadb              # MariaDB service start script
│   ├── S40network              # Network configuration (DHCP with static fallback)
│   ├── S41firewall             # Iptables firewall rules
│   ├── S50synapta-dbinit       # Database initialization (first boot)
│   ├── S60ollama               # Ollama AI service start script
│   ├── S99parrot               # Parrot FastAPI application start script (template)
│   ├── bootloader_setup.md     # Buildroot bootloader configuration guide
│   ├── genimage.cfg            # Genimage configuration for hybrid BIOS/UEFI boot
│   ├── grub.cfg                # GRUB boot menu configuration
│   ├── post_install.sh         # Post-install script (copies etc/ and opt/ to target)
│   ├── setup_network.sh        # Network setup script
│   ├── setup_ollama.sh         # Ollama setup script
│   └── synapta.env             # Environment configuration template
│
├── kernel/                     # Linux kernel source tree (78,697 files)
│
├── opt/                        # Application installation directory (Buildroot target)
│   ├── model_ai/               # AI models directory
│   │   ├── Modelfile           # Ollama model definition
│   │   └── ParrotAI1_1B_q8.gguf # Local AI Model file (1.1GB)
│   └── synapta/
│       └── parrot/             # Parrot application deployment directory
│           ├── parrot.py       # FastAPI backend (MariaDB + Ollama)
│           ├── readme.md
│           ├── static/         # Frontend assets (HTML/JS/CSS)
│           │   ├── index.html
│           │   ├── style.css
│           │   ├── highlight.min.js
│           │   ├── atom-one-dark.min.css
│           │   ├── default.min.css
│           │   ├── css/
│           │   │   └── bootstrap.min.css
│           │   └── js/
│           │       └── bootstrap.bundle.min.js
│           └── vendor/         # Vendored Python dependencies (FastAPI, Uvicorn, etc.)
│               ├── annotated_types/
│               ├── anyio/
│               ├── certifi/
│               ├── charset_normalizer/
│               ├── click/
│               ├── fastapi/
│               ├── h11/
│               ├── httpcore/
│               ├── httpx/
│               ├── idna/
│               ├── pydantic/
│               ├── pydantic_core/
│               ├── setuptools/
│               ├── sniffio/
│               ├── starlette/
│               ├── typing_inspection/
│               ├── urllib3/
│               └── uvicorn/
│
├── parrot/                     # Parrot source (development copy)
│   ├── parrot.py               # Backend source
│   ├── readme.md
│   └── static/                 # Frontend source
│
├── src/                        # Source directory (Work in Progress)
│   ├── ai_models/
│   ├── ollama/
│   │   └── ui/
│   └── ui/
│
└── Documentation Files (Root)
    ├── buildroot_blueprint.md      # Buildroot configuration blueprint
    ├── deployment_strategy.md      # Deployment strategy document
    ├── full_stack_blueprint.md     # Full stack integration plan (MariaDB + Ollama + Parrot)
    ├── iso_architecture.md         # ISO architecture design document
    ├── planing.md                  # Project planning and schema
    ├── proyectTree.md              # This file - Project structure documentation
    ├── qemu_test_guide.md          # QEMU testing and verification guide
    └── vendor_strategy.md          # Python dependency vendoring strategy
```

## Key Directories

### `/etc/` - System Configuration Overlay
Contains configuration files that will be copied to the target system's `/etc/` directory during Buildroot image creation or via `post_install.sh`.

### `/installer/` - Buildroot Overlay & Scripts
Contains init scripts (S##name format for SysV init), bootloader configurations, and post-installation scripts. The `post_install.sh` script copies `etc/` and `opt/` to the target filesystem.

### `/opt/` - Application Deployment
The production deployment directory structure. This mirrors how the application will be installed on the final Buildroot appliance. Includes vendored Python dependencies in `vendor/`.

### `/parrot/` - Development Source
The source code for the Parrot AI assistant application. This is the development version that gets copied to `/opt/synapta/parrot/` during deployment.

### `/kernel/` - Linux Kernel
Complete Linux kernel source tree for custom kernel builds.

## Deployment Workflow

1. **Development**: Edit code in `parrot/`
2. **Prepare**: Copy to `opt/synapta/parrot/`
3. **Vendor Dependencies**: Populate `opt/synapta/parrot/vendor/` with pure-Python libraries
4. **Install**: Run `installer/post_install.sh` to copy `etc/` and `opt/` to target
5. **Build**: Use Buildroot to create final image

## Build Artifacts (Generated)
The following directories/files are generated during the build process and are not tracked in Git:
- `output/` - Buildroot build output
- `*.img` - Generated disk images
- `*.iso` - Generated ISO images

## Notes
- **Build System**: Buildroot for creating a minimal Linux appliance
- **Init System**: BusyBox init (SysV-style)
- **Target Architecture**: x86_64
- **Boot Modes**: BIOS and UEFI (hybrid via GRUB)
- **Python Dependencies**: Hybrid approach (vendoring for pure-Python, Buildroot packages for binary modules like MariaDB connector)
