from connection import con

print('Beeping')
con.write(b'\x1b\x07')

con.write(b'\x1f\x56')
ver = con.read(8).decode()
print('Boot version: {}, Flash version: {}'.format(ver[:4], ver[4:]))

con.write(b'\x1d\x49\x40\x27')
model = con.read(17).decode()
print('Model: {}'.format(model))