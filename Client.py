def main(host=None, port=None):
	try:
		if host == None:
			host = input("IP address of the receiver(format: xxx.xxx.xxx.xxx): ")
		if port == None:
			port = 5001
			print('just checking... is port 5001 correct? y/n')
			if input() == 'n':
				while True:
					try:
						port = int(input('please input the port you wish to use(client port is 5004; server port is 5001): '))
						break
					except Exception as e:
						print(e)
						print("please try again or ctrl+c to cancel... (hold it)")
		import socket
		import tqdm
		import os
		import tarfile
		import Encrypt
		import Hasher

		key = Encrypt.load_key()

		def compress(tar_file, members):
			"""
			Adds files (`members`) to a tar_file and compresses it
			"""

			# open file for gzip compressed writing
			tar = tarfile.open(tar_file, mode="w:gz")

			# with progress bar
			# set the progress bar
			progress = tqdm.tqdm(members)

			for member in progress:
				# add file/folder/link to the tar file (compress)
				tar.add(member)

				# set the progress description of the progress bar
				progress.set_description(f"Compressing {member}")

			# close the file
			tar.close()

		SEPARATOR = "<SEPARATOR>"

		BUFFER_SIZE = 4096 # send 4096 bytes each time step

		# the ip address or hostname of the server, the receiver
		#host = input("IP address of the reciever(format: xxx.xxx.xxx.xxx): ")

		# the port, lets use 5001
		#port = 5001

		# the name of the file we want to send, make sure it exists
		filename = input("File to send(PATH/FILE.EXTENSION)(can be ./FILE.EXTENSION): ")

		compress('Files.tar.gz', [filename])

		filename = 'Files.tar.gz'

		fileContent = open(filename, 'rb').read()

		GennedHash = Hasher.GenerateHash(fileContent)

		print(GennedHash)

		Encrypt.encrypt(filename, key)

		# get the file size
		filesize = os.path.getsize(filename)

		# create the client socket
		s = socket.socket()

		print(f"[+] Connecting to {host}:{port}")

		s.connect((host,port))

		print("[+] Connected.")

		# send the filename and filesize
		s.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{GennedHash}".encode())


		# start sending the file
		progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

		with open(filename, "rb") as f:
			while True:
				# read the bytes from the file
				bytes_read = f.read(BUFFER_SIZE)

				if not bytes_read:
					# file transmitting is done
					break

				# we use sendall to assure transmission in
				# busy networks
				s.sendall(bytes_read)

				# update the progress bar
				progress.update(len(bytes_read))

			# close the socket
			s.close()
	except Exception as e:
		print(e)

if __name__ == '__main__':
	main()