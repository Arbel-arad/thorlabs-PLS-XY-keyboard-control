import serial
print(hex(256))
a = serial.to_bytes(hex(256))
print ((a)[::-1].from_bytes)