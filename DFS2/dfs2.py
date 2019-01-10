#! /usr/bin/env python3

"""
Distributed File System
Server 2
Marcelo Sanches
Jan 2019
"""

# modules
import os
import re 
import sys
import time
import socket
import glob
import pickle

# function to check port number assignment
def check_args():

	# error handling argument
	if len(sys.argv) != 2:
		print("ERROR: Must supply port number \nUSAGE: py dfs2.py 10002")
		sys.exit()

	# error handling port number 
	else:
		try:
			if int(sys.argv[1]) != 10002:
				print("ERROR: Port number must be 10002")
				sys.exit()
			else:
				return int(sys.argv[1])
				
		except ValueError:
				print("ERROR: Port number must be a number.")
				sys.exit()

check_args()

# get authentication parameters
def auth_params():

	# use dfs configuration file 
	config_file='dfs.conf'

	# get usernames from config file 
	fh=open(config_file, mode='r', encoding='cp1252')
	users=re.findall(r'Username: .*', fh.read())
	usernames=list()
	for i in range(0, len(users)):
		usernames.append(str(users[i]).split()[1])
	fh.close()

	# get passwords from config file
	fh=open(config_file, mode='r', encoding='cp1252')
	passes=re.findall(r'Password: .*', fh.read())
	passwords=list()
	for i in range(0, len(passes)):
		passwords.append(str(passes[i]).split()[1])
	fh.close()

	# create dict with usernames:passwords 
	global auth_dict 
	auth_dict = {}
	for i in range(0, len(users)):
		entry={usernames[i]:passwords[i]}
		auth_dict.update(entry)

	return auth_dict

# authorize client, given username and password
def client_auth(auth_dict, username, password):
	ct = 0
	auth_status=''
	for key, value in auth_dict.items():
		ct += 1
		if auth_status != '':
			pass
		else:
			# check all users up to last
			if ct < len(auth_dict):
			
				if username == key:
					print('Correct username.')
					
					if password == value:
						print('Correct password.')
						
						auth_status='Authorization Granted.\n'
						print(auth_status)
						conn.send(auth_status.encode())
						pass
					else:
						print('Incorrect password.')
						auth_status = 'Authorization Denied.\n'
						print(auth_status)
						conn.send(auth_status.encode())
						sys.exit()
				else:
					continue
			
			# check last user
			else:
				if username == key:
					print('Correct username.')
							
					if password == value:
						print('Correct password.')
						
						auth_status='Authorization Granted.\n'
						print(auth_status)
						conn.send(auth_status.encode())
						pass
					else:
						print('Incorrect password.')
						auth_status = 'Authorization Denied.\n'
						print(auth_status)
						conn.send(auth_status.encode())
						sys.exit()
				else:
					print('Incorrect username.')
					auth_status = 'Authorization Denied.\n'
					print(auth_status)
					conn.send(auth_status.encode())
					sys.exit()
				
# put files into servers
def put(new_dir_path):
	
	# get size of buffer
	try:
		buffersize = int(conn.recv(2048).decode())
		print('The buffer size is: ' +str(buffersize))
	except ValueError:
		print('The buffer size is not a number. \nExiting now...')
		sys.exit()
		
	# receive chunk 1 name and data 
	name1 = conn.recv(1024).decode()
	chunk1 = conn.recv(buffersize).decode()
	print('Receiving ' +name1 +'...\n')
	
	# create file folder for chunks
	file_folder = name1.split('_')[0]
	new_folder_path = os.getcwd() +'\\' +username +'\\' +file_folder
	
	if os.path.isdir(new_folder_path) == False:
		try:  
			os.mkdir(new_folder_path)
			print ("Successfully created the folder %s " % new_folder_path)	
			pass
		except OSError:
			print ("Creation of the folder %s failed" % new_folder_path)
	else:
		pass
	
	# write chunk1 to file folder
	fh=open(os.path.join(new_folder_path, name1), 'w')
	fh.write(chunk1)
	fh.close()

	# inform client if transfer was successful [check if file exists]			
	exists = new_folder_path +'\\' +name1
	if os.path.isfile(exists) == True:
		response = 'Chunk 1 successfully transferred.\n'
		print(response)
		conn.send(response.encode())
	else:
		response = 'Chunk 1 transfer incomplete.\n'
		print(response)
		conn.send(response.encode())		
	
	# receive chunk 2 name and data 
	name2 = conn.recv(1024).decode()
	chunk2 = conn.recv(buffersize).decode()
	print('Receiving ' +name2 +'...\n')	

	# write chunk2 to file folder
	fh=open(os.path.join(new_folder_path, name2), 'w')
	fh.write(chunk2)
	fh.close()
	
	# inform client if transfer was successful [check if file exists]			
	exists = new_folder_path +'\\' +name2
	if os.path.isfile(exists) == True:
		response = 'Chunk 2 successfully transferred.\n'
		print(response)
		conn.send(response.encode())
	else:
		response = 'Chunk 2 transfer incomplete.\n'
		print(response)
		conn.send(response.encode())						
	
	# close connection after chunks are sent 
	print('Exiting now...')
	sys.exit()


