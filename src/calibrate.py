import serial
import time
from pynput import keyboard

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=460800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
print("enter channel number then press return")
read = True
channel = int(input()) -1

get_pos = serial.to_bytes([0x0A,0x04])
header = serial.to_bytes([0x00,0x00,0x00])
set_count = serial.to_bytes([0x09,0x04,0x06]) + header
encoder_count = serial.to_bytes([0x00,0x00,0x00,0x00])

def get_position(channel):
    ser.write(serial.to_bytes(get_pos + channel.to_bytes(1, 'little', signed =True) + header))
    return(int.from_bytes(ser.read(12)[8:], byteorder='little', signed=True))


while(True):
    with keyboard.Events() as events:
        # Block at most one second
        event = events.get(0.2)
        if event is None:
            print(get_position(channel))
        else:
            if event.key == keyboard.Key.esc:
                print("wrote 0")
                ser.write(set_count + channel.to_bytes(2, 'little', signed =True) + encoder_count)
                time.sleep(0.5)
                print(get_position(channel))
                time.sleep(0.5)
                print(get_position(channel))
                print("done")
                break
            

                
            

