import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ("192.168.0.49", 30333)

while True:
    message = b"Test packet"
    sock.sendto(message, server_addr)
    print("Sent:", message)
    time.sleep(1)
