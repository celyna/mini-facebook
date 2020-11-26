import json
import socket
import datetime

from inspect import cleandoc
from thread import *

HOST = '10.0.0.4'
PORT = 4090

clients = { 
	'sid': {
		'password': 'bang',
		'isOnline': False,
		'connection': None,
		'newpost': 0,
		'queue': [],
		'fqueue': [],
		'friends': [],
		'timeline': [],
	}, 
	'user': {
		'password': 'pass',
		'isOnline': False,
		'connection': None,
		'newpost': 0,
		'queue': [],
		'fqueue': [],
		'friends': [],
		'timeline': [],
	},
	'man': {
		'password': 'man',
		'isOnline': False,
		'connection': None,
		'newpost': 0,
		'queue': [],
		'fqueue': [],
		'friends': [],
		'timeline': [],
	} 
}

def timestamp():
	time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
	return time[:-4]

def client_thread(conn):
	try:
		conn.send('Log in, friend!\n')
		conn.send('Username: ')
		usr = conn.recv(1024)
		conn.send('Password: ')
		pswd = conn.recv(1024)

		if usr not in clients or clients[usr]['password'] != pswd:
			conn.send('Username/Password invalid.\n')
			conn.close()
		
		clients[usr]['isOnline'] = True;
		clients[usr]['connection'] = conn;
		
		options = cleandoc("""
		Choose an action:
		1. Send Private Message | 5. Post Status (coming soon)
		2. Send Global Message  | 6. View Timeline (coming soon)
		3. View Messages        | 7. Change Password
		4. Friend Options       | 8. Logout
		""")
	
		foptions = cleandoc("""
		Choose an action:
		1. View Friends
		2. Add Friend
		3. Remove Friend
		4. View Friend Requests
		5. Exit Friend Options
		""")

		frqoptions = cleandoc("""
		Choose an action:
		1. Accept Friend Request
		2. Reject Friend Request
		3. Decide Later
		""")

		soptions = cleandoc("""
		Choose an action
		1. Yes, I would like to post this status
		2. No, I would like to post something else
		3. No, I do not want to post a status
		""")

		conn.send(options + "\n\n")
		conn.send('{} unread messages\n'.format(len(clients[usr]['queue'])))
		conn.send('{} pending friend requests\n'.format(len(clients[usr]['fqueue'])))
		conn.send('{} new posts on your timeline\n\n'.format(clients[usr]['newpost']))

		while 1:
			data = conn.recv(1024)
			if not data:
				conn.send('Failed to interpret, retry?')
				continue
			
			if data == '1': #private message
				conn.send('Target: ')
				target = conn.recv(1024)
				conn.send('Message: ')
				msg = conn.recv(1024)
				msg = msg + '\n'
			
				if clients[target]['isOnline']:
					conn.send('Message sent!\n\n')
					clients[target]['connection'].send('{}: {}'.format(usr, msg))
					clients[target]['connection'].send(options)
				else:
					conn.send('Target is offline and will receive this message later.\n\n')
					clients[target]['queue'].append({'from': usr, 'message': msg})

			if data == '2': #global message
				conn.send('Message: ')
				msg = conn.recv(1024)
				msg = msg + '\n'
				for usrs in clients:
					if clients[usrs]['isOnline']:
						clients[usrs]['connection'].send('{}: {}'.format(usr, msg))
						clients[usrs]['connection'].send(options)
				
				conn.send('Global message sent!')
			
			if data == '3': #view messages
				
				for message in clients[usr]['queue']:
					conn.send('{}: {}'.format(message['from'], message['message']))
				
				del clients[usr]['queue'][:]
			
			if data == '4': #friend options
				conn.send(foptions + "\n\n")

				while 1:
					fdata = conn.recv(1024)
					if fdata == '1': #view friends
						for f in clients[usr]['friends']:
							conn.send(f + "\n")

					if fdata == '2': #add friend
						conn.send("User to add: ")
						ftoadd = conn.recv(1024)
						if ftoadd not in clients:
							conn.send("User does not exist \n")
						elif usr in clients[ftoadd]['friends']:
							conn.send("User is already a friend")
						else:
							clients[ftoadd]['fqueue'].append(usr)

					if fdata == '3': #remove friend
						conn.send("List of friends: ")
						for f in clients[usr]['friends']:
							conn.send(f + "\n")
						
						conn.send("Chose friend to remove: ")
						rfriend = conn.recv(1024)
						
						if rfriend not in clients[usr]['friends']:
							conn.send("Invalid Choice \n")
						else:
							clients[usr]['friends'].remove(rfriend)
							clients[rfriend]['friends'].remove(usr)

					if fdata == '4': #view friend requests
						for frq in clients[usr]['fqueue']:
							conn.send(frq + ' wants to be friends\n')
							conn.send(frqoptions + '\n\n')
							frqoption = conn.recv(1024)

							if frqoption == '1': #accept friend request
								if frq in clients[usr]['friends']:
									conn.send(frq + " is already a friend \n")
									clients[usr]['fqueue'].remove(frq)
								else:
									clients[usr]['friends'].append(frq)
									clients[frq]['friends'].append(usr)
									clients[usr]['fqueue'].remove(frq)
		
							if frqoption == '2': #reject friend request
								if frq in clients[usr]['friends']:
									clients[usr]['friends'].remove(frq)
								
								clients[usr]['fqueue'].remove(frq)

							if frqoption == '3': #decide later
								pass		

					if fdata == '5': #exit friend options
						conn.send("Exiting friend options... \n")
						break
					
					conn.send("\n\n" + foptions + "\n\n")

			if data == '5': #post status
				while 1:
					conn.send("Enter status to post: ")
					status = conn.recv(1024)
					conn.send(soptions + '\n\n')
					confirm = conn.recv(1024)
					
					if confirm == '1': #post this status
						time = timestamp()
						clients[usr]['timeline'].append({'time': time, 'user': usr, 'status': status})
						for f in clients[usr]['friends']:
							clients[f]['timeline'].append({'time': time, 'user': usr, 'status': status})
							clients[f]['newpost'] += 1
						break
					
					if confirm == '2':
						pass

					if confirm == '3':
						break
					
			if data == '6': #view timeline
				for post in clients[usr]['timeline']:
					conn.send('{} {}: {}'.format(post['time'], post['user'], post['status']) + '\n')
				
				clients[usr]['newpost'] = 0	
				
			if data == '7': #change password
				conn.send('Old Password: ')
				oldPswd = conn.recv(1024)
				conn.send('New Password: ')
				newPswd = conn.recv(1024)
				
				if oldPswd == clients[usr]['password']:
					clients[usr]['password'] = newPswd
					conn.send('Password changed.\n')
				else:
					conn.send('Old passwords do not match.')
			if data == '8': #logout
				clients[usr]['isOnline'] = False
				conn.send('Logging out...\n')
				conn.close()
		
			conn.send('\n\n' + options + "\n\n")
			conn.send('{} unread messages\n'.format(len(clients[usr]['queue'])))
			conn.send('{} pending friend requests\n'.format(len(clients[usr]['fqueue'])))
			conn.send('{} new posts on your timeline\n\n'.format(clients[usr]['newpost']))
	except:
		print('Client disconnected')

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