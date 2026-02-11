# Python Vendoring Strategy (No runtime pip)

Este documento detalla cómo ejecutar FastAPI + Uvicorn + Requests dentro de Buildroot sin usar `pip` en el sistema final, mediante la técnica de "vendoring" (incluir las librerías en el código fuente).

## 1. Estructura de Directorios

Recomendamos una estructura clara en `/opt/synapta/parrot`:

```bash
/opt/synapta/parrot/
├── main.py               # Tu aplicación FastAPI (parrot.py renombrado)
├── vendor/               # Carpeta para librerías de terceros puras
│   ├── fastapi/
│   ├── uvicorn/
│   ├── starlette/
│   ├── pydantic/
│   ├── ... (otras librerías puras)
└── lib/                  # (Opcional) Librerías compiladas (binarias)
```

## 2. Dependencias Mínimas (Pure Python)

Para que FastAPI y Uvicorn funcionen en su modo más básico (sin uvloop/httptools compilados), necesitas copiar las siguientes carpetas al directorio `vendor/` desde una instalación local (`pip install -t vendor ...` en tu host):

### Core List:
1.  **fastapi**
2.  **starlette** (Dependencia de FastAPI)
3.  **pydantic** (Dependencia de FastAPI - Versión v2 core puede requerir binario `pydantic-core`. **OJO**: Pydantic v2 es mayormente Rust/C. **Recomendación**: Usar Pydantic v1.10.x si se busca 100% pure python o asegurarse de copiar el `.so` de `pydantic_core` compatible con la arquitectura target x86_64, o mejor aún **usar el paquete python-pydantic de Buildroot** y vendorizar solo lo que Buildroot no tenga).
4.  **typing_extensions** (Si usas Python < 3.10)
5.  **uvicorn**
6.  **click** (Dependencia de Uvicorn)
7.  **h11** (Protocolo HTTP puro de Uvicorn)
8.  **requests** (Para cliente Ollama)
9.  **urllib3**
10. **idna**
11. **certifi**
12. **charset_normalizer**

### Estrategia Híbrida (Recomendada)

1.  **Vendor (Librerías Puras)**:
    Incluye estas en `/opt/synapta/parrot/vendor/`:
    *   `fastapi`, `uvicorn`, `starlette`, `h11`, `idna`, `sniffio`, `anyio`, `typing_extensions`.
    *   **Pydantic**: Usa v1 (ej. `1.10.x`) para máxima portabilidad pura. Si usas v2, requiere compilación Rust (complejo), mejor usa paquete Buildroot.

2.  **Buildroot Packages (Binarios/Complejos)**:
    Habilita estos en `make menuconfig` (Target packages -> Interpreter -> Python -> External modules):
    *   `BR2_PACKAGE_PYTHON_REQUESTS`: Maneja certificados SSL/CA mejor que vendoring manual.
    *   `BR2_PACKAGE_PYTHON_MARIADB` (o `PYTHON_MYSQL_CONNECTOR`): **CRÍTICO**. El conector de MariaDB usa extensiones C (`_mariadb.cpython...so`). **NO SE PUEDE VENDORIZAR** copiando desde Windows/Linux ajeno. Debe compilarse con Buildroot.

## 3. Estructura Final en /opt/synapta/parrot/vendor

```bash
/opt/synapta/parrot/
├── main.py
└── vendor/
    ├── fastapi/
    ├── starlette/
    ├── uvicorn/
    ├── h11/
    ├── click/
    ├── anyio/
    ├── sniffio/
    ├── idna/
    └── typing_extensions.py (o carpeta)
```

## 4. Verificación en Target

Para probar que todo carga correctamente antes de iniciar la app:

```bash
# 1. Cargar Variables de Entorno
set -a; source /etc/synapta/synapta.env; set +a

# 2. Probar Imports
export PYTHONPATH=/opt/synapta/parrot/vendor
python3 -c "import fastapi; import uvicorn; import mariadb; print('Imports OK')"
```

Si falla `mariadb`, verifica que seleccionaste el paquete en Buildroot. Si falla `fastapi`, revisa la carpeta `vendor`.

## 4. Gestión de Ollama (Binario + Modelos)

Ollama es un binario Go estático, no una librería Python.

1.  **Binario**: Descargar `ollama-linux-amd64` y renombrarlo a `ollama`.
    *   Ubicación: `/usr/bin/ollama` (vía paquete Buildroot o script post-build).
    *   Permisos: `chmod +x`.
2.  **Modelo**: Archivo `.gguf` (ej. `ParrotAI.gguf`).
    *   Ubicación: Partición de datos persistente (ej. `/mnt/data/models/`).
    *   **NO** meterlo en la imagen base (rootfs) para no inflarla.
3.  **Interacción**:
    *   Tu script Python (`parrot.py`) usa `requests.post("http://localhost:11434/api/generate", ...)` para hablar con el servicio Ollama que corre en paralelo.

## 5. Resumen del Workflow de Empaquetado

1.  En tu máquina de desarrollo:
    ```bash
    mkdir -p package/python-parrot/source/vendor
    pip install fastapi uvicorn requests -t package/python-parrot/source/vendor --no-deps
    # Limpiar __pycache__ y .dist-info para ahorrar espacio
    find package/python-parrot/source/vendor -name "__pycache__" -exec rm -rf {} +
    ```
2.  En `python-parrot.mk` (Buildroot):
    Define una regla para copiar todo el contenido de `source/` a `/opt/synapta/parrot` en el target.
