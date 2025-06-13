import requests
import numpy as np
from scipy.signal import butter, filtfilt

# Configuration

class EmgTrigger:

    def __init__(self, server_ip, server_port):
        self.SERVER_URL = f"http://{server_ip}:{server_port}"
        self.HEADERS_URL = f"{self.SERVER_URL}/headers"
        self.SAMPLES_URL = f"{self.SERVER_URL}/samples"
        self.ENABLE_URL = f"{self.SERVER_URL}/enable/"
        self.DISABLE_URL = f"{self.SERVER_URL}/disable/"

        # Step 1: Get available channels
        self.response = requests.get(self.HEADERS_URL, timeout=5)
        self.channels = self.response.json()["headers"]


    def get_emg_channel(self):
        # Step 2: Select EMG channels (or prompt selection)
        print("Available Channels:")
        for i, ch in enumerate(self.channels):
            print(f"[{i}] {ch['name']} ({ch['type']})")

        self.selected_index = int(input("Enter channel index to stream: "))
        self.channel = self.channels[self.selected_index]
        self.channel_index = self.channel["index"]
        '''sample_rate = channel["samplerate"]
        channel_type = channel["type"]'''

        # Step 3: Enable the selected channel and disable all others
        requests.get(f"{self.DISABLE_URL}all")
        requests.get(f"{self.ENABLE_URL}{self.channel_index}")
        return


    def sample_get(self):
        samples = requests.get(self.SAMPLES_URL, timeout=5).json()
        return samples


    def emg_trigger_boolean(self,ch, threshold):
        trigger_boolean = False
        filtered_data = 0
        order = 4
        cutoff = 0.05
        b, a = butter(order, cutoff)

        '''samples = requests.get(self.SAMPLES_URL, timeout=5).json()
        for ch in samples['channels']:'''
        if ch['index'] == self.channel_index:
            rectified = list(map(abs, ch['samples']))
            filtered_data = filtfilt(b, a, rectified)
            for value in list(np.array(filtered_data)):
                if value > threshold:
                    trigger_boolean = True
        return trigger_boolean