#! /usr/bin/env python3

"""
Distributed File System
Client
Marcelo Sanches
Jan 2019
"""

# DFC

# modules
import re 
import os
import sys
import glob
import time
import pickle
import socket
import hashlib 

# check argument to open dfc.conf 
def check_args():

	# error handling no argument 
	if len(sys.argv) != 2:
		print("ERROR: Must supply an argument \nUSAGE: py dfc.py dfc.conf")
		sys.exit()

	# error handling argument passed 
	elif sys.argv[1].lower() != 'dfc.conf':
		print("ERROR: Must supply a valid argument \nUSAGE: py dfc.py dfc.conf")
		sys.exit()
		
	# error if there is no dfc.conf file
	elif os.path.isfile(sys.argv[1]) != True:
		print("ERROR: dfc.conf not found.")
		sys.exit()	
	
	# if no error, return dfc.conf 
	else:
		return sys.argv[1]


# params for user auth from dfc.conf
def user_auth():
	
	# get usernames
	fh = open('dfc.conf', mode='r', encoding='cp1252')
	users=re.findall(r'Username: .*', fh.read())
	usernames=list()
	for i in range(0, len(users)):
		usernames.append(str(users[i]).split()[1])
	fh.close()
		
	# get passwords 
	fh = open('dfc.conf', mode='r', encoding='cp1252')
	passes=re.findall(r'Password: .*', fh.read())
	passwords=list()
	for i in range(0, len(passes)):
		passwords.append(str(passes[i]).split()[1])
	fh.close()

	# dict with usernames:passwords 
	global auth_dict 
	auth_dict = {}
	for i in range(0, len(users)):
		entry={usernames[i]:passwords[i]}
		auth_dict.update(entry)
	
	return auth_dict

# client-side auth
def authenticate():
	
	# config params
	user_auth()
	
	# authenticate username
	
	# initialize an auth status 
	auth_status = ''
	
	# give user 4 attempts
	for i in range(0, 4):
		if auth_status == 'Valid username.':
			# go to password auth 
			pass
		
		else:
			# get username 
			username = input('username: ')
		
			# initialize username auth 
			username_auth = []
			ct = 0
			for key, value in auth_dict.items():
				ct += 1
				if username == key:
					# get specific username index in dictionary 
					username_auth.append(ct)
				else:
					username_auth.append(0)
							
			if i < 2:
				if sum(username_auth) > 0:
					auth_status = 'Valid username.'
					continue
				else:
					print('Username does not exist. You have ' +str(3-i) + ' attempts left.')
					continue 
			elif i == 2:
				if sum(username_auth) > 0:
					auth_status = 'Valid username.'
					continue
				else:
					print('Username does not exist. You have ' +str(3-i) + ' attempt left.')
					continue 				
			else:
				if sum(username_auth) > 0:
					auth_status = 'Valid username.'
					continue
				else:
					print('Username does not exist. You have no more attempts.\nExiting now....')
					sys.exit()
	
	# authenticate password 
	# get the index of the user in the auth_dict to check password in that index
	user_index = sum(username_auth)

	# re-initialize auth status
	auth_status = ''
	for i in range(0, 4):
		if auth_status == 'Valid password.':
			# pass authentication 
			pass
			
		else:
			# get password
			password = input('password: ')
			# hash 
			hash=hashlib.md5()
			hash.update(password.encode())
			password = hash.hexdigest()
			
			# initialize password auth 			
			password_auth = []
			ct = 0
			for key, value in auth_dict.items():
				ct += 1
				if password == value:
					password_auth.append(ct)
				else:
					password_auth.append(0)
			
			if i < 2:
				if sum(password_auth) > 0:
					# check that index of password matches user index
					if user_index == sum(password_auth):
						auth_status = 'Valid password.'
						continue
					else:
						print('Wrong password. You have ' +str(3-i) + ' attempts left.')
						continue
				else:
					print('Wrong password. You have ' +str(3-i) + ' attempts left.')
					continue
			elif i == 2:
				if sum(password_auth) > 0:
					if user_index == sum(password_auth):
						auth_status = 'Valid password.'
						continue
					else:
						print('Wrong password. You have ' +str(3-i) + ' attempt left.')
						continue 				
				else:
					print('Wrong password. You have ' +str(3-i) + ' attempt left.')
					continue 
			else:
				if user_index == sum(password_auth):
					auth_status = 'Valid password.'
					continue
				else:
					print('Wrong password. You have no more attempts.\nExiting now....')
					sys.exit()
					
	# Final auth after passing all checks
	print('Authorization Granted.')					
	global final_authorization
	final_authorization = (username, password)
	return final_authorization

	
