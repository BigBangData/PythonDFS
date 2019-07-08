#! /usr/bin/env python3

# Client-side user authentication functions


# modules
import re
import hashlib 

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
		if auth_status == 'Correct username.':
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
					auth_status = 'Correct username.'
					continue
				else:
					print('Wrong username. You have ' +str(3-i) + ' attempts left.')
					continue 
			elif i == 2:
				if sum(username_auth) > 0:
					auth_status = 'Correct username.'
					continue
				else:
					print('Wrong username. You have ' +str(3-i) + ' attempt left.')
					continue 				
			else:
				if sum(username_auth) > 0:
					auth_status = 'Correct username.'
					continue
				else:
					print('Wrong username. You have no more attempts.\nExiting now....')
					continue
	
	# authenticate password 
	# get the index of the user in the auth_dict to check password in that index
	user_index = sum(username_auth)

	# re-initialize auth status
	auth_status = ''
	for i in range(0, 4):
		if auth_status == 'Existing password.':
			# pass authentication 
			pass
			
		else:
			# get password
			password = input('password: ')
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
					auth_status = 'Existing password.'
					continue
				else:
					print('Wrong password. You have ' +str(3-i) + ' attempts left.')
					continue 
			elif i == 2:
				if sum(password_auth) > 0:
					auth_status = 'Existing password.'
					continue
				else:
					print('Wrong password. You have ' +str(3-i) + ' attempt left.')
					continue 				
			else:
				if sum(password_auth) > 0:
					auth_status = 'Existing password.'
					continue
				else:
					print('Wrong password. You have no more attempts.\nExiting now....')
					sys.exit()
					
	# Check that specific user used that password (auth username:password combination)

	# get the index of the password in the auth_dict
	pass_index = sum(password_auth)
	
	if user_index == pass_index:
		pass 
	else:
		print('Wrong password. You have no more attempts.\nExiting now....')
		sys.exit()		
	
	# Final auth after passing all checks
	print('Authorization Granted.')					
	global final_authorization
	final_authorization = (username, password)
	return final_authorization

	
	
authenticate()