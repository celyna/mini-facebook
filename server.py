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
		'inGroup': [], #name of groups are stored
	}, 

	'celyna': {
		'password': 'two',
		'isOnline': False,
		'connection': None,
		'queue': [],
		'inGroup': [],
	},

	'person': {
		'password': 'three',
		'isOnline': False,
		'connection': None,
		'queue': [],
		'inGroup': [],
	} 
}

groups = {} #dictionary for groups

def sendMsg(receivr, mssg, username): #function for sending a message directly to another user
	if clients[receivr]['isOnline']:
		clients[receivr]['connection'].send('{}: {}'.format(username, mssg))
		clients[receivr]['connection'].send('\n\n')
	
		conn.send('EndTime')
		endtime = conn.recv(1024)
		print(endtime)

		print('Time taken: ')
		print(float(endtime)-float(starttime))
	else:
		conn.send('Receiver is currently offline and will receive this message later!\n\n')
		clients[receivr]['queue'].append({'From': username, 'Message': mssg})

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
		6. View Groupchats
		""")

		goptions = cleandoc("""
		Choose an item from the menu:
		1. View Available Groups
		2. Send Group Messages
		3. Request to Join a Group
		4. Leave a Group
		5. Return to Main Menu
		""")	
			
		while 1:
			conn.send(options + "\n\n")
			conn.send('{} unread messages\n'.format(len(clients[username]['queue'])))
			conn.send("\n\n")
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
				
				conn.send('BeginTime') #timer for part 3
				starttime = conn.recv(1024)
				
				print(starttime)

				sendMsg(receivr, mssg, username)

			if data == '4': #broadcast message
				conn.send('Message to all: ')
				mssg = conn.recv(1024)
				mssg = mssg + '\n'
				for users in clients:
					if clients[users]['isOnline'] and users != username:
						sendMsg(users, mssg, username)

				conn.send('Your message was broadcasted !!!')

			if data == '5': #view ur messages
				for mssgs in clients[username]['queue']:
					conn.send('{}: {}'.format(mssgs['From'], mssgs['Message']))

				del clients[username]['queue'][:]

			if data == '6': #groupchat setting

				while 1:
					conn.send(goptions + "\n\n")
					groupData = conn.recv(1024)
					if groupData == '1': #view avail groups
						conn.send('These are all the available groups: \n')
						flag = not groups
						for g in groups:
							conn.send(g + "\n")
						
						if flag == True:
							conn.send('Whoops! No groups exist :(' + '\n\n')
					
					if groupData == '2': #send group msg
						conn.send('Choose a group you want to message or enter NEW to create a new group.\n')
						for g in clients[username]['inGroup']:
							conn.send(g + "\n\n")

						invalidGroup = True

						while invalidGroup:
							msgGroup = conn.recv(1024)
							for g in clients[username]['inGroup']:
								if msgGroup == g:
									invalidGroup = False
									break
							if msgGroup == "NEW":
								invalidGroup = False
							
							if invalidGroup:
								conn.send(msgGroup + '\n')
								conn.send("Choose a valid group :( \n")
						
						if msgGroup == "NEW": #create new group
							conn.send('Enter your groupchat name: ')
							groupName = conn.recv(1024)
							clients[username]['inGroup'].append(groupName) #add group name to user's group list
							groupList = [] 
							groups[groupName] = groupList 
							groups[groupName].append(username) #add username to group's member list
							#check if the username was correctly added
							#for g in groups[groupName]:
								#conn.send("Added " + g + " to " + groupName + "\n")
							while 1:
								conn.send('Enter the username you want to add into the groupchat or enter DONE when you are done: ')
								groupMate = conn.recv(1024)
								conn.send('\n')
								if groupMate == "DONE":
									break
								else:
									clients[groupMate]['inGroup'].append(groupName)
									groups[groupName].append(groupMate)
									conn.send(groupMate + ' has been successfully added!' + '\n\n')
									#for g in groups[groupName]:
										#conn.send("Added " + g + " to " + groupName + "\n")

							conn.send('Your groupchat titled ' + groupName + ' is created!\n\n')
							msgGroup = groupName
						#send group message
						conn.send('Message to all group members in ' + msgGroup + ': ')
						mssg = conn.recv(1024)
						mssg = mssg + '\n'
						for m in groups[msgGroup]:
							if m != username:
								sendMsg(m, mssg, username + ' from group ' + msgGroup) 
						
					if groupData == '3': #req to join a group
						#list all groups
						conn.send("Choose which group you would like to join: \n")
						for g in groups:
							conn.send(g + "\n")
						#prompt user to enter which group they wish to join
						invalidGroup = True
						while invalidGroup:
							joinGroup = conn.recv(1024)
							conn.send('\n\n')
							for g in groups:
								if joinGroup == g:
									invalidGroup = False
							if invalidGroup:
								conn.send("Please enter valid group name: \n")
						#add user to that group
						groups[joinGroup].append(username) #add user to group's member list
						clients[username]['inGroup'].append(joinGroup) #add group to user's group list
					
					if groupData == '4': #leave a group
						#list avail groups
						conn.send("Choose which group you would like to leave: \n")
						for g in clients[username]['inGroup']:
							conn.send(g + "\n")
						#prompt user to enter which group they wish to leave
							invalidGroup = True
	                                                while invalidGroup: #while there is not yet a valid group entered
        	                                                leaveGroup = conn.recv(1024) #prompt user for group to leave
                	                                        for g in clients[username]['inGroup']: #for all the user's groups theyre part of
                        	                                        if leaveGroup == g: #if the group they wish to leave is found
										invalidGroup = False #set invalid group bool to false because we have valid group
								if invalidGroup: #if the group entered is invalid
                                                                	conn.send("Please enter valid group name: \n") #output error message and loop again

						#remove user from that group
						conn.send("Leaving " + leaveGroup + "\n")
						try:
							groups[leaveGroup].remove(username)
						except:
							conn.send("Error trying to leave group!")
							break
						clients[username]['inGroup'].remove(leaveGroup)
					if groupData == '5': #go back
						break


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
