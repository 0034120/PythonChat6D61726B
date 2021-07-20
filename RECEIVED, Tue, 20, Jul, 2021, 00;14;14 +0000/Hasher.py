import hashlib

def CheckHash(Content, CrossCheck):
	received_file_hash = str(hashlib.sha3_512(Content).hexdigest())
	return str(received_file_hash)==str(CrossCheck)

def GenerateHash(Content):
	return str(hashlib.sha3_512(Content).hexdigest())