import socket
import sys
import random

address = ("localhost", 8080)
prob = 20
def receive_file(sock):
	filename = sys.argv[1]
	file = open(filename, "wb")

	expected_seq_num = 0
	while True:
		packet, from_address= sock.recvfrom(1024)
		if (not packet):
			break
		seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
		size = int.from_bytes(packet[4:8], byteorder = 'little', signed = True)
		if (seq_num == expected_seq_num):
			print("Got packet " + str(expected_seq_num))
			calc_prob = random.randint(0,prob)
			if (calc_prob != 0):
				sock.sendto(expected_seq_num.to_bytes(4, byteorder = 'little', signed = True) + b'', from_address)
			expected_seq_num+=1
			file.write(packet[8:])
		else:
			print("Did not get packet. sending for " + str(expected_seq_num - 1))
			temp = expected_seq_num - 1;
			calc_prob = random.randint(0,prob)
			if (calc_prob != 0):
				sock.sendto(temp.to_bytes(4, byteorder = 'little', signed = True) + b'', from_address)
	file.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(address) 
receive_file(sock)
sock.close()