# creates new directory for user
def new_dir(username):

	# define new path
	global new_dir_path
	new_dir_path = os.getcwd() +'\\' +username

	# if path does not exist, create new dir 
	if os.path.isdir(new_dir_path) == False:
		try:  
			os.mkdir(new_dir_path)
			print ("Successfully created the directory %s " % new_dir_path)	
			return new_dir_path
		except OSError:
			print ("Creation of the directory %s failed" % new_dir_path)
	
	# return the dir path if exists, however
	else:
		return new_dir_path
		pass

# command to list files in servers	
def list_files(username):

	# get list of files from subdirectory   
	user_dir = os.getcwd() +'\\' +username
	file_dir_list = next(os.walk(user_dir))[1]
	
	# if user has no file directory (has never sent files)
	if file_dir_list == []:
		response='There are no files yet.'
		print(response)
		conn.send(response.encode())
		
	else:
		# start a list of files
		file_list = []
		for i in range(0, len(file_dir_list)):
			file_dir = file_dir_list[i]
			file_list.append(os.listdir(user_dir +"\\" +file_dir))

		# if user has a file directory yet no files		
		if file_list == [[]]:
			response='There are no files yet.'
			print(response)
			conn.send(response.encode())
		
		else:
			# if user has files, write a txt file with their names 
			with open('filenames.txt', 'w') as fh:
				for list in file_list:
					for file in range(0, len(list)):
						fh.write('%s\n' % list[file])
			
			# send list (the txt file) to client
			file_names=open('filenames.txt', 'rb').read()
			conn.send(file_names)
			print('\nSending file names...\n')	

			# delete the file 
			os.remove('filenames.txt')
		
		
