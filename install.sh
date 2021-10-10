#!/bin/sh
set -e

CONFIG=/boot/config.txt

# install required packages
sudo apt install -y \
  git \
  python3-pip \
  pigpio \
  ir-keytable
pip3 install \
  pyyaml \
  pyserial \
  pigpio \
  evdev \
  flask \
  adafruit-circuitpython-ads1x15

# clone repository
if ! [ -d "/home/pi/raspeaker" ]; then
  git clone https://github.com/dominikberse/raspeaker.git /home/pi/raspeaker
fi

# disable serial console but enable serial hardware
sudo raspi-config nonint do_serial 2
sudo raspi-config nonint do_i2c 0

# configure service
sudo tee /etc/systemd/system/raspeaker.service > /dev/null <<'EOF'
[Unit]
Description=Raspeaker
After=network.target pigpiod.service

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/raspeaker
# ExecStartPre=+/usr/bin/ir-keytable -p nec
ExecStart=/home/pi/.local/bin/gunicorn --workers 1 --bind 0.0.0.0:5000 main:app

[Install]
WantedBy=multi-user.target
EOF

# enable IR GPIO
# TODO: adjust service file accordingly
if whiptail --yesno "Enable IR diode overlay?" --defaultno 20 60 ; then
  GPIO=$(whiptail --inputbox "To which GPIO is the IR diode connected?" 20 60 "26" 3>&1 1>&2 2>&3)
  if ! [ $? -eq 0 ] ; then
    return 0
  fi
  if ! grep -q "dtoverlay=gpio-ir" $CONFIG ; then
    sudo sed $CONFIG -i -e "\$adtoverlay=gpio-ir,gpio_pin=26"
  else
    sudo sed $CONFIG -i -e "s/^.*dtoverlay=gpio-ir.*/dtoverlay=gpio-ir,gpio_pin=26/"
  fi
fi

# move bluetooth to miniuart-bt
if ! grep -q "dtoverlay=pi3-miniuart-bt" $CONFIG ; then
  sudo sed $CONFIG -i -e "\$adtoverlay=pi3-miniuart-bt"
fi

# append -m option to pigpiod
if ! grep -q -E "^ExecStart=.*\s+-m\b$" /lib/systemd/system/pigpiod.service ; then
  if whiptail --yesno "Disable pigpiod sampling to reduce CPU usage?" 20 60 then
    sudo sed -i "s/^ExecStart=.*/&  -m/" /lib/systemd/system/pigpiod.service
  fi
fi

# adjust ALSA mixer
if whiptail --yesno "Set USB audio as default for alsa mixer?" --defaultno 20 60 ; then
  sudo sed -i "s/^defaults.ctl.card [[:digit:]]\+/defaults.ctl.card 1/" /usr/share/alsa/alsa.conf
  sudo sed -i "s/^defaults.pcm.card [[:digit:]]\+/defaults.pcm.card 1/" /usr/share/alsa/alsa.conf
fi

# enable services
sudo systemctl enable pigpiod
sudo systemctl enable raspeaker

# check raspotify
systemctl list-unit-files --all | grep -q "raspotify"
RASPOTIFY=$?
if [ "$RASPOTIFY" -eq 1 ] ; then
  
  # install raspotify
  if whiptail --yesno "Install raspotify?" 20 60 ; then
    (curl -sL https://dtcooper.github.io/raspotify/install.sh | sh)
    RASPOTIFY=0
    
    # set device name
    DEVNAME=$(whiptail --inputbox "Enter speaker name" 20 60 "raspotify" 3>&1 1>&2 2>&3)
    if [ $? -eq 0 ] ; then
      sudo sed -i "s/^#\?DEVICE_NAME=.*$/DEVICE_NAME=\"$DEVNAME\"/" /etc/default/raspotify
    fi
  fi
fi

if [ "$RASPOTIFY" -eq 0 ] ; then
  if whiptail --yesno "Configure raspotify for read-only filesystem?" 20 60 ; then

    # prepare for possible read-only mode
    sudo systemctl stop raspotify
    sudo sed -i "s/\/var\/cache\/raspotify/\/tmp\/raspotify/g" /lib/systemd/system/raspotify.service
    sudo systemctl daemon-reload

    sudo rm -r /var/cache/raspotify
    sudo ln -s /tmp/raspotify /var/cache/raspotify
    sudo systemctl start raspotify
  fi
fi

# reboot
if whiptail --yesno "Installation complete. System needs to be rebooted.\n\nReboot now?" 20 60 ; then
  sudo reboot
fi
