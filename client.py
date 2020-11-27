from __future__ import print_function

import getpass
import json
import socket

from threading import Timer

'''
Create Socket
''' 
try:
	# create an AF_INET, STREAM socket (TCP)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
except socket.error, msg:
	print ('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
	sys.exit();
print('Socket Created')


'''
Resolve Hostname
'''
HOST = '10.0.0.4'
PORT = 9486

try:
	remote_ip = socket.gethostbyname(HOST)
except socket.gaierror:
	print ( 'Hostname could not be resolved. Exiting ')
	sys.exit()
print ('Ip address of ' + HOST + ' is '  + remote_ip)

'''
Connect to remote server
'''
s.connect((remote_ip , PORT))
print ('Socket Connected to ' + HOST + ' on ip ' + remote_ip)

'''
LOGIN
'''

def login():
	usr = raw_input("Username [%s]: " % getpass.getuser())
	if not user:
		usr = getpass.getuser()

	prompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

	pswd, conf = prompt()
	while pswd != conf:
		print('Wrong password, try again!')
		pswd, conf = prompt()

	return usr, pswd

while 1:
	p, addr = s.recvfrom(1024)
	print(p, end='')
	
	if p == 'done\n':
		break;

	reply = ''
	if 'password' in p and 'Options' not in p:
		reply = getpass.getpass('')
	else:
		reply = raw_input()

	s.send(reply)

s.close()
