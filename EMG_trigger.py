import requests
import time
import numpy as np
from scipy.signal import butter, filtfilt


order = 4
cutoff = 20

b, a = butter(order, 1/cutoff)

# Configuration
SERVER_IP = "127.0.0.1"
PORT = 9220
SERVER_URL = f"http://{SERVER_IP}:{PORT}"

HEADERS_URL = f"{SERVER_URL}/headers"
SAMPLES_URL = f"{SERVER_URL}/samples"
ENABLE_URL = f"{SERVER_URL}/enable/"
DISABLE_URL = f"{SERVER_URL}/disable/"

# Step 1: Get available channels
response = requests.get(HEADERS_URL, timeout=5)
channels = response.json()["headers"]

# Step 2: Select EMG channels (or prompt selection)
print("Available Channels:")
for i, ch in enumerate(channels):
    print(f"[{i}] {ch['name']} ({ch['type']})")

selected_index = int(input("Enter channel index to stream: "))
channel = channels[selected_index]
channel_index = channel["index"]
sample_rate = channel["samplerate"]
channel_type = channel["type"]

# Step 3: Enable the selected channel and disable all others
requests.get(f"{DISABLE_URL}all")
requests.get(f"{ENABLE_URL}{channel_index}")


def emg_trigger(index):
    def_trigger = False
    if index == channel_index:
        rectified = list(map(abs, ch['samples']))
        filtered_data = filtfilt(b, a, rectified)
        print(filtered_data)
        for value in list(np.array(filtered_data)):
            if value > 400:
                def_trigger = True
    return def_trigger

trigger = False
while not trigger:
    samples = requests.get(SAMPLES_URL, timeout=5).json()
    for ch in samples['channels']:
        trigger = emg_trigger(ch['index'])
    time.sleep(0.05)
print('trigger')
