import requests
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

# Step 4: Prepare plot
buffer_size = int(sample_rate * 10)
data_buffer = [0] * buffer_size

fig, ax = plt.subplots()
line, = ax.plot(data_buffer)
ax.set_ylim(-3000, 3000)  # adjust as needed
ax.set_title(f"Streaming: {channel['name']} ({channel_type})")

def update_plot(frame):
    global data_buffer
    try:
        samples = requests.get(SAMPLES_URL, timeout=5).json()
        for ch in samples['channels']:
            if ch['index'] == channel_index:
                data_buffer = data_buffer[len(ch['samples']):] + ch['samples']
                break
        line.set_ydata(data_buffer)
    except Exception as e:
        print("Stream error:", e)
    return line,

ani = FuncAnimation(fig, update_plot, interval=200)
plt.show()
