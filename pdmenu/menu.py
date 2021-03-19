#!/usr/bin/env python3

import os
import subprocess
import sys
import time

class proc_mgr(object):
	def __init__(self):
		self.pproc = None
		self.midiin = None
		self.midiout = None
		self.last = None

	def setup(self):
		cmd = 'echo -ne "\x1b[?25l"' # turn cursor off
		subprocess.run(cmd, shell=True)
		no=1
		cmd = "ls -1 /dev/snd/midi*"
		mididev = subprocess.check_output(cmd, shell = True ).decode("utf-8").split()
		# symlink all midi devices
		for devname in mididev:
			if not os.path.islink('/dev/midi' + str(no)):
				os.symlink(devname,'/dev/midi' + str(no))
			no += 1
		# set midi options
		if no == 2:
			self.midiin = '1'
			self.midiout = '1'
		elif no == 3:
			self.midiin = '1,2'
			self.midiout = '1,2'

	def main_menu(self):
		diamsg = 'dialog --nook --no-cancel --stdout --no-shadow --menu "select function:" 12 24 4 0 Load 1 Info 2 Halt 3 Exit'
		selection = subprocess.check_output(diamsg, shell = True ).decode("utf-8")
		if selection == '0':
			print()
			self.load_prog()
		elif selection == '1':
			self.show_info()
		elif selection == '2':
			self.turn_off()
		elif selection == '3':
			self.exit_out()
		else:
			self.exit_out()

	def load_prog(self):
		presets = sorted([i for i in os.listdir('./') if i.endswith('.pd')])
		with open('plist', 'w') as filehandle:
			for idx in range(len(presets)):
				filehandle.write('{} {}\n'.format(idx,presets[idx]))
		diamsg = 'dialog --nook --cancel-label "esc" --stdout --no-shadow --menu "select program:" 12 24 {} --file plist'.format(idx)
		selection = int(subprocess.check_output(diamsg, shell = True ).decode("utf-8"))
		if presets[selection] != self.last:
			if self.pproc:
				self.pproc.terminate()
				self.pproc.wait()
				self.pproc = None
			with open("pdout.log","wb") as err:
				self.pproc = subprocess.Popen(['puredata','-nogui','-midiindev',self.midiin,'-midioutdev',self.midiout,'-open',presets[selection]],stderr=err,shell=False)
				self.last = presets[selection]
		diamsg = 'dialog --title {} --exit-label "ok" --no-shadow --tailbox pdout.log 12 24'.format(presets[selection])
		subprocess.run(diamsg, shell = True )
		os.remove("plist")
		self.main_menu()

	def show_info(self):
		cmd = 'hostname -I | awk \'{print "IP:",$1}\' > info.txt'
		subprocess.run(cmd, shell=True)
		cmd = 'uptime | awk \'{print "Load:", $9,$10,$11}\' | tr -d \',\' >> info.txt'
		subprocess.run(cmd, shell=True)
		cmd = r'''free -m | grep Mem: | awk '{printf "Mem: %s/%s MB\n",$3,$2}' >> info.txt'''
		subprocess.run(cmd, shell=True)
		cmd = r'''df -h | grep /dev/root | awk '{printf "Disk: %s/%s\n",$3,$2}' >> info.txt'''
		subprocess.run(cmd, shell=True)
		diamsg = 'dialog --title " Info" --exit-label "ok" --no-shadow --textbox info.txt 12 24'
		subprocess.run(diamsg, shell = True )
		os.remove("info.txt")
		self.main_menu()

	def exit_out(self):
		if self.pproc:
			self.pproc.terminate()
			self.pproc.wait()
			self.pproc = None
		if os.path.exists("pdout.log"):
			os.remove("pdout.log")
		if os.path.exists("plist"):
			os.remove("plist")

	def turn_off(self):
		diamsg = 'dialog --title "Shutdown" --ok-label yes --help-button --help-label esc --no-shadow --msgbox "Are you sure?" 12 24'
		selection = subprocess.call(diamsg, shell = True )
		if selection == 0:
			self.exit_out()
			diamsg = 'dialog --title "Message" --no-shadow --infobox "Unplug the pi after the green LED goes out" 12 24'
			subprocess.run(diamsg, shell = True )
			time.sleep( 3 )
			cmd = "halt"
			subprocess.run(cmd, shell = True )			
		else:
			self.main_menu()
	
	def block_cursor(self):
		cmd = 'echo -ne "\x1b[?25h"' # turn cursor on
		subprocess.run(cmd, shell = True)
				

def main():
	pm = proc_mgr()
	pm.setup()
	pm.main_menu()
	pm.block_cursor()
	exit

if __name__ == '__main__':
    main()


