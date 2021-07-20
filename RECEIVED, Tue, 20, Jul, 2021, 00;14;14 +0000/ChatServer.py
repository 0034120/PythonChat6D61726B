def main(IsMain=True):
	try:
		import socket
		import Server
		from threading import Thread

		serverthread = Thread(target=Server.main, args=(False,))
		serverthread.daemon = True
		serverthread.start()

		# server's IP address
		SERVER_HOST = "0.0.0.0"
		SERVER_PORT = 5002 # port we want to use
		separator_token = "<SEPARATOR>" # we will use this to separate the client name & message


		# initialize list/set of all connected client's sockets
		WhiteList = list()
		WhiteList.append('127.0.0.1')
		WhiteList.append(socket.gethostbyname(socket.gethostname()))
		BlackList = list()
		client_sockets = list()
		client_addresses = list()
		# create a TCP socket
		s = socket.socket()
		# make the port as reusable port
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# bind the socket to the address we specified
		s.bind((SERVER_HOST, SERVER_PORT))
		# listen for upcoming connections
		s.listen(5)
		print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

		def listen_for_client(cs,address,Mode=1):
			"""
			This function keep listening for a message from `cs` socket
			whenever a message is received, broadcast it to all other connected clients
			"""
			while True:
				try:
					# keep listening for a message from `cs` socket
					msg = cs.recv(1024).decode()
				except Exception as e:
					# client no longer connected
					# remove it from the set
					print(f"[!] Error: {e}")
					client_sockets.remove(cs)
					client_addresses.remove(address[0])
				else:
					#print(msg)
					#print(msg.startswith(f'{separator_token}ADDWHITELIST{separator_token}'))
					#print('nom')
					if msg.startswith(f"{separator_token}LISTCLIENT{separator_token}"):
						cs.send(f'REQUEST FROM {address}: LISTCLIENTS\n{client_addresses}'.encode())
						continue

					if msg.startswith(f"{separator_token}ADDWHITELIST{separator_token}"):# and (address == '127.0.0.1' or address == socket.gethostbyname(socket.gethostname())):
						msg = msg.split(' ')
						print("WHITELIST REQUEST RECEIVED")
						print(msg)
						print(WhiteList)
						if Mode==0:
							for i in range(1,len(msg)):
								if msg[i] in WhiteList:
									cs.send(f"ADDRESS ALREADY WHITELISTED.")
						if Mode==1:
							for i in range(1,len(msg)):
								if msg[i] in BlackList:
									BlackList.pop(BlackList.index(msg[i]))
								elif msg[i] not in BlackList:
									cs.send(f"ADDRESS IS NOT IN BLACKLIST ALREADY WHITELISTED\n\nBlacklist contains...\n\n{BlackList}")
						continue

					if msg.startswith(f"{separator_token}ADDBLACKLIST{separator_token}"):# anaad (address == '127.0.0.1' or address == socket.gethostbyname(socket.gethostname())):
						msg = msg.split(' ')
						print(msg)
						if Mode==0:
							for i in range(1,len(msg)):
								if msg[i] in WhiteList:
									WhiteList.pop(WhiteList.index(msg[i]))
								elif msg[i] not in WhiteList:
									cs.send(f'ADDRESS NOT IN WHITELIST\n\nWhitelist contains...\n\n{WhiteList}'.encode())
						if Mode==1:
							for i in range(1,len(msg)):
								if msg[i] not in BlackList:
									BlackList.append(msg[i])
								elif msg[i] in BlackList:
									cs.send(f'ADDRESS ALREADY BLACKLISTED\nBlackList contains...\n\n{BlackList}'.encode())
						continue

					else:
						# if we received a message, replace the <SEP>
						# token with ": " for nice printing
						msg = msg.replace(separator_token, ": ")
				# iterate over all connected sockets
				for client_address in client_addresses:
					if Mode==0:
						if client_address not in WhiteList:
							client_socket = client_sockets[client_addresses.index(client_address)]
							client_socket.send("You have been Blacklisted from this server sorry for the inconvenience".encode())
							client_socket.close()
							client_sockets.remove(client_socket)
							client_addresses.remove(client_address)
							print(f'[!] CLIENT HAS BEEN BLACKLISTED: {client_address[0]}')
					if Mode==1:
						if client_address in BlackList:
							client_socket = client_sockets[client_addresses.index(client_address)]
							client_socket.send("You have been Blacklisted from this server sorry for the inconvenience".encode())
							client_socket.close()
							client_sockets.remove(client_socket)
							client_addresses.remove(client_address)
							print(f"[!] CLIENT HAS BEEN BLACKLISTED: {client_address[0]}")
				for client_socket in client_sockets:
					# and send the message
					client_socket.send(msg.encode())

		def start_transfer_server():
			import Server
			try:
				Server.main()
				round1 = True
			except Exception as e:
				print(e)
				print("error restarting transfer server")

		while True:
			if IsMain==True:
				# we keep listening for new connections all the time
				client_socket, client_address = s.accept()
				print(client_address[0])
				print(client_address[0] in BlackList)
				print(BlackList)
				if client_address[0] not in BlackList:
					print(f"[+] {client_address} connected.")
					print("STEP1")
					# add the new connected client to connected sockets
					client_addresses.append(client_address[0])
					print("ADDED CLIENT ADDRESS")
					client_sockets.append(client_socket)
					print("ADDED CLIENT SOCKET")
					# start a new thread that listens for each clients messages
					t = Thread(target=listen_for_client, args=(client_socket,client_address,1,))
					print("CREATED THREAD")
					# make the thread daemon so it ends whenever the main thread ends
					t.daemon = True
					print("SET AS DAEMON")
					# start the thread
					t.start()
					print("STARTED THREAD\n\nALL STEPS COMPLETE")
					print(f"BlackList:\n{BlackList}")
				elif client_address[0] in BlackList:
					print(BlackList)
					print('\n\n')
					print(f"[!] {client_address} attempted to connect however the WhiteList Prevented a connection.\nTo WhiteList them open the client and connect on the server computer and type\n\n/WhiteList <IP ADDRESS>\n\n")
					#client_socket.shutdown(1)
					client_socket.close()
			if IsMain==False:
				client_socket, client_address = s.accept()
				print(client_address[0])
				print(client_address[0] in WhiteList)
				if client_address in WhiteList:
					print(f"[+] {client_address} connected to Private Chat Room.")
					client_addresses.append(client_address[0])
					client_sockets.append(client_socket)
					t = Thread(target=listen_for_client, args=(client_socket,client_address,0,))
					t.daemon = True
					t.start()
					print(f"WhiteList:\n{WhiteList}")

		# close client socket
		for cs in client_sockets:
			cs.close()
		# close server socket
		s.close()
	except Exception as e:
		print(e)

if __name__ == "__main__":
	main()