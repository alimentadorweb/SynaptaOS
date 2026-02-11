# Test Synapta OS with QEMU

Esta guía explica cómo emular la imagen `synapta-os.img` generada por Buildroot usando QEMU para validar el arranque y la red.

## 1. Comando de Emulación

Este comando emula una máquina x86_64 estándar, asigna 2GB de RAM, utiliza la imagen generada como disco duro principal, y hace forwarding del puerto 8000 del guest al 8000 del host.

```bash
qemu-system-x86_64 \
    -M pc \
    -m 2048 \
    -smp 2 \
    -drive file=output/images/synapta-os.img,format=raw,if=virtio \
    -net nic,model=virtio \
    -net user,hostfwd=tcp::8000-:8000 \
    -nographic
```

### Explicación de Flags:
*   `-M pc`: Máquina PC estándar (BIOS Legacy por defecto, Buildroot booteará grub i386-pc).
*   `-m 2048`: 2GB de RAM (Mínimo recomendado).
*   `-drive ...`: Monta la imagen como disco VirtIO (rápido).
*   `-net user,hostfwd=...`: Configura red de usuario (NAT) y redirige `localhost:8000` en tu PC al puerto `8000` de la VM.
*   `-nographic`: Salida por consola serial (útil si configuras `console=ttyS0` en kernel, si no, usa `-vga std` para ver ventana gráfica).

> **Para UEFI**: Añadir `-bios /path/to/OVMF.fd`.

## 2. Verificación de Funcionamiento

1.  **Boot Log**: Deberías ver el arranque de Linux y mensajes de OpenRC/Init/BusyBox.
2.  **Login**: Cuando aparezca el login, entra como `root` (password vacío o el que hayas configurado).
3.  **Verificar IP**:
    ```bash
    ip addr show eth0
    ```
    (Debería tener una IP tipo `10.0.2.15`).
4.  **Verificar Servicio**:
    Desde tu navegador en el **host**, entra a:
    `http://localhost:8000/docs`
    
    Si carga Swagger UI, ¡Parrot está vivo!

## 3. Troubleshooting (Depuración)

### A. No Arranca (Pantalla Negra/Grub Rescue)
*   **Causa**: Grub no encuentra la partición root.
*   **Fix**: En la consola de QEMU, presiona 'c' en Grub y exlora con `ls`. Verifica que `(hd0,gpt3)` existe.

### B. Arranca pero no hay Red
*   **Comando Guest**: `udhcpc -i eth0` manualmente.
*   **Logs**: `cat /var/log/messages` o revisa la salida del script `/etc/init.d/S40network`.

### C. Red OK, pero no abre http://localhost:8000
*   **Comprobar proceso**: En guest, ejecuta `ps | grep python`. ¿Está corriendo uvicorn?
*   **Ver logs de Parrot**:
    ```bash
    tail -f /var/log/parrot.log
    ```
    Busca errores de Python (ImportError son comunes si faltan dependencias vendored).
*   **Prueba Local**:
    ```bash
    wget -qO- http://localhost:8000
    ```
    Si responde HTML, el problema es el forwarding de QEMU.
