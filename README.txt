===================
README
===================

Project Description
===================

Toy example Python implementation* of a file distribution system with a server-client architecture.

*(for Windows machines as of 1.23.2019, Linux implementation pending)

The DFS folders refer to the Distribution File Servers. There are 4 servers (DFS1, ... DFS4) and one client (DFC).

- RUN (any number of) servers first, then the client:

	py dfs1.py 10001
	py dfs2.py 10002
	py dfs3.py 10003
	py dfs4.py 10004

	py dfc.py dfc.conf

	
- USERS and PASSWORDS:
	
		Alice: Crimson33
		Bob: Velvet77
		Eve: Magellan101
		
	Usernames and passwords can be changed in the configuration files. Changes must adhere to the 
	spacing and syntax found in the conf files and be identical across all conf files (dfs and dfc 
	conf files are identical except for the name).
	
	[A future addition to this project would include a "set username/password" component which 
	would populate the conf files. Note that usernames must be unique.]
	
	Password hashing: the hashing algorithm is md5. If another is desired, all the appropriate 
	hashes must be recomputed in the dfc.py file (CTRL+F 'hashlib').


- COMMANDS:

	[PUT] puts any text files located within the DFC folder into the servers.
	
		PUT splits files into 4 chunks, stores pairs of chunks into each server after hashing 
		file and taking the modulus of the hash to ensure fair distribution, according to 
		the table below. The duplication of files ensures reliability if 1 server is down.

		[File Chunk Pair Locations]
		---------------------------------------------------------------------
		hash mod  	DFS1 		DFS2 		DFS3		DFS4	   
		---------------------------------------------------------------------
		 0 		(1,2) 		(2,3) 		(3,4) 		(4,1) 	   
		 1 		(4,1) 		(1,2) 		(2,3) 		(3,4) 	   
		 2 		(3,4) 		(4,1) 		(1,2) 		(2,3) 	   
		 3 		(2,3) 		(3,4) 		(4,1) 		(1,2) 	   
		---------------------------------------------------------------------	 

		* NB: PUT lists the files within the DFC folder which are available for transfer.

	[GET] gets files from the servers into a user folder within the DFC folder. 
	
		GET joins the 4 chunks into a single file. If a single server is down, this operation can 
		still succeed. If the operation fails, the file is not created and the user gets a 
		'Transfer failed' message.

	[LIST] provides a list of file chunks a user has stored in the server. From the list, a user
	        can glean file names and specify a file to GET. If a user chooses PUT within LIST, 
		the user can determine a file to put as per the * NB above.

			
- NOTES:
			
	* When prompted for a file name, specify file name without the .txt extension.
	* This project is not intended to be an actual example to be followed, just a toy example.
	* There is a lot that can be improved, feel free to suggest improvements.


====================================================================================================================
TESTING
=======

Test DFC-DFS:
	
	- For any user (first cases vs last case differ, as they enter different loops within code).
	
	- For any number of running servers (0 through 4).
	
	- For any combination of servers:
	
		1. BEFORE a user dir exists.
		2. AFTER user dir exists but BEFORE a file dir exists.
		3. AFTER user dir and file dir exist but BEFORE files exist.
		4. AFTER files exist but not all files.
		5. AFTER all dirs and files exist. -->  Reliability of file transfer should be guaranteed 
							 with 1 server down, and in some cases for 2 servers 
							 down (consult table of chunk locations).

	- For any combination/order of commands:
		 - 	The natural order is PUT, LIST, GET.
		 -	Test any order.
		 -	Test GET/PUT within LIST.


====================================================================================================================
PROBLEMS FIXED
==============

Concatention of usernamepassword and buffersizechunkname ---> used timeouts (time.sleep(0.5)).

LIST error: case for when there is a directory (so user has TRIED to put files or actually put files),
			yet there are no files. 

GET error: same case as above, also fixed in GET within LIST.
 
GET within list: had already sent answer ('get'), deleted code block for sending it again (as in GET).

ONLY reconstruct file if all chunks are present, otherwise print/send 'Transfer failed' message.

GET second batch --> reliability w/ server down, +1 file in DFC user dir (check filename).

HASH passwords, store hashes in dfc.conf and dfs.conf.

Client-side authorization grants access to any correct username with any correct password (fixed).

When all servers are down, exit client instead of running through the entire program.

====================================================================================================================
TO DO
=====

Chunks stored and retrieved with every other line empty.

Less exiting out [GOTO equivalent?].

SALT passwords.

ENCRYPT all traffic.

Implement project for Linux machines.

====================================================================================================================

