import socket

import datetime


# KUKA iiwa robot IP and port

#KUKA_IP = "192.168.0.50"  # Replace with actual robot IP KUKA 141

KUKA_IP = "192.168.0.49"  # Replace with actual robot IP KUKA 141

LISTEN_IP = '0.0.0.0' # listen for all traffic

KUKA_PORT = 30300  # Replace with the correct port from the document

LISTEN_PORT = 30333 # port set to default in the workbench


class SimplePortOpen():

    def __init__(self, ip, port):

        global KUKA_IP, KUKA_PORT

        KUKA_IP = ip

        KUKA_PORT = port

        self.start_client()

   

    def start_client(self):

        #Get State message call

        self.send_status_udp_packet(KUKA_IP, KUKA_PORT)

        # now call listener

        received_msg = self.receive_udp_packet()

        if received_msg is not None:

            # expected message: 1740621953821;36;0;1;false;false;false;false;STARTING;false;false

            parts = received_msg.split(";")  # Split the message by semicolon

            cur_msg_id = int(parts[2]) # get the Data packet counter

            cur_msg_id += 1

            self.application_start(cur_msg_id)    


    def string2bool(self, s):

        return s.strip().lower() in ("true", "1", "yes", "y", "t", "on")


    def create_getstate_message(self):

        """Create a wake-up message for the KUKA iiwa robot."""

        timestamp = int(datetime.datetime.now().timestamp() * 1000)  # Current time in milliseconds

        message = f"{timestamp};1;Get_State;true"  # Formatting message as per document

        return message.encode('utf-8')  # Convert to bytes for UDP transmission

   

    def create_wakeup_message(self, idx, bool_val):

        """Create a wake-up message for the KUKA iiwa robot."""

        timestamp = int(datetime.datetime.now().timestamp() * 1000)  # Current time in milliseconds

        message = f"{timestamp};{idx};App_Start;{str(bool_val).lower()}"  # Formatting message as per document

        return message.encode('utf-8')  # Convert to bytes for UDP transmission

   

    def send_udp_packet(self, ip, port, message):

        """Send a UDP packet to the KUKA iiwa robot based on the bool value."""

        try:

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

                sock.sendto(message, (ip, port))

                print(f"Sent wake-up packet to {ip}:{port}: {message.decode('utf-8')}")

        except Exception as e:

            print(f"Error sending UDP packet: {e}")

            return False

       

    def send_status_udp_packet(self, ip, port):

        message = self.create_getstate_message()

        """Send a Status UDP packet to the KUKA iiwa robot."""

        try:

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

                sock.sendto(message, (ip, port))

                print(f"Sent wake-up packet to {ip}:{port}: {message.decode('utf-8')}")

        except Exception as e:

            print(f"Error sending UDP packet: {e}")

   

    def receive_udp_packet(self):

        """Listen for UDP packets from the KUKA iiwa robot."""

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

            print(LISTEN_PORT)

            sock.bind((LISTEN_IP, LISTEN_PORT))

            print(f"Listening for UDP packets on {LISTEN_IP}:{LISTEN_PORT}...")


            while True:

                data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes

                print(f"Received message from {addr}: {data.decode('utf-8')}")

                if data is not None:

                    return data.decode('utf-8')

   

    def application_start(self, cur_msg_id):
        message = self.create_wakeup_message(cur_msg_id, True)
        return self.send_udp_packet(KUKA_IP, KUKA_PORT, message) # port assugned in WB  

   


if __name__ == "__main__":
    obj_ = SimplePortOpen(KUKA_IP, KUKA_PORT)
    while True:
        received_msg = obj_.receive_udp_packet()
        # if received_msg is not None:
            # expected message: 1740621953821;36;0;1;false;false;false;false;STARTING;false;false
            # parts = received_msg.split(";")  # Split the message by semicolon
            # station_error = parts[-1]
        #     if obj_.string2bool(station_error): # if error assume 