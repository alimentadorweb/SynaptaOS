Synapta OS Server Manual

Installing Synapta OS Server

This manual explains how to install and access the Synapta OS Server from any computer on your local network.

1. Prepare the Installation Media

2. Download the Synapta OS ISO image from the official website.

3. Insert a USB drive (at least 8 GB) into your PC or Mac.

4. Use a tool to burn the ISO file to the USB:

   * Windows: Rufus ([https://rufus.ie](https://rufus.ie))
   * macOS / Linux: dd command or Balena Etcher ([https://etcher.io](https://etcher.io))

Example (Linux/macOS):
sudo dd if=SynaptaOS.iso of=/dev/sdX bs=4M status=progress
sync

2. Boot from the USB

3. Insert the USB drive into the computer where you will install the server.

4. Power on the device and enter the Boot Menu.

5. Select the USB drive as the boot device.

6. Wait for the Synapta OS environment to load.

7. Get the IP Address

Once the system terminal appears, run the following command:
ip a

Find the interface connected to your network (for example, eth0 or wlan0) and note the IP address.

Example output:
inet 192.168.1.25/24 brd 192.168.1.255 scope global eth0

In this case, the server’s IP address is:
192.168.1.25

4. Access from Another Computer

From any computer connected to the same network, open a web browser and go to:
[https://192.168.1.25:8000](https://192.168.1.25:8000)

(Use the IP address you obtained in the previous step.)

This will open the Synapta OS Server Web Interface, where you can manage your modules, local AI, and system configurations.

Additional Notes

* If you see a certificate warning, click “Continue anyway” or “Accept risk.”
  This happens because the server uses a default local certificate.
* For production environments, you can install your own SSL certificate or connect it to a domain.
* By default, server data is stored in:
  /home/david/parrot

Done

Your Synapta OS Server is now running!
You can manage it entirely from your web browser — no Internet connection required.