# config params for server
def server_conf():	

	# open config file 
	fh = open('dfc.conf', mode='r', encoding='cp1252')
	params = re.findall(r'DFS.*', fh.read())

	# get server names 
	s_names = list()
	for i in range(0, len(params)):
		s_names.append(str(params[i]).split()[1].split(":")[0])
	
	# get server ports 
	s_ports = list()
	for i in range(0, len(params)):
		s_ports.append(str(params[i]).split()[1].split(":")[1])

	# dict with server names
	s_names_dict = {}
	for i in range(0, len(params)):
		entry={'server' +str(i+1):s_names[i]}
		s_names_dict.update(entry)
		
	# dict with server ports
	s_ports_dict = {}
	for i in range(0, len(params)):
		entry={'server' +str(i+1):s_ports[i]}
		s_ports_dict.update(entry)
	
	# lists of (sever name, server port) lists
	global server_list
	server_list = list()
	ct = 0
	for i in range(0, len(params)):
		ct += 1
		server_list.append((s_names_dict['server' +str(ct)],\
							int(s_ports_dict['server' + str(ct)])))
	return server_list

	
# split a file given a chunk size 
def split_files(filename, chunksize):

	# create chunks 
	with open(filename + '.txt', 'rb') as bytefile:
		content = bytearray(os.path.getsize(filename + '.txt'))
		bytefile.readinto(content)
		
		for count, i in enumerate(range(0, len(content), chunksize)):
			with open(filename + '_' + str(count+1) + '.txt.', 'wb') as fh:
				fh.write(content[i: i + chunksize])

				
# determine server location for chunk pairs
def chunk_pairs(filename):
		
	# group chunks in paired lists							# per table:
	pair1 = [filename +'_1.txt', filename +'_2.txt']    	# 1,2
	pair2 = [filename +'_2.txt', filename +'_3.txt'] 		# 2,3
	pair3 = [filename +'_3.txt', filename +'_4.txt']		# 3,4 
	pair4 = [filename +'_4.txt', filename +'_1.txt']		# 4,1

	# md5 hash value of file 

	hash=hashlib.md5()
	with open(filename +'.txt', 'rb') as fh:
		buffer = fh.read()
		hash.update(buffer)
		
		# molulus determines server pairs
		storeval = int(hash.hexdigest(), 16) % 4

	# server pairs depending on modulus
	if storeval == 0:
		dfs1 = pair1
		dfs2 = pair2
		dfs3 = pair3
		dfs4 = pair4
	elif storeval == 1:
		dfs1 = pair4
		dfs2 = pair1
		dfs3 = pair2
		dfs4 = pair3
	elif storeval == 2:
		dfs1 = pair3
		dfs2 = pair4
		dfs3 = pair1
		dfs4 = pair2
	else:
		dfs1 = pair2
		dfs2 = pair3
		dfs3 = pair4
		dfs4 = pair1
	
	return dfs1, dfs2, dfs3, dfs4 
	

# get command from user
def get_command():

	global command
	command = ''
	for i in range(0, 4):
		if command != '':
			return command
			break
		else:
			comm = input('Please specify a command [get, list, put]: ')
			if i < 2:
				if comm.lower() == 'get':
					command = 'get'
					continue
				elif comm.lower() == 'list':
					command = 'list'
					continue
				elif comm.lower() == 'put':
					command = 'put'
					continue
				else:
					print('There is no such command. You have ' +str(3-i) + ' attempts left.')
					continue
			elif i == 2:
				if comm.lower() == 'get':
					command = 'get'
					continue
				elif comm.lower() == 'list':
					command = 'list'
					continue
				elif comm.lower() == 'put':
					command = 'put'
					continue
				else:
					print('There is no such command. You have ' +str(3-i) + ' attempt left.')
					continue
			else:
				print('There is no such command. You have no more attempts.\nExiting now....')
				sys.exit()

