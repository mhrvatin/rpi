1. Set correct date `sudo date -s 'yyyy-mm-dd hh:MM:ss'`
2. Update wifi credentials `sudo vim /etc/wpa_supplicant/wpa_supplicant.conf`
3. Connect to inet `wpa_cli -i wlan0 reconfigure`
4. Update package source
  * `sudo vim /etc/apt/sources.list.d/raspi.list`
  * `sudo vim /etc/apt/sources.list`
5. Update certificates `sudo apt update && sudo apt install ca-certificates`
6. Clone this repo
7. Copy files to `~` and update secrets
