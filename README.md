
# A Low-Level Python Distributed File System (DFS)

## Project Description

This project was conceived as a proof-of-concept for a low-level implementation of a Python DFS using only 
stdlib modules (i.e. 'socket' for networking) to transfer and store files in a distributed and resilient manner.

This project is an MVP, and as such it does not incorporate all the [design goals of a DFS](https://en.wikipedia.org/wiki/Clustered_file_system#Distributed_file_systems).
This Python DFS is defined here simply as a cluster of servers in a server-client architecture, hosting potentially large text files 
that need to be transferred and stored reliably and securely in a fault-tolerant way. 

Below I demonstrate how to run the Python DFS locally, simulating a distributed cluster. 
A given file is distributed (`PUT <file_name>`) from the DFC (the Client) to four DFS (the Servers) in chunks,
which can be retrieved (`GET <file_name>`) and used to reconstruct the file. 

There's a built-in redundancy in the way the file chunks are stored in the servers, ensuring that if a given server fails,
the file can still be reconstructed. Traffic optimization is achieved by not sending any redundant file chunks unless necessary.
Some security is implemented via authentication, and storage of password hashes. 


## Running the Project 

**RUN** (any number of) servers first, then the client:

```
$ py dfs1.py 10001
$ py dfs2.py 10002
$ py dfs3.py 10003
$ py dfs4.py 10004

$ py dfc.py dfc.conf
```
	
**USERS and PASSWORDS**:

```	
Alice: Crimson33
Bob: Velvet77
Eve: Magellan101
```
		
Usernames and passwords can be changed in the configuration files. Changes must adhere to the 
spacing and syntax found in the conf files and be identical across all .conf files (dfs and dfc 
.conf files are identical except for the name).
	
The password hashing algorithm is md5. If another is desired, all the appropriate hashes must be 
recomputed in the dfc.py file (CTRL+F: 'hashlib').


## Commands


- **`[PUT]` method**:

`PUT` sends any text files located within the DFC folder into the DFS folders for distributed storage.
	
`PUT` splits files into 4 chunks, stores pairs of chunks into each server after hashing 
file and taking the modulus of the hash to ensure fair distribution, according to 
the table below. The duplication of files ensures reliability if 1 server is down.

`PUT` also lists files within the DFC folder which are available for transfer.


### File Chunk Pair Locations


|hash mod|DFS1|DFS2|DFS3|DFS4|
|:--:|:-----:|:-----:|:-----:|:-----:|
| 0  | (1,2) | (2,3) | (3,4) | (4,1) | 
| 1  | (4,1) | (1,2) | (2,3) | (3,4) |
| 2  | (3,4) | (4,1) | (1,2) | (2,3) |
| 3  | (2,3) | (3,4) | (4,1) | (1,2) |



- **`[GET]` method**:


`GET` retrieves files from the servers into a user folder within the DFC folder. 
	
`GET` joins the 4 chunks into a single file. If a single server is down, this operation can 
still succeed. If the operation fails, the file is not created and the user gets a 'Transfer failed' message.



- **`[LIST]` method**:

`LIST` provides a list of file chunks a user has stored in the server. 
From the list, a user can glean file names and specify a file to `GET`. 
If a user chooses `PUT` within `LIST`, the user can determine a file to send for distributed storage.


			
- __Note__: When prompted for a file name, specify file name without the .txt extension.


## Test Cases

1. For any user: first cases vs last case differ, as they enter different loops within code
	
2. For any number of running servers (0 through 4)
	
3. For any combination of servers:
	
	- BEFORE a user dir exists
	- AFTER user dir exists but BEFORE a file dir exists
	- AFTER user dir and file dir exist but BEFORE files exist
	- AFTER files exist but not all files
	- AFTER all dirs and files exist: Reliability of file transfer should be guaranteed with 1 server down, and in some cases for 2 servers down (consult table of chunk locations).

4. For any combination and order of commands:
		 
	- The natural order is `PUT`, `LIST`, `GET`
	- Test any order
	- Test `GET` or `PUT` within `LIST`

## Demo 

Here I show some ways to test the file system for reliability when one server is down. 
On the left are the three servers up (DFS1, DFS2, DFS3) and on the right the client (DFC).

![image: PythonDFSdemo](./images/PythonDFSdemo.gif) 


## Problems Fixed

- Concatention of usernamepassword and `buffersizechunkname`: used timeouts (`time.sleep(0.5)`)
- `LIST` error: case when there *is* a directory, i.e. user has TRIED to put files or actually put files, yet there are no files
- `GET` error: same case as above, also fixed in `GET` within `LIST`
- `GET` within list: had already sent answer ('get'), deleted code block for sending it again (as in `GET`)
- ONLY reconstruct file if all chunks are present, otherwise print/send 'Transfer failed' message
- `GET` second batch: reliability with server down, +1 file in DFC user dir (check filename)
- HASH passwords, store hashes in dfc.conf and dfs.conf
- Client-side authorization grants access to any correct username with any correct password (fixed)
- When all servers are down, exit client instead of running through the entire program

## Ideas for Future Iterations

- Populate .conf files dynamically via a `SET` method for usernames and passwords 
- Chunks stored and retrieved with every other line empty
- Less exiting out: `GOTO` equivalent?
- SALT passwords
- ENCRYPT all traffic
- Send other file types (images, etc.)
- Redo in a streaming architecture

--- 