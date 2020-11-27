import json
import socket

import time
import getpass

from inspect import cleandoc
from thread import *

HOST = '' # Symbolic name meaning all available interfaces
PORT = 9486

clients = { 
	'user': {
		'password': 'one',
		'isOnline': False,
		'connection': None,
	}, 

	'celyna': {
		'password': 'two',
		'isOnline': False,
		'connection': None,
	},

	'person': {
		'password': 'three',
		'isOnline': False,
		'connection': None,
	} 
}

def client_thread(conn):
	try:
		conn.send('Welcome to the login page:\n')
		conn.send('Enter your username: ')
		username = conn.recv(1024)
		conn.send('Enter your password: ')
		pswd = conn.recv(1024)

		if username not in clients or clients[username]['password'] != pswd:
			conn.send('Incorrect username or password.\n')
			conn.close()
		
		clients[username]['isOnline'] = True;
		clients[username]['connection'] = conn;
		
		options = cleandoc("""
		Choose an item from the menu:
		1. Change Password
		2. Logout
		""")
		conn.send(options + "\n\n")
		while 1:
			data = conn.recv(1024)
			if not data:
				conn.send('There seems to be  an error. Please try again.')
				continue
				
			if data == '1': #change password
				conn.send('Old password: ')
				oldPass = conn.recv(1024)
				conn.send('New password: ')
				newPass = conn.recv(1024)
				
				if oldPass == clients[username]['password']:
					clients[username]['password'] = newPass
					conn.send('Password changed.\n')
				else:
					conn.send('Old passwords do not match.')
			if data == '2': #logout
				clients[username]['isOnline'] = False
				conn.send('Logging out...\n')
				conn.close()
		
			conn.send('\n\n' + options + "\n\n")

	except:
		print('Client has been disconnected.')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)
print('Waiting for clients:{}'.format(PORT))

while 1:
	conn, addr = s.accept()
	print('Connected with {}:{}'.format(addr[0], addr[1]))
	start_new_thread(client_thread, (conn,))

s.close()
