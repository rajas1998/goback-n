import socket
import sys
import _thread
import time
import os
import random

packet_size_min = 512/8
packet_size_max = 2048/8
ack_size = 256/8
base = 0
mutex = _thread.allocate_lock()
sender_address = ("localhost",0)
receiver_address = ("localhost",8080)
filename = sys.argv[1]
default_window = 4
timer_start = 0
timer_duration = 0.5
sleep_duration = 0.05
stop_timer = False
prob = 10

def make_packet(seq_num, size, data):
	seq_num_string = seq_num.to_bytes(4, byteorder = 'little', signed = True)
	size_string = size.to_bytes(4, byteorder = 'little', signed = True)
	return seq_num_string + size_string + data

def send(sock):
	global base
	global mutex
	global stop_timer
	global timer_start
	file = open(filename,"rb")
	packets = []
	size_of_file = os.path.getsize(filename)
	bytes_done = 0
	seq_num = 0
	while bytes_done < size_of_file:
		packet_size = random.randint(packet_size_min,packet_size_max)
		if (bytes_done + packet_size > size_of_file):
			packet_size = size_of_file - bytes_done
		bytes_done += packet_size
		data = file.read(packet_size)
		packets.append(make_packet(seq_num,packet_size,data))
		seq_num += 1
	num_packets = len(packets)
	print("I have made a total of " + str(num_packets) + " packets")
	_thread.start_new_thread(receive, (sock,))
	window_size = min(default_window,num_packets-base)

	while base < num_packets:
		mutex.acquire()
		for i in range(base, base + window_size):
			print("Sending the packet number " + str(i))
			calc_prob = random.randint(0,prob)
			if (calc_prob != 0):
				sock.sendto(packets[i],receiver_address)
		timer_start = time.time()
		stop_timer = False
		while time.time() - timer_start < timer_duration:
			mutex.release()
			time.sleep(sleep_duration)
			if (stop_timer):
				break
			mutex.acquire()
		if (stop_timer):
			window_size = min(default_window,num_packets-base)
		else:
			mutex.release()
	sock.sendto(b'',receiver_address)
	file.close()

def receive(sock):
	global mutex
	global base
	global timer_start
	global stop_timer
	while True:
		try:
			packet, _ = sock.recvfrom(1024)
			ack = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
			print("Received ack for " + str(ack))
			if (ack >= base):
				mutex.acquire()
				base = ack + 1
				stop_timer = True
				mutex.release()
		except:
			pass
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(sender_address)
    send(sock)
    sock.close()
