# Synapta OS Full Stack Integration Plan

Este documento detalla la configuración completa para integrar MariaDB, Ollama y Parrot en una imagen Buildroot autoejecutable.

## 1. Stack de Servicios

| Orden | Script Init | Servicio | Puerto | Notas |
| :--- | :--- | :--- | :--- | :--- |
| 10 | `S10mdev` | Device Manager | - | Core System |
| 40 | `S40network` | Network (DHCP/Static) | - | Fallback 192.168.50.10 |
| 50 | `S50mariadb` | Database Server | 3306 | Requiere inicialización de DB en primer arranque |
| 60 | `S60ollama` | AI Inference Engine | 11434 | Binario estático en `/usr/bin` |
| 99 | `S99parrot` | FastAPI App | 8000 | Depende de DB y Ollama |

## 2. Configuración Buildroot (Adicional a Blueprint base)

### Packages
*   `mariadb` (Server & Client).
*   `libatomic` (A veces requerido por MariaDB/Ollama en algunas archs, x86_64 suele tenerlo).
*   `openssl` (Requerido por MariaDB/Python).

### Filesystem Layout (Rootfs RW vs Data)
Para que MariaDB y Ollama funcionen bien y persistan datos:
*   `/var/lib/mysql`: Debe ser escribible y persistente.
*   `/root/.ollama`: Debe ser escribible y persistente (para modelos descargados).

**Estrategia "Data Partition Overlay"**:
1.  En el boot, montar la partición `DATA` (etiqueta `DATA` o UUID específico) en `/mnt/data`.
2.  Crear symlinks o bind mounts desde `/mnt/data` a las rutas del sistema.

**Script `S01mount_data`**:
```bash
mount -L DATA /mnt/data
mkdir -p /mnt/data/mysql /mnt/data/ollama
ln -sf /mnt/data/mysql /var/lib/mysql
ln -sf /mnt/data/ollama /root/.ollama
```

## 3. Scripts de Inicialización

### A. `S50mariadb` (Database)
Lógica crítica:
1.  Verificar si `/var/lib/mysql` está vacío (primer boot).
2.  Si está vacío, ejecutar `mysql_install_db --user=mysql --datadir=/var/lib/mysql`.
3.  Iniciar `mysqld_safe`.
4.  Esperar a que el socket `/run/mysqld/mysqld.sock` esté activo.
5.  Crear base de datos `chatbot_db` y usuario si no existen (script SQL bootstrap).

### B. `S60ollama` (AI Engine)
Lógica:
1.  Definir `OLLAMA_MODELS=/root/.ollama/models`.
2.  Iniciar `ollama serve` en background.
3.  Esperar respuesta en `localhost:11434`.

### C. `S99parrot` (App)
Actualización:
1.  Loop de espera explícito (`wait_for_port 3306`, `wait_for_port 11434`) antes de lanzar Uvicorn.
2.  Esto evita que la app falle al inicio por "Connection Refused".

## 4. Comandos de Build

1.  **Copiar Scripts**: Todos los `Sxx` van a `board/synapta/overlay/etc/init.d/`.
2.  **Permisos**: `chmod +x` a todos.
3.  **Compilar**: `make`.

---
Este plan asegura que los servicios se levanten en orden y que la base de datos se inicialice correctamente en el primer arranque virgen.
