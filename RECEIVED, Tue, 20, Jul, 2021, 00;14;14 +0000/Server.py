def main(local=False):
	while True:
		try:
			import socket
			import tqdm
			import os
			import Client
			import tarfile
			import Encrypt
			import Hasher
			from time import gmtime, strftime

			key = Encrypt.load_key()

			def decompress(tar_file, path, members=None):
				"""
				Extracts  `tar_file` and puts the `members` to `path`.
				If members is None, all members on `tar_file` will be extracted
				"""

				tar = tarfile.open(tar_file, mode="r:gz")
				if members is None:
					members = tar.getmembers()

				# with progress bar
				# set the progress bar
				progress = tqdm.tqdm(members)

				for member in progress:
					tar.extract(member, path=path)

					# set the progress description of the progress bar
					progress.set_description(f"Extracting {member.name}")

				# or use this
				# tar.extractall(members=members, path=path)
				# close the file
				tar.close()

			while True:

				# devices IP address
				SERVER_HOST = "0.0.0.0"

				if local:
					SERVER_PORT = 5004

				else:
					SERVER_PORT = 5001

				# receive 4096 bytes each time
				BUFFER_SIZE = 4096

				SEPARATOR = "<SEPARATOR>"

				# create the server socket
				# TCP socket
				s = socket.socket()

				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

				s.bind((SERVER_HOST, SERVER_PORT))

				# enabling our server to accept connections
				# 5 here is the number of unaccepted connections that
				# the system will allow before refusing new connections
				s.listen(5)
				while True:
					print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

					# accept connection if there is any
					client_socket, address = s.accept()

					# if below code is executed, that means the send is connected
					print(f"[+] {address} is connected.")

					# receive the file infos
					# receive using client socket, not server socket
					received = client_socket.recv(BUFFER_SIZE).decode()

					print(received)

					checker = received.split(SEPARATOR)
					print(checker)

					if checker[0] == 'PWD':
						s2 = socket.socket()
						print(address[0])
						s2.connect((address[0], 5003))
						PWD = os.getcwd()
						print(PWD)
						s2.send(PWD.encode())
						s2.shutdown(1)
						s2.close()

					if checker[0] == 'DIR':
						s2 = socket.socket()
						print(address[0])
						s2.connect((address[0], 5003))
						DIR = os.listdir(checker[1])
						print(DIR)
						s2.send(DIR.encode())
						s2.shutdown(1)
						s2.close()

					if checker[0] == 'RUpdate':
						print(address)
						Client.main(address[0], '5004', '../ApplicationFiles')

					if 'PWD' or 'DIR' or 'RUpdate' not in checker:

						filename, filesize, ReceivedHash = received.split(SEPARATOR)

						# remove absolute path if there is
						filename = os.path.basename(filename)

						# convert to integer
						filesize = int(filesize)

						# start receiving the file from the socket
						# and writing to the file stream
						progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

						with open(filename, "wb") as f:
							while True:
								# read 1024 bytes from the socket (receive)
								bytes_read = client_socket.recv(BUFFER_SIZE)

								if not bytes_read:
									# nothing is received
									# file transmitting is done
									break

								# write to the file the bytes we just received
								f.write(bytes_read)

								# update the progress bar
								progress.update(len(bytes_read))

						# close the client socket
						client_socket.close()

						# close the server socket
						s.close()

						Encrypt.decrypt(filename, key)

						fileContent = open(filename, 'rb').read()

						Genned_hash = Hasher.GenerateHash(fileContent)

						#print(Genned_hash)

						if Hasher.CheckHash(fileContent, ReceivedHash):
							date = strftime("%a, %d, %b, %Y, %H;%M;%S +0000", gmtime())
							
							decompress(filename, "../RECEIVED, "+str(date))
						else:
							print('Did not match')
							print(Hasher.CheckHash(fileContent, ReceivedHash))
							#print('\n')
							#print(fileContent)
							print(Genned_hash)
							print(ReceivedHash)
		except Exception as e:
			print(e)
if __name__ == '__main__':
	main()