#!/usr/bin/env python3

import curses
import os
import RPi.GPIO as GPIO
import subprocess
import sys
import time

# GPIO define
#RST_PIN        = 25
#CS_PIN         = 8
#DC_PIN         = 24
#RST = 27
#DC = 25
#BL = 24
#bus = 0 
#device = 0 

buttons = {'KEY_UP_PIN': 6, 'KEY_DOWN_PIN': 19, 'KEY_LEFT_PIN': 5,
           'KEY_RIGHT_PIN': 26, 'KEY_PRESS_PIN': 13, 'KEY1_PIN': 21,
           'KEY2_PIN': 20, 'KEY3_PIN': 16 }

#init GPIO
# for P4:
# sudo vi /boot/config.txt
# gpio=6,19,5,26,13,21,20,16=pu
GPIO.setmode(GPIO.BCM) 
for key in buttons:
    GPIO.setup(buttons[key], GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up


if not os.path.islink('/dev/midi1'):
    os.symlink('/dev/snd/midiC1D0','/dev/midi1')
if not os.path.islink('/dev/midi2'):
    os.symlink('/dev/snd/midiC2D0','/dev/midi2')


###### Begin state machine code ######
class ScreenState(object):
    
    name = "state"
    allowed = []
    
    def switch(self, state):
        if state.name in self.allowed:
            #print('Current:',self,' => switching to new state [',state.name,']')
            self.__class__ = state
            return True
        else:
            #print('Current:',self,' => switching to new state [',state.name,'] not possible.')
            return False

    def __str__(self):
        return self.name
    
class Menu(ScreenState):
    name = "menu"
    allowed = ['up','down','load','halt']

class Up(ScreenState):
    name = "up"
    allowed = ['up','down','load','halt','menu']

class Down(ScreenState):
    name = "down"
    allowed = ['up','down','load','halt','menu']

class Load(ScreenState):
    name = "load"
    allowed = ['menu','info','clear']

class Clear(ScreenState):
    name = "clear"
    allowed = ['menu','clear','info']

class Info(ScreenState):
    name = "info"
    allowed = ['load']

class Halt(ScreenState):
    name = "halt"
    allowed = ['menu','off']

class Off(ScreenState):
    name = "off"
    allowed = []

class On(ScreenState):
    name = "on"
    allowed = ['menu']

class Screen(object):
    def __init__(self):
        # State of the screen - default is menu.
        self.state = On()

    def change(self, state):
        """ Change state """
        status = self.state.switch(state)
        return status

    def current(self):
        return self.state

###### End state machine code ######

def rot(presets,num):
    if num > 0:
        for i in range(0,num):
            p = presets.pop(0)
            presets.append(p)
    elif num < 0:
        for i in (range(0,num,-1)):
            p = presets.pop()
            presets.insert(0,p)

def menu(stdscr,scrn,presets):
    if scrn.change(Menu):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        x = 0
        y = 0
        for idx in range(0,12):
            if idx == 6:
                stdscr.addstr(y, x, presets[idx][:-3],  curses.A_UNDERLINE | curses.A_BOLD )
            else:
                #stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, presets[idx][:-3], curses.color_pair(1) )
            y += 1

        stdscr.addstr(1,w-4, "LOAD", curses.color_pair(2))
        stdscr.addstr(h-2,w-4, "HALT", curses.color_pair(2))
        stdscr.refresh()

def up(stdscr,scrn,presets):
    if scrn.change(Up):
        rot(presets,-1)
        menu(stdscr,scrn,presets)

def down(stdscr,scrn,presets):
    if scrn.change(Down):
        rot(presets,1)
        menu(stdscr,scrn,presets)

def key1(stdscr,scrn,presets):
    prev = str(scrn.current())
    if prev == 'load' or prev == 'clear' or prev == 'halt':
        menu(stdscr,scrn, presets)
    elif prev == 'menu' or prev == 'up' or prev =='down':
        if scrn.change(Load):
            prev = str(scrn.current())
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            stdscr.addstr(0,1, presets[6][:-3], curses.A_UNDERLINE | curses.A_BOLD )
            stdscr.addstr(1,w-4, "MENU", curses.color_pair(2))
            stdscr.addstr(h-2,w-4, "INFO", curses.color_pair(2))
            stdscr.refresh()
            subprocess.run(['pkill', '-u', 'root', 'puredata'])
            pdproc = subprocess.Popen(['puredata', '-nogui', '-midiindev', '1', '-midioutdev', '1', '-open', presets[6] ], stdout=subprocess.PIPE, shell=False)
            #pdproc = subprocess.Popen(['puredata', '-nogui', '-midiindev', '1,2', '-midioutdev', '1,2', '-open', presets[6] ], stdout=subprocess.PIPE, shell=False)
            # puredata -nogui -midiindev 1,2 -midioutdev 1,2 -open 
    
def key3(stdscr,scrn,presets):
    prev = str(scrn.current())
    if prev == 'halt':
        if scrn.change(Off):
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            stdscr.addstr(h//2, 1, "Let green LED turn off", curses.A_UNDERLINE | curses.A_BOLD )
            stdscr.refresh()
            time.sleep( 2 )
            subprocess.run(['pkill', '-u', 'root', 'puredata'])
            cmd = "halt"
            out = subprocess.check_output(cmd, shell = True )
    elif prev == 'menu' or prev == 'up' or prev =='down':
        if scrn.change(Halt):
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            cmd = "hostname -I | cut -d' ' -f 1"
            ip = subprocess.check_output(cmd, shell = True ).decode("utf-8")
            stdscr.addstr(1,w-4, "MENU", curses.color_pair(2))
            stdscr.addstr(h//2-1, 1, "Shutdown. Are you sure?", curses.A_UNDERLINE | curses.A_BOLD )
            stdscr.addstr(h-4,1, "IP: " + ip, curses.color_pair(1))
            stdscr.addstr(h-2,w-3, "YES", curses.color_pair(2))
            stdscr.refresh()
    elif prev == 'load':
        if scrn.change(Info):
            subprocess.run(['pkill', '-u', 'root', 'puredata'])
            GPIO.cleanup()       # clean up GPIO on normal exit  
            curses.endwin()
            sys.exit(0)

def main(stdscr):
    presets = sorted([i for i in os.listdir('./') if i.endswith('.pd')])
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    rot(presets,-6) 
    scrn = Screen()
    menu(stdscr,scrn,presets)

    # button interrupts section
    GPIO.add_event_detect(buttons['KEY_UP_PIN'], GPIO.FALLING,callback=lambda x: up(stdscr,scrn,presets), bouncetime=200)
    GPIO.add_event_detect(buttons['KEY_DOWN_PIN'], GPIO.FALLING,callback=lambda x: down(stdscr,scrn,presets), bouncetime=200)
    GPIO.add_event_detect(buttons['KEY1_PIN'], GPIO.FALLING,callback=lambda x: key1(stdscr,scrn,presets), bouncetime=200)
    GPIO.add_event_detect(buttons['KEY3_PIN'], GPIO.FALLING,callback=lambda x: key3(stdscr,scrn,presets), bouncetime=200)

    try:  
        GPIO.wait_for_edge(buttons['KEY_LEFT_PIN'], GPIO.FALLING)  
  
    except KeyboardInterrupt:  
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
    GPIO.cleanup()       # clean up GPIO on normal exit  
    subprocess.run(['pkill', '-u', 'root', 'puredata'])

curses.wrapper(main)
