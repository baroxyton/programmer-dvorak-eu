#!/usr/bin/python
import os
import sys

reboot_recommended = False

if len(sys.argv) == 1:
	print('Error: Please enter an action (help, install, uninstall, backup-recover)')
	exit();
if os.getuid() != 0:
	print('Error: Not executed as root')
	exit();
def INSTALL():
	""
	# Check for (manual) installation of layout and abort if found
	# Create backup
	# Insert keyboard layout
def UNINSTALL():
	""
	# Check for script installation, abort if not found
	# Remove inserted keyboard layouts
def BACKUP_RECOVER():
	""
	# Check for backup file
	# Abort if not found
	# Copy backup file to original
def HELP():
	print('./installer.py help: show this help page')
	print('./installer.py install: install the programmer-dvorak-eu layout globally and create a backup')
	print('./installer.py uninstall: uninstall the programmer-dvorak-eu layout if found')
	print('./installer.py backup-recover: recover the original state of the keyboard files')

if sys.argv[1] == "help":
	HELP()
elif sys.argv[1] == "install":
	INSTALL()
elif sys.argv[1] == "uninstall":
	UNINSTALL()
elif sys.argv[1] == "backup-recover":
	BACKUP_RECOVER()
else:
	print: 'Invalid option ' + sys.argv[1] + '. See ./installer.py help'
