# Estrategia de Despliegue y Hardware (Buildroot Edition)

## 1. Perfiles de Hardware Target

Al migrar a Buildroot, el consumo de RAM del sistema base se reduce drásticamente (< 100MB), liberando recursos para la IA.

### 🥉 Perfil Mínimo ("IoT / Kiosk")
*Objetivo: Ejecutar la interfaz web y consultar modelos muy pequeños (TinyLlama 1.1B q4_0) o actuar como cliente de otro nodo.*

| Componente | Especificación | Notas |
| :--- | :--- | :--- |
| **CPU** | Dual Core x86_64 o ARM64 (RPi 4) | Buildroot permite compilar para ARM fácilmente. |
| **RAM** | 2 GB | El OS consume ~100MB. Quedan ~1.8GB para modelos pequeños. |
| **Almacenamiento** | 8 GB SD Card / USB | Suficiente para OS + Swap + Modelo pequeño. |

### 🥇 Perfil Recomendado ("AI Appliance")
*Objetivo: Servidor de inferencia local fluido para varios alumnos.*

| Componente | Especificación | Notas |
| :--- | :--- | :--- |
| **CPU** | Quad Core Intel/AMD o ARM64 (RK3588) | Inferencia rápida (10-20 tok/sec). |
| **RAM** | 8 GB+ | Permite modelos como Llama 3 8B o Mistral 7B cuantizados. |
| **Almacenamiento** | 32 GB SSD/NVMe | Carga instantánea de modelos grandes. |

---

## 2. Modos de Experiencia: "Appliance Puro"

Con Buildroot, la distinción entre "Live" e "Instalado" se desvanece. La imagen generada (`sdcard.img`) *es* el sistema instalado.

### Estrategia: "Flash & Run" 🔥
El usuario descarga un solo archivo de imagen y lo "quema" (flashea) en el medio de arranque.

| Fases | Descripción |
| :--- | :--- |
| **1. Flasheo** | Usar Etcher, Rufus o `dd` para escribir la imagen `.img` en SD/USB/SSD. |
| **2. Primer Boot** | El sistema arranca en segundos. Un script `S99firstboot` expande la partición de datos para usar todo el disco disponible. |
| **3. Persistencia** | `/mnt/data` (partición 3) guarda configuraciones, historial de chat y modelos descargados. Si se corrompe el sistema (`rootfs`), se puede reflashear sin perder `/mnt/data`. |

### Comparativa con ISO Clásica:
*   **Ventaja**: Robustez total. El sistema base (`/`) es de solo lectura (SquashFS/RO-Ext4). Es inmune a virus comunes o errores de usuario que borren archivos del sistema.
*   **Desventaja**: Menos flexible para instalar "junto a Windows". Es un sistema dedicado.

---

## 3. Recomendación Final 🎯

**Modelo de "Caja Negra" (Appliance)**

1.  **Imagen Única**: Distribuir una imagen `synapta-os-[version].img.gz`.
2.  **Gestión de Discos**: El sistema asume control total del disco donde se flashea. Ideal para revivir PCs antiguas transformándolas en "Kioscos de IA".
3.  **Actualizaciones**: Vía reemplazo de partición de sistema (A/B partitioning) o reflasheo simple (manteniendo partición de datos).

**Justificación**: Las escuelas prefieren que el equipo "simplemente funcione" al encenderlo. Un appliance inmutable reduce el soporte técnico a cero: si falla, "apagar y encender" o "volver a flashear".
