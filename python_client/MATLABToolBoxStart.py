import socket
import datetime
import time
# KUKA iiwa robot IP and port
#KUKA_IP = "192.168.0.50"  # Replace with actual robot IP KUKA 141
KUKA_IP = "192.168.0.49"  # Replace with actual robot IP KUKA 141
LISTEN_IP = '0.0.0.0' # listen for all traffic 
KUKA_PORT = 30300  # Replace with the correct port from the document
LISTEN_PORT = 30333 # port set to default in the workbench
NUM_RETRIES = 5 # max number of total retires

class MATLABToolBoxStart():
    def __init__(self, ip, port):
        global KUKA_IP, KUKA_PORT
        KUKA_IP = ip
        KUKA_PORT = port

    def application_close(self, cur_msg_id):
        message = self.create_wakeup_message(cur_msg_id, False)
        print(message.decode('utf-8'))
        return self.send_udp_packet(KUKA_IP, KUKA_PORT, message, False) # port assugned in WB
    
    def application_start(self, cur_msg_id):
        message = self.create_wakeup_message(cur_msg_id, True)
        print(message.decode('utf-8'))
        return self.send_udp_packet(KUKA_IP, KUKA_PORT, message, True) # port assugned in WB  
    
    def _str2bool(self,v):
        #print(f"string is {v}, of type: {type(v)}")
        return v.lower() in ("True", "true", "TRUE")
    
    def resolve_err_state(self, cur_msg_id, cur_state):
        num_retry = 0
        bool_val = True
        while True:
            if cur_state: # if the app is currently set to start change it before trying
                cur_msg_id += 1
                self.application_close(cur_msg_id)
            cur_msg_id += 1
            stop_message = self.create_wakeup_message(cur_msg_id, True)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                print(f"Sent wake-up packet: {stop_message.decode('utf-8')}")
                sock.sendto(stop_message, (KUKA_IP, KUKA_PORT))
            received_msg = self.receive_udp_packet(LISTEN_IP,LISTEN_PORT)
            if received_msg is not None:
                parts = received_msg.split(";")  # Split the message by semicolon
                cur_state = str(parts[9])
                if parts[8] == "ERROR" and num_retry < NUM_RETRIES: 
                    print(f"Error state not resolved, trying {num_retry}/{NUM_RETRIES}")
                    num_retry += 1
                    time.sleep(5)
                else:
                    break
                    bool_val = False
        return cur_msg_id, bool_val
    

    def start_until_success(self, cur_msg_id):
        num_retry = 0
        cur_msg_id+= 1
        bool_val = self.application_start(cur_msg_id)
        local_retry = 0 # counter for closing application in the middle of opening
        while True and (not bool_val): # if not true try action again by setting to false
            if (num_retry < NUM_RETRIES):
                print(f"Appication starting failed, trying again: {num_retry}/{NUM_RETRIES}")
                num_retry += 1
                cur_msg_id += 1
                temp_bool = self.application_close(cur_msg_id)
                while (not temp_bool) and (local_retry < NUM_RETRIES):
                    print(f"Appication closing failed during {num_retry}/{NUM_RETRIES}, trying again {local_retry}/{NUM_RETRIES}")
                    cur_msg_id += 1
                    temp_bool = self.application_close(cur_msg_id)
                    local_retry += 1
                if not temp_bool:
                    print("Error during restarting application")
                    return False, cur_msg_id
                print("trying to start")
                cur_msg_id += 1
                bool_val = self.application_start(cur_msg_id)
            else:
                print("!!!!!!!!!!!All retries failed!!!!!!!!!!!!")
                return False, cur_msg_id
        return True, cur_msg_id
    
    def start_client(self):
        num_retry = 0
        try:
            #Get State message call
            self.send_status_udp_packet(KUKA_IP, KUKA_PORT)
            # now call listener
            received_msg = self.receive_udp_packet(LISTEN_IP,LISTEN_PORT)
            if received_msg is not None:
                # expected message: 1740621953821;36;0;1;false;false;false;false;STARTING;false;false
                parts = received_msg.split(";")  # Split the message by semicolon
                cur_msg_id = int(parts[2]) # get the Data packet counter 
                if self._str2bool(parts[4]): # check AutExt_Active - AUT mode or not
                    if self._str2bool(parts[5]): # AutExt_AppReadyToStart - if not ready restart
                        if parts[8] == "MOTIONPAUSED": # case where the motion is paused by the controller 
                            cur_msg_id+=1
                            self.start_until_success(cur_msg_id)
                            return True
                        if parts[8] == "ERROR": # check if the application has spit out an error and keep trying to stop until the error is resolved
                            print("SOlving error")
                            cur_msg_id, bool_val = self.resolve_err_state(cur_msg_id, self._str2bool(parts[9]))
                        if self._str2bool(parts[9]): # Current status of the input signal App_Start
                            print(self._str2bool(parts[9]))
                            print(parts[9])
                            if parts[8] == "RUNNING": # check if the application is already running
                                return True
                            # only reset the values if the app is not running or if there is an error
                            cur_msg_id += 1
                            bool_val = self.application_close(cur_msg_id)
                            while True and (not bool_val): # if not true try action again by setting to false
                                if (num_retry < NUM_RETRIES):
                                    print(f"Appication closing failed, trying again: {num_retry}/{NUM_RETRIES}")
                                    num_retry += 1
                                    cur_msg_id += 1
                                    bool_val = self.application_close(cur_msg_id)
                                else:
                                    return False
                            num_retry = 0 # reset value for the activation messages
                            start_bool,cur_msg_id = self.start_until_success(cur_msg_id)
                            return start_bool
                        else:
                            print(self._str2bool(parts[9]))
                            start_bool,cur_msg_id = self.start_until_success(cur_msg_id)
                            return start_bool
                    else:
                        # make sure there is not any other errors
                        if parts[8] == "ERROR": # check if the application has spit out an error and keep trying to stop until the error is resolved
                            print("SOlving error")
                            cur_msg_id, bool_val = self.resolve_err_state(cur_msg_id, self._str2bool(parts[9]))
                        cur_msg_id+=1
                        self.application_close(cur_msg_id)
                        cur_msg_id+=1
                        _, cur_msg_id = self.start_until_success(cur_msg_id)
                        return True
                return True
        except Exception as e:
            print(e)
            return False
        
    def stop_client(self):
        try:
            #Get State message call
            self.send_status_udp_packet(KUKA_IP, KUKA_PORT)
            # now call listener
            received_msg = self.receive_udp_packet(LISTEN_IP,LISTEN_PORT)
            if received_msg is not None:
                # expected message: 1740621953821;36;0;1;false;false;false;false;STARTING;false;false
                parts = received_msg.split(";")  # Split the message by semicolon
                cur_msg_id = int(parts[2]) # get the Data packet counter 
                if (not self._str2bool(parts[9])) or parts[8] != "IDLE": # Current status of the input signal App_Start
                    if parts[8] == "MOTIONPAUSED": # need to start and stop againg in this case 
                        cur_msg_id+=1
                        self.application_start(cur_msg_id)
                    cur_msg_id+= 1
                    wakeup_message = self.create_wakeup_message(cur_msg_id, False)
                    self.send_udp_packet(KUKA_IP, KUKA_PORT, wakeup_message, False) # port assugned in WB
                    print("Client Shutoff")
                else:
                    print("Client not runnning")
        except Exception as e:
            print(e)
            return False
        
    def create_wakeup_message(self, idx, bool_val):
        """Create a wake-up message for the KUKA iiwa robot."""
        timestamp = int(datetime.datetime.now().timestamp() * 1000)  # Current time in milliseconds
        message = f"{timestamp};{idx};App_Start;{str(bool_val).lower()}"  # Formatting message as per document
        return message.encode('utf-8')  # Convert to bytes for UDP transmission
    
    def create_getstate_message(self):
        """Create a wake-up message for the KUKA iiwa robot."""
        timestamp = int(datetime.datetime.now().timestamp() * 1000)  # Current time in milliseconds
        message = f"{timestamp};1;Get_State;true"  # Formatting message as per document
        return message.encode('utf-8')  # Convert to bytes for UDP transmission
    
    def send_status_udp_packet(self, ip, port):
        message = self.create_getstate_message()
        """Send a Status UDP packet to the KUKA iiwa robot."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(message, (ip, port))
                print(f"Sent wake-up packet to {ip}:{port}: {message.decode('utf-8')}")
        except Exception as e:
            print(f"Error sending UDP packet: {e}")

    def receive_udp_packet_until_status(self, status):
        """Listen for UDP packets until the 8th element says the desired status."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((LISTEN_IP, LISTEN_PORT))
                print(f"Listening for UDP packets on {LISTEN_IP}:{LISTEN_PORT}...")

                while True:
                    try:
                        data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
                        print(f"Received message from {addr}: {data.decode('utf-8')}")
                        # Check if the 8th element in the data message matches the desired status
                        message_elements = data.decode('utf-8').split(';')
                        print(message_elements[8])
                        if message_elements[8] == "ERROR" and status == "IDLE": # ignore error only if trying to close
                            if self._str2bool(message_elements[9]): # means succesfully set the state but app state is error
                                return True
                        if message_elements[8] == status:
                            if int(message_elements[3]) != 0: # this means there is an error with the controller message/application activateion
                                return False
                            print(f"Received expected status '{status}' in the message.")
                            return True
                    except Exception as e:
                        print(f"Error is: {e}")
        except Exception as e:
            print(f"Error receiving UDP packet: {e}")
            return False

    def send_udp_packet(self, ip, port, message, bool_val):
        """Send a UDP packet to the KUKA iiwa robot based on the bool value."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(message, (ip, port))
                print(f"Sent wake-up packet to {ip}:{port}: {message.decode('utf-8')}")
                
                # Based on bool_val, decide what to wait for in the response
                if bool_val:  # Wait for 'running' if bool_val is True
                    return self.receive_udp_packet_until_status("RUNNING")
                else:  # Wait for 'IDLE' if bool_val is False
                    return self.receive_udp_packet_until_status("IDLE")
        except Exception as e:
            print(f"Error sending UDP packet: {e}")
            return False
            
    def receive_udp_packet(self, ip, port):
        """Listen for UDP packets from the KUKA iiwa robot."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((ip, port))
                print(f"Listening for UDP packets on {ip}:{port}...")

                while True:
                    data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
                    print(f"Received message from {addr}: {data.decode('utf-8')}")
                    if data is not None: 
                        return data.decode('utf-8')
        except Exception as e:
            print(f"Error receiving UDP packet: {e}")
        

if __name__ == "__main__":
    obj = MATLABToolBoxStart(KUKA_IP,KUKA_PORT)
    obj.start_client()
    while True:
        obj.receive_udp_packet()
    #obj.stop_client()

    # bool_val = True
    # wakeup_message = obj.create_wakeup_message(55, bool_val)
    # obj.send_udp_packet(KUKA_IP, KUKA_PORT, wakeup_message, bool_val)
    # msg = obj.create_getstate_message()
    # obj.send_udp_packet(KUKA_IP, KUKA_PORT, msg)

    #obj.receive_udp_packet(Listen_IP, 30333)
    # print(abc)
