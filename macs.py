#/usr/bin/python3

import subprocess, random
from os import urandom
from sys import argv
from macvendors import macVendors

menu =\
'''  
  MACSwitcher  - (C) Hemanta Pokharel
  https://github.com/hemantapkh

  usage: macs [Option/s] <interface>

  Options:

      -m, --mac <custom mac>     : Set the custom MAC address
      -v, --vendor <vendor>      : Set a MAC address from a vendor
      -r, --random-registered    : Set a random registered MAC
      -R, --random [option/s]    : Set a random MAC address
      
  Random MAC Options:

      --transmission <type>    : Choose transmission type [unicast/multicast]
      --administration <type>  : Choose administrative type [Local/Global]

  [Other Options]

      -h, --help    : Show this help menu and exit
      -s, --show    : Show current MAC address/es with interface/s
'''

def macChanger(interface, newMac):
	'''[Change the MAC address of an interface]

	Args:
		interface ([string]): [Name of an interface to change the address of]
		newMac ([string]): [New MAC address to use]
	'''
	
	oldMac = currentAddr(interface)

	downProc = subprocess.run(f'ifconfig {interface} down', shell=True, capture_output=True)
	if downProc.returncode != 0:
		print(f"Error: '{downProc.stderr.decode('utf-8').rstrip()}'")
		exit()

	changeProc = subprocess.run(f'ifconfig {interface} hw ether {newMac}', shell=True, capture_output=True)
	if changeProc.returncode != 0:
		print(f"Error: '{changeProc.stderr.decode('utf-8').rstrip()}'")
		exit()

	upProc = subprocess.run(f'ifconfig {interface} up', shell=True, capture_output=True)
	if upProc.returncode != 0:
		print(f"Error: '{upProc.stderr.decode('utf-8').rstrip()}'")
		exit()

	currentMac = currentAddr(interface)

	print(f'Old MAC: {oldMac} ({vendorIndetify(oldMac)})')
	print(f'New MAC: {currentMac} ({vendorIndetify(currentMac)})')

def currentAddr(interface):
	'''[Return the current MAC address of an interface]

	Args:
		interface ([string]): [Name of an interface to to get the address of]

	Returns:
		[string]: [MAC address of an interface]
	'''
	
	currentAddrProc = subprocess.run(f'cat /sys/class/net/{interface}/address', shell=True, capture_output=True)
	if currentAddrProc.returncode != 0:
		print(f"Error: '{currentAddrProc.stderr.decode('utf-8').rstrip()}'")
		exit()
	else:
		return currentAddrProc.stdout.decode("utf-8").rstrip()

def elementAfter(lst,element):
	'''[Return the next element after the specified element]

	Args:
		lst ([list]): [List of elements]
		element ([string]): [String after which the next element should be returned]

	Returns:
		[string]: [String after the specified element]
	'''
	
	try:
		elementIndex = lst.index(element)

		elementAfter = lst[elementIndex + 1]
		return elementAfter
	except ValueError:
		return False

def macGenerator(oui='random', transmission='unicast', administration='local'):
	'''[Generate a MAC address]

	Args:
		oui (str, optional): [Provide an OUI of MAC address to be generated]. Defaults to 'random'.
		transmission (str, optional): [Type of transmission]. Defaults to 'unicast'.
		administration (str, optional): [Type of administration]. Defaults to 'local'.

	Returns:
		[string]: [Generated MAC address]
	'''

	if oui == 'random':
		randBytes = [ i for i in urandom(6) ]

		# Transmission type i.e unicast and multicast
		if transmission == 'unicast':
			randBytes[0] &= ~0x01
		elif transmission == 'multicast':
			randBytes[0] |=  0x01

		# Administration type i.e local and global
		if administration in  ['local','laa']:
			randBytes[0] |=  0x02
		elif administration in ['global','universal','uaa']:
			randBytes[0] &= ~0x02
			
		return ''.join([ f'{i:02X}' for i in randBytes ])
		
	else:
		# OUI specified MAC address
		randBytes = [ i for i in urandom(3) ]
		return oui+''.join([ f'{i:02X}' for i in randBytes ])

def vendorIndetify(oui):
	'''[Identify the vendor of the given MAC address]

	Args:
		oui ([string]): [OUI of the MAC address]

	Returns:
		[string]: [Vendor of the MAC address or None if unknown]
	'''

	oui = oui.replace(':','').upper()[:6]
	for key, value in macVendors.items():
		if oui in value[1]:
			return value[0]
		
def macSwitcher():
	# Finding the list of interfaces
	interfaceProc = subprocess.run('ls /sys/class/net', shell=True, capture_output=True)
	if interfaceProc.returncode != 0:
		print(f"Error: '{interfaceProc.stderr.decode('utf-8').rstrip()}'")
		exit()
	else:
		interfaces = interfaceProc.stdout.decode("utf-8").rstrip().split()
	
	# Main menu
	if '-h' in argv or '--help' in argv or (len(argv) <= 2 and argv[-1] not in ['-s','--show']):
		print(menu)

	# Show MAC and interface
	elif '-s' in argv or '--show' in argv:
		for interface in interfaces:
			print(f'{interface}: {currentAddr(interface)}')

	# Unknown interface
	elif argv[-1] not in interfaces:
			print(f"Error: '{argv[-1]}: No such interface'")
			exit()

	# Random MAC switcher
	elif '-R' in argv or '--random' in argv:

		# Default settings for Random MAC changer
		transmission = 'unicast'
		administration = 'local'

		if '--transmission' in argv:
			transmission = elementAfter(argv, '--transmission')
			if transmission.lower() not in ['multicast','unicast']:
				print(f"Error: '{transmission}: Wrong transmission type'")
				exit()

		if '--administration' in argv:
			administration = elementAfter(argv, '--administration')
			if administration.lower() not in ['local','laa','global','universal','uaa']:
				print(f"Error: '{administration}: Wrong administration type'")
				exit()

		macChanger(interface=argv[-1], newMac=macGenerator(transmission=transmission, administration=administration))

	# Custom MAC switcher
	elif '-m' in argv or '--mac' in argv:
		newMac = elementAfter(argv,'-m') or elementAfter(argv,'--mac')
		macChanger(interface=argv[-1], newMac=newMac)

	# Vendor MAC switcher
	elif '-v' in argv or '--vendor' in argv:
		vendor = elementAfter(argv,'-v') or elementAfter(argv,'--vendor')

		if vendor.upper() in macVendors.keys():
			macChanger(interface=argv[-1], newMac=macGenerator(oui=random.choice(macVendors[vendor.upper()][1])))
		else:
			print(f"Error: '{vendor}: No such vendor'")

	# Random Registered MAC Switcher
	elif '-r' in argv or '--random-registered' in argv:

		randomOUI = random.choice(macVendors[random.choice(list(macVendors))][1])
		randomRegMac = macGenerator(oui=randomOUI)

		macChanger(interface=argv[-1], newMac=randomRegMac)

	else:
		print(menu)

macSwitcher()
