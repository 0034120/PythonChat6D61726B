try:
	import socket
	import random
	import Client
	import Server
	import CamMain as CM
	from threading import Thread
	from datetime import datetime
	from colorama import Fore, init, Back

	# init colors
	init()

	# set the available colors
	colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
		Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
		Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
		Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
	]

	# choose a random color for the client
	client_color = random.choice(colors)

	# server's IP address
	# if the server is not on this machine,
	# put the private (network) IP address (e.g. 192.168.1.2)
	SERVER_HOST = input("Server's IP address(127.0.0.1 is this machine): ")
	SERVER_PORT = 5002 # server's port
	servhost = "0.0.0.0"
	sp = 5003
	separator_token = "<SEPARATOR>" # we will use this to separate the client name & message

	# initialize TCP socket
	s = socket.socket()
	s2 = socket.socket()
	serv = socket.socket()
	print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
	# connect to the server
	serv.bind((servhost, sp))
	serv.listen(5)
	try:
		s.connect((SERVER_HOST, SERVER_PORT))
		Chat = True
	except Exception as e:
		print(e)
		print("Check the chat server if it is offline then this program will not be able to connect")
		print("attempting to connect to transfer server (this won't do anything useful so you may as well quit)")
		Chat = False
	try:
		s2.connect((SERVER_HOST, 5001))
	except Exception as e:
		print(e)
		print("Transfer server offline unable to connect")
		if not Chat:
			quit()
	print("[+] Connnected.")

	# prompt the client for a name
	name = input("Enter your name: ")

	print('step1')

	Local_transfer_server = Thread(target=Server.main, args=(True,))
	Local_transfer_server.daemon = True
	Local_transfer_server.start()

	print('step2')

	CamServer = CM.Camera()

	print('step3')

	Local_Camera_Server = Thread(target=CamServer.Server)
	Local_Camera_Server.daemon = True
	Local_Camera_Server.start()

	print('step4')

	def listen_for_messages():
		while True:
			message = s.recv(1024).decode()
			print("\n" + message)

	# make a thread that listens for message to this client & print them
	t = Thread(target=listen_for_messages)
	# make the thread daemon so it ends whenever the main thread ends
	t.daemon = True
	# start the thread
	t.start()

	Cam = CM.Camera()

	print('type /<command> to do something or /help for a list of commands')

	while True:
		# input message we want to send to the server
		to_send = input()
		# a way to exit the program
		
		if to_send.startswith('/ViewCam'):
			try:
				Temp = to_send.split(' ')
				if len(Temp) == 2:
					Cam.Client(Temp[1])
				if len(Temp) == 3:
					Cam.Client(Temp[1],Temp[2])
				if len(Temp) > 3:
					print("TO MANY INPUTS!!!")
				if len(Temp) < 2:
					print("TO FEW INPUTS!!!")
			except Exception as e:
				print(e)
				print("\n\nError... Perhaps you forgot to specify an IP address?")

		if to_send == '/dir':
			try:
				s2.send('DIR{separator_token}'.encode())
				client_socket, address = serv.accept()
				#print(f"client_socket: {client_socket}\nAddress: {address}")
				print('\n'+client_socket.recv(1024).decode())
			except Exception as e:
				print(e)
		if to_send == '/pwd':
			try:
				s2.send('PWD'.encode())
				client_socket, address = serv.accept()
				#print(f"client_socket: {client_socket}\nAddress: {address}")
				print('\n'+client_socket.recv(1024).decode())
		
			except Exception as e:
				print(e)
		
		if to_send == '/help':
			date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print(f"""{client_color}[{date_now}] {name}: \t/transfer\n\t\t\t\t/quit\n\t\t\t\t/help\n\t\t\t\t/pwd
				\n\t\t\t\t/download\n\t\t\t\t/ChangeDir\n\t\t\t\t/dir\n\t\t\t\t/RequestUpdate\n\n\t\t\t\tIMPORTANT with /RequestUpdate make sure that you copy the new version from the received folder into the current directory otherwise it will not be a proper update{Fore.RESET}""")	

		if to_send == '/RequestUpdate':
			s2.send('RUpdate'.encode())

		if to_send.startswith('/transfer'):
			transfer_host = to_send.split(" ")
			print(transfer_host)
			#print(f"command: {transfer_host[0]}\ntransfer_host: {transfer_host[1]}")
			
			if transfer_host==['/transfer']:
				transfer_host=None
			
			else:
				transfer_host = transfer_host[1]
			Client.main(transfer_host)
		
		if to_send.startswith('/ChangeDir'):
			directory = to_send.split(' ')
			directory.pop(0)
			print(directory)
		
		if to_send == '/quit':
			break
		# the datetime, name & color of the sender
		date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		to_send = f"{client_color}[{date_now}] {name}{separator_token}{to_send}{Fore.RESET}"
		# finally, send the message
		s.send(to_send.encode())

	# close the socket
	s.close()
except Exception as e:
	print(e)