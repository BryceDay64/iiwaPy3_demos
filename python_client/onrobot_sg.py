#!/usr/bin/env python3

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import time

class SG():
    def __init__(self, ip, port):
        self.client = ModbusClient(
            ip,
            port=port,
            stopbits=1,
            bytesize=8,
            parity='E',
            baudrate=115200,
            timeout=1)
        self.open_connection()
        self.max_width = self.get_gp_max_wd()
        self.min_width = self.get_gp_min_wd()
        self.set_model_id(2) # 2 is for SG - a/H
        self.set_init()
        self.set_gentle()

    def open_connection(self):
        """Opens the connection with a gripper."""
        self.client.connect()

    def close_connection(self):
        """Closes the connection with the gripper."""
        self.client.close()

    def set_target(self, command):
        if command < self.min_width:
            command = self.min_width
        elif command > self.max_width:
            command = self.max_width
        self.client.write_register(
            address=0, value=command, unit=65)
        self.set_move()

    def set_init(self):
        self.client.write_register(
            address=1, value=0x3, unit=65)  
        
    def set_move(self):
        self.client.write_register(
            address=1, value=0x1, unit=65)  
        
    def set_stop(self):
        self.client.write_register(
            address=1, value=0x2, unit=65)     
             
    def set_gentle(self):
        self.client.write_register(
            address=2, value=1, unit=65) 
    
    def set_ungentle(self):
        self.client.write_register(
            address=2, value=0, unit=65) 

    def set_model_id(self, type_id):
        self.client.write_register(
            address=3, value=type_id, unit=65)

    def get_gp_wd(self):
        result = self.client.read_holding_registers(
            address=256, count=1, unit=65) 
        return result.registers[0]

    def get_status(self):
        result = self.client.read_holding_registers(
            address=259, count=1, unit=65)
        status = format(result.registers[0], '016b')
        status_list = [0] * 7
        if int(status[-1]):
            print("A motion is ongoing so new commands are not accepted.")
            status_list[0] = 1
        return status_list

    def get_gp_max_wd(self):
        result = self.client.read_holding_registers(
            address=261, count=1, unit=65) 
        return result.registers[0]

    def get_gp_min_wd(self):
        result = self.client.read_holding_registers(
            address=262, count=1, unit=65) 
        return result.registers[0]