# gets files from servers
def get(username):

	# get file name from client
	filename = conn.recv(1024).decode()
	print('User ' +username +' requested: ' +filename)
	
	# check whether file exists 
	
	# establish paths
	user_dir = os.getcwd() +'\\' +username
	file_dir = os.path.join(user_dir, filename)
	user_dir_filelist = next(os.walk(user_dir))[1]

	# if user directory is empty		
	if user_dir_filelist == []:
		response='Your directory has no files yet.\nExiting now...'
		print('User directory has no file folders.\nExiting now...')
		conn.send(response.encode())
		sys.exit()
		
	# else, if user dir is not empty 
	else:
		# check if there are any file chunks
		# establish list of chunks
		file_dir_chunklist = next(os.walk(file_dir))[2]

		if file_dir_chunklist == []:
			response='You do not have any files in the folder yet.\nExiting now...'
			print('File folder empty.\nExiting now...')
			conn.send(response.encode())
			sys.exit()
		
		# if there are any file chunks...
		else:
			# send chunks ('get', from user's perspective)
			ct = 0
			for chunk in user_dir_filelist:
				ct += 1
				if ct < len(user_dir_filelist):
					# file exists, send file
					if filename == chunk:				
						response='Server is preparing file transfer...'
						print('File found.')
						conn.send(response.encode())
						time.sleep(1)
						break
					else:
						continue
				# if ct == length of list
				else:
					if filename == chunk:
						response='Server is preparing file transfer...'
						print('File found.')
						conn.send(response.encode())
						time.sleep(1)
						pass
					# otherwise, exit 
					else:
						response='No such file exists.\nExiting now...'
						print(response)
						conn.send(response.encode())
						sys.exit()
						
	# establish chunk paths
	name1, name2 = os.listdir(file_dir)
	chunk1 = username +'\\' +chunk +'\\' +name1
	chunk2 = username +'\\' +chunk +'\\' +name2
	
	# send buffersize 
	statinfo=os.stat(chunk1)
	buffersize=round(float(statinfo.st_size)) +4
	conn.send(str(buffersize).encode())
	time.sleep(1)
	
	# send first batch of chunks
	# get numbers of chunks 
	chunk1_num = name1.split('_')[1]
	chunk2_num = name2.split('_')[1]
	
	if chunk1_num == '1.txt' and chunk2_num == '4.txt':
		# send chunk 2 instead
		conn.send(name2.encode())
		time.sleep(0.5)
		chunk2=open(chunk2,'rb').read()
		conn.send(chunk2)
		# name it chunk 1, however
		print('Sending chunk 1: ' +name2)
	else:
		# all other cases send chunk 1
		conn.send(name1.encode())
		time.sleep(0.5)
		chunk1=open(chunk1,'rb').read()
		conn.send(chunk1)
		print('Sending chunk 1: ' +name1)
		
	# get a FIN or a NACK
	FINACK = conn.recv(1024).decode()
	
	# if NACK, send second batch 
	if FINACK == 'Transfer incomplete':
		
		# second batch, reverse rules 
		if chunk1_num == '1.txt' and chunk2_num == '4.txt':
			# send chunk 1 instead
			conn.send(name1.encode())
			time.sleep(0.5)
			chunk1=open(chunk1,'rb').read()
			conn.send(chunk1)
			# name it chunk 2, however 
			print('Sending chunk 2: ' +name1)
		else:
			# all other cases send chunk 2
			conn.send(name2.encode())
			time.sleep(0.5)
			chunk2=open(chunk2,'rb').read()
			conn.send(chunk2)
			print('Sending chunk 2: ' +name2)

			# get actual FIN since previous was NACK
			FIN = conn.recv(1024).decode()
			print(FIN)
		
	# iff FIN, exit (FINACK == 'Transfer successful.')
	else: 
		
		# print and exit 
		print(FINACK +'\nExiting now...')
		
	sys.exit()

	
# RUN DFS -------------------------------------------------	

server_name = '127.0.0.1'
server_port = int(sys.argv[1])
	
# define socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_name, server_port))
server_socket.listen(5)
print('Server listening...')

while True:
	conn, client_address = server_socket.accept()
	print('Connected to Client.')
	
	# get username  
	username = conn.recv(2048)
	username = username.decode()
	print('received username')
	
	# get password 
	password = conn.recv(2048)
	password = password.decode()
	print('received password')
	
	# authorize client
	auth_params()	
	client_auth(auth_dict, username, password)
				
	# create a new directory for user, if none exists 
	new_dir(username)
	
	# receive command from user
	command = conn.recv(1024).decode()
	print('The user requested to ' +command + ' files.')
		
	# PUT 
	if command == 'put':
		put(new_dir_path)
						
	# LIST
	elif command == 'list':
		list_files(username)
		
		# after listing, get further action
		answer = conn.recv(1024).decode()
		print('The user now requests to ' +answer +' files.')

		# PUT within LIST
		if answer == 'put':
			print('Receiving files...')
			put(new_dir_path)

		# GET within LIST 
		elif answer == 'get':
			get(username)
			
		# exit 
		else:
			print('Exiting now...')
			sys.exit()	
			
	# GET
	elif command == 'get':
		get(username)
					
	# handle wrong command  
	else:
		print('Command does not exist.\nExiting now...')
		sys.exit()	

conn.close()