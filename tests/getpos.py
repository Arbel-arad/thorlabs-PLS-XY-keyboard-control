import serial
import time
from pynput.keyboard import Key, Listener
import pynput

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=460800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
print("enter channel number then press return")
channel = int(input()) -1

get_pos = serial.to_bytes([0x0A, 0x04])
header = serial.to_bytes([0x00, 0x00, 0x00])

payload = serial.to_bytes(get_pos + channel.to_bytes(1, 'little', signed =True) + header)
#print (payload)
while(True):
    ser.write(payload)
    s = ser.read(12)
    print(int.from_bytes(s[8:], byteorder='little', signed=True))