#/usr/bin/python
"""

"""


import os
import pygame
import struct
import errno
import time


# globals
imagesource1=os.path.join('resources',  'blob1.png')
imagesource2=os.path.join('resources',  'blob2.png')
blob1image= pygame.image.load(imagesource1)
blob2image= pygame.image.load(imagesource2)

#define the classes for game objects

class strobe(pygame.sprite.Sprite):
    ''' displays the moving strobe line and triggers playing sounds'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        self.imagesource=os.path.join('resources',  'strobe.png')
        self.image= pygame.image.load(self.imagesource)
        self.rect=self.image.get_rect()
        self.xpos=0
        self.tempo=1
	self.last=-1

        
    def update(self,tempo):
	self.last = self.xpos
	self.tempo = tempo
        self.xpos += self.tempo
        if self.xpos>=320:
            self.xpos=0
	    self.last=-1
	    #print time.time()
        self.rect.left=self.xpos

        
        
        
class blob(pygame.sprite.Sprite):
    def __init__(self):
        # call the Sprite init method 
        pygame.sprite.Sprite.__init__(self) 
        #load the image resource
        self.image=blob1image
        # get the rectangle describing the loaded image
        self.rect=self.image.get_rect()
        self.state= 0
    def toggle(self):
        self.state += 1
        if self.state > 1 :
            self.state = 0
            self.image=blob1image
        else:
            self.image=blob2image

#def safe_read(fd):
#   try:
#      return os.read(fd, 16)
#   except OSError, exc:
#      if exc.errno == errno.EAGAIN:
#         return None
#      raise


def main():
    """the main game logic"""
#Initialize Everything
    pygame.mixer.pre_init(44100,-16,2, 1024)
    pygame.init()
    pygame.mixer.set_num_channels(12)
    screensize=(320, 240)
    screen = pygame.display.set_mode(screensize)
    pygame.display.set_caption('The Drumby')
    pygame.mouse.set_visible(1)
    sounds=[]
    for item in range(12):
        source=os.path.join('resources',  'soundsquare'+str(item+1)+'.wav')
        sounds.append(pygame.mixer.Sound(source))
    
    # set up a controlling timer for the game
    clock = pygame.time.Clock()
    #create sprite objects and add them to render groups
    spritegroup= pygame.sprite.RenderPlain()
    strobegroup= pygame.sprite.RenderPlain()
    s=strobe()
    s.add(strobegroup)
    cols=[]
    for col in range(16):
        rows=[]
        for row in range(12):
            newblob=blob()
            newblob.rect.top=row*20
            newblob.rect.left=col*20
            rows.append(newblob)
            newblob.add(spritegroup)
        cols.append(rows)
    spritegroup.draw(screen)    

    # control loop

    fmt = 'iiii'
#    fd = os.open("/dev/input/event2", os.O_RDONLY | os.O_NONBLOCK )    
    tempo=1

    while 1:
        clock.tick(50)
#       event = safe_read(fd)
	event=0
        if event:
                (time, type, code, value) =  struct.unpack(fmt,event)
                newval = float(value)
		tempo += newval / 100 
		print tempo
		if tempo < .01:
			tempo = .01

        #check what events Pygame has caught
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
		#os.close(fd)
		print tempo
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #determine row and column
                (mx,  my) = pygame.mouse.get_pos()
                mrow=int(my/20)
                mcol=int(mx/20)
                cols[mcol][mrow].toggle()



    	#refresh the screen by drawing everything again
        strobegroup.update(tempo)
        spritegroup.draw(screen)
        strobegroup.draw(screen)
        pygame.display.flip()
        # time to play sounds? check position of strobe...
        #if not s.xpos%20:
        if s.xpos//20 - s.last//20: 
            #reached a new column
            column=cols[int(s.xpos/20)]
            # list of blobs?  iterate through
            for item in range(12):
                if column[item].state:
                    sounds[item].play()
        # end of playing sequence
                


if __name__ == '__main__': 
    main()
    pygame.quit()
