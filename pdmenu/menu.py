#!/usr/bin/python

import time
import os

import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

########### SETUP ############
# /dev/snd/midiC1D0 /dev/midi1  
# /dev/snd/midiC2D0 /dev/midi2
if not os.path.islink('/dev/midi1'):
    os.symlink('/dev/snd/midiC1D0','/dev/midi1')
if not os.path.islink('/dev/midi2'):
    os.symlink('/dev/snd/midiC2D0','/dev/midi2')

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
# Initialize library.
disp.begin()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width 
height = disp.height 
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Load default font.
#font = ImageFont.load_default()
font = ImageFont.truetype('FreeSansBold.ttf', 9)

# Input pins:
L_pin = 27 
R_pin = 23 
C_pin = 4 
U_pin = 17 
D_pin = 22 
A_pin = 5 
B_pin = 6 

preset = 0
page = "main" 
pdfiles = sorted([i for i in os.listdir('./') if i.endswith('.pd')])
numpre = len(pdfiles)
pdproc = ''

GPIO.setmode(GPIO.BCM) 
GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

# Clear display.
disp.clear()
disp.display()

# Draw a black filled box to clear the image.
#draw.rectangle((0,0,width,height), outline=0, fill=0)
#disp.image(image)
#disp.display()

cmd = "hostname -I | awk '{print \"IP: \" $1}'"
ip = subprocess.check_output(cmd, shell = True )


########### FUNCTIONS ############

def view(pre):
    global preset
    preset = pre
    draw.rectangle((0,0,width-1,height-1), outline=0, fill=0)
    font = ImageFont.truetype('FreeSansBold.ttf', 9)
    draw.text((104, 0), "[info]", font=font, fill=255)
    row=0
    for x in range(pre-2,pre+3):
        if x == pre:
            font = ImageFont.truetype('FreeSansBold.ttf', 16)
            draw.text((0, row-4), pdfiles[x % numpre][:-3],  font=font, fill=255)
        else:
            font = ImageFont.truetype('FreeSansBold.ttf', 9)
            draw.text((0, row), pdfiles[x % numpre][:-3],  font=font, fill=255)
        row += 13
    draw.text((105, 54), "[halt]", font=font, fill=255)
    disp.image(image)
    disp.display()

def up(channel):
    view((preset - 1) % numpre)

def down(channel):
    view((preset + 1) % numpre)

def pick(channel):
    global pdproc
    if pdproc != '':
        pdproc.terminate()
        pdproc.kill()
    pdproc = subprocess.Popen(['puredata', '-nogui', '-midiindev', '1,2', '-midioutdev', '1,2', '-open', pdfiles[preset] ], stdout=subprocess.PIPE, shell=False)
    # puredata -nogui -midiindev 1,2 -midioutdev 1,2 -open 
    draw.rectangle((0,0,width-1,height-1), outline=1, fill=0)
    font = ImageFont.truetype('FreeSansBold.ttf', 16)
    draw.text((24, 12), "LOADING",  font=font, fill=255)
    draw.text((2, 32), pdfiles[preset][:-3] ,  font=font, fill=255)
    disp.image(image)
    disp.display()
    view(preset)
    

def info(channel):
    global page
    if page == "fin":
        page = "main"
        view(preset)
    elif page == "main":
        cmd = "w | head -1 | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        load = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%smb %.2f%%\", $3,$2,$3*100/$2 }'"
        mem = subprocess.check_output(cmd, shell = True )
        draw.rectangle((0,0,width-1,height-1), outline=0, fill=0)
        page = "info"
        font = ImageFont.truetype('FreeSansBold.ttf', 9)
        draw.text((0, 0), ip, font=font, fill=255)
        draw.text((0, 9), load, font=font, fill=255)
        draw.text((0, 18), mem, font=font, fill=255)
        if pdproc != '':
            draw.text((0,27), "Name: "+pdfiles[preset][:-3], font=font, fill=255)
        draw.text((102, 0), "[back]", font=font, fill=255)
        disp.image(image)
        disp.display()
    elif page == "info":
        page = "main"
        view(preset)
        

def kill(channel):
    global pdproc
    if pdproc != '':
        pdproc.terminate()
        pdproc.kill()
    

def fin(channel):
    global page
    draw.rectangle((0,0,width-1,height-1), outline=0, fill=0)
    if page == "fin":
        draw.text((0, 32), "wait for green light to go off", font=font, fill=255)
        disp.image(image)
        disp.display()
    	if pdproc != '':
            pdproc.terminate()
        cmd = "sudo halt"
        out = subprocess.check_output(cmd, shell = True ) 
    elif page == "main":
        draw.text((102, 0), "[back]", font=font, fill=255)
        draw.text((32, 32), "Are you sure?", font=font, fill=255)
        draw.text((105, 54), "[halt]", font=font, fill=255)
        page = "fin" 
        disp.image(image)
        disp.display()
    elif page == "info":
        page = "main"
        info(B_pin)
    

def main():
    global pdproc
    view(preset)
    GPIO.add_event_detect(U_pin, GPIO.FALLING, callback=up, bouncetime=500)
    GPIO.add_event_detect(D_pin, GPIO.FALLING, callback=down, bouncetime=500)
    GPIO.add_event_detect(C_pin, GPIO.FALLING, callback=pick, bouncetime=700)
    GPIO.add_event_detect(A_pin, GPIO.FALLING, callback=fin, bouncetime=500)
    GPIO.add_event_detect(B_pin, GPIO.FALLING, callback=info, bouncetime=500)
    GPIO.add_event_detect(R_pin, GPIO.FALLING, callback=kill, bouncetime=500)
    try:  
        #GPIO.wait_for_edge(L_pin, GPIO.RISING)  
        GPIO.wait_for_edge(L_pin, GPIO.FALLING)  
  
    except KeyboardInterrupt:  
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
    GPIO.cleanup()       # clean up GPIO on normal exit  
    if pdproc != '':
        pdproc.terminate()
        pdproc.kill()
    draw.rectangle((0,0,width-1,height-1), outline=0, fill=0)
    disp.image(image)
    disp.display()


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main() 
