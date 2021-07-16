import socket, cv2, pickle, struct, threading

class Camera:
	"""docstring for Camera"""
	def __init__(self):
		self.host = '0.0.0.0'
		self.port = 2945
		self.port2 = 2946
		self.socket_address = (self.host,self.port)

	def Server(self):
		Server_Socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		Server_Socket.bind(self.socket_address)

		Server_Socket.listen(5)

		print("LISTENING AT:",self.socket_address)

		while True:
			try:
				client_socket,addr = Server_Socket.accept()
				print("GOT CONNECTION FROM:",addr)
				if client_socket:
					Red = client_socket.recv(1024).decode().split(' ')
					CamNo = int(Red[0])
					vid = cv2.VideoCapture(CamNo)
					while vid.isOpened():
						img,frame = vid.read()
						a = pickle.dumps(frame)
						message = struct.pack("q",len(a))+a
						client_socket.sendall(message)
						#cv2.imshow('TRANSMITTING VIDEO',frame)
						key = cv2.waitKey(1) & 0xFF
			except Exception as e:
				print(e)
				try:
					vid.release()
				except Exception as e:
					print(e)
					print(len(Red))
					ClientSocket = socket.socket()
					client_socket2, addr2 = ClientSocket.connect((addr[0],Red[1]))
					client_socket2.send('ERROR'.encode())
					client_socket2.close()
				client_socket.close()
				#cv2.destroyAllWindows()

	def Client(self, host_ip=None, CameraNo=0):
		Count = 0
		PQuit = False
		BreakOut = False
		running = True
		while running:
			try:
				client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				if host_ip == None or '':
					host_ip = input("Host IP: ")

				LocalServer = socket.socket()
				LocalServer.bind((self.host,self.port2))

				def CrashReloadOnError():
					while True:
						client_socket2, addr2 = LocalServer.accept()
						chom = client_socket2.recv(1024).decode()
						if chom == 'ERROR':
							print("ERROR")

				client_socket.connect((host_ip,self.port))

				ip = socket.gethostbyname(socket.gethostname())

				port2 = self.port2

				print(str(CameraNo)+' {port2}')

				client_socket.send((str(CameraNo)+' {port2}').encode())

				data = b""
				payload_size = struct.calcsize("Q")
				while True:
					while len(data) < payload_size:
						packet = client_socket.recv(4*1024)
						if not packet:
							break
						data += packet
					packed_msg_size = data[:payload_size]
					data = data[payload_size:]
					msg_size = struct.unpack("Q",packed_msg_size)[0]

					while len(data) < msg_size:
						data += client_socket.recv(4*1024)
					frame_data = data[:msg_size]
					data = data[msg_size:]
					frame = pickle.loads(frame_data)
					cv2.imshow("received",frame)
					key = cv2.waitKey(1) & 0xFF
					if key == ord('q'):
						PQuit = True
						break
					Count = 0
				cv2.destroyAllWindows()
				client_socket.close()
				BreakOut = True
			except Exception as e:
				print(e)
				print('Error Restarting Count + 1')
				print(Count)
				Count + 1
				if PQuit == True:
					print('ree')
					BreakOut = True
				if Count > 3:
					print('oomf')
					BreakOut = True
			if BreakOut == True:
				print("break")
				running = False
				break