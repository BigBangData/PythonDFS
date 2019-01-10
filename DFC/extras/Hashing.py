#! /usr/bin/env python3

# Hashes a command-line given password

import hashlib 

password = input('Enter password: ')
hash=hashlib.md5()
hash.update(password.encode())
password = hash.hexdigest()
print(password)

