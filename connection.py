import serial

con = serial.Serial(port = '/dev/ttyUSB0',
                    baudrate = 115200,
                    bytesize = serial.EIGHTBITS,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    timeout = 3,
                    xonxoff = False,
                    rtscts = True,
                    dsrdtr = True)
