from imageprinter import *
from PIL import Image, ImageDraw, ImageFont
import time

for i in range(2):
#for i in range(100):
    img = Image.new('L', (576, 128), 255)
    draw = ImageDraw.Draw(img)
    draw.line([(0, 0), (576, 128)], fill=0, width=2)
    font = ImageFont.truetype('/home/lacop/.fonts/RobotoSlab-Regular.ttf', 20)
    draw.text((20, 50), str(i), font=font)
    queue_bitmap(img.point(lambda x: 0 if x < 128 else 255, '1'))
    time.sleep(0.3)
    #if i % 5 == 0:
    #    time.sleep(2)

finish()