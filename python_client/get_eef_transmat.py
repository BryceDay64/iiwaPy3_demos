# -*- coding: utf-8 -*-
"""
KUKA iiwa Robot EEF Pose Extraction Class
A class-based implementation for controlling KUKA iiwa robots using iiwaPy3.

Based on original script by Mohammad SAFEEA (2018)
"""
import time
import numpy as np
from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

class IIWAEEFPose:
    def __init__(self, ip="192.168.0.49", port=30300, bool_toolbox_start = True): # KUKA 71
        """
        Initialize the KUKA iiwa Robot Controller.
        
        Args:
            ip (str): IP address of the KUKA robot (default: "192.168.0.49")
            port (int): Port number for connection (default: 30300)
        """
        self.ip = ip
        self.port = port
        self.wakeup = None
        self.iiwa = None
        self.connected = False
        self.bool_toolbox_start = bool_toolbox_start
        
    def start_toolbox(self):
        """
        Start the MATLAB Toolbox client.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.wakeup = MATLABToolBoxStart(self.ip, self.port)
            self.wakeup.start_client()
            time.sleep(2)  # Give time for client to initialize
            print("MATLAB Toolbox client started successfully")
            return True
        except Exception as e:
            print(f"Starting client failed with error message: {e}")
            return False
    
    def connect(self):
        """
        Connect to the KUKA iiwa robot.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.iiwa = iiwaPy3(self.ip)
            self.connected = True
            print(f"Connected to KUKA iiwa robot at {self.ip}")
            return True
        except Exception as e:
            print(f"Client running but connection failed with error message: {e}")
            self.connected = False
            return False
    
    def initialize(self):
        """
        Initialize both toolbox and robot connection.
        
        Returns:
            bool: True if both steps succeeded, False otherwise
        """
        if self.bool_toolbox_start: # only start the matlab client if prompted.
            toolbox_result = self.start_toolbox()
            if not toolbox_result:
                return False
            
        connect_result = self.connect()
        return connect_result
    
    def get_orientation(self):
        """
        Get the end effector orientation (Euler angles).
        Returns:
            list: [rx, ry, rz] orientation in radians (XYZ fixed rotation angles)
        """
        if not self.connected or self.iiwa is None:
            print("Robot not connected. Call connect() first.")
            return None
        
        try:
            ori = np.array(self.iiwa.getEEFCartizianOrientation(),dtype=float)
            return ori
        except Exception as e:
            print(f"Failed to get end effector orientation: {e}")
            return None
        
    def get_eef_pose(self):
        """
        Get the end effector pose (position and orientation) and build H.
        Returns:
            numpy.ndarray: 4x4 homogeneous transformation matrix representing pose wr
        """
        if not self.connected or self.iiwa is None:
            print("Robot not connected. Call connect() first.")
            return None
        
        # Get XYZ position and Orientation wrt base
        try:
            pos = np.array(self.iiwa.getEEFCartizianPosition(), dtype=float)/1000.0 # Convert to meters
            ori = np.array(self.iiwa.getEEFCartizianOrientation(),dtype=float)
        except Exception as e:
            print(f"Failed to get end effector pose: {e}")
            return None
        try:
            pose_matrix = self.convert_to_pose_matrix(pos, ori)
            # print(f"End effector pose: {pose_matrix}")
            return pose_matrix
        except Exception as e:
            print(f"Failed to process end effector pose: {e}")
            return None

    @staticmethod
    def convert_to_pose_matrix(position, orientation):
        """
        Convert position and orientation to a 4x4 homogeneous transformation matrix.
        
        Args:
            position (list): [x, y, z] position in mm
            orientation (list): [rx, ry, rz] orientation in radians (XYZ fixed rotation angles)
            
        Returns:
            numpy.ndarray: 4x4 homogeneous transformation matrix representing pose wrt base
        """
        # Extract position and orientation values
        x, y, z = position
        rx, ry, rz = orientation
        # Compute rotation matrices for each axis
        # Rotation around X-axis
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx), np.cos(rx)]
        ])
        
        # Rotation around Y-axis
        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
        
        # Rotation around Z-axis
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz), np.cos(rz), 0],
            [0, 0, 1]
        ])
        
        # For XYZ fixed angle convention, the rotations are applied in order: Rx * Ry * Rz
        R = Rx @ Ry @ Rz
        
        # Create the 4x4 homogeneous transformation matrix
        pose_matrix = np.eye(4)
        pose_matrix[:3, :3] = R
        pose_matrix[:3, 3] = [x, y, z] 
        
        return pose_matrix
    
    def close(self):
        """Close the connection to the robot."""
        if self.iiwa is not None:
            try:
                self.iiwa.close()
                print("Robot connection closed")
            except Exception as e:
                print(f"Error closing robot connection: {e}")
        
        self.connected = False
        self.iiwa = None


# Example usage
if __name__ == "__main__":
    # Create robot controller with default IP and port
    robot = IIWAEEFPose()
    
    try:
        # Initialize connection
        if robot.initialize():
            # Get end effector position
            pos = robot.get_eef_pose()
            # print(f"End effector position: {pos}")
            
            # Wait a moment
            time.sleep(0.1)
            
            # Additional operations can be performed here
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always close the connection when done
        robot.close()