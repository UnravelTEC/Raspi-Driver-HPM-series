#!/usr/bin/python
# coding=utf-8
#
# Copyright © 2018 UnravelTEC
# Michael Maier <michael.maier+github@unraveltec.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# If you want to relicense this code under another license, please contact info+github@unraveltec.com.


from __future__ import print_function
import serial, sys, time
import datetime, time
import os
import signal

LOGFILE = "/run/hpm"

ser = serial.Serial()
ser.port = "/dev/serial0"
ser.baudrate = 9600
ser.timeout = 1

ser.open()

def exit_gracefully(a,b):
    print("set sleep")
    sendSimpleCommand("\x68\x01\x02\x95", "Stop Particle Measurement")
    ser.close()
    os.path.isfile(LOGFILE) and os.access(LOGFILE, os.W_OK) and os.remove(LOGFILE)
    print("exit")
    exit(0)

signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def sendSimpleCommand(cmd, description):
  for tried in range(5):
    try:
      ser.write(cmd)
      ret = ser.read(size=2)
    except:
      eprint("serial comm error")
      exit(1)
    if len(ret) < 2:
      eprint("Error: only " + str(len(ret)) + " bytes received")
      continue

    if ord(ret[0]) != 0xA5 or ord(ret[1]) != 0xA5:
      print(description + ": ret should be 0xA5 0xA5, is", hex(ord(ret[0])), hex(ord(ret[1])))
    else:
      return
  eprint(description, "unsuccessful, exit")
  exit(1)


def startMeasurement():
  sendSimpleCommand("\x68\x01\x01\x96", "start measurement")


def stopAutoSend():
  sendSimpleCommand("\x68\x01\x20\x77", "stop auto send")

def readMeasurement():
  try:
      ser.write("\x68\x01\x04\x93")
      ret = ser.read(size=8)
  except:
      exit(1)
  if len(ret) <8:
    eprint("Error: only " + str(len(ret)) + " bytes received")
    exit(1)

  if ord(ret[0]) != 0x40 or ord(ret[1]) != 0x5 or ord(ret[2]) != 0x4:
    eprint("header NOK\n0x40 0x05 0x04")
    for i in range(len(ret)):
      eprint(hex(ord(ret[i])) + ' ',end='')
    eprint('')

  pm25 = ord(ret[3]) * 256 + ord(ret[4])
  pm10 = ord(ret[5]) * 256 + ord(ret[6])
  output_string = 'particulate_matter_ugpm3{{size="pm2.5",sensor="HPM"}} {0}\n'.format(pm25)
  output_string += 'particulate_matter_ugpm3{{size="pm10",sensor="HPM"}} {0}\n'.format(pm10)

  return(output_string)


if __name__ == "__main__":
  print("resetting sensor...")
  ser.flushInput()
  sendSimpleCommand("\x68\x01\x02\x95", "Stop Particle Measurement")
  time.sleep(2)

  stopAutoSend()
  print("starting measurement...")
  startMeasurement()
  stopAutoSend()

  for i in range(15): # throw away first measurements because of internal running average over 10s and fan speed up
    output_string = readMeasurement()
    print(output_string, end='')
    time.sleep(1)

  print("starting logging.")
  while True:
    output_string = readMeasurement()
    logfilehandle = open(LOGFILE, "w",1)
    logfilehandle.write(output_string)
    logfilehandle.close()
    time.sleep(1)
