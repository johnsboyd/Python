#!/usr/bin/env python3

from dialog import Dialog
import os
import shlex
import subprocess
import sys
import time

class proc_mgr(object):
	def __init__(self):
		self.pproc = None
		self.midiin = ''
		self.midiout = ''
		self.last = None
		self.d = Dialog(dialog="dialog")

	def setup(self):
		os.system('setterm -cursor off')
		mididev = sorted([i for i in os.listdir('/dev/snd/') if i.startswith('midi')])
		# symlink all midi devices
		no=1
		for devname in mididev:
			if not os.path.islink('/dev/midi' + str(no)):
				os.symlink('/dev/snd/' + devname,'/dev/midi' + str(no))
			no += 1
		# set midi options
		if no == 2:
			self.midiin = '-midiindev 1'
			self.midiout = '-midioutdev 1'
		elif no == 3:
			self.midiin = '-midiindev 1,2'
			self.midiout = '-midioutdev 1,2'
		else:
			self.midiin = ''
			self.midiout = ''

	def splash(self):
		buttons = 'Up                Ok\n\n\n\n      Synpathi\n\n\n\n\nDown             Esc'
		self.d.infobox(buttons, height=12, width=24, no_shadow=True, no_collapse=True )
		time.sleep( 2 )

	def main_menu(self):
		code, selection = self.d.menu("select function:", height = 12, width = 24,
			choices=[('0','Load'), ('1','Info'), ('2','Halt'), ('3','Exit')],
			no_ok=True, no_cancel=True, no_shadow=True)
		if code == self.d.OK:
			if selection == '0':
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
		preset = []
		[ preset.append((str(len(preset)),i)) for i in os.listdir('./') if i.endswith('.pd') ]
		code, select = self.d.menu("select program:", height = 12, width = 24,
        	choices=preset, no_ok=True, no_cancel=False, no_shadow=True)
		if code == self.d.OK:
			selection=int(select)
			if preset[selection][1] != self.last:
				if self.pproc:
					self.pproc.terminate()
					self.pproc.wait()
					self.pproc = None
				with open("pdout.log","wb") as err:
					cmd = 'puredata -nogui {} {} -open {}'.format(self.midiin, self.midiout, preset[selection][1])
					self.pproc = subprocess.Popen(shlex.split(cmd),stderr=err,shell=False)
					self.last = preset[selection][1]
			self.d.tailbox("pdout.log", height=12, width=24, title=preset[selection][1], exit_label="ok", no_cancel=True, no_shadow=True)
		self.main_menu()

	def show_info(self):
		ipaddress = subprocess.check_output(['hostname', '-I']).decode('utf-8').split(" ")[0]
		load = subprocess.check_output(['uptime']).decode('utf-8').split(":")[-1].replace(',', '').rstrip()
		free = subprocess.check_output(['free','-m']).decode('utf-8').split(":")[1].split()
		dfree = subprocess.check_output(['df','-h']).decode('utf-8').split("/")[2].split()
		info_text = 'IP: {}\nLoad:{}\nMem: {}/{}\nDisk: {}/{}'.format(ipaddress,load,free[1],free[0],dfree[2],dfree[1])
		self.d.msgbox(info_text, height=12, width=24, exit_label="ok", no_cancel=True, no_shadow=True)
		self.main_menu()

	def exit_out(self):
		if self.pproc:
			self.pproc.terminate()
			self.pproc.wait()
			self.pproc = None
		if os.path.exists("pdout.log"):
			os.remove("pdout.log")

	def turn_off(self):
		selection = self.d.msgbox("You can halt, reboot or esc", height=12, width=24, ok_label="halt", help_button=True, help_label=" reboot ", no_shadow=True, title=
"Shutdown")
		if selection == "ok":
			self.exit_out()
			self.d.infobox("Unplug the pi after the green LED goes out", height=12, width=24, title="Message", no_shadow=True )
			time.sleep( 3 )
			cmd = "halt"
			subprocess.run(shlex.split(cmd), shell = False )			
		elif selection == "help":
			self.exit_out()
			self.d.infobox("Rebooting...", height=12, width=24, title="Message", no_shadow=True )
			time.sleep( 2 )
			cmd = "reboot"
			subprocess.run(shlex.split(cmd), shell = False )			
		else:
			self.main_menu()
	
	def block_cursor(self):
		os.system('setterm -cursor on')

def main():
	pm = proc_mgr()
	pm.setup()
	pm.splash()
	pm.main_menu()
	pm.block_cursor()
	sys.exit()

if __name__ == '__main__':
    main()


