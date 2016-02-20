from connection import con

#con.write(b'\x11')
#for i in range(72):
#    con.write(bytes([2**i]))

#for i in range(8):
#i = 2
for i in range(1, 7):
    con.write(b'\x11')
    for _ in range(72):
        con.write(bytes([2**i]))

#i = 7
#con.write(b'\x11')
#for _ in range(72):
#    con.write(bytes([2**i]))
