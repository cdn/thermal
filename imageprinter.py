from connection import con
import sys
import queue, threading
import pygame
import time

pos = -1
def printloop():
    global pos, stopped
    while not stopped:
        it = q.get()
        if it is None:
            break

        # TODO support cutting operation ...
        print('Print img')
        px = it.load()
        for y in range(it.size[1]):
            pos = y
            #con.write(b'\x11')
            for i in range(72):
                p = 0
                for j in range(8):
                    p *= 2
                    if i*8+j < it.size[0] and px[i*8+j,y] == 0:
                        p += 1
                #con.write(bytes([p]))
            time.sleep(0.01)

        pos = -1
        qgui.put('REM')

        q.task_done()
        time.sleep(1)

def finish():
    global stopped
    q.join()
    q.put(None)
    printer.join()
    stopped = True
    renderer.join()

def queue_bitmap(img):
    if img.size[0] != 576:
        sys.stderr.write('Invalid width of input bitmap\n')
        return False
    q.put(img)
    qgui.put(('ADD', img))
    print('Queued img')

def render():
    global stopped
    pygame.init()
    real_screen = pygame.display.set_mode((576//2, 2048//2))
    screen = pygame.Surface((576, 2048))

    imgs = []
    yoff = 0

    fnt = pygame.font.SysFont('monospace', 20)

    while not stopped:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.stderr.write('Aborting')
                stopped = True
                sys.exit(1)
        #add, rem = False, False
        try:
            r = qgui.get_nowait()
            if r == 'REM':
                imgs = imgs[1:]
                #rem = True
            else:
                imgs.append(pygame.image.fromstring(r[1].convert('RGBA').tostring('raw', 'RGBA'), r[1].size, 'RGBA'))
                #add = True
        except queue.Empty:
            pass

        screen.fill((255, 255, 255))
        voff = 0
        for img in imgs:
            screen.blit(img, (0, voff))
            voff += img.get_height()
            pygame.draw.line(screen, (0, 255, 0), (0, voff-1), (576, voff-1))
            pygame.draw.line(screen, (0, 255, 0), (0, voff), (576, voff))

        pygame.draw.line(screen, (255, 0, 0), (0, pos), (576, pos))
        pygame.draw.line(screen, (255, 0, 0), (0, pos+1), (576, pos+1))

        real_screen.blit(pygame.transform.scale(screen, (576//2, 2048//2)), (0, 0))

        pygame.draw.rect(real_screen, (255, 255, 255), (16, 1000, 544, 64))
        lbl = fnt.render('Queue size: {}'.format(len(imgs)), 1, (0, 0, 0))
        real_screen.blit(lbl, (32, 960))

        pygame.display.flip()

q = queue.Queue()
qgui = queue.Queue()
stopped = False

printer = threading.Thread(target=printloop)
printer.start()

renderer = threading.Thread(target=render)
renderer.start()