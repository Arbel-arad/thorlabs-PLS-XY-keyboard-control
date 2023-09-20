import serial
import time
from pynput.keyboard import Key, Listener
import pynput

x_axis = 1
y_axis = 2
x_step = 1000
y_step = 1000

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=460800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

get_pos = serial.to_bytes([0x0A, 0x04])
header = serial.to_bytes([0x00, 0x00, 0x00])
set_pos = serial.to_bytes([0x53, 0x04, 0x06])


def move(channel, there):
    pos = int(there)
    payload = serial.to_bytes(set_pos + header + channel.to_bytes(2,
                              'little', signed=True)) + pos.to_bytes(4, 'little', signed=True)
    ser.write(payload)
    time.sleep(0.1)
    here_x = get_position(x_axis)
    here_y = get_position(y_axis)
    print("     position: X= " + str(here_x) + " Y= " + str(here_y))


def get_position(channel):
    ser.write(serial.to_bytes(
        get_pos + channel.to_bytes(1, 'little', signed=True) + header))
    return (int.from_bytes(ser.read(12)[8:], byteorder='little', signed=True))


def on_press(key):
    # print('{0} pressed'.format(key))
    check_key(key)


def on_release(key):
    if key == Key.esc:
        return False    # Stop listener


def check_key(key):
    global x_axis, y_axis, x_step, y_step
    if key == Key.up:
        move(y_axis, get_position(y_axis) + y_step)
    if key == Key.down:
        move(y_axis, get_position(y_axis) - y_step)
    if key == Key.left:
        move(x_axis, get_position(x_axis) - x_step)
    if key == Key.right:
        move(x_axis, get_position(x_axis) + x_step)
    if key == pynput.keyboard.KeyCode(char="0"):
        move(y_axis, "0")
        move(x_axis, "0")
    if key == pynput.keyboard.KeyCode(char="1"):
        speed = 500
        x_step = speed
        y_step = speed
        print("speed = " + str(speed))
    if key == pynput.keyboard.KeyCode(char="2"):
        speed = 5000
        x_step = speed
        y_step = speed
        print("speed = " + str(speed))
    if key == pynput.keyboard.KeyCode(char="3"):
        speed = 20000
        x_step = speed
        y_step = speed
        print("speed = " + str(speed))


x_pos = get_position(x_axis)
y_pos = get_position(y_axis)
# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
