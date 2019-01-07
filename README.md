# Raspi-Driver-HPM
Software to read out Honeywell HPM series PM sensor values over UART on Raspberry Pi.

This software is licenced under GPLv3 by [UnravelTEC OG](https://unraveltec.com) (https://unraveltec.com), 2018.

## Prerequsites 

* `raspi-config`
  * interfacing -> serial
    * disable login
    * enable port

* `systemctl disable serial-getty@ttyAMA0.service`

Sensor needs 5V, on UART 3.3V.

### Python 

Install the following python-libraries:

```
aptitude install python-serial
```


## Run program

```
python hpm-series.py
```

## Installation

To install it as a background service run ./install.sh (install dependencies, e.g. via apt, first).

This service writes a file - suited for scraping by prometheus - (onto ramdisk on /run/hpm) and updates it every second.
