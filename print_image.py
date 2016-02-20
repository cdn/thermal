from connection import con
from PIL import Image
import sys

if len(sys.argv) < 2:
    print('Provide image path')
    sys.exit(1)

orig = Image.open(sys.argv[1])
orig.convert('L') # grayscale

maxs = 576
if len(sys.argv) > 2:
    maxs = int(sys.argv[2])
orig.thumbnail((maxs, maxs), Image.NEAREST)
gs = Image.new('L', orig.size, (255))
gs.paste(orig)

bw = gs.point(lambda x: 0 if x < 128 else 255, '1')
bw.show()

# PREVIEW ONLY?
#sys.exit()

px = bw.load()
print('Printing {} lines of {} columns'.format(bw.size[1], bw.size[0]))
for y in range(bw.size[1]):
    con.write(b'\x11')
    for i in range(72):
        p = 0
        for j in range(8):
            p *= 2
            if i*8+j < bw.size[0] and px[i*8+j,y] == 0:
                p += 1
        con.write(bytes([p]))
