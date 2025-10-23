🧠 Synapta OS Server Manual
🖥️ Instalación del Servidor Synapta OS

Este manual explica cómo instalar y acceder al servidor Synapta OS desde cualquier computadora en la red local.

⚙️ 1. Preparar el medio de instalación

Descarga la imagen ISO de Synapta OS desde el sitio oficial.

Inserta una USB de al menos 8 GB en tu PC o Mac.

Usa una herramienta para grabar la ISO en la USB:

Windows: Rufus
macOS / Linux: comando dd o Balena Etcher

sudo dd if=SynaptaOS.iso of=/dev/sdX bs=4M status=progress
sync

🧩 2. Iniciar desde la USB

Inserta la USB en la computadora donde se instalará el servidor.

Enciende el equipo y entra al menú de arranque (Boot Menu).

Selecciona la USB como dispositivo de arranque.

Espera a que cargue el entorno de Synapta OS.

3. Obtener la dirección IP

Cuando aparezca el terminal del sistema, ejecuta el siguiente comando:
ip a

Busca la interfaz conectada a la red (por ejemplo eth0 o wlan0) y anota la dirección IP.
Ejemplo de salida:

inet 192.168.1.25/24 brd 192.168.1.255 scope global eth0

La dirección IP del servidor en este caso es:

192.168.1.25

🌐 4. Acceder desde otra computadora

https://192.168.1.25:8000

(Usa la IP que obtuviste en el paso anterior.)

Esto abrirá la interfaz web de Synapta OS Server, donde podrás gestionar tus módulos, IA locales, o configuraciones del sistema.

💡 Notas adicionales

Si aparece una advertencia de certificado no confiable, selecciona “Continuar de todos modos” o “Aceptar riesgo”.
Esto ocurre porque el servidor utiliza un certificado local por defecto.

Para producción, puedes instalar tu propio certificado SSL o conectarlo a un dominio.

Por defecto, los datos del servidor se almacenan en /home/david/parrot

🚀 Listo

¡Tu servidor Synapta OS está en funcionamiento!
Puedes administrarlo completamente desde tu navegador sin necesidad de conexión a Internet.