# get a file name from user				
def get_filename():
	for i in range(0, 2):
		if i == 0:
			txtfiles = []
			print('Current files: ')
			print('-' * 15)
			for file in glob.glob("*.txt"):
				txtfiles.append(file)
				print(file.split(".")[0])
			print('\n')
			filename = input('Please specify a file: ')
			
			# check if file exists
			try:
				statinfo = os.stat(filename + '.txt')
				break
			except FileNotFoundError:
				print('There is no such file in the directory.\nPlease try again.\n')
				continue 
		else:
			txtfiles = []
			print('Current files: ')
			print('-' * 15)
			for file in glob.glob("*.txt"):
				txtfiles.append(file)
				print(file.split(".")[0])
			print('\n')
			filename = input('Please specify a file: ')
			
			# check if file exists
			try:
				statinfo = os.stat(filename + '.txt')
			except FileNotFoundError:
				print('There is no such file in the directory.\nExiting now...')
				sys.exit()
	
	global filename_statinfo
	filename_statinfo = (filename, statinfo)
	return filename_statinfo


	
# define client socket connection
def client():
	
	# authenticate with client ----------------------------
	authenticate()
	username = final_authorization[0]
	password = final_authorization[1]
	
	# connect to servers ----------------------------------
	
	# config params for servers 
	server_conf()

	# DFS1 
	try:
		client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket1.connect(server_list[0])
		status1 = ('Connected to server', 'DFS1')
		print(status1[0], status1[1])
		time.sleep(1)
	except ConnectionRefusedError:
		status1 = ('Could not connect to server', 'DFS1')
		print(status1[0], status1[1])
		
	# DFS2
	try:
		client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket2.connect(server_list[1])
		status2 = ('Connected to server', 'DFS2')
		print(status2[0], status2[1])
		time.sleep(1)
	except ConnectionRefusedError:
		status2 = ('Could not connect to server', 'DFS2')
		print(status2[0], status2[1])
		
	# DFS3
	try:
		client_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket3.connect(server_list[2])
		status3 = ('Connected to server', 'DFS3')
		print(status3[0], status3[1])
		time.sleep(1)
	except ConnectionRefusedError:
		status3 = ('Could not connect to server', 'DFS3')
		print(status3[0], status3[1])
		
	# DFS4
	try:
		client_socket4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket4.connect(server_list[3])
		status4 = ('Connected to server', 'DFS4')
		print(status4[0], status4[1])
		time.sleep(1)
	except ConnectionRefusedError:
		status4 = ('Could not connect to server', 'DFS4')
		print(status4[0], status4[1])	


	# if all servers are down, exit client 
	if status1[0] == 'Could not connect to server' and status2[0] == 'Could not connect to server' \
		and status3[0] == 'Could not connect to server' and status4[0] == 'Could not connect to server':
		print('All servers are down.\nExiting now...')
		sys.exit()
	else:
		pass
		
	# looping lists: connections, and server names
	conns = (client_socket1, client_socket2, client_socket3, client_socket4)
	DFSS = ('DFS1', 'DFS2', 'DFS3', 'DFS4')	

	
	# authenticate with servers ---------------------------
	
	# send usernames 
	for i in range(0,4):
		try:
			conns[i].send(username.encode())
			time.sleep(1)
		except OSError:
			pass 
	
	# send passwords
	for i in range(0,4):
		try:
			conns[i].send(password.encode())
		except OSError:
			pass 		
				
	# server authorization response
	for i in range(0,4):
		try:
			response = conns[i].recv(1024)
			print('From ' +DFSS[i] +': ' +response.decode())
		except OSError:
			pass

	# get command from user -------------------------------
	get_command()
			
	# PUT
	if command.lower() == 'put':
		for i in range(0,4):
			try:
				conns[i].send(command.encode())
			except OSError:
				pass

		# get a file name from user
		get_filename()
		filename = filename_statinfo[0]
		statinfo = filename_statinfo[1]
					
		# determine size of file and chunks
		filesize = statinfo.st_size	
		buffersize = round(float(filesize)/4) +4
			
		# split files into 4 chunks	
		split_files(filename, buffersize)
				
		# determine chunk pairs and server locations 
		dfs1, dfs2, dfs3, dfs4 = chunk_pairs(filename)
		
		# list to loop through
		dfss = (dfs1, dfs2, dfs3, dfs4)	
		
		# send chunk pairs to servers
		
		# buffer size
		for i in range(0,4):
			try:
				conns[i].send(str(buffersize).encode())
			except OSError:
				pass 
		
		# chunk1 name and data
		for i in range(0,4):
			try:
				conns[i].send(dfss[i][0].encode())
				time.sleep(0.5)
				chunk1=open(dfss[i][0], 'rb').read()
				conns[i].send(chunk1)
				print('\nSending ' +str(dfss[i][0]) +'...\n')
			except OSError:
				pass
		
		# get chunk1 response
		for i in range(0,4):
			try:
				response=conns[i].recv(1024).decode()
				if response == 'Chunk 1 successfully transferred.\n':
					print(DFSS[i] +' Chunk 1 transfer complete.')
				else:
					print(DFSS[i] +' Chunk 1 transfer failed.')
			except OSError:
				pass
			
		# chunk2 name and data 
		for i in range(0,4):
			try:
				conns[i].send(dfss[i][1].encode())
				time.sleep(0.5)				
				chunk2=open(dfss[i][1], 'rb').read()
				conns[i].send(chunk2)
				print('\nSending ' +str(dfss[i][1]) +'...\n')
			except OSError:
				pass
			
		# get chunk2 response
		for i in range(0,4):
			try:
				response=conns[i].recv(1024).decode()
				if response == 'Chunk 2 successfully transferred.\n':
					print(DFSS[i] +' Chunk 2 transfer complete.')
				else:
					print(DFSS[i] +' Chunk 2 transfer incomplete.')
			except OSError:
				pass
			
		# delete chunks from client directory
		os.remove(str(dfs1[0]))
		os.remove(str(dfs1[1]))
		os.remove(str(dfs3[0]))
		os.remove(str(dfs3[1]))
		
		print('\nExiting now...')
		sys.exit()
			
	# LIST
	elif command.lower() == 'list':
			
		# inform servers
		for i in range(0,4):
			try:
				conns[i].send(command.encode())
			except OSError:
				pass
			
		# get list of files, print to console
		for i in range(0,4):		
			try:
				file_names=conns[i].recv(4096).decode()
				# print a table for each server 
				print('\nCurrent ' +DFSS[i] +'\%s files:' %username)
				print('-' * 27)
				print(file_names)
			except OSError:
				pass
		
		# print to console whether a file is reconstructable?
		
		
		# ask if user wants to put a file
		print('\nWould you like to get files, put files, or exit?')
		answer = input('[get, put, exit]: ')
		
		# inform servers
		for i in range(0,4):
			try:
				conns[i].send(answer.encode())
			except OSError:
				pass
		
		# PUT (within LIST)
		if answer.lower() == 'put':

			# get a file name from user
			get_filename()
			filename = filename_statinfo[0]
			statinfo = filename_statinfo[1]
						
			# determine size of file and chunks
			filesize = statinfo.st_size	
			buffersize = round(float(filesize)/4) +4
				
			# split files into 4 chunks	
			split_files(filename, buffersize)
					
			# determine chunk pairs and server locations 
			dfs1, dfs2, dfs3, dfs4 = chunk_pairs(filename)
			
			# list to loop through
			dfss = (dfs1, dfs2, dfs3, dfs4)	
			
			# send chunk pairs to servers
			
			# buffer size
			for i in range(0,4):
				try:
					conns[i].send(str(buffersize).encode())
				except OSError:
					pass 
			
			# chunk1 name and data
			for i in range(0,4):
				try:
					conns[i].send(dfss[i][0].encode())
					time.sleep(0.5)
					chunk1=open(dfss[i][0], 'rb').read()
					conns[i].send(chunk1)
					print('\nSending ' +str(dfss[i][0]) +'...\n')
				except OSError:
					pass
			
			# get chunk1 response
			for i in range(0,4):
				try:
					response=conns[i].recv(1024).decode()
					if response == 'Chunk 1 successfully transferred.\n':
						print(DFSS[i] +' Chunk 1 transfer complete.')
					else:
						print(DFSS[i] +' Chunk 1 transfer failed.')
				except OSError:
					pass
				
			# chunk2 name and data 
			for i in range(0,4):
				try:
					conns[i].send(dfss[i][1].encode())
					time.sleep(0.5)					
					chunk2=open(dfss[i][1], 'rb').read()
					conns[i].send(chunk2)
					print('\nSending ' +str(dfss[i][1]) +'...\n')
				except OSError:
					pass
				
			# get chunk2 response
			for i in range(0,4):
				try:
					response=conns[i].recv(1024).decode()
					if response == 'Chunk 2 successfully transferred.\n':
						print(DFSS[i] +' Chunk 2 transfer complete.')
					else:
						print(DFSS[i] +' Chunk 2 transfer incomplete.')
				except OSError:
					pass
				
			# delete chunks from client directory
			os.remove(str(dfs1[0]))
			os.remove(str(dfs1[1]))
			os.remove(str(dfs3[0]))
			os.remove(str(dfs3[1]))
			
			print('\nExiting now...')
			sys.exit()

			
		# GET (within LIST)			
		elif answer.lower() == 'get':
			# already informed servers! 
			
			# create a subdirectory for user in client
			new_dir_path = os.getcwd() +'\\' +username

			if os.path.isdir(new_dir_path) == False:
				try:  
					os.mkdir(new_dir_path)
					print ("Successfully created the directory %s " % new_dir_path)	
					pass
				except OSError:
					print ("Creation of the directory %s failed" % new_dir_path)
			else:
				pass
			
			# get filename from user
			filename = input('Please specify a file: ')
			
			# send file name to server
			for i in range(0,4):
				try:
					conns[i].send(filename.encode())
				except OSError:
					pass
			
			# receive server answer 
			for i in range(0,4):
				try:
					answer=conns[i].recv(1024).decode()
				except OSError:
					pass
			
			# get buffersize if answer is positive
			for i in range(0,4):
				if answer == 'Server is preparing file transfer...':
					try:
						buffersize=int(conns[i].recv(1024).decode())
					except OSError:
						pass
				else:
					try:
						print(answer)
						sys.exit()
					except OSError:
						pass			
								
			# get names of first batch of chunks 
			chunk_list = []
			for i in range(0,4):
				try:
					name=conns[i].recv(1024).decode()
					chunk_list.append(name)
				except OSError:
					pass
			
			# get first batch of chunks
			# if not all servers are connected limit range to len(chunk_list)
			for i in range(0,len(chunk_list)):
				try:
					chunk1=conns[i].recv(buffersize).decode()
					with open(os.path.join(new_dir_path, chunk_list[i]), 'w') as fh:
						fh.write(chunk1)
					print('File chunks successfully transferred.')
				except OSError:
					pass			
					
			# check that all chunks arrived
			arrived = chunk_list
			num_chunks = len(arrived)
			
			# if not all 4 arrived 
			if num_chunks < 4:

				# send NACK
				NACK = 'Transfer incomplete'
				print(NACK +'\nOnly ' +str(num_chunks) +' out of 4 chunks arrived.')
				for i in range(0,4):
					try:
						conns[i].send(NACK.encode())
					except OSError:
						pass 			

				# get names of second batch
				chunk2_list = []
				for i in range(0,4):
					try:
						name2=conns[i].recv(1024).decode()
						chunk2_list.append(name2)
					except OSError:
						pass
					
				# get second batch
				print('Receiving second batch...')
				for i in range(0,len(chunk2_list)):
					try:
						chunk2=conns[i].recv(buffersize).decode()
						with open(os.path.join(new_dir_path, chunk2_list[i]), 'w') as fh:
							fh.write(chunk2)
						print('File chunks successfully transferred.')
					except OSError:
						pass
				
				# check if the chunks are the correct ones now
				# list all files (list already ordered)
				arrived2 = os.listdir(new_dir_path)

				# subset the 4 chunks of interst (filename)
				arrived2_clean = []
				for i in range(0, len(arrived2)):
					if arrived2[i].split('_')[0] == filename:
						arrived2_clean.append(arrived2[i])
					else:
						pass 
					
				# create integer list
				arrived2_intlist = []
				for i in range(0,len(arrived2_clean)):
					arrived2_intlist.append(int(arrived2_clean[i].split('_')[1].split('.')[0]))

				# compare with [1,2,3,4], if a match
				if arrived2_intlist == [1,2,3,4]:
					print('Chunks 1 through 4 are present.')
					
					# send FIN
					FIN = 'Transfer successful.'
					for i in range(0,4):
						try:
							conns[i].send(FIN.encode())
						except OSError:
							pass 
							
					# concatenate chunks into file
					final_filename = arrived2_clean[0].split('_')[0] +'.txt'	
					
					with open(username +'\\' +final_filename, 'wb') as outfile:		
						for chunk_name in arrived2_clean:
							with open(username +'\\' +chunk_name, 'rb') as infile:
								outfile.write(infile.read())
					
					print('File successfully reconstructed.')
					
					# delete temporary files
					for i in range(0,len(arrived2_clean)):
						try:
							os.remove(str(username +'\\' +arrived2_clean[i]))
						except IndexError:
							pass
						
					print('Exiting now...')
					sys.exit()
					
				else:

					FIN = 'Transfer failed.\nExiting now...'
					for i in range(0,4):
						try:
							conns[i].send(FIN.encode())
						except OSError:
							pass
							
					print(FIN)
					sys.exit()
				
			# else if there are 4 chunks	
			else:
				# which might contain repeated chunks
				print('A total of ' +str(num_chunks) +' chunks arrived.')
				
				# check if the 4 chunks are all different [1 through 4]
				# create a list for numbers
				arrived_ordered = []
				for i in range(0,4):
					arrived_ordered.append(int(arrived[i].split('_')[1].split('.')[0]))
				
				# should be [1,2,3,4]
				arrived_ordered.sort()
			
				# if it is, as expected
				if arrived_ordered == [1,2,3,4]:
				
					print('All four chunks are present.')
					
					# send FIN ACK
					FIN = 'Transfer successful.'
					for i in range(0,4):
						try:
							conns[i].send(FIN.encode())
						except OSError:
							pass 
							
					# concatenate chunks into file
					chunk_list.sort()
					final_filename = chunk_list[0].split('_')[0] +'.txt'	
					
					with open(username +'\\' +final_filename, 'wb') as outfile:		
						for chunk_name in chunk_list:
							with open(username +'\\' +chunk_name, 'rb') as infile:
								outfile.write(infile.read())
					
					print('File successfully reconstructed.')
					
					# delete temporary files
					for i in range(0,4):
						try:
							os.remove(str(username +'\\' +chunk_list[i]))
						except IndexError:
							pass
						
					print('Exiting now...')
					sys.exit()
					
				else:
					# if the ordered list is not [1,2,3,4]
					FIN = 'Transfer failed.\Exiting now...'
					for i in range(0,4):
						try:
							conns[i].send(FIN.encode())
						except OSError:
							pass
							
					print(FIN)
					sys.exit()
					
		# end of GET (within LIST) --------------------------------
			
		elif answer.lower() == 'exit':
			print('Exiting now...')
			sys.exit()
			
		# allow user to try again possibly...
		else:
			print('This method does not exist.\nExiting now...')
			sys.exit()		
			
	# GET ----------------------------------------
	else:
		# inform servers 
		for i in range(0,4):		
			try:
				conns[i].send(command.encode())
			except OSError:
				pass
		
		
		# create a subdirectory for user in client
		new_dir_path = os.getcwd() +'\\' +username

		if os.path.isdir(new_dir_path) == False:
			try:  
				os.mkdir(new_dir_path)
				print ("Successfully created the directory %s " % new_dir_path)	
				pass
			except OSError:
				print ("Creation of the directory %s failed" % new_dir_path)
		else:
			pass
		
		# get filename from user
		filename = input('Please specify a file: ')
		
		# send file name to server
		for i in range(0,4):
			try:
				conns[i].send(filename.encode())
			except OSError:
				pass	
		
		# receive server answer 
		for i in range(0,4):
			try:
				answer=conns[i].recv(1024).decode()
			except OSError:
				pass
		
		# get buffersize if answer is positive
		for i in range(0,4):
			if answer == 'Server is preparing file transfer...':
				try:
					buffersize=int(conns[i].recv(1024).decode())
					print(answer)
				except OSError:
					pass

			else:
				try:
					print(answer)
					sys.exit()
				except OSError:
					pass			
							
		# get names of first batch of chunks 
		chunk_list = []
		for i in range(0,4):
			try:
				name=conns[i].recv(1024).decode()
				chunk_list.append(name)
			except OSError:
				pass
		
		# get first batch of chunks 
		# if not all servers are connected limit range to len(chunk_list)		
		for i in range(0,len(chunk_list)):
			try:
				chunk1=conns[i].recv(buffersize).decode()
				with open(os.path.join(new_dir_path, chunk_list[i]), 'w') as fh:
					fh.write(chunk1)
				print('File chunks successfully transferred.')
			except OSError:
				pass

		# check that all chunks arrived
		arrived = chunk_list
		num_chunks = len(arrived)
		
		# if not all 4 arrived 
		if num_chunks < 4:

			# send NACK
			NACK = 'Transfer incomplete'
			print(NACK +'\nOnly ' +str(num_chunks) +' out of 4 chunks arrived.')
			for i in range(0,4):
				try:
					conns[i].send(NACK.encode())
				except OSError:
					pass 			

			# get names of second batch
			chunk2_list = []
			for i in range(0,4):
				try:
					name2=conns[i].recv(1024).decode()
					chunk2_list.append(name2)
				except OSError:
					pass
				
			# get second batch
			print('Receiving second batch...')
			for i in range(0,len(chunk2_list)):
				try:
					chunk2=conns[i].recv(buffersize).decode()
					with open(os.path.join(new_dir_path, chunk2_list[i]), 'w') as fh:
						fh.write(chunk2)
					print('File chunks successfully transferred.')
				except OSError:
					pass
			
			# check if the chunks are the correct ones now
			# list all files (list already ordered)
			arrived2 = os.listdir(new_dir_path)

			# subset the 4 chunks of interst (filename)
			arrived2_clean = []
			for i in range(0, len(arrived2)):
				if arrived2[i].split('_')[0] == filename:
					arrived2_clean.append(arrived2[i])
				else:
					pass 
					
			# create integer list
			arrived2_intlist = []
			for i in range(0,len(arrived2_clean)):
				arrived2_intlist.append(int(arrived2_clean[i].split('_')[1].split('.')[0]))

			# compare with [1,2,3,4], if a match
			if arrived2_intlist == [1,2,3,4]:
				print('Chunks 1 through 4 are present.')
					
				# send FIN
				FIN = 'Transfer successful.'
				for i in range(0,4):
					try:
						conns[i].send(FIN.encode())
					except OSError:
						pass 
						
				# concatenate chunks into file
				final_filename = arrived2_clean[0].split('_')[0] +'.txt'	
				
				with open(username +'\\' +final_filename, 'wb') as outfile:		
					for chunk_name in arrived2_clean:
						with open(username +'\\' +chunk_name, 'rb') as infile:
							outfile.write(infile.read())
				
				print('File successfully reconstructed.')
				
				# delete temporary files
				for i in range(0,len(arrived2_clean)):
					try:
						os.remove(str(username +'\\' +arrived2_clean[i]))
					except IndexError:
						pass
					
				print('Exiting now...')
				sys.exit()
				
			else:

				FIN = 'Transfer failed.\nExiting now...'
				for i in range(0,4):
					try:
						conns[i].send(FIN.encode())
					except OSError:
						pass
							
				print(FIN)
				sys.exit()
			
		# else if there are 4 chunks	
		else:
			# which might contain repeated chunks
			print('A total of ' +str(num_chunks) +' chunks arrived.')
			
			# check if the 4 chunks are all different [1 through 4]
			# create a list for numbers
			arrived_ordered = []
			for i in range(0,4):
				arrived_ordered.append(int(arrived[i].split('_')[1].split('.')[0]))
			
			# should be [1,2,3,4]
			arrived_ordered.sort()
		
			# if it is, as expected
			if arrived_ordered == [1,2,3,4]:
			
				print('All four chunks are present.')
				
				# send FIN ACK
				FIN = 'Transfer successful.'
				for i in range(0,4):
					try:
						conns[i].send(FIN.encode())
					except OSError:
						pass 
						
				# concatenate chunks into file
				chunk_list.sort()
				final_filename = chunk_list[0].split('_')[0] +'.txt'	
				
				with open(username +'\\' +final_filename, 'wb') as outfile:		
					for chunk_name in chunk_list:
						with open(username +'\\' +chunk_name, 'rb') as infile:
							outfile.write(infile.read())
				
				print('File successfully reconstructed.')
				
				# delete temporary files
				for i in range(0,4):
					try:
						os.remove(str(username +'\\' +chunk_list[i]))
					except IndexError:
						pass
					
				print('Exiting now...')
				sys.exit()
				
			else:
				# if the ordered list is not [1,2,3,4]
				FIN = 'Transfer failed.\Exiting now...'
				for i in range(0,4):
					try:
						conns[i].send(FIN.encode())
					except OSError:
						pass
						
				print(FIN)
				sys.exit()			
							
			
# run client
if __name__=='__main__':
	check_args()
	client()