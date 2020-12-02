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
		'queue': [],
	}, 

	'celyna': {
		'password': 'two',
		'isOnline': False,
		'connection': None,
		'queue': [],
	},

	'person': {
		'password': 'three',
		'isOnline': False,
		'connection': None,
		'queue': [],
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
		3. Send a Private Message
		4. Send a Broadcast
		5. View Messages
		""")

		conn.send(options + "\n\n")
		conn.send('{} unread messages\n'.format(len(clients[username]['queue'])))
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

			if data == '3': #sending a private message
				conn.send('Send to: ')
				receivr = conn.recv(1024)
				conn.send('Message: ')
				mssg = conn.recv(1024)
				mssg = mssg + '\n'

				if clients[receivr]['isOnline']:
					conn.send('Message sent succesfully :)\n\n')
					clients[username]['connection'].send('{}: {}'.format(username, mssg))
					clients[username]['connection'].send(options)

				else:
					conn.send('Receiver is currently offline and will receive this message later!\n\n')
					clients[username]['queue'].append({'From': username, 'Message': mssg})

			if data == '4': #broadcast message
				conn.send('Message to all: ')
				mssg = conn.recv(1024)
				mssg = mssg + '\n'
				for users in clients:
					if clients[users]['isOnline']:
						clients[users]['connection'].send('{}: {}'.format(username, mssg))
						clients[users]['connection'].send(options)

				conn.send('Your message was broadcasted !!!')

			if data == '5': #view ur messages
				for mssgs in client[username]['queue']:
					conn.send('{}: {}'.format(mssgs['from'], mssgs['message']))

				del clients[username]['queue'][:]

			conn.send('\n\n' + options + "\n\n")
			conn.send('{} unread message(s)\n'.format(len(clients[username]['queue'])))

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
